import fastapi
from ml_service_model.api.rest.dependencies import (get_current_user,
                                                    get_database)
from ml_service_model.api.rest.models.schemas import ModelResponse
from ml_service_model.database.repositories import \
    SqlAlchemyAltMLModelRepository
from ml_service_model.database.service import Service


async def list_models(
    database: Service = fastapi.Depends(get_database),
) -> list[ModelResponse]:
    repo = SqlAlchemyAltMLModelRepository(database)
    models = await repo.list_active()
    return [ModelResponse.from_domain(m) for m in models]
