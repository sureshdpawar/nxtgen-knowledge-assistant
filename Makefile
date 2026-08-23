COMPOSE = docker compose --env-file .env.prod -f docker-compose.prod.yml

POSTGRES_USER = $(shell grep '^POSTGRES_USER=' .env.prod | cut -d '=' -f2)
POSTGRES_DB = $(shell grep '^POSTGRES_DB=' .env.prod | cut -d '=' -f2)

BACKUP_DIR = backups


# ============================================================
# Docker
# ============================================================

.PHONY: \
	up \
	down \
	build \
	rebuild \
	restart \
	ps \
	logs


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

.PHONY: \
	backend-logs \
	backend-shell


backend-logs:
	$(COMPOSE) logs -f backend


backend-shell:
	$(COMPOSE) exec backend bash


# ============================================================
# Alembic / Database Migrations
# ============================================================

.PHONY: \
	migrate \
	migration-current \
	migration-heads \
	migration-history


#
# Use "run --rm" rather than "exec".
#
# This ensures migrations are executed using
# the newly built backend image and do not
# depend on the currently running backend
# container.
#

migrate:
	$(COMPOSE) run --rm backend alembic upgrade head


migration-current:
	$(COMPOSE) run --rm backend alembic current


migration-heads:
	$(COMPOSE) run --rm backend alembic heads


migration-history:
	$(COMPOSE) run --rm backend alembic history


# ============================================================
# Background Worker
# ============================================================

.PHONY: \
	worker-logs \
	worker-shell


worker-logs:
	$(COMPOSE) logs -f backend-worker


worker-shell:
	$(COMPOSE) exec backend-worker bash


# ============================================================
# Database
# ============================================================

.PHONY: \
	db-shell \
	db-status \
	db-extensions \
	db-backup


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


db-extensions:
	$(COMPOSE) exec postgres \
		psql \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) \
		-c '\dx'


#
# Create a PostgreSQL custom-format backup.
#
# Backups are stored on the host machine,
# not inside the PostgreSQL container.
#

db-backup:
	@mkdir -p $(BACKUP_DIR)
	@echo "Creating PostgreSQL backup..."
	@$(COMPOSE) exec -T postgres \
		pg_dump \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) \
		-F c \
		> $(BACKUP_DIR)/nxtgen-$$(date +%Y%m%d-%H%M%S).dump
	@echo "Database backup completed."
	@ls -lh $(BACKUP_DIR) | tail -5


# ============================================================
# MCP
# ============================================================

.PHONY: \
	mcp-logs


mcp-logs:
	$(COMPOSE) logs -f mcp


# ============================================================
# Mock REST API
# ============================================================

.PHONY: \
	rest-logs


rest-logs:
	$(COMPOSE) logs -f mock-rest


# ============================================================
# Application Bootstrap
# ============================================================

.PHONY: \
	superadmin


superadmin:
	$(COMPOSE) exec backend \
		python create_superadmin.py


# ============================================================
# Production Preflight
# ============================================================

.PHONY: \
	preflight


preflight:
	@echo ""
	@echo "=========================================="
	@echo "NXTGEN production preflight"
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

.PHONY: \
	deploy


#
# Production deployment order:
#
# 1. Build new application images.
# 2. Verify PostgreSQL is available.
# 3. Backup the existing production database.
# 4. Display current DB migration.
# 5. Display application migration head.
# 6. Upgrade DB schema.
# 7. Start/recreate application containers.
# 8. Display final service status.
#
# PostgreSQL volumes are NOT removed.
#

deploy:
	@echo ""
	@echo "=========================================="
	@echo "NXTGEN production deployment"
	@echo "=========================================="
	@echo ""

	@echo "Step 1/7 - Building images..."
	$(COMPOSE) build

	@echo ""
	@echo "Step 2/7 - Checking PostgreSQL..."
	$(MAKE) db-status

	@echo ""
	@echo "Step 3/7 - Backing up PostgreSQL..."
	$(MAKE) db-backup

	@echo ""
	@echo "Step 4/7 - Checking current migration..."
	$(MAKE) migration-current

	@echo ""
	@echo "Step 5/7 - Checking migration head..."
	$(MAKE) migration-heads

	@echo ""
	@echo "Step 6/7 - Applying database migrations..."
	$(MAKE) migrate

	@echo ""
	@echo "Step 7/7 - Starting application..."
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