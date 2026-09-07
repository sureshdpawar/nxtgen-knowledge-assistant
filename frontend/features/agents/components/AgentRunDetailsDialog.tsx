"use client";

import {
  Bot,
  CheckCircle2,
  Clock3,
  CircleDollarSign,
  CirclePause,
  MessageSquareText,
  ShieldCheck,
  Timer,
  Wrench,
  XCircle,
} from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { useAgentRun } from "../hooks";
import type {
  AgentRunApproval,
  AgentRunApprovalAction,
  AgentRunApprovalStatus,
  AgentRunStatus,
} from "../types";

type Props = {
  runId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

function formatDuration(durationMs: number | null) {
  if (durationMs === null) return "-";
  if (durationMs < 1000) return `${durationMs.toFixed(0)} ms`;
  return `${(durationMs / 1000).toFixed(2)} s`;
}

function formatDate(value: string | null) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

function formatCost(value: number | null, currency: string | null) {
  if (value === null || !currency) return "Unavailable";
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    }).format(value);
  } catch {
    return `${currency} ${value.toFixed(6)}`;
  }
}

function JsonBlock({ value }: { value: unknown }) {
  return (
    <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

function RunStatusBadge({ status }: { status: AgentRunStatus }) {
  const classes =
    status === "COMPLETED"
      ? "border-emerald-200 bg-emerald-50 text-emerald-700"
      : status === "FAILED"
        ? "border-red-200 bg-red-50 text-red-700"
        : status === "WAITING_FOR_APPROVAL"
          ? "border-amber-200 bg-amber-50 text-amber-700"
          : "border-blue-200 bg-blue-50 text-blue-700";

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${classes}`}>
      {status}
    </span>
  );
}

function ApprovalStatusBadge({ status }: { status: AgentRunApprovalStatus }) {
  if (status === "APPROVED") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" /> Approved
      </span>
    );
  }

  if (status === "REJECTED") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-red-200 bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
        <XCircle className="h-3.5 w-3.5" /> Rejected
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
      <CirclePause className="h-3.5 w-3.5" /> Pending
    </span>
  );
}

function actionName(action: AgentRunApprovalAction, index: number) {
  if (typeof action.name === "string" && action.name.trim()) return action.name;
  return `Action ${index + 1}`;
}

function ApprovalCard({ approval }: { approval: AgentRunApproval }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-amber-50 p-2">
            <ShieldCheck className="h-4 w-4 text-amber-700" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">Human approval checkpoint</p>
            <p className="mt-1 break-all font-mono text-[11px] text-slate-500">
              {approval.checkpoint_id}
            </p>
          </div>
        </div>
        <ApprovalStatusBadge status={approval.status} />
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Requested</p>
          <p className="mt-1 text-sm text-slate-700">{formatDate(approval.requested_at)}</p>
        </div>
        <div className="rounded-lg bg-slate-50 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Decided</p>
          <p className="mt-1 text-sm text-slate-700">{formatDate(approval.decided_at)}</p>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Governed actions</p>
        {approval.actions.length === 0 ? (
          <div className="mt-2 rounded-lg border border-dashed p-3 text-sm text-slate-500">
            No action payload was persisted for this checkpoint.
          </div>
        ) : (
          <div className="mt-2 space-y-2">
            {approval.actions.map((action, index) => (
              <div key={`${approval.id}-${index}`} className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                <div className="flex flex-wrap items-center gap-2">
                  <Wrench className="h-3.5 w-3.5 text-violet-600" />
                  <span className="text-sm font-semibold text-slate-800">{actionName(action, index)}</span>
                  {typeof action.execution_policy === "string" && (
                    <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[11px] font-semibold text-amber-700">
                      {action.execution_policy}
                    </span>
                  )}
                  {typeof action.risk_level === "string" && (
                    <span className="rounded-full bg-slate-200 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                      Risk: {action.risk_level}
                    </span>
                  )}
                </div>
                {action.args && <JsonBlock value={action.args} />}
              </div>
            ))}
          </div>
        )}
      </div>

      {(approval.decided_by_user_id || approval.decision_reason) && (
        <div className="mt-4 border-t border-slate-100 pt-4">
          {approval.decided_by_user_id && (
            <p className="text-xs text-slate-500">
              Decision by <span className="font-mono text-slate-700">{approval.decided_by_user_id}</span>
            </p>
          )}
          {approval.decision_reason && (
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-700">{approval.decision_reason}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default function AgentRunDetailsDialog({ runId, open, onOpenChange }: Props) {
  const runQuery = useAgentRun(runId);
  const run = runQuery.data;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92vh] overflow-y-auto sm:max-w-6xl">
        <DialogHeader>
          <div className="flex flex-wrap items-center gap-3">
            <DialogTitle>Agent Run Details</DialogTitle>
            {run && <RunStatusBadge status={run.status} />}
          </div>
          <DialogDescription>
            Read-only execution audit showing the request, tools, governance decisions, usage, and persisted runtime steps.
          </DialogDescription>
        </DialogHeader>

        {runQuery.isLoading && (
          <div className="rounded-lg border bg-slate-50 p-6 text-sm text-slate-500">Loading run details...</div>
        )}

        {runQuery.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Failed to load agent run details.
          </div>
        )}

        {run && (
          <div className="space-y-7">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
              {[
                ["Status", run.status],
                ["LLM Calls", String(run.llm_calls)],
                ["Executed Tools", String(run.tools_used.length)],
                ["Approvals", String(run.approvals.length)],
                ["Tokens", run.usage.total_tokens.toLocaleString()],
                ["Duration", formatDuration(run.duration_ms)],
              ].map(([label, value]) => (
                <div key={label} className="rounded-lg border p-3">
                  <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
                  <p className="mt-1 text-sm font-semibold text-slate-900">{value}</p>
                </div>
              ))}
            </div>

            <div className="grid gap-3 md:grid-cols-3">
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center gap-2 text-slate-700">
                  <CircleDollarSign className="h-4 w-4" />
                  <p className="text-xs font-semibold uppercase tracking-wide">Estimated cost</p>
                </div>
                <p className="mt-2 text-lg font-bold text-slate-900">
                  {formatCost(run.usage.estimated_cost, run.usage.currency)}
                </p>
                {!run.usage.pricing_complete && (
                  <p className="mt-1 text-xs text-slate-500">Some pricing data is unavailable.</p>
                )}
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center gap-2 text-slate-700">
                  <Timer className="h-4 w-4" />
                  <p className="text-xs font-semibold uppercase tracking-wide">Started</p>
                </div>
                <p className="mt-2 text-sm font-semibold text-slate-900">{formatDate(run.started_at)}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
                <div className="flex items-center gap-2 text-slate-700">
                  <CheckCircle2 className="h-4 w-4" />
                  <p className="text-xs font-semibold uppercase tracking-wide">Completed</p>
                </div>
                <p className="mt-2 text-sm font-semibold text-slate-900">{formatDate(run.completed_at)}</p>
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-slate-900">Request & Response</h3>
              <div className="mt-3 grid gap-4 lg:grid-cols-2">
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="flex items-center gap-2">
                    <MessageSquareText className="h-4 w-4 text-slate-500" />
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">User request</p>
                  </div>
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">{run.query}</p>
                </div>
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="flex items-center gap-2">
                    <Bot className="h-4 w-4 text-slate-500" />
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Final response</p>
                  </div>
                  <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                    {run.answer ?? "No answer recorded."}
                  </p>
                </div>
              </div>
            </div>

            {run.error_message && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-red-500">Error</p>
                <p className="mt-2 whitespace-pre-wrap text-sm text-red-700">{run.error_message}</p>
              </div>
            )}

            <div>
              <h3 className="font-semibold text-slate-900">Executed Tools</h3>
              {run.tools_used.length === 0 ? (
                <div className="mt-3 rounded-lg border border-dashed p-4 text-sm text-slate-500">
                  No tools executed during this run.
                </div>
              ) : (
                <div className="mt-3 flex flex-wrap gap-2">
                  {run.tools_used.map((toolName) => (
                    <span key={toolName} className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700">
                      {toolName}
                    </span>
                  ))}
                </div>
              )}
            </div>

            <div>
              <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">Governance Audit</h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Read-only approval evidence. Decisions remain exclusively in Governance → Approvals.
                  </p>
                </div>
                <span className="w-fit rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                  {run.approvals.length} checkpoint{run.approvals.length === 1 ? "" : "s"}
                </span>
              </div>

              {run.approvals.length === 0 ? (
                <div className="mt-3 rounded-lg border border-dashed p-4 text-sm text-slate-500">
                  No human approval was required for this run.
                </div>
              ) : (
                <div className="mt-3 space-y-3">
                  {run.approvals.map((approval) => (
                    <ApprovalCard key={approval.id} approval={approval} />
                  ))}
                </div>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h3 className="font-semibold text-slate-900">Execution Trace</h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Persisted operational steps only. This is execution evidence, not model chain-of-thought.
                  </p>
                </div>
                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                  {run.steps.length} steps
                </span>
              </div>

              <div className="mt-4 space-y-3">
                {run.steps.length === 0 && (
                  <div className="rounded-lg border border-dashed p-5 text-sm text-slate-500">No execution steps recorded.</div>
                )}
                {run.steps.map((step) => (
                  <div key={step.id} className="rounded-xl border border-slate-200 bg-white p-4">
                    <div className="flex items-start gap-3">
                      <div className={step.step_type === "TOOL" ? "rounded-lg bg-violet-50 p-2" : "rounded-lg bg-blue-50 p-2"}>
                        {step.step_type === "TOOL" ? (
                          <Wrench className="h-4 w-4 text-violet-600" />
                        ) : (
                          <Bot className="h-4 w-4 text-blue-600" />
                        )}
                      </div>
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <p className="text-sm font-semibold text-slate-900">Step {step.step_number} · {step.name}</p>
                          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">{step.step_type}</span>
                        </div>
                        <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                          <span className="flex items-center gap-1">
                            {step.status === "COMPLETED" ? (
                              <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />
                            ) : (
                              <XCircle className="h-3.5 w-3.5 text-red-600" />
                            )}
                            {step.status}
                          </span>
                          {step.duration_ms !== null && (
                            <span className="flex items-center gap-1">
                              <Clock3 className="h-3.5 w-3.5" /> {formatDuration(step.duration_ms)}
                            </span>
                          )}
                          <span>{formatDate(step.created_at)}</span>
                        </div>
                      </div>
                    </div>

                    {step.input_data && (
                      <details className="mt-4">
                        <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-slate-500">Input</summary>
                        <JsonBlock value={step.input_data} />
                      </details>
                    )}
                    {step.output_data && (
                      <details className="mt-3">
                        <summary className="cursor-pointer text-xs font-semibold uppercase tracking-wide text-slate-500">Output</summary>
                        <JsonBlock value={step.output_data} />
                      </details>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="font-semibold text-slate-900">Execution Context</h3>
              <div className="mt-3 grid gap-3 sm:grid-cols-2">
                {[
                  ["Actor Type", run.actor_type],
                  ["Actor ID", run.actor_id],
                  ["Thread ID", run.thread_id ?? "-"],
                  ["Checkpoint ID", run.checkpoint_id ?? "-"],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-lg border bg-slate-50 p-3">
                    <p className="text-xs uppercase tracking-wide text-slate-400">{label}</p>
                    <p className="mt-1 break-all font-mono text-xs text-slate-700">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {run.context_metadata && Object.keys(run.context_metadata).length > 0 && (
              <div>
                <h3 className="font-semibold text-slate-900">Correlation Context</h3>
                <p className="mt-1 text-xs text-slate-500">Platform and business identifiers attached to this run.</p>
                <JsonBlock value={run.context_metadata} />
              </div>
            )}

            <div className="rounded-lg border bg-slate-50 p-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Run ID</p>
                  <p className="mt-1 break-all font-mono text-xs text-slate-600">{run.id}</p>
                </div>
                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">Agent ID</p>
                  <p className="mt-1 break-all font-mono text-xs text-slate-600">{run.agent_id}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
