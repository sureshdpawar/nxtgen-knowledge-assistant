# NXTGEN MVP Demo Script

Target duration: **5–7 minutes**

The goal is to tell one coherent story: trusted knowledge → agent action → governance → durable execution → production feedback.

## Before the demo

Prepare one active **Academy Assistant** agent with:

- academy knowledge base attached,
- `search_knowledge`,
- `create_enquiry`,
- `update_enquiry`,
- one normal user assigned.

Policies:

```text
search_knowledge  → AUTO
create_enquiry    → AUTO
update_enquiry    → HUMAN_APPROVAL
```

Have two browser sessions ready if possible:

- normal USER session,
- ADMIN session.

Confirm there are no stale pending approvals that could confuse the flow.

## 0:00–0:45 — Frame the problem

Say:

> This started as an enterprise RAG system. Once I allowed agents to take business actions, the problem changed. I needed explicit execution policy, durable human approval, tenant and user access enforcement, and enough persisted evidence to audit and evaluate production behavior.

Show the application briefly.

Do not begin with implementation details.

## 0:45–1:30 — Show agent configuration

ADMIN → Agent Studio → Agents → Academy Assistant.

Show:

- attached knowledge base,
- assigned tools,
- execution policies,
- user access.

Call out:

> Risk and execution policy are intentionally separate. Policy is explicit per agent/tool assignment.

Do not spend time editing configuration.

## 1:30–2:15 — Grounded knowledge

USER → Agent Chat.

Ask:

> What courses are available at the academy?

Show the grounded response.

Explain:

> This is an agent interaction, but because it used knowledge retrieval it is also eligible for production RAG quality evaluation.

## 2:15–3:00 — Automatic action

Ask for an enquiry/callback with the demo user's prepared details.

Show `create_enquiry` completing automatically.

Say:

> This tool is explicitly AUTO for this agent, so no human decision is introduced merely because it changes business state.

## 3:00–4:10 — Human approval

Trigger a request that requires `update_enquiry`.

When Agent Chat pauses, point out the waiting state.

Say:

> The chat is only the request surface. Approval decisions are centralized in Governance, so both admins and end users see consistent behavior here.

Switch to ADMIN → Governance → Approvals.

Inspect:

- action,
- arguments,
- policy.

Approve it.

Return to Agent Chat and show the resumed final answer.

Say:

> The original execution is resumed from a durable LangGraph checkpoint. This is not a second ad-hoc tool invocation.

## 4:10–5:10 — Run audit

Open Agent Run History → completed run → Run Details.

Show:

- request/final response,
- tools,
- approval evidence,
- execution steps,
- tokens/cost,
- duration.

Say:

> Run History answers what happened. It is persisted operational evidence, not chain-of-thought.

## 5:10–6:00 — Production evaluation

Open Evaluation → Production Quality.

Show a sampled KB-backed interaction.

Say:

> Online Evaluation answers a different question: was the RAG interaction good? I intentionally do not force tool-only agent runs through faithfulness or context-relevancy metrics when no retrieval context exists.

If useful, show promotion of a completed production run to an eval case.

## 6:00–6:45 — Close with architecture judgment

Say:

> For the MVP I stopped before immutable agent versions and eval-gated deployment. Those become valuable once multiple agent configurations are being promoted across environments. The current system proves the core governed lifecycle: knowledge, action, policy, approval, access, durable execution, observability, and production RAG feedback.

Then stop.

## Questions to expect

### Why not approve inline in Agent Chat?

Because the interaction surface should not become the governance decision surface. Centralizing decisions gives consistent behavior, clearer authorization, and one audit trail.

### Why persist approvals separately from LangGraph state?

LangGraph checkpointing provides execution durability. The product-level approval record provides governance state, actor, timestamps, reason, tenant scoping, and operator visibility.

### Why separate risk and execution policy?

Risk is descriptive classification. Execution policy is the actual behavior the runtime must enforce. Conflating them makes explicit business policy impossible.

### Why is Agent Run History not Agent Evaluation?

Run History records execution evidence. Evaluation judges quality. A successful tool call can still be the wrong tool or an inefficient plan.

### Why do tool-only agent runs not appear in RAG Online Evaluation?

Faithfulness and context relevancy require retrieval evidence. Tool workflows need agent-specific metrics such as task completion, tool selection, argument correctness, efficiency, and policy compliance.

### What is intentionally post-MVP?

Immutable agent versions, environment promotion, eval-gated deployment, generalized workflow authoring, and broad AgentRun quality judging.
