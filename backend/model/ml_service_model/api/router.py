import fastapi

from ml_service_model.api.health import HealthResponse, health
from ml_service_model.api.rest.router import router as rest_router

router = fastapi.APIRouter()
router.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse, tags=["health"])
router.include_router(rest_router)
