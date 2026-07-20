from typing import Annotated

from fastapi import APIRouter, Depends

from app.modules.audit.schemas import DashboardResponse
from app.modules.audit.service import AuditService, get_audit_service

router = APIRouter(tags=["audit"])


@router.get("/dashboard", response_model=DashboardResponse)
def get_dashboard(
    service: Annotated[AuditService, Depends(get_audit_service)],
) -> DashboardResponse:
    return service.dashboard()
