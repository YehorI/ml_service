from typing import Any

from transformers import pipeline

from ml_service_model.domains.ml_model import MLModel

_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
_sentiment = pipeline("sentiment-analysis", model=_MODEL_NAME)


class StoredMLModel(MLModel):
    def predict(self, input_data: Any) -> Any:
        text = input_data.get("text", "")
        result = _sentiment(text)[0]
        return {"label": result["label"], "score": round(result["score"], 4)}

