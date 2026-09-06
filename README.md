# Knowgentiq - Enterprise Knowledge & Agents Platform 

**A governed enterprise RAG and agent platform for organizational knowledge, controlled tool execution, human approval, access enforcement, and production feedback.**

NXTGEN started as an enterprise knowledge assistant and evolved into a governed agent platform as soon as the system moved from answering questions to taking actions.

The core product question is no longer only:

> Can the model answer from trusted organizational knowledge?

It is also:

> Can an agent act safely, under explicit policy, with durable approval and enough evidence to understand what happened in production?

## Product at a glance

NXTGEN provides two distinct user experiences:

- **KB Chat** — direct retrieval-augmented chat against a selected knowledge base.
- **Agent Chat** — conversations with assigned agents that can search configured knowledge bases, invoke business tools, pause for human approval, and resume after a governance decision.

Administrators configure agents, tools, execution policies, knowledge access, user access, approvals, operational metrics, and evaluation.

## Core capabilities

### Enterprise knowledge and RAG

- Multi-tenant knowledge bases and sources
- Document ingestion, chunking, embeddings, and semantic retrieval
- KB Chat with grounded answers and citations
- Knowledge search for both direct users and agents

### Governed agents

- LangGraph-based agent execution
- Durable agent threads and checkpoints
- Configurable knowledge bases and tools per agent
- Explicit tool execution policy:
  - `AUTO`
  - `HUMAN_APPROVAL`
- Tool risk and execution policy remain separate concepts
- Durable pause/resume for governed actions

### Access control

- Tenant isolation
- Admin and end-user product surfaces
- User-to-agent assignment
- Admins can operate all tenant agents
- End users only see and execute assigned agents

### Human-in-the-loop governance

All governed decisions are centralized under **Governance → Approvals**.

Agent Chat never performs inline approval decisions. When a `HUMAN_APPROVAL` tool is requested:

1. the agent run pauses,
2. an approval record is persisted,
3. Agent Chat shows a waiting state,
4. an administrator approves or rejects through Governance → Approvals,
5. LangGraph resumes from the durable checkpoint,
6. the final response is synchronized back to the Agent Chat conversation.

### Durable run observability

Every agent execution is represented by an `AgentRun` with persisted operational evidence such as:

- request and final response,
- run status,
- LLM calls,
- tools used,
- execution steps,
- duration,
- token usage,
- estimated cost,
- actor and thread correlation,
- approval checkpoints and decisions.

Run Details is an execution audit view, not a chain-of-thought viewer.

### Production evaluation

Production RAG interactions can be sampled into Online Evaluation and scored using RAG-appropriate quality dimensions such as:

- faithfulness,
- answer relevancy,
- context relevancy.

Good production runs can be explicitly promoted into reusable evaluation cases.

Tool-only agent interactions are intentionally not forced through RAG metrics. Agent-specific production evaluation—task completion, tool selection, argument correctness, execution efficiency, and policy compliance—is a natural post-MVP evaluation layer over `AgentRun` evidence.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      Web Client      │
                         │  KB Chat / Agent Chat│
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐
                         │      FastAPI API      │
                         │ Auth / Tenant / Access│
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼──────────────────────┐
              │                     │                      │
     ┌────────▼────────┐   ┌────────▼────────┐   ┌────────▼────────┐
     │ Knowledge / RAG │   │ Agent Runtime   │   │   Governance    │
     │ search/citations│   │    LangGraph    │   │ approvals/policy│
     └────────┬────────┘   └────────┬────────┘   └────────┬────────┘
              │                     │                      │
              │            ┌────────┼────────┐             │
              │            │                 │             │
              │     ┌──────▼──────┐   ┌─────▼──────┐      │
              │     │    Tools    │   │ Checkpoint │◄─────┘
              │     │ AUTO / HITL │   │  Resume    │
              │     └──────┬──────┘   └─────┬──────┘
              │            │                │
              └────────────┴────────┬───────┘
                                    │
                         ┌──────────▼───────────┐
                         │ Durable Persistence  │
                         │ PostgreSQL / pgvector│
                         │ Runs / Steps / Usage │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
          ┌─────────▼─────────┐           ┌────────▼────────┐
          │  Observability    │           │   Evaluation    │
          │ cost/latency/runs │           │ production RAG  │
          └───────────────────┘           └─────────────────┘
