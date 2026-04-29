from datetime import datetime, timezone

import pytest

from ml_service_common.messaging.schemas import PredictTaskMessage


def _msg(input_data: dict) -> PredictTaskMessage:
    return PredictTaskMessage(
        task_id=1,
        model_id=42,
        user_id=7,
        model_name="mock-model",
        input_data=input_data,
        submitted_at=datetime.now(timezone.utc),
    )


def test_predict_task_message_round_trips():
    msg = _msg({"a": 1, "b": 3, "label": "x"})
    assert msg.task_id == 1
    assert msg.model_name == "mock-model"
    assert msg.input_data == {"a": 1, "b": 3, "label": "x"}


def test_predict_task_message_rejects_blank_model_name():
    with pytest.raises(ValueError):
        PredictTaskMessage(
            task_id=1,
            model_id=42,
            user_id=7,
            model_name="",
            input_data={},
            submitted_at=datetime.now(timezone.utc),
        )
