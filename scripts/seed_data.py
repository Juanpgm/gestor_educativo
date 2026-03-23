"""Seed the local database with ~100 realistic test records."""

import asyncio
import os
import random
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("ENV_FILE", "secrets/.env")

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import hash_password
from app.database import AsyncSessionLocal, engine
from app.models.alumno import Alumno, alumno_tutores
from app.models.curso import Curso
from app.models.docente import Docente, docente_materias
from app.models.materia import Materia, materia_grados
from app.models.nota import Nota
from app.models.periodo import PeriodoAcademico
from app.models.tutor import Tutor
from app.models.usuario import UserRole, Usuario
from app.utils.encryption import encrypt_value

random.seed(42)

# ── Helper data ──────────────────────────────────────────────

NOMBRES_M = [
    "Carlos", "Juan", "Pedro", "Miguel", "Luis", "Andrés", "Jorge", "Diego",
    "Fernando", "Ricardo", "Santiago", "Mateo", "Sebastián", "Daniel", "Alejandro",
    "Gabriel", "David", "Nicolás", "Samuel", "Emilio",
]
NOMBRES_F = [
    "María", "Ana", "Laura", "Sofía", "Valentina", "Camila", "Isabella", "Lucía",
    "Gabriela", "Paula", "Andrea", "Carolina", "Diana", "Elena", "Natalia",
    "Daniela", "Mariana", "Juliana", "Sara", "Catalina",
]
APELLIDOS = [
    "García", "Rodríguez", "Martínez", "López", "González", "Hernández",
    "Pérez", "Sánchez", "Ramírez", "Torres", "Flores", "Rivera", "Gómez",
    "Díaz", "Cruz", "Morales", "Reyes", "Gutiérrez", "Ortiz", "Ramos",
    "Vargas", "Castillo", "Mendoza", "Rojas", "Herrera", "Medina",
    "Aguilar", "Castro", "Vega", "Ruiz",
]

GRADOS = [
    "1ro Primaria", "2do Primaria", "3ro Primaria", "4to Primaria",
    "5to Primaria", "6to Primaria", "1ro Secundaria", "2do Secundaria",
    "3ro Secundaria",
]

PARENTESCOS = ["Padre", "Madre", "Abuelo", "Abuela", "Tío", "Tía", "Hermano", "Hermana"]

MATERIAS_DATA = [
    ("MAT-001", "Matemáticas"),
    ("LEN-001", "Lenguaje y Comunicación"),
    ("CNA-001", "Ciencias Naturales"),
    ("CSO-001", "Ciencias Sociales"),
    ("ING-001", "Inglés"),
    ("EFI-001", "Educación Física"),
    ("ART-001", "Artes Plásticas"),
    ("MUS-001", "Música"),
    ("INF-001", "Informática"),
    ("ETI-001", "Ética y Valores"),
]


def rand_name():
    pool = NOMBRES_M + NOMBRES_F
    return random.choice(pool)


def rand_cedula():
    return f"{random.randint(100000000, 999999999)}"


def rand_phone():
    return f"+593 9{random.randint(10000000, 99999999)}"


def rand_email(nombre: str, apellido: str, domain: str = "mail.com"):
    tag = random.randint(1, 999)
    return f"{nombre.lower()}.{apellido.lower()}{tag}@{domain}"


def rand_date(start_year: int, end_year: int) -> date:
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


