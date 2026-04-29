import fastapi

from database_repository.dto.users import User
from ml_service_model.api.rest.dependencies import get_current_user, get_database
from ml_service_model.database.repositories import SqlAlchemyAltMLTaskRepository
from ml_service_model.database.service import Service
from ml_service_model.domains.task import MLTask


class TaskNotFoundError(Exception):
    pass


class TaskAccessDeniedError(Exception):
    pass


async def get_task(
    task_id: int = fastapi.Path(),
    user: User = fastapi.Depends(get_current_user),
    database: Service = fastapi.Depends(get_database),
) -> MLTask:
    repo = SqlAlchemyAltMLTaskRepository(database)
    task = await repo.get_by_id(task_id)
    if task is None:
        raise TaskNotFoundError(f"Task id={task_id} not found")
    if task.user.user_id != user.user_id:
        raise TaskAccessDeniedError("Access denied")
    return task
