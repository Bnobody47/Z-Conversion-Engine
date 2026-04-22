from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmailMessage:
    to_email: str
    subject: str
    body: str


def send_email(message: EmailMessage) -> dict:
    """
    Adapter boundary for Resend/MailerSend integration.
    Replace this stub with a real provider client.
    """
    return {"status": "queued", "provider": "stub", "to": message.to_email}
