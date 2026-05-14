from __future__ import annotations

import os
import re
import smtplib
import ssl
import time
from email.message import EmailMessage
from mimetypes import guess_type
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DOWNLOADS_DIR = BASE_DIR / "downloads"
LOCAL_ENV_FILE = BASE_DIR / "contact.local.env"

STATIC_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


def load_local_env_file(file_path: Path) -> None:
    if not file_path.is_file():
        return

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("\"'")

        if key and key not in os.environ:
            os.environ[key] = value


load_local_env_file(LOCAL_ENV_FILE)

app = FastAPI(title="AI in Actie Website")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

HTML_HEADERS = {"Cache-Control": "no-store, no-cache, must-revalidate"}
DOWNLOAD_METADATA = {
    "spelregels v7.pdf": {
        "priority": 1,
        "title": "Spelregels",
        "description": "De volledige uitleg van voorbereiding, materiaal en spelverloop.",
        "category": "Spelmateriaal",
        "badge": "PDF",
    },
    "onderzoeksrapportv6.docx": {
        "priority": 2,
        "title": "Onderzoeksrapport",
        "description": "Achtergrond, ontwerpkeuzes en didactische onderbouwing van het concept.",
        "category": "Voor leerkrachten",
        "badge": "DOCX",
    },
}
CONTACT_EMAIL = "timdemunck@skynet.be"
CONTACT_SUBJECT = "Vraag over AI in Actie"
CONTACT_FORM_SUCCESS = "Je bericht is goed verzonden. Bedankt, ik neem zo snel mogelijk contact met je op."
CONTACT_RATE_LIMIT_SECONDS = int(os.getenv("CONTACT_RATE_LIMIT_SECONDS", "45"))
CONTACT_SMTP_HOST = os.getenv("CONTACT_SMTP_HOST", "").strip()
CONTACT_SMTP_PORT = int(os.getenv("CONTACT_SMTP_PORT", "587"))
CONTACT_SMTP_USERNAME = os.getenv("CONTACT_SMTP_USERNAME", "").strip()
CONTACT_SMTP_PASSWORD = os.getenv("CONTACT_SMTP_PASSWORD", "").strip()
CONTACT_SMTP_FROM = os.getenv("CONTACT_SMTP_FROM", CONTACT_SMTP_USERNAME or CONTACT_EMAIL).strip() or CONTACT_EMAIL
CONTACT_SMTP_TO = os.getenv("CONTACT_SMTP_TO", CONTACT_EMAIL).strip() or CONTACT_EMAIL
CONTACT_SMTP_SECURITY = os.getenv("CONTACT_SMTP_SECURITY", "starttls").strip().lower()
CONTACT_REQUEST_LOG: dict[str, float] = {}
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_CONTACT_NAME_LENGTH = 120
MAX_CONTACT_EMAIL_LENGTH = 254
MAX_CONTACT_MESSAGE_LENGTH = 4000


class ContactSubmission(BaseModel):
    name: str
    email: str
    message: str
    company: str = ""


def sanitize_single_line(value: str, max_length: int) -> str:
    collapsed = " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
    return collapsed[:max_length].strip()


