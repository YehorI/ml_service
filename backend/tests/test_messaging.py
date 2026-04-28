from datetime import datetime, timezone

import pytest

from ml_service.messaging.predictor import MockPredictor
from ml_service.messaging.schemas import PredictTaskMessage


def test_predictor_returns_average_of_numeric_values():
    output = MockPredictor().predict("mock-model", {"a": 1, "b": 3, "label": "x"})

    assert output["model"] == "mock-model"
    assert output["score"] == 2.0
    assert output["input_keys"] == ["a", "b", "label"]


def test_predictor_returns_zero_when_no_numeric_values():
    output = MockPredictor().predict("mock-model", {"label": "x"})
    assert output["score"] == 0.0


def test_predict_task_message_rejects_non_positive_ids():
    with pytest.raises(ValueError):
        PredictTaskMessage(
            task_id=0,
            user_id=1,
            model_id=1,
            submitted_at=datetime.now(timezone.utc),
        )

    with pytest.raises(ValueError):
        PredictTaskMessage(
            task_id=1,
            user_id=0,
            model_id=1,
            submitted_at=datetime.now(timezone.utc),
        )
