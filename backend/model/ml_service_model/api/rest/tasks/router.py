import fastapi
from ml_service_model.api.rest.tasks import handlers
from ml_service_model.api.rest.tasks.schemas import TaskResponse

router = fastapi.APIRouter()
router.add_api_route("", handlers.list_tasks, methods=["GET"], response_model=list[TaskResponse])
router.add_api_route("", handlers.predict, methods=["POST"], response_model=TaskResponse, status_code=202)
router.add_api_route("/{task_id}", handlers.get_task_handler, methods=["GET"], response_model=TaskResponse)
