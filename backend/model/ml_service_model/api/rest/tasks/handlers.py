from datetime import datetime, timezone

import fastapi

from database_repository.dto.users import User
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_common.messaging.schemas import PredictTaskMessage
from ml_service_model.api.rest.dependencies import get_current_user, get_database, get_publisher
from ml_service_model.api.rest.tasks.dependencies import get_task
from ml_service_model.api.rest.tasks.schemas import PredictRequest, TaskResponse
from ml_service_model.database.repositories import (
    SqlAlchemyAltMLModelRepository,
    SqlAlchemyAltMLTaskRepository,
    SqlAlchemyAltPredictionResultRepository,
)
from ml_service_model.database.service import Service
from ml_service_model.domains.task import MLTask
from ml_service_model.services.task_service import ModelInactiveError, ModelNotFoundError, TaskService


async def predict(
    data: PredictRequest = fastapi.Body(embed=False),
    user: User = fastapi.Depends(get_current_user),
    database: Service = fastapi.Depends(get_database),
    publisher: RabbitMQPublisher = fastapi.Depends(get_publisher),
) -> TaskResponse:
    model_repo = SqlAlchemyAltMLModelRepository(database)
    task_repo = SqlAlchemyAltMLTaskRepository(database)
    result_repo = SqlAlchemyAltPredictionResultRepository(database)
    task_service = TaskService(
        task_repository=task_repo,
        model_repository=model_repo,
        result_repository=result_repo,
    )
    task = await task_service.create_task(user=user, model_id=data.model_id, input_data=data.input_data)

    message = PredictTaskMessage(
        task_id=task.task_id,
        model_id=task.model.model_id,
        user_id=user.user_id,
        model_name=task.model.name,
        input_data=data.input_data,
        submitted_at=datetime.now(timezone.utc),
    )
    await publisher.publish(message)

    return TaskResponse.from_domain(task)


async def get_task_handler(task: MLTask = fastapi.Depends(get_task)) -> TaskResponse:
    return TaskResponse.from_domain(task)


async def list_tasks(
    user: User = fastapi.Depends(get_current_user),
    database: Service = fastapi.Depends(get_database),
) -> list[TaskResponse]:
    repo = SqlAlchemyAltMLTaskRepository(database)
    tasks = await repo.list_by_user(user.user_id)
    return [TaskResponse.from_domain(t) for t in tasks]
