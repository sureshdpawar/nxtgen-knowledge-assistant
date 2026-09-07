# Knowgentiq — AWS Lightsail Docker Deployment

This package is aligned to the current `dev` codebase and the Academy agent/MCP path.

## Target runtime

```text
Internet
   ↓
Lightsail firewall
   ↓
Nginx / HTTPS
   ├── /        → 127.0.0.1:3000 → frontend
   └── /api/*   → 127.0.0.1:8000 → backend

Docker network
   ├── frontend
   ├── backend
   ├── backend-worker
   ├── mcp (Academy MCP, internal only)
   └── postgres (pgvector, internal only)
```

There are four application containers:

1. frontend
2. backend
3. backend-worker
4. mcp

and one infrastructure container:

5. postgres

## Image strategy

The backend API, ingestion worker, and Academy MCP currently use the same backend Dockerfile and Python dependency set.

For the Lightsail MVP, build two custom images:

```text
knowgentiq-frontend:<tag>
knowgentiq-backend:<tag>
```

Run the backend image three times:

```text
backend API      → Dockerfile default CMD
ingestion worker → python -m app.workers.ingestion_worker
Academy MCP      → uvicorn mcp_servers.academy.server:app ...
```

This avoids rebuilding and storing the same large Python/PyTorch runtime three times.

If a future registry/release process requires four distinct application image names, the same backend image digest can be tagged separately for backend, worker, and MCP.

---

# Production runtime changes

## Removed from Compose

- `mock-rest`
- Procurement MCP startup

The old Procurement/mock REST source code can remain in the repository for now. Keeping source deletion separate reduces deployment risk and preserves an easy rollback.

## Production MCP

The `mcp` service now starts:

```text
mcp_servers.academy.server:app
```

The current Academy MCP exposes:

```text
create_enquiry
update_enquiry
schedule_consultation
```

It uses Google service-account credentials plus Academy spreadsheet/calendar settings.

## Internal MCP URL

Configure the MCP endpoint inside Knowgentiq as:

```text
http://mcp:9000/mcp
```

Do not configure the backend to call:

```text
http://localhost:9000/mcp
```

because `localhost` inside the backend container points back to the backend container itself.

MCP is intentionally not published on the Lightsail host.

---

# 1. Lightsail host

Use a static IP and point the production DNS record to it.

Recommended public inbound ports:

```text
22/tcp   SSH        restrict to your admin IP where practical
80/tcp   HTTP
443/tcp  HTTPS
```

Do not publicly expose:

```text
3000 frontend
8000 backend
9000 MCP
5432 PostgreSQL
```

Compose binds frontend/backend to `127.0.0.1`; PostgreSQL and MCP remain Docker-network-only.

Install:

- Git
- Docker Engine
- Docker Compose plugin
- Nginx
- TLS/certificate tooling

---

# 2. Pull a known revision

Example:

```bash
cd /opt
sudo git clone <YOUR_REPOSITORY_URL> knowgentiq
sudo chown -R "$USER":"$USER" /opt/knowgentiq

cd /opt/knowgentiq
git checkout dev
git pull
```

For actual releases, prefer deploying a known tag/commit rather than treating a moving `dev` branch as the release identifier.

Set `APP_IMAGE_TAG` in `.env.prod` to a release value or Git SHA.

---

# 3. Prepare `.env.prod`

## Existing Lightsail deployment: merge, do not overwrite

If the Lightsail host already has a working `.env.prod`, **do not replace it blindly**.

First back it up:

```bash
cp .env.prod .env.prod.before-knowgentiq-$(date +%Y%m%d-%H%M%S)
chmod 600 .env.prod.before-knowgentiq-*
```

Then use the new `.env.prod.example` as the field checklist and manually merge the new variables into the existing production file.

