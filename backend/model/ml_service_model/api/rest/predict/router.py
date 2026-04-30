import fastapi
from ml_service_model.api.rest.predict.handlers import submit_predict
from ml_service_model.api.rest.predict.schemas import PredictResponse

router = fastapi.APIRouter()
router.add_api_route("", submit_predict, methods=["POST"], response_model=PredictResponse, status_code=202)
