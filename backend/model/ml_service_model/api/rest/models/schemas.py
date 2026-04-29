from pydantic import BaseModel

from ml_service_model.domains.ml_model import MLModel


class ModelResponse(BaseModel):
    id: int
    name: str
    description: str
    cost_per_request: float
    is_active: bool

    @classmethod
    def from_domain(cls, model: MLModel) -> "ModelResponse":
        return cls(
            id=model.model_id,
            name=model.name,
            description=model.description,
            cost_per_request=model.cost_per_request,
            is_active=model.is_active,
        )
