from datetime import datetime, timezone

import pytest
from ml_service_common.messaging.schemas import (BillingRequestMessage,
                                                 PredictRequestMessage)


def _billing_msg(input_data: dict) -> BillingRequestMessage:
    return BillingRequestMessage(
        task_id=1,
        user_id=7,
        model_id=42,
        model_name="mock-model",
        cost_per_request=1.5,
        input_data=input_data,
        submitted_at=datetime.now(timezone.utc),
    )


def test_billing_request_message_round_trips():
    msg = _billing_msg({"a": 1, "b": 3, "label": "x"})
    assert msg.task_id == 1
    assert msg.model_name == "mock-model"
    assert msg.cost_per_request == 1.5
    assert msg.input_data == {"a": 1, "b": 3, "label": "x"}


def test_billing_request_message_rejects_blank_model_name():
    with pytest.raises(ValueError):
        BillingRequestMessage(
            task_id=1,
            user_id=7,
            model_id=42,
            model_name="",
            cost_per_request=1.5,
            input_data={},
            submitted_at=datetime.now(timezone.utc),
        )


def test_predict_request_message_round_trips():
    msg = PredictRequestMessage(
        task_id=1,
        model_id=42,
        model_name="mock-model",
        input_data={"x": 1},
    )
    assert msg.task_id == 1
    assert msg.input_data == {"x": 1}
