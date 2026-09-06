# Knowgentiq - Enterprise Knowledge & Agents Platform 

> **Enterprise AI agents that can use organizational knowledge, take business actions, operate under explicit policy, pause for human authorization, and leave behind a durable production audit trail.**

Knowgentiq is a **governed enterprise agent platform** for organizations that want AI to do more than answer questions.

The platform combines trusted organizational knowledge with controlled agent execution, access enforcement, human-in-the-loop governance, durable runtime state, operational observability, and production quality feedback.

The problem Knowgentiq addresses begins when AI moves from **answering** to **acting**.

A model that retrieves a document is useful.

An agent that can search internal knowledge, call enterprise systems, create or modify business records, and act on behalf of a user introduces a very different class of engineering problems:

- Who is allowed to use the agent?
- Which organizational knowledge can it access?
- Which tools is it allowed to invoke?
- Which actions can run automatically?
- Which actions require human authorization?
- Can a paused execution safely resume after the original request is gone?
- Can operators reconstruct exactly what happened?
- Can production quality, latency, token usage, and cost be measured?
- Can useful production behavior become future evaluation data?

Knowgentiq is designed around those questions.

It is not simply a document chatbot with tool calling layered on top.

It is an **enterprise agent control plane** for the full lifecycle of an AI-powered business action:

```text
Organizational Knowledge
        ↓
   Grounded AI Agent
        ↓
 Identity & Access Control
        ↓
   Tool Execution Policy
        │
        ├── AUTO ───────────────→ Execute
        │
        └── HUMAN_APPROVAL ─────→ Pause
                                      ↓
                              Governance Review
                                      ↓
                               Durable Resume
        ↓
 Enterprise Systems / APIs
        ↓
 Durable Execution Evidence
        ↓
 Observability & Evaluation
```

---

## What Knowgentiq enables

### Knowledge-aware enterprise agents

Agents can reason over configured organizational knowledge rather than relying only on model memory.

The platform supports:

- multi-tenant knowledge bases,
- knowledge sources and document ingestion,
- chunking and embeddings,
- semantic retrieval,
- grounded answers,
- citations,
- direct knowledge search,
- knowledge access from agent workflows.

### Governed business actions

Agents can invoke business tools under **explicit execution policy**.

Each agent-tool assignment can be configured as:

- `AUTO`
- `HUMAN_APPROVAL`

Risk classification and execution policy are deliberately separate.

A tool may be operationally sensitive but explicitly approved for automatic execution in one workflow, while another tool may require a human decision even if its technical risk is low.

This makes execution policy a business-control decision rather than an implicit side effect of tool metadata.

### Durable human-in-the-loop execution

Governed actions do not depend on keeping an HTTP request alive.

When a `HUMAN_APPROVAL` action is reached:

1. the agent execution pauses,
2. a durable approval record is persisted,
3. the LangGraph checkpoint is retained,
4. the user sees a waiting state,
5. an administrator reviews the action in **Governance → Approvals**,
6. the decision is persisted,
7. the original execution resumes from the checkpoint,
8. the final response is written back into the user conversation.

Approval decisions are never performed inline in Agent Chat.

The interaction surface and the governance decision surface remain intentionally separate.

### Tenant and user access enforcement

The runtime enforces who can discover and execute agents.

- Tenant isolation is preserved.
- Administrators can manage and operate tenant agents.
- End users only see agents explicitly assigned to them.
- Agent configuration and governance surfaces remain admin-only.
- Unauthorized agent access is blocked at the backend, not merely hidden in the UI.

### Durable production execution evidence

Every agent execution is represented as a durable `AgentRun`.

Operational evidence includes:

- user request,
- final response,
- execution status,
- LLM calls,
- tools used,
- persisted execution steps,
- tool inputs and outputs,
- approval checkpoints,
- governance decisions,
- duration,
- token usage,
- estimated cost,
- actor identity,
- thread and checkpoint correlation.

Run Details is an **execution audit**, not a chain-of-thought viewer.

The objective is to answer:

> **What did the system actually do?**

### Production quality feedback

Knowgentiq separates execution observability from quality evaluation.

Knowledge-backed production interactions can be sampled into Online Evaluation and scored on RAG-appropriate quality dimensions such as:

- faithfulness,
- answer relevancy,
- context relevancy.

Useful production runs can be explicitly promoted into reusable evaluation cases.

Tool-only workflows are intentionally not forced through retrieval metrics when no retrieval context exists.

