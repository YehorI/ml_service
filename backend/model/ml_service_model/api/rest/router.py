import fastapi

from ml_service_model.api.rest.models.router import router as models_router
from ml_service_model.api.rest.tasks.router import router as tasks_router

router = fastapi.APIRouter()
router.include_router(models_router, prefix="/models", tags=["models"])
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
