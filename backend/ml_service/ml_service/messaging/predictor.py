from typing import Any


class MockPredictor:
    """Lightweight stand-in for a real ML model.

    Returns deterministic output derived from the input so workers can be
    verified end-to-end without loading model weights.
    """

    def predict(self, model_name: str, input_data: dict[str, Any]) -> dict[str, Any]:
        return {
            "model": model_name,
            "input_keys": sorted(input_data.keys()),
            "score": self._score(input_data),
        }

    @staticmethod
    def _score(payload: dict[str, Any]) -> float:
        numeric = [v for v in payload.values() if isinstance(v, (int, float))]
        if not numeric:
            return 0.0
        return round(sum(numeric) / len(numeric), 6)
