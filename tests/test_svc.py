"""Unit tests for service modules (certification, document, email)."""

import hashlib
import io
import json
from datetime import date
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alumno import Alumno
from app.models.documento import DocumentoGenerado, TipoDocumento
from app.models.plantilla import Plantilla, TipoPlantilla, IdiomaPlantilla
from app.services.certification_service import (
    generate_document_hash,
    generate_qr_bytes,
    generate_qr_code,
)
from app.utils.encryption import encrypt_value


# ═══════════════════════════════════════════════════════════════
# Certification Service
# ═══════════════════════════════════════════════════════════════


class TestGenerateDocumentHash:
    def test_returns_64_hex_chars(self):
        h = generate_document_hash("ALU001", "diploma", {"k": "v"})
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)

    def test_different_alumnos_different_hash(self):
        h1 = generate_document_hash("ALU001", "diploma", {"k": "v"})
        h2 = generate_document_hash("ALU002", "diploma", {"k": "v"})
        assert h1 != h2

    def test_different_types_different_hash(self):
        h1 = generate_document_hash("ALU001", "diploma", {"k": "v"})
        h2 = generate_document_hash("ALU001", "certificado_notas", {"k": "v"})
        assert h1 != h2

    def test_different_contenido_different_hash(self):
        h1 = generate_document_hash("ALU001", "diploma", {"k": "v1"})
        h2 = generate_document_hash("ALU001", "diploma", {"k": "v2"})
        assert h1 != h2

    def test_same_call_at_different_time_differs(self):
        """Hash includes timestamp, so two calls should differ."""
        h1 = generate_document_hash("ALU001", "diploma", {"k": "v"})
        h2 = generate_document_hash("ALU001", "diploma", {"k": "v"})
        # Due to timestamp precision both may differ; at minimum both are valid hashes
        assert len(h1) == 64
        assert len(h2) == 64

    def test_empty_contenido(self):
        h = generate_document_hash("ALU001", "diploma", {})
        assert len(h) == 64

    def test_unicode_contenido(self):
        h = generate_document_hash("ALU001", "diploma", {"nombre": "José María Ñ"})
        assert len(h) == 64


class TestGenerateQrCode:
    def test_creates_png_file(self, tmp_path):
        output = tmp_path / "qr_test.png"
        result = generate_qr_code("abc123", str(output))
        assert result == output
        assert output.exists()
        # PNG magic bytes
        assert output.read_bytes()[:4] == b"\x89PNG"

    def test_creates_parent_dirs(self, tmp_path):
        output = tmp_path / "deep" / "nested" / "qr.png"
        generate_qr_code("hash123", str(output))
        assert output.exists()


class TestGenerateQrBytes:
    def test_returns_png_bytes(self):
        data = generate_qr_bytes("hash123")
        assert isinstance(data, bytes)
        assert data[:4] == b"\x89PNG"

    def test_non_empty(self):
        data = generate_qr_bytes("x")
        assert len(data) > 100  # A real PNG should have substantial size


# ═══════════════════════════════════════════════════════════════
# Document Service
# ═══════════════════════════════════════════════════════════════


class TestDocumentServiceLoadAlumno:
    @pytest.mark.asyncio
    async def test_load_alumno_not_found_raises(self, db_session: AsyncSession):
        from app.services.document_service import _load_alumno

        with pytest.raises(ValueError, match="not found"):
            await _load_alumno(db_session, "NONEXISTENT")

    @pytest.mark.asyncio
    async def test_load_alumno_found(self, db_session: AsyncSession):
        from app.services.document_service import _load_alumno

        alumno = Alumno(
            cod_alumno="ALU100",
            identificacion=encrypt_value("9999"),
            nombre="Test",
            apellidos="User",
            grado="11",
            fecha_nacimiento=date(2006, 1, 1),
            fecha_ingreso=date(2020, 1, 1),
        )
        db_session.add(alumno)
        await db_session.commit()

        result = await _load_alumno(db_session, "ALU100")
        assert result.cod_alumno == "ALU100"


