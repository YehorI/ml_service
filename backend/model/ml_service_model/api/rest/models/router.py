import fastapi
from ml_service_model.api.rest.models import handlers
from ml_service_model.api.rest.models.schemas import ModelResponse

router = fastapi.APIRouter()
router.add_api_route("", handlers.list_models, methods=["GET"], response_model=list[ModelResponse])
