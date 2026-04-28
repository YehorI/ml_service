from datetime import datetime, timezone

import pytest

from ml_service.messaging.predictor import MockPredictor
from ml_service.messaging.schemas import PredictTaskMessage


def _msg(input_data: dict) -> PredictTaskMessage:
    return PredictTaskMessage(
        task_id="abc-123",
        model_name="mock-model",
        input_data=input_data,
        submitted_at=datetime.now(timezone.utc),
    )


def test_predictor_returns_average_of_numeric_values():
    result = MockPredictor().predict(_msg({"a": 1, "b": 3, "label": "x"}))

    assert result.task_id == "abc-123"
    assert result.model_name == "mock-model"
    assert result.output_data["score"] == 2.0
    assert result.output_data["input_keys"] == ["a", "b", "label"]


def test_predictor_returns_zero_when_no_numeric_values():
    result = MockPredictor().predict(_msg({"label": "x"}))

    assert result.output_data["score"] == 0.0


def test_predict_task_message_rejects_blank_model_name():
    with pytest.raises(ValueError):
        PredictTaskMessage(
            task_id="abc",
            model_name="",
            input_data={},
            submitted_at=datetime.now(timezone.utc),
        )
