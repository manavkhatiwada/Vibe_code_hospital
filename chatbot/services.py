import base64
import mimetypes
import os
from pathlib import Path

import requests
from django.conf import settings

GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.5-flash-lite:generateContent"
)

MAX_INLINE_FILE_BYTES = 15 * 1024 * 1024  # keeps the base64 payload well under safe request-size limits
SUPPORTED_INLINE_MIME_TYPES = {
    "image/png",
    "image/jpeg",
    "image/webp",
    "image/heic",
    "image/heif",
    "application/pdf",
}

SYSTEM_PROMPT = (
    "You are a patient-facing assistant that explains the CONTENTS of an "
    "already-uploaded medical report in plain, layman's language.\n"
    "Rules you must always follow:\n"
    "1. Explain what the report says and define any medical jargon in simple terms.\n"
    "2. NEVER state or imply a diagnosis, never name a likely condition, and never "
    "recommend a specific treatment, medication, or dosage.\n"
    "3. If anything in the report looks abnormal, serious, or urgent, clearly and "
    "explicitly recommend the patient see a doctor soon, in plain language.\n"
    "4. If nothing looks concerning, reassure the patient but still note that only a "
    "licensed doctor can properly interpret or diagnose the report.\n"
    "5. Keep the tone calm, clear, and non-alarming."
)

FALLBACK_TEXT = (
    "I wasn't able to analyze your report right now. Please try again in a "
    "moment, and be sure to discuss this report directly with your doctor."
)


def _load_env_file(path):
    # Mirrors users/management/commands/bootstrap_admin.py's private helper —
    # this repo has no global dotenv loading, so root .env isn't auto-read.
    values = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _get_gemini_api_key():
    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key
    env_values = _load_env_file(Path(settings.BASE_DIR) / ".env")
    return env_values.get("GEMINI_API_KEY")


def _build_inline_part(record):
    if not record.report_file:
        return None

    try:
        size = record.report_file.size
    except (OSError, ValueError):
        return None
    if size > MAX_INLINE_FILE_BYTES:
        return None

    mime_type, _ = mimetypes.guess_type(record.report_file.name)
    if mime_type not in SUPPORTED_INLINE_MIME_TYPES:
        return None

    try:
        with record.report_file.open("rb") as fh:
            raw = fh.read()
    except (OSError, ValueError):
        return None

    encoded = base64.b64encode(raw).decode("ascii")
    return {"inline_data": {"mime_type": mime_type, "data": encoded}}


def _build_prompt_text(record, user_message_text, file_included):
    lines = [
        f"Folder: {record.folder_name or 'General'}",
        f"Patient notes on this report: {record.notes or '(none provided)'}",
    ]
    if record.report_file and not file_included:
        lines.append(
            "(A file was attached to this report but its type or size could not "
            "be read directly — base your explanation only on the notes above.)"
        )
    lines.append(f"Patient's question: {user_message_text}")
    return "\n".join(lines)


def generate_record_explanation(record, user_message_text):
    api_key = _get_gemini_api_key()
    if not api_key:
        return FALLBACK_TEXT

    inline_part = _build_inline_part(record)
    prompt_text = _build_prompt_text(record, user_message_text, inline_part is not None)

    parts = [{"text": prompt_text}]
    if inline_part:
        parts.append(inline_part)

    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 700},
    }

    try:
        response = requests.post(
            GEMINI_ENDPOINT,
            params={"key": api_key},
            json=payload,
            timeout=30,
        )
    except requests.exceptions.RequestException:
        return FALLBACK_TEXT

    if response.status_code != 200:
        return FALLBACK_TEXT

    try:
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, ValueError, TypeError):
        return FALLBACK_TEXT

    return text.strip() or FALLBACK_TEXT
