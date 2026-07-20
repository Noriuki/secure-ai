from app.integrations.pii.presidio import PresidioPiiProcessor
from app.integrations.pii.protocols import PiiProcessor


def get_pii_processor() -> PiiProcessor:
    return PresidioPiiProcessor()
