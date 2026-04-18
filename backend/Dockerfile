FROM python:3.14-slim-trixie

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml ./uv.lock /app/

COPY ./ml_service /app/ml_service

RUN uv pip install --system --no-cache -r pyproject.toml

ENTRYPOINT ["python", "-m", "ml_service"]
