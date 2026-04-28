from datetime import datetime, timezone
from typing import Any

from ml_service.messaging.schemas import PredictTaskMessage, PredictTaskResult


class MockPredictor:
    """Lightweight stand-in for a real ML model.

    Returns deterministic output derived from the input so workers can be
    verified end-to-end without loading model weights.
    """

    def predict(self, message: PredictTaskMessage) -> PredictTaskResult:
        output: dict[str, Any] = {
            "model": message.model_name,
            "input_keys": sorted(message.input_data.keys()),
            "score": self._score(message.input_data),
        }
        return PredictTaskResult(
            task_id=message.task_id,
            model_name=message.model_name,
            output_data=output,
            processed_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _score(payload: dict[str, Any]) -> float:
        numeric = [v for v in payload.values() if isinstance(v, (int, float))]
        if not numeric:
            return 0.0
        return round(sum(numeric) / len(numeric), 6)