async def seed(db: AsyncSession):
    # Check if data already exists
    result = await db.execute(text("SELECT count(*) FROM usuarios"))
    count = result.scalar()
    if count and count > 0:
        print(f"⚠️  La base de datos ya tiene {count} usuarios. Abortando seed.")
        print("   Para re-poblar, vacía las tablas primero.")
        return

    print("🌱 Sembrando datos de prueba...")

    # ── 1. Usuarios (5) ─────────────────────────────────────
    usuarios = []
    user_specs = [
        ("admin@gestor.edu", "Admin", "Sistema", UserRole.admin),
        ("secretaria@gestor.edu", "Rosa", "Mejía", UserRole.secretaria),
        ("docente1@gestor.edu", "Carlos", "García", UserRole.docente),
        ("docente2@gestor.edu", "Ana", "Martínez", UserRole.docente),
        ("docente3@gestor.edu", "Pedro", "López", UserRole.docente),
    ]
    hashed_pw = hash_password("Test1234!")
    for email, nombre, apellido, rol in user_specs:
        u = Usuario(
            email=email,
            password_hash=hashed_pw,
            nombre=nombre,
            apellidos=apellido,
            rol=rol,
            activo=True,
        )
        db.add(u)
        usuarios.append(u)
    await db.flush()
    print(f"   ✅ {len(usuarios)} usuarios creados (contraseña: Test1234!)")

    # ── 2. Periodos académicos (4) ──────────────────────────
    periodos = []
    periodos_data = [
        ("2025-Q1", "Primer Quimestre 2025", 2025, date(2025, 2, 3), date(2025, 6, 27)),
        ("2025-Q2", "Segundo Quimestre 2025", 2025, date(2025, 9, 1), date(2026, 1, 16)),
        ("2026-Q1", "Primer Quimestre 2026", 2026, date(2026, 2, 2), date(2026, 6, 26)),
        ("2026-Q2", "Segundo Quimestre 2026", 2026, date(2026, 9, 1), date(2027, 1, 15)),
    ]
    for cod, nombre, anio, fi, ff in periodos_data:
        p = PeriodoAcademico(
            cod_periodo=cod, nombre=nombre, anio=anio,
            fecha_inicio=fi, fecha_fin=ff, activo=(anio == 2026),
        )
        db.add(p)
        periodos.append(p)
    await db.flush()
    print(f"   ✅ {len(periodos)} periodos académicos creados")

    # ── 3. Cursos (9) ───────────────────────────────────────
    cursos = []
    for i, grado in enumerate(GRADOS, start=1):
        c = Curso(
            cod_curso=f"CUR-{i:03d}",
            nombre_curso=f"Curso {grado}",
            descripcion=f"Grupo principal de {grado}",
            grado=grado,
            activo=True,
        )
        db.add(c)
        cursos.append(c)
    await db.flush()
    print(f"   ✅ {len(cursos)} cursos creados")

    # ── 4. Materias (10) ────────────────────────────────────
    materias = []
    for cod, nombre in MATERIAS_DATA:
        m = Materia(
            cod_materia=cod,
            nombre_materia=nombre,
            descripcion=f"Asignatura de {nombre}",
            activo=True,
        )
        db.add(m)
        materias.append(m)
    await db.flush()

    # Assign grados to materias
    for m in materias:
        assigned_grados = random.sample(GRADOS, k=random.randint(3, len(GRADOS)))
        for g in assigned_grados:
            await db.execute(
                materia_grados.insert().values(cod_materia=m.cod_materia, grado=g)
            )
    await db.flush()
    print(f"   ✅ {len(materias)} materias creadas (con grados asignados)")

    # ── 5. Docentes (10) ────────────────────────────────────
    docentes = []
    for i in range(1, 11):
        nombre = random.choice(NOMBRES_M + NOMBRES_F)
        apellido = random.choice(APELLIDOS)
        d = Docente(
            cod_docente=f"DOC-{i:03d}",
            identificacion=encrypt_value(rand_cedula()),
            nombre=nombre,
            apellidos=apellido,
            fecha_nacimiento=rand_date(1970, 1995),
            fecha_ingreso=rand_date(2015, 2024),
            email=encrypt_value(rand_email(nombre, apellido, "escuela.edu")),
            telefono=encrypt_value(rand_phone()),
            direccion=encrypt_value(f"Calle {random.randint(1,50)} y Av. {random.choice(APELLIDOS)}"),
        )
        db.add(d)
        docentes.append(d)
    await db.flush()

    # Assign materias to docentes for active periods
    active_periodos = [p for p in periodos if p.activo]
    for d in docentes:
        assigned = random.sample(materias, k=random.randint(1, 3))
        for m in assigned:
            for p in active_periodos:
                await db.execute(
                    docente_materias.insert().values(
                        cod_docente=d.cod_docente,
                        cod_materia=m.cod_materia,
                        cod_periodo=p.cod_periodo,
                    )
                )
    await db.flush()
    print(f"   ✅ {len(docentes)} docentes creados (con materias asignadas)")

    # ── 6. Tutores (15) ─────────────────────────────────────
    tutores = []
    for i in range(1, 16):
        nombre = random.choice(NOMBRES_M + NOMBRES_F)
        apellido = random.choice(APELLIDOS)
        t = Tutor(
            cod_tutor=f"TUT-{i:03d}",
            identificacion=encrypt_value(rand_cedula()),
            nombre=nombre,
            apellidos=apellido,
            parentesco=random.choice(PARENTESCOS),
            fecha_nacimiento=rand_date(1965, 1995),
            email=encrypt_value(rand_email(nombre, apellido)),
            telefono=encrypt_value(rand_phone()),
            direccion=encrypt_value(f"Calle {random.randint(1,80)} y Av. {random.choice(APELLIDOS)}"),
        )
        db.add(t)
        tutores.append(t)
    await db.flush()
    print(f"   ✅ {len(tutores)} tutores creados")

    # ── 7. Alumnos (30) ─────────────────────────────────────
    alumnos = []
    for i in range(1, 31):
        nombre = random.choice(NOMBRES_M + NOMBRES_F)
        apellido = random.choice(APELLIDOS)
        grado = random.choice(GRADOS)
        a = Alumno(
            cod_alumno=f"ALU-{i:03d}",
            identificacion=encrypt_value(rand_cedula()),
            nombre=nombre,
            apellidos=apellido,
            grado=grado,
            fecha_nacimiento=rand_date(2010, 2018),
            fecha_ingreso=rand_date(2022, 2025),
            email=encrypt_value(rand_email(nombre, apellido, "estudiante.edu") if random.random() > 0.3 else ""),
            telefono=encrypt_value(rand_phone() if random.random() > 0.4 else ""),
            direccion=encrypt_value(f"Calle {random.randint(1,100)} y Av. {random.choice(APELLIDOS)}"),
        )
        db.add(a)
        alumnos.append(a)
    await db.flush()

    # Assign tutores to alumnos
    for a in alumnos:
        assigned_tutors = random.sample(tutores, k=random.randint(1, 2))
        for t in assigned_tutors:
            await db.execute(
                alumno_tutores.insert().values(
                    cod_alumno=a.cod_alumno, cod_tutor=t.cod_tutor
                )
            )
    await db.flush()
    print(f"   ✅ {len(alumnos)} alumnos creados (con tutores asignados)")

    # ── 8. Notas (~100+) ────────────────────────────────────
    notas_count = 0
    # For each alumno, assign 3-5 materias across active periods
    for a in alumnos:
        n_materias = random.randint(3, 5)
        selected_materias = random.sample(materias, k=n_materias)
        for m in selected_materias:
            for p in active_periodos:
                nota_val = Decimal(str(round(random.uniform(4.0, 10.0), 2)))
                n = Nota(
                    cod_alumno=a.cod_alumno,
                    cod_materia=m.cod_materia,
                    cod_periodo=p.cod_periodo,
                    nota=nota_val,
                )
                db.add(n)
                notas_count += 1
    await db.flush()
    print(f"   ✅ {notas_count} notas creadas")

    await db.commit()

    total = (
        len(usuarios) + len(periodos) + len(cursos) + len(materias)
        + len(docentes) + len(tutores) + len(alumnos) + notas_count
    )
    print(f"\n🎉 Seed completado: {total} registros totales insertados.")
    print("\n📋 Resumen:")
    print(f"   Usuarios:  {len(usuarios):>4}  (admin@gestor.edu / Test1234!)")
    print(f"   Periodos:  {len(periodos):>4}")
    print(f"   Cursos:    {len(cursos):>4}")
    print(f"   Materias:  {len(materias):>4}")
    print(f"   Docentes:  {len(docentes):>4}")
    print(f"   Tutores:   {len(tutores):>4}")
    print(f"   Alumnos:   {len(alumnos):>4}")
    print(f"   Notas:     {notas_count:>4}")
    print(f"   {'─' * 20}")
    print(f"   TOTAL:     {total:>4}")


async def main():
    print("=" * 60)
    print("  Gestor Educativo — Seed de datos de prueba")
    print("=" * 60)
    settings = get_settings()
    print(f"  DB: {settings.database_url.split('@')[1] if '@' in settings.database_url else settings.database_url}")
    print("=" * 60)

    async with AsyncSessionLocal() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
