"""Envio del reporte por correo (SMTP). Credenciales SOLO por variables de entorno."""

from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


class EmailConfigError(RuntimeError):
    """Falta configuracion SMTP en el entorno."""


def _env(name: str, required: bool = True, default: str | None = None) -> str | None:
    val = os.environ.get(name, default)
    if required and not val:
        raise EmailConfigError(
            f"Falta la variable de entorno {name}. "
            "Configura SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS y SMTP_FROM."
        )
    return val


def send_report(
    *,
    to: list[str],
    subject: str,
    html_body: str,
    attachments: list[str | Path] | None = None,
) -> None:
    """Envia el reporte HTML con adjuntos opcionales via SMTP + STARTTLS."""
    host = _env("SMTP_HOST")
    port = int(_env("SMTP_PORT", required=False, default="587"))
    user = _env("SMTP_USER")
    password = _env("SMTP_PASS")
    sender = _env("SMTP_FROM")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg.set_content("Tu cliente no soporta HTML. Abre el adjunto del reporte.")
    msg.add_alternative(html_body, subtype="html")

    for att in attachments or []:
        path = Path(att)
        if not path.exists():
            continue
        data = path.read_bytes()
        msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=path.name)

    context = ssl.create_default_context()
    with smtplib.SMTP(host, port, timeout=30) as server:
        server.starttls(context=context)
        server.login(user, password)
        server.send_message(msg)
