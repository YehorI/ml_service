import fastapi

from ml_service_model.api.health import HealthResponse, health

router = fastapi.APIRouter()
router.add_api_route("/health", health, methods=["GET"], response_model=HealthResponse, tags=["health"])
