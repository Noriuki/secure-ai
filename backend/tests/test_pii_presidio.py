from uuid import uuid4

from app.integrations.pii.presidio import PresidioPiiProcessor


def test_presidio_text_anonymize(monkeypatch) -> None:
    def fake_analyze(self, text: str) -> list[dict]:
        email = "maria@demo.com"
        start = text.index(email)
        return [
            {
                "start": start,
                "end": start + len(email),
                "entity_type": "EMAIL_ADDRESS",
                "score": 0.9,
            }
        ]

    monkeypatch.setattr(PresidioPiiProcessor, "_analyze_text", fake_analyze)
    processor = PresidioPiiProcessor()
    result = processor.anonymize("Contato: maria@demo.com", document_id=uuid4())
    assert "{{PII_EMAIL_ADDRESS_1}}" in result.text
    assert result.matches[0].original_value == "maria@demo.com"
