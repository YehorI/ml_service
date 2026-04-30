COMPOSE := docker compose -f deploy/docker-compose.yml
PROD_COMPOSE := $(COMPOSE) -f deploy/docker-compose.prod.yml
STAGE_COMPOSE := $(COMPOSE) -f deploy/docker-compose.stage.yml

FIXTURE ?= database/database/fixtures/autotests.yaml
WORKERS ?= 2

.PHONY: \
	build build-backend build-worker \
	prod-up prod-down prod-migrate prod-downgrade prod-revision \
	stage-build stage-up stage-reup stage-down \
	stage-migrate stage-downgrade stage-revision stage-fixtures \
	logs logs-worker logs-backend test

build: build-backend build-worker

build-backend:
	$(COMPOSE) build backend

build-worker:
	$(COMPOSE) build worker

prod-up:
	$(PROD_COMPOSE) up -d --wait postgres rabbitmq
	$(PROD_COMPOSE) run --rm backend database migrate
	$(PROD_COMPOSE) up -d --remove-orphans --scale worker=$(WORKERS)

prod-down:
	$(PROD_COMPOSE) down

prod-migrate:
	$(PROD_COMPOSE) run --rm backend database migrate

prod-downgrade:
	$(PROD_COMPOSE) run --rm backend database downgrade $(or $(REV),-1)

prod-revision:
	$(PROD_COMPOSE) run --rm backend database revision "$(MSG)"

stage-build:
	$(STAGE_COMPOSE) build backend worker

stage-up:
	$(STAGE_COMPOSE) up -d --wait postgres rabbitmq
	$(STAGE_COMPOSE) run --rm backend database migrate
	$(STAGE_COMPOSE) run --rm backend database loadfixtures "$(FIXTURE)"
	$(STAGE_COMPOSE) up -d --remove-orphans --scale worker=$(WORKERS)

stage-reup: stage-down stage-build stage-up

stage-down:
	$(STAGE_COMPOSE) down

stage-migrate:
	$(STAGE_COMPOSE) run --rm backend database migrate

stage-downgrade:
	$(STAGE_COMPOSE) run --rm backend database downgrade $(or $(REV),-1)

stage-revision:
	$(STAGE_COMPOSE) run --rm backend database revision "$(MSG)"

stage-fixtures:
	$(STAGE_COMPOSE) run --rm backend database loadfixtures "$(FIXTURE)"

logs:
	$(COMPOSE) logs -f

logs-backend:
	$(COMPOSE) logs -f backend

logs-worker:
	$(COMPOSE) logs -f worker
w
test:
	cd backend && uv run pytest
