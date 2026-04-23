PROD_COMPOSE  := docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.prod.yml
STAGE_COMPOSE := docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.stage.yml
FIXTURE       ?= database/database/fixtures/autotests.yaml

.PHONY: \
	prod-up prod-down prod-migrate prod-downgrade prod-revision \
	stage-up stage-down stage-migrate stage-downgrade stage-revision stage-fixtures

prod-up:
	$(PROD_COMPOSE) up -d --wait postgres rabbitmq
	$(PROD_COMPOSE) run --rm backend database migrate
	$(PROD_COMPOSE) up -d --remove-orphans

prod-down:
	$(PROD_COMPOSE) down

prod-migrate:
	$(PROD_COMPOSE) run --rm backend database migrate

prod-downgrade:
	$(PROD_COMPOSE) run --rm backend database downgrade $(or $(REV),-1)

prod-revision:
	$(PROD_COMPOSE) run --rm backend database revision "$(MSG)"

stage-up:
	$(STAGE_COMPOSE) up -d --wait postgres rabbitmq
	$(STAGE_COMPOSE) run --rm backend database migrate
	$(STAGE_COMPOSE) run --rm backend database loadfixtures "$(FIXTURE)"
	$(STAGE_COMPOSE) up -d --remove-orphans

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