```

## Why the architecture evolved this way

The project intentionally follows the problems introduced by increasing agent capability:

```text
Enterprise RAG
      ↓
Agentic execution
      ↓
Tool execution requires governance
      ↓
Explicit AUTO vs HUMAN_APPROVAL policy
      ↓
Sensitive actions require durable HITL
      ↓
Agents require tenant/user access controls
      ↓
Production execution requires durable runs and steps
      ↓
Operations require latency/token/cost observability
      ↓
Production RAG requires continuous quality evaluation
      ↓
Useful production behavior can become golden eval cases
```

This progression is central to the design: adding agents is not only a prompting problem. It creates authorization, governance, durability, auditability, and evaluation problems.

---

## Product surfaces

### Admin

```text
Dashboard

Knowledge
├── Knowledge Bases
├── Search
└── Chat

Agent Studio
├── Agents
├── Chat
├── Tools
└── Integrations

Evaluation
├── Test & Benchmark
└── Production Quality

Governance
├── LLM Profiles
├── Approvals
├── Usage & Quotas
└── Cost Analytics

Admin
└── Users
```

### End user

```text
Chat
├── KB Chat
└── Agent Chat

Knowledge
└── Search
```

KB Chat and Agent Chat are deliberately separate products. Agent configuration and operational tooling are admin-only.

---

## Governed execution model

Risk and execution policy are independent.

A tool may be conceptually low risk but still require human approval for a particular agent, or a write tool may be explicitly configured for automatic execution.

```text
Tool requested
      ↓
Read persisted execution policy
      ↓
┌───────────────────┬────────────────────────┐
│ AUTO              │ HUMAN_APPROVAL         │
│ execute           │ persist approval       │
│ continue          │ checkpoint + pause     │
└───────────────────┴────────────┬───────────┘
                                 ↓
                       Governance → Approvals
                                 ↓
                         approve / reject
                                 ↓
                         resume LangGraph
                                 ↓
                          final response
