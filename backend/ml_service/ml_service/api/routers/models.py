from fastapi import APIRouter, Depends
from ml_service_model.interfaces.repositories import MLModelRepository
from ml_service_users.domains.user import User

from ml_service.api.deps import get_current_user, get_model_repository
from ml_service.api.schemas import ModelItem

router = APIRouter()


@router.get("", response_model=list[ModelItem])
async def list_models(
    _: User = Depends(get_current_user),
    repo: MLModelRepository = Depends(get_model_repository),
):
    models = await repo.list_active()
    return [
        ModelItem(
            model_id=m.model_id,
            name=m.name,
            description=m.description,
            cost_per_request=float(m.cost_per_request),
            is_active=m.is_active,
        )
        for m in models
    ]