Preserve the existing production values for:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DATABASE_URL
SECRET_KEY
```

unless you are intentionally performing a separate database/authentication migration.

The replacement Compose file also deliberately preserves the existing named Docker volumes:

```text
nxtgen-postgres-data
nxtgen-storage-data
```

so the deployment continues to attach to the current PostgreSQL and document-storage data.

## New Lightsail deployment

For a fresh host:

```bash
cp .env.prod.example .env.prod
chmod 600 .env.prod
nano .env.prod
```

Replace every `CHANGE_ME` and `YOUR_DOMAIN`.

At minimum configure:

```text
NEXT_PUBLIC_API_URL
CORS_ORIGINS
POSTGRES_PASSWORD
DATABASE_URL
SECRET_KEY
WEBSITE_WIDGET_TOKEN_SECRET
LLM_API / LLM_API_KEY
ACADEMY_ENQUIRY_SPREADSHEET_ID
ACADEMY_CALENDAR_ID
ACADEMY_ATTENDEE_EMAIL (if used)
```

Generate independent secrets:

```bash
openssl rand -hex 64
openssl rand -hex 64
```

Use one for `SECRET_KEY` and one for `WEBSITE_WIDGET_TOKEN_SECRET`.

## Critical frontend build-time setting

Set:

```env
NEXT_PUBLIC_API_URL=https://YOUR_DOMAIN/api/v1
```

before:

```bash
make build
```

or:

```bash
make deploy
```

Next.js embeds this value at image build time. Editing only the runtime environment after the image is built does not rewrite the browser bundle; rebuild the frontend after changing it.

---

# 4. Google service-account credential

Create:

```bash
cd /opt/knowgentiq
mkdir -p backend/secrets
chmod 700 backend/secrets
```

Place the credential file at:

```text
/opt/knowgentiq/backend/secrets/google-service-account.json
```

Then:

```bash
chmod 600 backend/secrets/google-service-account.json
```

The template uses:

```env
GOOGLE_SERVICE_ACCOUNT_HOST_FILE=./backend/secrets/google-service-account.json
GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/google-service-account.json
```

The file is mounted read-only into backend, ingestion worker, and Academy MCP.

The service account must have access to:

- the configured Academy enquiry spreadsheet,
- the configured Google Calendar,
- any Google Drive sources used by ingestion.

Never commit the service-account JSON.

---

# 5. Validate configuration

```bash
make env-check
make config
```

`env-check` catches:

- missing `.env.prod`,
- missing Google service-account file,
- remaining `CHANGE_ME`,
- remaining `YOUR_DOMAIN`.

`make config` renders/validates the Docker Compose configuration.

---

# 6. First deployment

For a new database:

```bash
make build

docker compose --env-file .env.prod \
  -f docker-compose.prod.yml \
  up -d postgres

make migrate

docker compose --env-file .env.prod \
  -f docker-compose.prod.yml \
  up -d