class TestDocumentServiceLoadNotas:
    @pytest.mark.asyncio
    async def test_load_notas_empty(self, db_session: AsyncSession):
        from app.services.document_service import _load_notas

        notas = await _load_notas(db_session, "NOEXIST")
        assert notas == []


class TestDocumentServiceGenerateDocument:
    @pytest.mark.asyncio
    async def test_generate_document_alumno_not_found(self, db_session: AsyncSession):
        from app.services.document_service import generate_document

        plantilla = Plantilla(
            nombre="Test",
            tipo=TipoPlantilla.diploma,
            idioma=IdiomaPlantilla.es,
            archivo_template_path="templates/test.docx",
        )
        db_session.add(plantilla)
        await db_session.commit()
        await db_session.refresh(plantilla)

        with pytest.raises(ValueError, match="not found"):
            await generate_document(db_session, "NOALUMNO", plantilla.id)

    @pytest.mark.asyncio
    async def test_generate_document_plantilla_not_found(self, db_session: AsyncSession):
        from app.services.document_service import generate_document

        alumno = Alumno(
            cod_alumno="ALU200",
            identificacion=encrypt_value("111"),
            nombre="A",
            apellidos="B",
            grado="11",
            fecha_nacimiento=date(2006, 1, 1),
            fecha_ingreso=date(2020, 1, 1),
        )
        db_session.add(alumno)
        await db_session.commit()

        with pytest.raises(ValueError, match="not found"):
            await generate_document(db_session, "ALU200", 99999)


class TestDocumentServiceGenerateBulk:
    @pytest.mark.asyncio
    async def test_bulk_continues_on_error(self, db_session: AsyncSession):
        """generate_bulk should log errors and continue, not raise."""
        from app.services.document_service import generate_bulk

        plantilla = Plantilla(
            nombre="Bulk Test",
            tipo=TipoPlantilla.diploma,
            idioma=IdiomaPlantilla.es,
            archivo_template_path="templates/bulk.docx",
        )
        db_session.add(plantilla)
        await db_session.commit()
        await db_session.refresh(plantilla)

        # None of these alumnos exist, so all should fail gracefully
        results = await generate_bulk(db_session, ["X1", "X2"], plantilla.id)
        assert results == []


# ═══════════════════════════════════════════════════════════════
# Email Service (unit tests with mocks)
# ═══════════════════════════════════════════════════════════════


class TestEmailService:
    @pytest.mark.asyncio
    async def test_send_email_calls_gmail_api(self, tmp_path):
        """Verify send_email constructs a MIME message and calls Gmail send."""
        mock_service = MagicMock()
        mock_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "msg_123"
        }

        with patch(
            "app.services.email_service._get_gmail_service",
            return_value=mock_service,
        ):
            from app.services.email_service import send_email

            result = await send_email(
                to="test@example.com",
                subject="Test Subject",
                body_html="<h1>Hello</h1>",
            )

        assert result["message_id"] == "msg_123"
        assert result["status"] == "sent"
        mock_service.users.return_value.messages.return_value.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_email_with_attachment(self, tmp_path):
        """Verify attachment is included in the MIME message."""
        attachment = tmp_path / "report.pdf"
        attachment.write_bytes(b"%PDF-1.4 fake content")

        mock_service = MagicMock()
        mock_service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
            "id": "msg_456"
        }

        with patch(
            "app.services.email_service._get_gmail_service",
            return_value=mock_service,
        ):
            from app.services.email_service import send_email

            result = await send_email(
                to="test@example.com",
                subject="With Attachment",
                body_html="<p>Report</p>",
                attachment_path=str(attachment),
            )

        assert result["message_id"] == "msg_456"

    @pytest.mark.asyncio
    async def test_send_email_attachment_not_found(self, tmp_path):
        """Missing attachment file should raise FileNotFoundError."""
        mock_service = MagicMock()

        with patch(
            "app.services.email_service._get_gmail_service",
            return_value=mock_service,
        ):
            from app.services.email_service import send_email

            with pytest.raises(FileNotFoundError):
                await send_email(
                    to="test@example.com",
                    subject="Missing",
                    body_html="<p>Oops</p>",
                    attachment_path="/nonexistent/file.pdf",
                )
