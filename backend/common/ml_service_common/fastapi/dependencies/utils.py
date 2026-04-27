import inspect
from typing import Callable

import fastapi
from pydantic import BaseModel


def model_to_query_params(model: type[BaseModel]) -> Callable:
    def dependency(**kwargs) -> model:
        return model(**kwargs)

    parameters = [
        inspect.Parameter(
            name=name,
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=fastapi.Query(info.default),
            annotation=info.annotation,
        )
        for name, info in model.model_fields.items()
    ]
    dependency.__signature__ = inspect.Signature(parameters=parameters)
    dependency.__annotations__ = {
        p.name: p.annotation for p in parameters
    }

    return fastapi.Depends(dependency)
