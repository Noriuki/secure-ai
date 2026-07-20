from fastapi import APIRouter

from app.modules.audit.router import router as audit_router
from app.modules.conversations.router import router as conversations_router
from app.modules.documents.router import router as documents_router
from app.modules.health.router import router as health_router
from app.modules.workspaces.router import router as workspaces_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(workspaces_router)
api_router.include_router(documents_router)
api_router.include_router(conversations_router)
api_router.include_router(audit_router)
