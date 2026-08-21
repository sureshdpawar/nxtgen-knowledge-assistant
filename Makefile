COMPOSE = docker compose --env-file .env.prod -f docker-compose.prod.yml


# ============================================================
# Docker
# ============================================================

.PHONY: up down build rebuild restart ps logs


up:
	$(COMPOSE) up -d


down:
	$(COMPOSE) down


build:
	$(COMPOSE) build


rebuild:
	$(COMPOSE) build --no-cache


restart:
	$(COMPOSE) restart


ps:
	$(COMPOSE) ps


logs:
	$(COMPOSE) logs -f


# ============================================================
# Backend
# ============================================================

.PHONY: backend-logs backend-shell migrate migration-current


backend-logs:
	$(COMPOSE) logs -f backend


backend-shell:
	$(COMPOSE) exec backend bash


migrate:
	$(COMPOSE) exec backend alembic upgrade head


migration-current:
	$(COMPOSE) exec backend alembic current


# ============================================================
# Background Worker
# ============================================================

.PHONY: worker-logs worker-shell


worker-logs:
	$(COMPOSE) logs -f backend-worker


worker-shell:
	$(COMPOSE) exec backend-worker bash


# ============================================================
# Database
# ============================================================

.PHONY: db-shell db-status db-extensions


db-shell:
	$(COMPOSE) exec postgres psql \
		-U $(shell grep '^POSTGRES_USER=' .env.prod | cut -d '=' -f2) \
		-d $(shell grep '^POSTGRES_DB=' .env.prod | cut -d '=' -f2)


db-status:
	$(COMPOSE) exec postgres pg_isready \
		-U $(shell grep '^POSTGRES_USER=' .env.prod | cut -d '=' -f2) \
		-d $(shell grep '^POSTGRES_DB=' .env.prod | cut -d '=' -f2)


db-extensions:
	$(COMPOSE) exec postgres psql \
		-U $(shell grep '^POSTGRES_USER=' .env.prod | cut -d '=' -f2) \
		-d $(shell grep '^POSTGRES_DB=' .env.prod | cut -d '=' -f2) \
		-c '\dx'


# ============================================================
# MCP
# ============================================================

.PHONY: mcp-logs


mcp-logs:
	$(COMPOSE) logs -f mcp


# ============================================================
# Mock REST API
# ============================================================

.PHONY: rest-logs


rest-logs:
	$(COMPOSE) logs -f mock-rest


# ============================================================
# Application Bootstrap
# ============================================================

.PHONY: superadmin


superadmin:
	$(COMPOSE) exec backend python create_superadmin.py


# ============================================================
# Deployment
# ============================================================

.PHONY: deploy


deploy:
	$(COMPOSE) build
	$(COMPOSE) up -d
	$(COMPOSE) exec backend alembic upgrade head
	$(COMPOSE) ps