That distinction matters: successful execution and high-quality reasoning are related, but they are not the same problem.

---

# Product model

Knowgentiq exposes two distinct conversational products.

### KB Chat

Direct retrieval-augmented chat against a selected knowledge base.

```text
User
  ↓
Select Knowledge Base
  ↓
Question
  ↓
Retrieval
  ↓
Grounded Answer + Citations
```

### Agent Chat

Conversation with an assigned AI agent that can combine knowledge retrieval and controlled business actions.

```text
User
  ↓
Assigned Agent
  ↓
Conversation
  ↓
Agent Runtime
  ├── Search configured knowledge
  ├── Execute AUTO tools
  ├── Pause on HUMAN_APPROVAL tools
  └── Produce final response
```

KB Chat and Agent Chat are intentionally separate.

The first is a direct knowledge experience.

The second is a governed agent runtime.

---

# Platform architecture

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
     │ Knowledge Layer │   │ Agent Runtime   │   │   Governance    │
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

---

# Why the architecture evolved this way

Knowgentiq started with enterprise knowledge retrieval.

The architecture changed when the system began taking actions.

```text
Enterprise Knowledge + RAG
          ↓
     Agentic execution
          ↓
 Business tools become callable
          ↓
Tool execution requires explicit policy
          ↓
Sensitive actions require durable HITL
          ↓
Agents require tenant/user access controls
          ↓
Execution requires durable runs and checkpoints
          ↓
Operations require latency/token/cost visibility
          ↓
Production RAG requires continuous quality evaluation
          ↓
Useful production behavior becomes evaluation data
```

The key architectural lesson is:

> **Adding agents is not primarily a prompting problem. It creates authorization, governance, durability, auditability, operational, and evaluation problems.**

Knowgentiq treats those as first-class platform concerns.

---

# Governed execution model

Execution behavior comes from persisted policy.

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

A later configuration change does not silently reinterpret an already-paused checkpoint.

The execution semantics attached to the paused action remain the semantics used when that execution resumes.

---

# Product surfaces

## Administrator

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

Administrators configure:

- agents,
- knowledge access,
- tools,
- execution policies,
- user assignments,
- approvals,
- LLM profiles,
- operational metrics,
- production evaluation.

## End user

```text
Chat
├── KB Chat
└── Agent Chat

Knowledge
└── Search
```

End users interact only with permitted knowledge and assigned agents.

---

# Execution observability

Knowgentiq treats `AgentRun` as the durable execution record.

Run History answers:

> **What happened?**

Run Details can show:

- request,
- response,
- execution status,
- agent and actor identity,
- tools executed,
- approval activity,
- persisted execution steps,
- tool inputs and outputs,
- LLM calls,
- token usage,
- estimated cost,
- latency,
- thread and checkpoint correlation.

This creates an operator-facing execution story without exposing private model reasoning.

---

# Evaluation model

Knowgentiq separates **execution evidence** from **quality judgment**.

## Agent Run History

Answers:

> What happened during execution?

It captures operational and governance evidence.

## Production Quality

Answers:

> Was this knowledge-backed interaction good?

For production RAG interactions, the platform can evaluate:

- faithfulness,
- answer relevancy,
- context relevancy.

## Production → evaluation feedback loop

High-value production behavior can be promoted into reusable evaluation cases.

```text
Production Interaction
        ↓
Durable Agent / RAG Evidence
        ↓
Operator Review
        ↓
Promote to Eval
        ↓
Reusable Benchmark Case
```

This connects production behavior back into the evaluation lifecycle.

## Future Agent Quality

Agent-specific quality is intentionally treated as a separate evaluation model.

A future `AgentRun`-based evaluator can measure:

- task completion,
- tool selection,
- tool argument correctness,
- unnecessary/repeated actions,
- execution efficiency,
- policy compliance,
- final-response correctness.

Many execution and governance checks can be deterministic.

Subjective workflow-quality questions can use an LLM judge.

A single agent run may eventually have both:

```text
Agent Quality
+
RAG Quality
```

when the same run both takes actions and uses retrieved organizational knowledge.

---

# Demo scenario

A useful end-to-end demonstration is an **Academy Assistant** with:

- an academy knowledge base,
- `search_knowledge`,
- `create_enquiry`,
- `update_enquiry`,
- one assigned normal user.

Suggested execution policy:

