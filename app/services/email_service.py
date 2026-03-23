"""Gmail API service: OAuth2 authentication and send emails with attachments."""

import base64
import json
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_gmail_service():
    """Authenticate and return a Gmail API service."""
    settings = get_settings()
    token_path = Path(settings.gmail_token_path)
    creds_path = Path(settings.gmail_credentials_path)

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"Gmail credentials not found at {creds_path}. "
                    "Download from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


async def send_email(
    to: str,
    subject: str,
    body_html: str,
    attachment_path: str | Path | None = None,
) -> dict:
    """Send an email via Gmail API, optionally with one attachment."""
    service = _get_gmail_service()

    message = MIMEMultipart()
    message["to"] = to
    message["subject"] = subject
    message.attach(MIMEText(body_html, "html"))

    if attachment_path:
        attachment_path = Path(attachment_path)
        if not attachment_path.exists():
            raise FileNotFoundError(f"Attachment not found: {attachment_path}")

        with open(attachment_path, "rb") as f:
            part = MIMEApplication(f.read(), Name=attachment_path.name)
        part["Content-Disposition"] = f'attachment; filename="{attachment_path.name}"'
        message.attach(part)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    result = service.users().messages().send(userId="me", body={"raw": raw}).execute()

    logger.info("email_sent", to=to, subject=subject, message_id=result.get("id"))
    return {"message_id": result.get("id"), "status": "sent"}
