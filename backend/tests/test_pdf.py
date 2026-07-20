import pytest

from app.core.exceptions import ValidationAppError
from app.shared.parsing.pdf import extract_text_from_pdf


def test_extract_text_from_pdf_rejects_empty() -> None:
    with pytest.raises(ValidationAppError):
        extract_text_from_pdf(b"")


def test_extract_text_from_pdf_rejects_invalid() -> None:
    with pytest.raises(ValidationAppError):
        extract_text_from_pdf(b"not-a-pdf")
