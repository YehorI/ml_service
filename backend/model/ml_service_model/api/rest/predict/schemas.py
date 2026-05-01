from pydantic import BaseModel


class PredictRequest(BaseModel):
    features: dict
    model: str = "demo_model"


class PredictResponse(BaseModel):
    task_id: str
    status: str