```

The policy stored for the execution is respected across resume so a later configuration change does not silently rewrite the meaning of an already-paused checkpoint.

---

## Demo scenario

A useful demo agent is an **Academy Assistant** configured with:

- an academy knowledge base,
- `search_knowledge`,
- `create_enquiry`,
- `update_enquiry`,
- an assigned end user.

Suggested policy:

```text
search_knowledge  → AUTO
create_enquiry    → AUTO
update_enquiry    → HUMAN_APPROVAL
```

### 1. Demonstrate grounded knowledge

As an end user, open Agent Chat and ask:

> What courses are available at the academy?

Expected behavior:

- the assigned agent is available,
- `search_knowledge` executes,
- the answer is grounded in configured organizational knowledge,
- the RAG interaction is eligible for production quality sampling.

### 2. Demonstrate automatic business action

Ask the agent to create an enquiry or callback request.

Expected behavior:

- `create_enquiry` executes automatically,
- the agent reports the business outcome,
- Agent Run History records the execution.

### 3. Demonstrate governed action

Trigger an update requiring `update_enquiry`.

Expected behavior:

- the agent reaches the governed tool,
- the run enters `WAITING_FOR_APPROVAL`,
- Agent Chat displays a waiting state,
- no approval/rejection controls appear inline.

### 4. Demonstrate centralized governance

As an administrator:

- open **Governance → Approvals**,
- inspect the pending action and arguments,
- approve or reject it.

Expected behavior:

- the persisted decision resumes the LangGraph checkpoint,
- the run completes,
- Agent Chat receives the final response.

### 5. Demonstrate auditability

Open the completed run in Agent Run History.

Show:

- user request,
- final response,
- tools executed,
- governance approval evidence,
- persisted execution steps,
- LLM calls,
- tokens,
- estimated cost,
- duration,
- actor/thread/checkpoint correlation.

### 6. Demonstrate production feedback

Open Production Quality and show a sampled KB-backed interaction.

Explain that RAG metrics are applied only when retrieval evidence exists. Tool-only workflows remain observable through Agent Runs rather than being assigned meaningless retrieval metrics.

Optionally promote a useful completed run into an evaluation case.

---

## Technology

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- pgvector
- LangChain
- LangGraph
- LangGraph PostgreSQL checkpointing
- Model Context Protocol (MCP)
- OpenTelemetry

### Frontend

- Next.js
- React
- TypeScript
- TanStack Query
- Tailwind CSS
- shadcn/ui

### Runtime / deployment

- Docker Compose
- PostgreSQL + pgvector
- FastAPI backend
- background ingestion worker
- frontend service
- MCP service
- mock REST service for integration/demo workflows

---

## Production-style deployment

The repository includes a production-oriented Docker Compose configuration and Makefile targets for lifecycle, migrations, backup, and preflight checks.

Create the environment file:

```bash
cp .env.prod.example .env.prod
```

Set strong secrets and the required LLM/API configuration before starting the stack.

Build and start:

```bash
make build
make up
```

Apply database migrations:

```bash
make migrate
```

Create the initial superadmin:

```bash
make superadmin
```

Useful operational commands:

```bash
make ps
make logs
make backend-logs
make worker-logs
make db-status
make migration-current
make migration-heads
make preflight
```

The deployment target also supports database backup before migration/deployment:

```bash
make db-backup
make deploy
```

> The environment example is production-oriented. Review credentials, CORS, public ports, LLM endpoints, and deployment-specific infrastructure before exposing the application outside a controlled environment.

---

## Evaluation model

NXTGEN separates **execution observability** from **quality evaluation**.

### Agent Run History

Answers:

> What happened?

It captures durable operational evidence for agent execution.

### Online Evaluation

Answers:

> Was this grounded RAG interaction good?

It evaluates production RAG interactions where retrieved context exists.

### Post-MVP Agent Quality

A future AgentRun-based evaluator can answer:

- Did the agent complete the task?
- Did it choose the correct tool?
- Were tool arguments correct?
- Were unnecessary tool calls avoided?
- Was execution policy respected?
- Did the final response accurately describe the actual outcome?

Many governance and execution checks can be deterministic; subjective task-quality dimensions can use an LLM judge.

---

## Deliberate MVP boundaries

The MVP intentionally stops before several platform-level capabilities that become valuable at larger operational scale:

- immutable agent configuration versions,
- environment-based agent promotion,
- evaluation-gated deployment,
- generalized visual workflow authoring,
- broad agent-quality judging across arbitrary tool workflows.

These are not required to demonstrate the core governed-agent lifecycle and would add substantial operational complexity before the product has multiple production agent versions to manage.

---

## Architecture Discussion

A concise description of the project:

> I designed and built a governed enterprise agent platform around organizational knowledge. It began as RAG, but once agents could take business actions the architecture had to evolve: tool execution needed explicit policies, sensitive actions needed durable human approval, agents needed tenant/user access controls, and production behavior needed durable run observability and evaluation.

Useful design questions this project can demonstrate:

- Why is tool risk different from execution policy?
- How does a human approval survive beyond the original HTTP request?
- How is a paused agent resumed safely?
- How are users prevented from executing unassigned agents?
- How are tenant boundaries enforced?
- What evidence is persisted for production agent execution?
- How are token usage, cost, and latency observed?
- Why should tool-only agent workflows not be scored with RAG faithfulness metrics?
- How can production behavior feed offline evaluation?

---

## Current MVP positioning

**NXTGEN is a governed enterprise RAG agent MVP that can answer from organizational knowledge, invoke tools under explicit execution policies, require human approval for sensitive actions, enforce user access, and provide operational and evaluation feedback.**

The product is intended as an MVP and architecture demonstration rather than a claim of feature parity with mature enterprise AI platforms.
