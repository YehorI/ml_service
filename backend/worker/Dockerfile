FROM python:3.14-slim-trixie

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml ./uv.lock /app/

COPY ./common /app/common
COPY ./database /app/database
COPY ./database_repository /app/database_repository
COPY ./wallet /app/wallet
COPY ./model /app/model
COPY ./worker /app/worker

RUN uv pip install --system --no-cache \
    -e ./common \
    -e ./database \
    -e ./database_repository \
    -e ./wallet \
    -e ./model \
    -e ./worker

CMD ["python", "-m", "ml_service_worker"]
