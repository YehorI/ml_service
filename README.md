# ml_service

ML inference platform. FastAPI backend split into three microservices (users, wallet, model), an async worker for model inference, a Leptos/Rust SSR frontend, PostgreSQL, and RabbitMQ for inter-service messaging.

## Prerequisites

- Docker
- Docker Compose
- Make
- Rust toolchain with `wasm32-unknown-unknown` target and `cargo-leptos` (frontend only)

## Configuration

Copy the example env files and adjust if needed. The defaults work for local development without changes.

```sh
cp backend/.env.example backend/.env
cp deploy/.env.example deploy/.env
cp frontend/.env.example frontend/.env
```

For production, set your email for Let's Encrypt in `deploy/.env`:

```
TRAEFIK__LETS_ENCRYPT_EMAIL=you@example.com
```

## Quickstart (staging)

Staging mounts local source directories as volumes and loads test fixtures on startup.

```sh
make stage-build
make stage-up
```

To rebuild and restart from scratch:

```sh
make stage-reup
```

The staging setup does not containerize the frontend. Run it separately after the backend is up:

```sh
cd frontend && cargo leptos serve
```

The UI will be available at http://localhost:3000.

## Production

```sh
make prod-up
```

Runs the full stack behind Traefik with automatic TLS. Requires `TRAEFIK__LETS_ENCRYPT_EMAIL` to be set.

To stop:

```sh
make prod-down
```

## Common commands

| Command | Description |
|---|---|
| `make logs` | Tail logs for all services |
| `make logs-backend` | Tail backend logs |
| `make logs-worker` | Tail worker logs |
| `make stage-migrate` | Run database migrations (staging) |
| `make stage-downgrade` | Rollback last migration (staging) |
| `make stage-revision` | Generate a new migration (staging) |
| `make stage-fixtures` | Reload test fixtures |
| `make prod-migrate` | Run database migrations (prod) |
| `make test` | Run the test suite |

Scale workers by passing `WORKERS=n`:

```sh
make stage-up WORKERS=4
```

Load a custom fixture file:

```sh
make stage-fixtures FIXTURE=backend/database/database/fixtures/my_fixtures.yaml
```

## Services

| Service | Port | Description |
|---|---|---|
| frontend | 3000 | Leptos SSR web app |
| users | 8000 | User management REST API |
| wallet | 8001 | Billing REST API |
| model | 8002 | Model inference REST API + WebSocket |
| postgres | 5432 | Primary database |
| rabbitmq | 5672 | Message broker |
| rabbitmq management | 15672 | RabbitMQ admin UI |

## Messaging

Three RabbitMQ queues connect the services:

- `ml.predict` — model service → worker (inference requests)
- `ml.completed` — worker → model service (inference results)
- `ml.billing` — worker → wallet service (charge events)
