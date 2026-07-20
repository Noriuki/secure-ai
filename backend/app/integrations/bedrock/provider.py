from app.integrations.bedrock.client import BedrockRag
from app.integrations.bedrock.protocols import RagPort


def get_rag() -> RagPort:
    return BedrockRag()
