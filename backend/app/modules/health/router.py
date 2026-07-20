from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.health.schemas import HealthResponse
from app.modules.health.service import HealthService, get_health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(
    service: Annotated[HealthService, Depends(get_health_service)],
) -> HealthResponse:
    return service.check()
