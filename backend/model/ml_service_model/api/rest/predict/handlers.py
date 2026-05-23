import uuid
from datetime import datetime, timezone

import fastapi
from database_repository.dto.users import User
from database_repository.models import MLModelORM, MLTaskORM
from database_repository.models.task import TaskStatusORM
from ml_service_common.messaging.publisher import RabbitMQPublisher
from ml_service_common.messaging.schemas import WorkerTaskMessage
from ml_service_model.api.rest.dependencies import (get_current_user,
                                                    get_database,
                                                    get_worker_publisher)
from ml_service_model.api.rest.predict.schemas import (PredictRequest,
                                                       PredictResponse)
from ml_service_model.database.service import Service
from sqlalchemy import select


class ModelNotFoundError(Exception):
    pass


async def submit_predict(
    data: PredictRequest,
    current_user: User = fastapi.Depends(get_current_user),
    database: Service = fastapi.Depends(get_database),
    worker_publisher: RabbitMQPublisher = fastapi.Depends(get_worker_publisher),
) -> PredictResponse:
    task_uuid = str(uuid.uuid4())

    model_orm = (
        await database.session.execute(
            select(MLModelORM).where(
                MLModelORM.name == data.model,
                MLModelORM.is_active.is_(True),
            )
        )
    ).scalar_one_or_none()

    if model_orm is None:
        raise ModelNotFoundError(f"Model {data.model!r} not found or inactive")

    task_orm = MLTaskORM(
        user_id=current_user.user_id,
        model_id=model_orm.id,
        input_data={"_task_uuid": task_uuid, **data.features},
        status=TaskStatusORM.PENDING,
    )
    database.session.add(task_orm)

    message = WorkerTaskMessage(
        task_id=task_uuid,
        features=data.features,
        model=data.model,
        timestamp=datetime.now(timezone.utc),
    )
    await worker_publisher.publish(message)

    return PredictResponse(task_id=task_uuid, status="queued")
