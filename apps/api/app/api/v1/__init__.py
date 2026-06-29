from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.workspaces import router as workspaces_router
from app.api.v1.projects import router as projects_router
from app.api.v1.generation import router as generation_router
from app.api.v1.domains import router as domains_router
from app.api.v1.trademarks import router as trademarks_router
from app.api.v1.exports import router as exports_router
from app.api.v1.feature_flags import router as feature_flags_router
from app.api.v1.metrics import router as metrics_router
from app.api.v1.billing import router as billing_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.collaboration import router as collaboration_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.search import router as search_router
from app.api.v1.activity import router as activity_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(workspaces_router)
router.include_router(projects_router)
router.include_router(generation_router)
router.include_router(domains_router)
router.include_router(trademarks_router)
router.include_router(exports_router)
router.include_router(feature_flags_router)
router.include_router(metrics_router)
router.include_router(billing_router)
router.include_router(webhooks_router)
router.include_router(collaboration_router)
router.include_router(notifications_router)
router.include_router(search_router)
router.include_router(activity_router)
