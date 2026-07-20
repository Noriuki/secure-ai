from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader

from app.core.exceptions import ValidationAppError


def extract_text_from_pdf(data: bytes) -> str:
    if not data:
        raise ValidationAppError("PDF vazio")

    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:  # noqa: BLE001
        raise ValidationAppError("Não foi possível ler o PDF") from exc

    parts: list[str] = []
    for page in reader.pages:
        try:
            text = page.extract_text() or ""
        except Exception:  # noqa: BLE001
            continue
        cleaned = text.strip()
        if cleaned:
            parts.append(cleaned)

    combined = "\n\n".join(parts).strip()
    if not combined:
        raise ValidationAppError(
            "PDF sem texto extraível (pode ser só imagem/escaneado)",
        )
    return combined
