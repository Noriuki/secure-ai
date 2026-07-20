from app.core.config import Settings, get_settings
from app.modules.health.schemas import HealthResponse


class HealthService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def check(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=self._settings.app_name,
            version=self._settings.app_version,
        )


def get_health_service() -> HealthService:
    return HealthService()
