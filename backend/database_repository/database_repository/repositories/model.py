from sqlalchemy import select

from database_repository.models import MLModelORM, MLTaskORM, PredictionResultORM, UserORM
from database_repository.models.task import TaskStatusORM
from database_repository.repositories._mappers import (
    to_domain_prediction_result,
    to_domain_task,
    to_domain_user,
)
from ml_service_common.sqlalchemy.service import Service
from model.domains.stored_model import StoredMLModel
from model.domains.task import MLTask, PredictionResult
from model.interfaces.repositories import (
    MLModelRepository,
    MLTaskRepository,
    PredictionResultRepository,
)


class SqlAlchemyMLModelRepository(MLModelRepository):
    def __init__(self, service: Service) -> None:
        self._service = service

    async def get_by_id(self, model_id: int) -> StoredMLModel | None:
        row = (
            await self._service.session.execute(select(MLModelORM).where(MLModelORM.id == model_id))
        ).scalar_one_or_none()
        if row is None:
            return None
        return StoredMLModel(
            model_id=row.id,
            name=row.name,
            description=row.description,
            cost_per_request=float(row.cost_per_request),
            is_active=bool(row.is_active),
        )

    async def list_active(self) -> list[StoredMLModel]:
        rows = (
            await self._service.session.execute(select(MLModelORM).where(MLModelORM.is_active == True))  # noqa: E712
        ).scalars().all()
        return [
            StoredMLModel(
                model_id=r.id,
                name=r.name,
                description=r.description,
                cost_per_request=float(r.cost_per_request),
                is_active=bool(r.is_active),
            )
            for r in rows
        ]

    async def save(self, model: StoredMLModel) -> StoredMLModel:
        orm = MLModelORM(
            name=model.name,
            description=model.description,
            cost_per_request=model.cost_per_request,
            is_active=model.is_active,
        )
        self._service.session.add(orm)
        await self._service.session.flush()
        return StoredMLModel(
            model_id=orm.id,
            name=orm.name,
            description=orm.description,
            cost_per_request=float(orm.cost_per_request),
            is_active=bool(orm.is_active),
        )


class SqlAlchemyMLTaskRepository(MLTaskRepository):
    def __init__(self, service: Service) -> None:
        self._service = service

    async def get_by_id(self, task_id: int) -> MLTask | None:
        task = (
            await self._service.session.execute(select(MLTaskORM).where(MLTaskORM.id == task_id))
        ).scalar_one_or_none()
        if task is None:
            return None
        user_orm = (
            await self._service.session.execute(select(UserORM).where(UserORM.id == task.user_id))
        ).scalar_one()
        model_orm = (
            await self._service.session.execute(select(MLModelORM).where(MLModelORM.id == task.model_id))
        ).scalar_one()
        return to_domain_task(task, to_domain_user(user_orm), model_orm)

    async def list_by_user(self, user_id: int) -> list[MLTask]:
        user_orm = (
            await self._service.session.execute(select(UserORM).where(UserORM.id == user_id))
        ).scalar_one()
        tasks = (
            await self._service.session.execute(
                select(MLTaskORM).where(MLTaskORM.user_id == user_id).order_by(MLTaskORM.created_at.desc())
            )
        ).scalars().all()
        result: list[MLTask] = []
        user = to_domain_user(user_orm)
        for task in tasks:
            model_orm = (
                await self._service.session.execute(select(MLModelORM).where(MLModelORM.id == task.model_id))
            ).scalar_one()
            result.append(to_domain_task(task, user, model_orm))
        return result

    async def save(self, task: MLTask) -> MLTask:
        orm = MLTaskORM(
            user_id=task.user.user_id,
            model_id=task.model.model_id,
            input_data=task.input_data,
            status=TaskStatusORM(task.status.value),
            created_at=task.created_at,
            completed_at=task.completed_at,
        )
        self._service.session.add(orm)
        await self._service.session.flush()
        return await self.get_by_id(int(orm.id))

    async def update(self, task: MLTask) -> MLTask:
        orm = (
            await self._service.session.execute(select(MLTaskORM).where(MLTaskORM.id == task.task_id))
        ).scalar_one()
        orm.status = TaskStatusORM(task.status.value)
        orm.completed_at = task.completed_at
        return await self.get_by_id(int(orm.id))


class SqlAlchemyPredictionResultRepository(PredictionResultRepository):
    def __init__(self, service: Service) -> None:
        self._service = service

    async def get_by_task_id(self, task_id: int) -> PredictionResult | None:
        row = (
            await self._service.session.execute(
                select(PredictionResultORM).where(PredictionResultORM.task_id == task_id)
            )
        ).scalar_one_or_none()
        return None if row is None else to_domain_prediction_result(row)

    async def save(self, result: PredictionResult) -> PredictionResult:
        orm = PredictionResultORM(
            task_id=result.task_id,
            output_data=result.output_data,
            credits_charged=result.credits_charged,
            created_at=result.created_at,
        )
        self._service.session.add(orm)
        await self._service.session.flush()
        return to_domain_prediction_result(orm)