```text
search_knowledge  → AUTO
create_enquiry    → AUTO
update_enquiry    → HUMAN_APPROVAL
```

## 1. Trusted organizational knowledge

As an end user, ask:

> What courses are available at the academy?

Expected behavior:

- the assigned agent is available,
- `search_knowledge` executes,
- the answer is grounded in configured organizational knowledge,
- the interaction is eligible for production RAG evaluation.

## 2. Automatic business action

Ask the agent to create an enquiry or callback request.

Expected behavior:

- `create_enquiry` executes automatically,
- the business action completes,
- Agent Run History records the execution.

## 3. Governed action

Trigger an action requiring `update_enquiry`.

Expected behavior:

- the agent reaches the governed tool,
- the run enters `WAITING_FOR_APPROVAL`,
- Agent Chat shows a waiting state,
- no inline decision buttons are shown.

## 4. Centralized approval

As an administrator:

- open **Governance → Approvals**,
- inspect the pending tool call and arguments,
- approve or reject it.

Expected behavior:

- the persisted governance decision resumes the LangGraph checkpoint,
- the original run completes,
- Agent Chat receives the final response.

## 5. Audit the execution

Open the completed Agent Run.

Inspect:

- original request,
- final response,
- tools used,
- approval evidence,
- execution steps,
- LLM calls,
- tokens,
- cost,
- duration,
- thread/checkpoint correlation.

## 6. Inspect production quality

Open Production Quality and inspect a sampled KB-backed interaction.

This demonstrates the distinction between:

```text
Execution Observability
        vs
Quality Evaluation
```

---

# Technology

## Backend

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

## Frontend

- Next.js
- React
- TypeScript
- TanStack Query
- Tailwind CSS
- shadcn/ui

## Runtime / deployment

- Docker Compose
- PostgreSQL + pgvector
- FastAPI backend
- background ingestion worker
- frontend service
- MCP service
- mock REST service for integration/demo workflows

---

# Production-style deployment

The repository includes a Docker Compose deployment model and Makefile targets for lifecycle management, migrations, backup, and deployment preflight checks.

Create the environment file:

```bash
cp .env.prod.example .env.prod
```

Set strong credentials and the required LLM/API configuration.

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

Database backup and deployment:

```bash
make db-backup
make deploy
```

> The provided environment example is production-oriented but must still be reviewed for deployment-specific secrets, CORS, networking, public exposure, LLM configuration, backup policy, and infrastructure controls.

---

# Deliberate MVP boundaries

Knowgentiq intentionally stops before several capabilities that become more valuable once organizations operate multiple agent configurations across environments:

- immutable agent configuration versions,
- environment-based agent promotion,
- evaluation-gated agent deployment,
- generalized visual workflow authoring,
- broad production Agent Quality judging.

These are deliberate post-MVP evolutions.

They are not required to demonstrate the core governed-agent lifecycle:

```text
Knowledge
→ Agent
→ Tool
→ Policy
→ Approval
→ Durable Resume
→ Audit
→ Observability
→ Evaluation
```

---

# Architecture discussion

A concise way to describe Knowgentiq:

> **I designed and built a governed enterprise AI agent platform around organizational knowledge. The architecture began with RAG, but once agents could take business actions, the system had to solve a different class of problems: explicit execution policy, durable human approval, tenant and user authorization, checkpointed execution, production auditability, cost and latency observability, and continuous quality evaluation.**

The project supports deeper architecture discussions such as:

- Why is tool risk different from execution policy?
- How does human approval survive beyond the original HTTP request?
- How is a paused agent safely resumed?
- How are users prevented from executing unassigned agents?
- How are tenant boundaries enforced?
- How are already-paused actions protected from later policy changes?
- What evidence is persisted for production execution?
- How are token consumption, cost, and latency observed?
- Why should tool-only agent workflows not be scored with RAG faithfulness metrics?
- How can production behavior become future evaluation data?

---

# Product positioning

**Knowgentiq is a governed enterprise AI agent platform for organizations that need AI to work with trusted internal knowledge and safely participate in real business processes.**

It combines:

```text
Trusted Knowledge
+ AI Agents
+ Business Tools
+ Identity & Access
+ Explicit Execution Policy
+ Human Governance
+ Durable Runtime State
+ Execution Auditability
+ Operational Observability
+ Production Evaluation
```

The MVP demonstrates the core technical and product controls required before enterprise AI agents can move from answering questions to participating safely in operational workflows.
