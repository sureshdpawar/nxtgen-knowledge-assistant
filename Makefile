COMPOSE = docker compose --env-file .env.prod -f docker-compose.prod.yml

POSTGRES_USER = $(shell grep '^POSTGRES_USER=' .env.prod | cut -d '=' -f2)
POSTGRES_DB = $(shell grep '^POSTGRES_DB=' .env.prod | cut -d '=' -f2)

BACKUP_DIR = backups


# ============================================================
# Validation
# ============================================================

.PHONY: env-check config

env-check:
	@test -f .env.prod || (echo "ERROR: .env.prod does not exist."; exit 1)
	@test -f $$(grep '^GOOGLE_SERVICE_ACCOUNT_HOST_FILE=' .env.prod | cut -d '=' -f2-) || \
		(echo "ERROR: Google service-account file does not exist."; exit 1)
	@! grep -Eq 'CHANGE_ME|YOUR_DOMAIN' .env.prod || \
		(echo "ERROR: .env.prod still contains CHANGE_ME or YOUR_DOMAIN placeholders."; exit 1)
	@echo "Production environment preflight passed."

config:
	$(COMPOSE) config


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
# Backend / frontend
# ============================================================

.PHONY: backend-logs backend-shell frontend-logs

backend-logs:
	$(COMPOSE) logs -f backend

backend-shell:
	$(COMPOSE) exec backend bash

frontend-logs:
	$(COMPOSE) logs -f frontend


# ============================================================
# Alembic / Database Migrations
# ============================================================

.PHONY: migrate migration-current migration-heads migration-history

migrate:
	$(COMPOSE) run --rm backend alembic upgrade head

migration-current:
	$(COMPOSE) run --rm backend alembic current

migration-heads:
	$(COMPOSE) run --rm backend alembic heads

migration-history:
	$(COMPOSE) run --rm backend alembic history


# ============================================================
# Background ingestion worker
# ============================================================

.PHONY: worker-logs worker-shell

worker-logs:
	$(COMPOSE) logs -f backend-worker

worker-shell:
	$(COMPOSE) exec backend-worker bash


# ============================================================
# Academy MCP
# ============================================================

.PHONY: mcp-logs mcp-shell

mcp-logs:
	$(COMPOSE) logs -f mcp

mcp-shell:
	$(COMPOSE) exec mcp bash


# ============================================================
# Database
# ============================================================

.PHONY: db-shell db-status db-wait db-extensions db-backup

db-shell:
	$(COMPOSE) exec postgres \
		psql \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB)

db-status:
	$(COMPOSE) exec postgres \
		pg_isready \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB)

db-wait:
	@echo "Waiting for PostgreSQL to become ready..."
	@until $(COMPOSE) exec -T postgres \
		pg_isready \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) >/dev/null 2>&1; do \
		sleep 2; \
	done
	@echo "PostgreSQL is ready."

db-extensions:
	$(COMPOSE) exec postgres \
		psql \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) \
		-c '\dx'

db-backup:
	@mkdir -p $(BACKUP_DIR)
	@echo "Creating PostgreSQL backup..."
	@$(COMPOSE) exec -T postgres \
		pg_dump \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) \
		-F c \
		> $(BACKUP_DIR)/knowgentiq-$$(date +%Y%m%d-%H%M%S).dump
	@echo "Database backup completed."
	@ls -lh $(BACKUP_DIR) | tail -5


# ============================================================
# Application Bootstrap
# ============================================================

.PHONY: superadmin

superadmin:
	$(COMPOSE) exec backend python create_superadmin.py


# ============================================================
# Production Preflight
# ============================================================

.PHONY: preflight

preflight: env-check config
	@echo ""
	@echo "=========================================="
	@echo "Knowgentiq production preflight"
	@echo "=========================================="
	@echo ""

	@echo "Checking Docker services..."
	$(COMPOSE) ps

	@echo ""
	@echo "Checking PostgreSQL..."
	$(MAKE) db-status

	@echo ""
	@echo "Current database migration:"
	$(MAKE) migration-current

	@echo ""
	@echo "Application migration head:"
	$(MAKE) migration-heads

	@echo ""
	@echo "Preflight completed."


# ============================================================
# Production Deployment
# ============================================================

.PHONY: deploy

deploy: env-check config
	@echo ""
	@echo "=========================================="
	@echo "Knowgentiq production deployment"
	@echo "=========================================="
	@echo ""

	@echo "Step 1/7 - Building application images..."
	$(COMPOSE) build

	@echo ""
	@echo "Step 2/7 - Starting PostgreSQL..."
	$(COMPOSE) up -d postgres
	$(MAKE) db-wait
	$(MAKE) db-status

	@echo ""
	@echo "Step 3/7 - Backing up PostgreSQL..."
	$(MAKE) db-backup

	@echo ""
	@echo "Step 4/7 - Checking current migration..."
	$(MAKE) migration-current

	@echo ""
	@echo "Step 5/7 - Checking application migration head..."
	$(MAKE) migration-heads

	@echo ""
	@echo "Step 6/7 - Applying database migrations..."
	$(MAKE) migrate

	@echo ""
	@echo "Step 7/7 - Starting application services..."
	$(COMPOSE) up -d

	@echo ""
	@echo "=========================================="
	@echo "Deployment status"
	@echo "=========================================="
	@echo ""

	$(COMPOSE) ps

	@echo ""
	@echo "Deployment completed."
	@echo ""
