# MVP Demo Readiness Checklist

Use this immediately before recording or interviewing.

## Environment

- [ ] Backend starts cleanly
- [ ] Frontend starts cleanly
- [ ] Database migrations are at head
- [ ] Background worker is healthy
- [ ] LLM profile/API is working
- [ ] Demo MCP/REST service is reachable
- [ ] No browser console errors on demo pages

## Demo identities

- [ ] ADMIN login works
- [ ] USER login works
- [ ] USER is assigned only to the intended demo agent
- [ ] USER cannot access admin Agent Studio / Governance pages

## Academy Assistant

- [ ] Agent is ACTIVE
- [ ] Academy KB is assigned
- [ ] `search_knowledge` assigned and AUTO
- [ ] `create_enquiry` assigned and AUTO
- [ ] `update_enquiry` assigned and HUMAN_APPROVAL
- [ ] Demo user has agent access

## Knowledge path

- [ ] A known academy question returns a good answer
- [ ] `search_knowledge` appears in the Agent Run
- [ ] Citations/grounding display correctly where expected
- [ ] KB-backed interaction can be found in Production Quality after sampling/evaluation

## AUTO tool path

- [ ] Prepared demo user details are valid
- [ ] `create_enquiry` succeeds
- [ ] No approval is requested for the AUTO action
- [ ] Run History records the tool

## HUMAN_APPROVAL path

- [ ] `update_enquiry` creates a pending approval
- [ ] Agent Chat shows waiting state only
- [ ] No inline approve/reject buttons exist
- [ ] Approval appears under Governance → Approvals
- [ ] Admin can inspect the requested action/arguments
- [ ] Approve/reject is protected against duplicate decisions
- [ ] Approval resumes the paused execution
- [ ] Final response appears back in Agent Chat

## Run Details

- [ ] Completed run opens
- [ ] Request and response visible
- [ ] Tools visible
- [ ] Governance approval evidence visible
- [ ] Execution steps visible
- [ ] Token usage visible
- [ ] Cost visible or clearly marked unavailable
- [ ] Duration visible
- [ ] No chain-of-thought is exposed

## Evaluation

- [ ] Production Quality page loads
- [ ] At least one completed RAG evaluation exists for demonstration
- [ ] Source trace/debug view works for the prepared example
- [ ] Promotion to eval case works for an eligible run if you plan to show it

## Presentation hygiene

- [ ] Remove stale test conversations that distract from the demo
- [ ] Remove stale pending approvals
- [ ] Use believable names and data
- [ ] Keep one clean Academy Assistant scenario
- [ ] Browser zoom/layout looks good
- [ ] Avoid showing secrets, `.env` values, tokens, or private credentials
- [ ] Keep admin and user sessions in separate browser profiles/windows
- [ ] Rehearse once with a stopwatch

## Final rule

If a non-essential feature fails during rehearsal, do not expand architecture to fix the demo.

Fix only issues that block this story:

```text
Knowledge
→ Agent
→ AUTO action
→ HUMAN_APPROVAL
→ Resume
→ Run audit
→ Production RAG evaluation
```
