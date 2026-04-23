FROM python:3.14-slim-trixie

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY ./pyproject.toml ./uv.lock /app/

COPY ./ml_service /app/ml_service
COPY ./users /app/users
COPY ./wallet /app/wallet
COPY ./model /app/model
COPY ./database /app/database
COPY ./database_repository /app/database_repository
COPY ./common /app/common

# RUN uv pip install --system --no-cache -r pyproject.toml
# RUN uv pip install --system --no-cache -e .
RUN uv pip install --system --no-cache \
    -e ./common \
    -e ./database \
    -e ./database_repository \
    -e ./users \
    -e ./wallet \
    -e ./model \
    -e ./ml_service

ENTRYPOINT ["python", "-m", "ml_service"]
CMD ["api", "--host", "0.0.0.0", "--port", "80"]
