"""Safe delivery adapter for account-recovery codes."""
from __future__ import annotations

import os
import re
from email.message import EmailMessage
from smtplib import SMTP, SMTP_SSL
from ssl import create_default_context


class DeliveryUnavailable(RuntimeError):
    """Raised when a configured delivery provider cannot deliver a code."""


def _email_configured() -> bool:
    provider = os.getenv("SECURITY_EMAIL_PROVIDER", "resend").strip().lower()
    if provider == "smtp":
        return all(os.getenv(key, "").strip() for key in ("SECURITY_FROM_EMAIL", "SMTP_HOST", "SMTP_USERNAME", "SMTP_PASSWORD"))
    return provider == "resend" and bool(os.getenv("SECURITY_FROM_EMAIL", "").strip() and os.getenv("RESEND_API_KEY", "").strip())


def send_code(channel: str, destination: str, code: str, delivery_id: str) -> None:
    if channel != "email" or not _email_configured() or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", destination):
        raise DeliveryUnavailable("delivery_not_configured")
    body = f"Tu código de seguridad SmartResto es {code}. Vence en 10 minutos. No lo compartas."
    provider = os.getenv("SECURITY_EMAIL_PROVIDER", "resend").strip().lower()
    try:
        if provider == "smtp":
            port = int(os.getenv("SMTP_PORT", "587"))
            server = SMTP_SSL(os.environ["SMTP_HOST"], port, timeout=15, context=create_default_context()) if port == 465 else SMTP(os.environ["SMTP_HOST"], port, timeout=15)
            with server:
                if port != 465:
                    server.starttls(context=create_default_context())
                server.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
                message = EmailMessage()
                message["From"] = os.environ["SECURITY_FROM_EMAIL"]
                message["To"] = destination
                message["Subject"] = "Código de seguridad SmartResto"
                message.set_content(body)
                server.send_message(message)
        else:
            import requests
            response = requests.post("https://api.resend.com/emails", headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY']}", "Idempotency-Key": delivery_id}, json={"from": os.environ["SECURITY_FROM_EMAIL"], "to": [destination], "subject": "Código de seguridad SmartResto", "text": body}, timeout=15, allow_redirects=False)
            if response.status_code not in {200, 201, 202}:
                raise DeliveryUnavailable("email_rejected")
    except DeliveryUnavailable:
        raise
    except Exception as exc:
        raise DeliveryUnavailable("delivery_failed") from exc
