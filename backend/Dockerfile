FROM python:3.14-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./ml_service /app
COPY ./pyproject.toml ./uv.lock /app/

WORKDIR /app

RUN uv sync --all-groups --no-dev --all-extras
ENTRYPOINT ["uv", "run", "python", "-m", "ml_service"]