def sanitize_message(value: str, max_length: int) -> str:
    cleaned = str(value or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    return cleaned[:max_length]


def validate_contact_submission(payload: ContactSubmission) -> tuple[str, str, str]:
    name = sanitize_single_line(payload.name, MAX_CONTACT_NAME_LENGTH)
    email = sanitize_single_line(payload.email, MAX_CONTACT_EMAIL_LENGTH)
    message = sanitize_message(payload.message, MAX_CONTACT_MESSAGE_LENGTH)

    if not name:
        raise HTTPException(status_code=422, detail="Vul je naam in.")
    if not email or not EMAIL_PATTERN.match(email):
        raise HTTPException(status_code=422, detail="Vul een geldig e-mailadres in.")
    if not message:
        raise HTTPException(status_code=422, detail="Typ eerst een bericht.")

    return name, email, message


def assert_contact_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    now = time.time()
    last_request = CONTACT_REQUEST_LOG.get(client_host, 0.0)

    if now - last_request < CONTACT_RATE_LIMIT_SECONDS:
        raise HTTPException(
            status_code=429,
            detail="Wacht heel even voor je nog een bericht verstuurt.",
        )

    CONTACT_REQUEST_LOG[client_host] = now


def send_contact_email(name: str, email: str, message: str) -> None:
    if not CONTACT_SMTP_HOST:
        raise RuntimeError("Contactformulier is nog niet geconfigureerd op de server.")

    mail = EmailMessage()
    mail["Subject"] = CONTACT_SUBJECT
    mail["From"] = CONTACT_SMTP_FROM
    mail["To"] = CONTACT_SMTP_TO
    mail["Reply-To"] = email
    mail.set_content(
        "\n".join(
            [
                "Nieuw bericht via het contactformulier van AI in Actie",
                "",
                f"Naam: {name}",
                f"E-mailadres: {email}",
                "",
                "Bericht:",
                message,
            ]
        )
    )

    if CONTACT_SMTP_SECURITY == "ssl":
        with smtplib.SMTP_SSL(
            CONTACT_SMTP_HOST,
            CONTACT_SMTP_PORT,
            context=ssl.create_default_context(),
            timeout=20,
        ) as smtp:
            if CONTACT_SMTP_USERNAME and CONTACT_SMTP_PASSWORD:
                smtp.login(CONTACT_SMTP_USERNAME, CONTACT_SMTP_PASSWORD)
            smtp.send_message(mail)
        return

    with smtplib.SMTP(CONTACT_SMTP_HOST, CONTACT_SMTP_PORT, timeout=20) as smtp:
        if CONTACT_SMTP_SECURITY == "starttls":
            smtp.starttls(context=ssl.create_default_context())
        if CONTACT_SMTP_USERNAME and CONTACT_SMTP_PASSWORD:
            smtp.login(CONTACT_SMTP_USERNAME, CONTACT_SMTP_PASSWORD)
        smtp.send_message(mail)


def humanize_label(raw_value: str) -> str:
    cleaned = raw_value.replace("_", " ").replace("-", " ").strip()
    if not cleaned:
        return "Onbenoemd"
    return cleaned.title()


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{int(num_bytes)} B"


def build_download_url(relative_path: Path) -> str:
    return "/downloads/" + "/".join(quote(part) for part in relative_path.parts)


def iter_downloads() -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    file_paths = sorted(
        DOWNLOADS_DIR.rglob("*"),
        key=lambda path: (
            int(DOWNLOAD_METADATA.get(path.name.lower(), {}).get("priority", 999)),
            str(path).lower(),
        ),
    )
    for file_path in file_paths:
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(DOWNLOADS_DIR)
        if any(part.startswith(".") for part in relative_path.parts):
            continue

        metadata = DOWNLOAD_METADATA.get(file_path.name.lower(), {})
        top_level = relative_path.parts[0] if len(relative_path.parts) > 1 else "algemeen"
        items.append(
            {
                "title": str(metadata.get("title") or humanize_label(file_path.stem)),
                "filename": file_path.name,
                "category": str(metadata.get("category") or humanize_label(top_level)),
                "description": str(metadata.get("description") or "Download dit bestand voor de opbouw of begeleiding van het spel."),
                "badge": str(metadata.get("badge") or file_path.suffix.replace(".", "").upper() or "BESTAND"),
                "size": format_size(file_path.stat().st_size),
                "url": build_download_url(relative_path),
            }
        )

    return items


def resolve_download(file_path: str) -> Path:
    candidate = (DOWNLOADS_DIR / file_path).resolve()
    try:
        candidate.relative_to(DOWNLOADS_DIR.resolve())
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Bestand niet gevonden.") from exc

    if not candidate.is_file() or any(part.startswith(".") for part in candidate.relative_to(DOWNLOADS_DIR).parts):
        raise HTTPException(status_code=404, detail="Bestand niet gevonden.")

    return candidate


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html", headers=HTML_HEADERS)


@app.post("/api/contact")
def submit_contact_form(payload: ContactSubmission, request: Request) -> dict[str, str]:
    if payload.company.strip():
        return {"message": CONTACT_FORM_SUCCESS}

    name, email, message = validate_contact_submission(payload)

    if not CONTACT_SMTP_HOST:
        raise HTTPException(
            status_code=503,
            detail="Contactformulier is nog niet geconfigureerd op de server.",
        )

    assert_contact_rate_limit(request)

    try:
        send_contact_email(name, email, message)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Het bericht kon niet verzonden worden. Probeer het later opnieuw.",
        ) from exc

    return {"message": CONTACT_FORM_SUCCESS}


@app.get("/api/downloads")
def get_downloads() -> dict[str, list[dict[str, str]]]:
    return {"items": iter_downloads()}


@app.get("/downloads/{file_path:path}")
def serve_download(file_path: str) -> FileResponse:
    asset_path = resolve_download(file_path)
    media_type, _ = guess_type(asset_path.name)
    return FileResponse(asset_path, media_type=media_type or "application/octet-stream")