make superadmin
make ps
```

Watch logs:

```bash
make backend-logs
make worker-logs
make mcp-logs
make frontend-logs
```

Verify migration state:

```bash
make migration-current
make migration-heads
```

---

# 7. Existing production deployment

For an existing production database:

```bash
git pull
make deploy
```

The deployment target:

1. validates `.env.prod` and Compose,
2. builds frontend and shared backend runtime images,
3. starts/verifies PostgreSQL,
4. creates a PostgreSQL backup,
5. inspects current/head migration state,
6. applies Alembic migrations,
7. recreates/starts application services.

Backups are written under:

```text
./backups/
```

Do not use:

```bash
docker compose down -v
```

in production because `-v` removes named volumes.

---

# 8. Nginx / HTTPS

Docker publishes only:

```text
127.0.0.1:3000 → frontend
127.0.0.1:8000 → backend
```

The package includes:

```text
deploy/nginx/knowgentiq.conf.example
```

Replace `YOUR_DOMAIN` and adapt certificate paths.

Agent Chat uses streaming responses, so the API proxy includes:

```nginx
proxy_buffering off;
proxy_read_timeout 300s;
```

After changing Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

# 9. Academy MCP application configuration

After the containers are up:

```bash
make mcp-logs
```

Configure the MCP integration/tool URL in Knowgentiq as:

```text
http://mcp:9000/mcp
```

Example agent policy:

```text
search_knowledge      → AUTO
create_enquiry        → AUTO
update_enquiry        → HUMAN_APPROVAL
schedule_consultation → choose explicitly for the demo/business case
```

Execution policy remains application configuration; do not encode those choices into Docker.

---

# 10. Environment fields missing from the old production template

The old template was behind the current backend settings.

The replacement includes these current groups.

## Retrieval and embeddings

```text
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
RERANKING_ENABLED
RERANKER_MODEL
RERANKER_CANDIDATE_MULTIPLIER
RERANKER_MAX_CANDIDATES
```

## Usage quota defaults

```text
DEFAULT_DAILY_MESSAGE_LIMIT
DEFAULT_DAILY_INPUT_TOKEN_LIMIT
DEFAULT_DAILY_OUTPUT_TOKEN_LIMIT
DEFAULT_DAILY_TOTAL_TOKEN_LIMIT
DEFAULT_MONTHLY_MESSAGE_LIMIT
DEFAULT_MONTHLY_INPUT_TOKEN_LIMIT
DEFAULT_MONTHLY_OUTPUT_TOKEN_LIMIT
DEFAULT_MONTHLY_TOTAL_TOKEN_LIMIT
DEFAULT_MAX_INPUT_TOKENS_PER_REQUEST
DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST
DEFAULT_USAGE_TIMEZONE
```

## Website widget security

```text
WEBSITE_WIDGET_TOKEN_SECRET
WEBSITE_WIDGET_TOKEN_TTL_MINUTES
```

Always set a unique production `WEBSITE_WIDGET_TOKEN_SECRET`; do not rely on the fallback value in code.

## Online Evaluation

```text
ONLINE_EVAL_ENABLED
ONLINE_EVAL_SAMPLE_RATE
```

The template uses:

```env
ONLINE_EVAL_ENABLED=true
ONLINE_EVAL_SAMPLE_RATE=1.0
```

for the MVP/demo so every eligible RAG interaction is sampled.

Reduce the sample rate later if production traffic grows.

## OpenTelemetry

```text
OTEL_ENABLED
OTEL_SERVICE_NAME
OTEL_TRACE_EXPORTER
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT
```

Current supported exporters are:

```text
none
console
memory
otlp
```

The template uses `memory` for the current MVP because the UI's source-trace snapshot/debug flow can use locally finished spans.

The application itself describes the memory exporter as a development/debug backend. For mature production telemetry, move to:

```env
OTEL_TRACE_EXPORTER=otlp
OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=<collector endpoint>
```

with an external collector/backend.

Durable AgentRun/AgentRunStep persistence remains independent of the telemetry exporter.

## Academy MCP

```text
ACADEMY_ENQUIRY_SPREADSHEET_ID
ACADEMY_ENQUIRY_SHEET_NAME
ACADEMY_CALENDAR_ID
ACADEMY_ATTENDEE_EMAIL
ACADEMY_TIMEZONE
ACADEMY_CONSULTATION_DURATION_MINUTES
```

---

# 11. Important data compatibility rule

Do not casually change:

```text
EMBEDDING_MODEL
EMBEDDING_DIMENSIONS
```

on an existing production database.

Existing vectors were produced using a specific model/dimension. Changing these settings can require schema changes and re-embedding persisted documents.

For the first production deployment, keep them aligned with the environment used to create the current data.

---

# 12. Production smoke test

## Authentication and access

- ADMIN signs in.
- USER signs in.
- USER sees only assigned agents.
- USER cannot access admin governance/configuration pages.

## Knowledge

- KB Chat answers a known question.
- Citations/grounding work.
- New ingestion work is claimed by `backend-worker`.

## Agent

- Agent Chat answers a KB-backed question.
- `search_knowledge` is visible in the Agent Run.

## AUTO action

- `create_enquiry` executes without approval.
- Google Sheet is updated.

## Human approval

- `update_enquiry` pauses.
- Agent Chat shows waiting state only.
- Governance → Approvals shows the pending action.
- ADMIN approves/rejects there.
- Original LangGraph execution resumes.
- Final answer appears back in Agent Chat.

## Audit

- Agent Run Details shows tools, approval evidence, execution steps, tokens, cost, and duration.

## Evaluation

- Ask an Agent Chat question that actually uses `search_knowledge`.
- Verify an eligible Production Quality row.
- Verify the Source Trace path for the prepared demo.
- Verify production-to-eval promotion if it is part of the demo.

---

# 13. Do not delete Procurement/mock REST source yet

For this deployment, removing those services from Compose is enough.

Keep source deletion as a later, isolated cleanup commit after the Academy deployment has been verified.

That preserves:

- easy rollback,
- smaller deployment risk,
- cleaner Git history,
- protection from removing code still referenced by old test/demo records.

---

# Final production topology

```text
                   Internet
                      │
                Lightsail 80/443
                      │
                    Nginx
                 ┌────┴────┐
                 │         │
            Next.js      FastAPI
            frontend     backend
                            │
                 ┌──────────┼──────────┐
                 │          │          │
              pgvector   Academy MCP  storage
                 │          │
                 │       Google APIs
                 │
          ingestion worker
```

Governed execution:

```text
User
  ↓
Agent Chat
  ↓
Authorized Agent
  ├── Knowledge retrieval
  ├── AUTO tool → Academy MCP → execute
  └── HUMAN_APPROVAL tool
          ↓
      persist + pause
          ↓
  Governance → Approvals
          ↓
      durable resume
          ↓
      final response
```
