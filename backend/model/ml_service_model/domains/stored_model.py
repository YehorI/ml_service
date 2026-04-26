from typing import Any

from ml_service_model.domains.ml_model import MLModel


class StoredMLModel(MLModel):
    """
    Mock model
    """

    def predict(self, input_data: Any) -> Any:
        return {
            "ml_service_model": {"id": self.model_id, "name": self.name},
            "input": input_data,
        }

