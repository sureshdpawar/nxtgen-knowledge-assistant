"use client";

import { type FormEvent, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock3,
  History,
  LoaderCircle,
  Play,
  RefreshCw,
  RotateCcw,
  ShieldAlert,
  Wrench,
} from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { runAgentStream } from "../api";
import {
  useAgentCheckpointHistory,
  useAgentGraphState,
  useAgentRun,
} from "../hooks";

import type {
  Agent,
  AgentProgressEvent,
  AgentProgressItem,
  AgentRunResponse,
  ConversationMessage,
} from "../types";

type Props = { agent: Agent };

function shortId(value: string | null | undefined) {
  if (!value) return "-";
  return value.length > 16 ? `${value.slice(0, 8)}…${value.slice(-6)}` : value;
}

export default function TestAgentDialog({ agent }: Props) {
  const queryClient = useQueryClient();

  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [runId, setRunId] = useState<string | null>(null);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [approval, setApproval] = useState<AgentRunResponse | null>(null);
  const [progress, setProgress] = useState<AgentProgressItem[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [error, setError] = useState<string | null>(null);

  const runDetailsQuery = useAgentRun(runId);
  const graphStateQuery = useAgentGraphState(agent.id, threadId);
  const historyQuery = useAgentCheckpointHistory(agent.id, threadId);

  async function refreshRuntime() {
    const [
      graphStateResult,
      historyResult,
      runResult,
    ] = await Promise.all([
      graphStateQuery.refetch(),
      historyQuery.refetch(),
      runId
        ? runDetailsQuery.refetch()
        : Promise.resolve(null),
    ]);

    if (
      approval
      && runResult?.data
      && runResult.data.status
        !== "WAITING_FOR_APPROVAL"
    ) {
      setApproval(null);

      setMessages((current) => {
        const next: ConversationMessage[] = [
          ...current,
          {
            id: `approval-resolved-${Date.now()}`,
            role: "system",
            content:
              runResult.data.status === "COMPLETED"
                ? "The approval was resolved and the agent run resumed successfully."
                : "The approval decision was recorded and the agent run resumed.",
          },
        ];

        if (
          runResult.data.answer
          && !current.some(
            (message) =>
              message.role === "assistant"
              && message.content
                === runResult.data.answer,
          )
        ) {
          next.push({
            id: `assistant-resumed-${runResult.data.id}-${Date.now()}`,
            role: "assistant",
            content:
              runResult.data.answer,
          });
        }

        return next;
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agent-runs",
          agent.id,
        ],
      });
    }

    return {
      graphStateResult,
      historyResult,
      runResult,
    };
  }

  function newConversation() {
    if (running) return;
    setQuery("");
    setThreadId(null);
    setRunId(null);
    setResult(null);
    setApproval(null);
    setProgress([]);
    setMessages([]);
    setError(null);
  }

  function handleOpenChange(nextOpen: boolean) {
    setOpen(nextOpen);
    if (!nextOpen) newConversation();
  }

  function handleProgressEvent(event: AgentProgressEvent) {
    if (event.type === "run_started") {
      setRunId(event.run_id);
      if (event.thread_id) setThreadId(event.thread_id);
      return;
    }

    if (event.type === "llm_started") {
      setProgress((current) => [
        ...current,
        {
          id: `llm-${event.iteration}-${Date.now()}`,
          type: "LLM",
          name: event.iteration === 1 ? "Thinking" : "Generating response",
          status: "RUNNING",
        },
      ]);
      return;
    }

    if (event.type === "llm_completed") {
      setProgress((current) => {
        const next = [...current];
        const index = next.findLastIndex(
          (item) => item.type === "LLM" && item.status === "RUNNING",
        );
        if (index !== -1) {
          next[index] = {
            ...next[index],
            status: "COMPLETED",
            duration_ms: event.duration_ms,
          };
        }
        return next;
      });
      return;
    }

    if (event.type === "tool_started") {
      setProgress((current) => [
        ...current,
        {
          id: `tool-${event.name}-${Date.now()}`,
          type: "TOOL",
          name: event.name,
          status: "RUNNING",
        },
      ]);
      return;
    }

    if (event.type === "tool_completed") {
      setProgress((current) => {
        const next = [...current];
        const index = next.findLastIndex(
          (item) =>
            item.type === "TOOL" &&
            item.name === event.name &&
            item.status === "RUNNING",
        );
        if (index !== -1) {
          next[index] = {
            ...next[index],
            status: "COMPLETED",
            duration_ms: event.duration_ms,
          };
        }
        return next;
      });
      return;
    }

    if (event.type === "approval_required") {
      setApproval(event.result);
      setResult(event.result);
      setRunId(event.result.run_id);
      setThreadId(event.result.thread_id);
      setRunning(false);
      setMessages((current) => [
        ...current,
        {
          id: `approval-${event.result.run_id}`,
          role: "system",
          content:
            "This run is waiting for a governed action approval. Review and decide it from Governance → Approvals.",
        },
      ]);
      void refreshRuntime();
      return;
    }

    if (event.type === "completed") {
      setResult(event.result);
      setRunId(event.result.run_id);
      setThreadId(event.result.thread_id);
      setApproval(null);
      setRunning(false);

      if (event.result.answer) {
        setMessages((current) => [
          ...current,
          {
            id: `assistant-${event.result.run_id}`,
            role: "assistant",
            content: event.result.answer!,
          },
        ]);
      }

      queryClient.invalidateQueries({ queryKey: ["agent-runs", agent.id] });
      void refreshRuntime();
      return;
    }

    if (event.type === "failed") {
      setError(event.message);
      setRunning(false);
    }
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const cleanQuery = query.trim();
    if (!cleanQuery || running || approval) return;

    setMessages((current) => [
      ...current,
      {
        id: `user-${Date.now()}`,
        role: "user",
        content: cleanQuery,
      },
    ]);
    setQuery("");
    setResult(null);
    setProgress([]);
    setError(null);
    setRunning(true);

    try {
      await runAgentStream(
        agent.id,
        {
          query: cleanQuery,
          thread_id: threadId,
        },
        handleProgressEvent,
      );
    } catch {
      setError("Agent execution failed.");
      setRunning(false);
    }
  }

  const graphState = graphStateQuery.data;

  return (
    <>
      <Button
        type="button"
        disabled={agent.status !== "ACTIVE"}
        onClick={() => setOpen(true)}
      >
        <Play className="mr-2 h-4 w-4" />
        Test Agent
      </Button>

      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="max-h-[94vh] overflow-y-auto sm:max-w-7xl">
          <DialogHeader>
            <div className="flex items-start justify-between gap-4 pr-8">
              <div>
                <DialogTitle className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-violet-600" />
                  Agent Studio · Runtime
                </DialogTitle>
                <DialogDescription className="mt-1">
                  Exercise durable LangGraph threads, checkpoints, tools and governed action approvals for{" "}
                  <span className="font-medium text-slate-700">{agent.name}</span>.
                </DialogDescription>
              </div>
              <Button type="button" variant="outline" onClick={newConversation} disabled={running}>
                <RotateCcw className="mr-2 h-4 w-4" />
                New Conversation
              </Button>
            </div>
          </DialogHeader>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="space-y-4">
              <div className="rounded-xl border bg-white">
                <div className="border-b px-4 py-3">
                  <div className="flex flex-wrap items-center gap-3 text-xs text-slate-500">
                    <span>Thread <span className="font-mono text-slate-700">{shortId(threadId)}</span></span>
                    <span>Run <span className="font-mono text-slate-700">{shortId(runId)}</span></span>
                    <span>Checkpoint <span className="font-mono text-slate-700">{shortId(result?.checkpoint_id ?? graphState?.checkpoint_id)}</span></span>
                  </div>
                </div>

                <div className="max-h-[360px] min-h-[240px] space-y-3 overflow-y-auto p-4">
                  {messages.length === 0 && (
                    <div className="flex min-h-[200px] items-center justify-center text-center text-sm text-slate-400">
                      Start a conversation. The first turn creates a durable LangGraph thread.
                    </div>
                  )}

                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={
                        message.role === "user"
                          ? "ml-10 rounded-xl bg-blue-600 p-3 text-sm text-white"
                          : message.role === "assistant"
                            ? "mr-10 rounded-xl bg-slate-100 p-3 text-sm text-slate-700"
                            : "rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800"
                      }
                    >
                      <p className="mb-1 text-[10px] font-semibold uppercase tracking-wide opacity-70">
                        {message.role}
                      </p>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>
                  ))}
                </div>

                <form onSubmit={submit} className="border-t p-4">
                  <textarea
                    value={query}
                    onChange={(event) =>
                      setQuery(event.target.value)
                    }
                    onKeyDown={(event) => {
                      if (
                        event.key === "Enter"
                        && !event.shiftKey
                      ) {
                        event.preventDefault();

                        if (
                          !running
                          && !approval
                          && query.trim()
                        ) {
                          event.currentTarget
                            .form
                            ?.requestSubmit();
                        }
                      }
                    }}
                    rows={3}
                    disabled={
                      running || Boolean(approval)
                    }
                    placeholder={
                      approval
                        ? "This run is waiting for an Admin decision in Governance → Approvals."
                        : "Message the agent..."
                    }
                    className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 disabled:bg-slate-50"
                  />
                  <div className="mt-3 flex items-center justify-between">
                    <p className="text-xs text-slate-400">
                      {threadId ? "Continuing persisted thread" : "New LangGraph thread"}
                    </p>
                    <Button type="submit" disabled={running || Boolean(approval) || !query.trim()}>
                      {running ? (
                        <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                      ) : (
                        <Play className="mr-2 h-4 w-4" />
                      )}
                      Send
                    </Button>
                  </div>
                </form>
              </div>

              {approval && (
                <div className="rounded-xl border border-amber-300 bg-amber-50 p-5">
                  <div className="flex items-start gap-3">
                    <ShieldAlert className="mt-0.5 h-5 w-5 text-amber-700" />
                    <div className="min-w-0 flex-1">
                      <h3 className="font-semibold text-amber-950">Waiting for approval</h3>
                      <p className="mt-1 text-sm text-amber-800">
                        LangGraph has persisted and paused this run because one or more proposed actions require human approval. The action has not executed.
                      </p>

                      <p className="mt-2 text-sm text-amber-800">
                        Approval decisions are managed centrally under Governance → Approvals. After an Admin approves or rejects the request, this persisted run resumes from the same checkpoint.
                      </p>

                      <div className="mt-4 space-y-3">
                        {approval.interrupts.map((interrupt, index) => (
                          <pre
                            key={index}
                            className="max-h-56 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-100"
                          >
                            {JSON.stringify(interrupt, null, 2)}
                          </pre>
                        ))}
                      </div>

                      <div className="mt-4 flex flex-wrap items-center gap-2">
                        <Link
                          href="/approvals"
                          className="
                            inline-flex
                            h-10
                            items-center
                            justify-center
                            rounded-md
                            bg-primary
                            px-4
                            py-2
                            text-sm
                            font-medium
                            text-primary-foreground
                            shadow
                            transition-colors
                            hover:bg-primary/90
                            focus-visible:outline-none
                            focus-visible:ring-1
                            focus-visible:ring-ring
                          "
                        >
                          Open Governance Approvals
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </Link>

                        <Button
                          type="button"
                          variant="outline"
                          disabled={graphStateQuery.isFetching || historyQuery.isFetching}
                          onClick={() => void refreshRuntime()}
                        >
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Refresh Runtime
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  {error}
                </div>
              )}

              {(running || progress.length > 0) && (
                <div className="rounded-xl border bg-white p-5">
                  <h3 className="font-semibold text-slate-900">Live Execution</h3>
                  <div className="mt-4 space-y-3">
                    {progress.map((item) => (
                      <div key={item.id} className="flex items-center gap-3 text-sm">
                        {item.status === "RUNNING" ? (
                          <LoaderCircle className="h-4 w-4 animate-spin text-blue-600" />
                        ) : (
                          <CheckCircle2 className="h-4 w-4 text-green-600" />
                        )}
                        {item.type === "TOOL" ? (
                          <Wrench className="h-4 w-4 text-violet-600" />
                        ) : (
                          <Bot className="h-4 w-4 text-blue-600" />
                        )}
                        <span className="flex-1">{item.name}</span>
                        {item.duration_ms !== undefined && (
                          <span className="text-xs text-slate-400">
                            {item.duration_ms.toFixed(0)} ms
                          </span>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div className="rounded-xl border bg-slate-50 p-5">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="font-semibold text-slate-900">LangGraph State</h3>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={!threadId || graphStateQuery.isFetching}
                    onClick={() => void refreshRuntime()}
                  >
                    <RefreshCw className="mr-2 h-3.5 w-3.5" />
                    Refresh
                  </Button>
                </div>

                {!threadId && (
                  <p className="mt-4 text-sm text-slate-500">
                    State appears after the first persisted turn.
                  </p>
                )}

                {graphState && (
                  <div className="mt-4 space-y-3 text-sm">
                    <div className="grid grid-cols-2 gap-3">
                      <div className="rounded-lg border bg-white p-3">
                        <p className="text-xs uppercase text-slate-400">Messages</p>
                        <p className="mt-1 font-semibold">{graphState.state.message_count ?? 0}</p>
                      </div>
                      <div className="rounded-lg border bg-white p-3">
                        <p className="text-xs uppercase text-slate-400">LLM Calls</p>
                        <p className="mt-1 font-semibold">{graphState.state.llm_calls ?? 0}</p>
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-medium uppercase text-slate-400">Next Nodes</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {graphState.next.length === 0 ? (
                          <span className="text-xs text-slate-500">Graph idle / completed</span>
                        ) : (
                          graphState.next.map((node) => (
                            <span key={node} className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700">
                              {node}
                            </span>
                          ))
                        )}
                      </div>
                    </div>

                    <div>
                      <p className="text-xs font-medium uppercase text-slate-400">Current State</p>
                      <pre className="mt-2 max-h-64 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-100">
                        {JSON.stringify(graphState.state, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>

              <div className="rounded-xl border bg-white p-5">
                <div className="flex items-center gap-2">
                  <History className="h-4 w-4 text-violet-600" />
                  <h3 className="font-semibold text-slate-900">Checkpoint History</h3>
                </div>

                <div className="mt-4 max-h-[330px] space-y-2 overflow-y-auto">
                  {!threadId && (
                    <p className="text-sm text-slate-500">No thread yet.</p>
                  )}

                  {historyQuery.data?.checkpoints.map((checkpoint, index) => (
                    <div key={`${checkpoint.checkpoint_id}-${index}`} className="rounded-lg border p-3">
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-xs font-semibold text-slate-700">
                          #{historyQuery.data!.checkpoints.length - index}
                        </span>
                        <span className="font-mono text-[10px] text-slate-400">
                          {shortId(checkpoint.checkpoint_id)}
                        </span>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {checkpoint.interrupts.length > 0 && (
                          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-medium text-amber-800">
                            INTERRUPTED
                          </span>
                        )}
                        {checkpoint.next.map((node) => (
                          <span key={node} className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-600">
                            next: {node}
                          </span>
                        ))}
                        {checkpoint.next.length === 0 && (
                          <span className="rounded-full bg-green-50 px-2 py-0.5 text-[10px] text-green-700">
                            terminal
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-xl border bg-white p-5">
                <h3 className="font-semibold text-slate-900">Persisted Run Audit</h3>
                {!runDetailsQuery.data && (
                  <p className="mt-3 text-sm text-slate-500">Run details appear after execution starts.</p>
                )}
                {runDetailsQuery.data && (
                  <div className="mt-4 space-y-3">
                    <div className="flex flex-wrap gap-2 text-xs">
                      <span className="rounded-full bg-slate-100 px-2.5 py-1">
                        {runDetailsQuery.data.status}
                      </span>
                      <span className="rounded-full bg-slate-100 px-2.5 py-1">
                        {runDetailsQuery.data.llm_calls} LLM calls
                      </span>
                      <span className="rounded-full bg-slate-100 px-2.5 py-1">
                        {runDetailsQuery.data.tools_used.length} tools
                      </span>
                    </div>

                    {runDetailsQuery.data.steps.map((step) => (
                      <div key={step.id} className="rounded-lg border p-3">
                        <div className="flex items-center gap-2">
                          {step.step_type === "TOOL" ? (
                            <Wrench className="h-3.5 w-3.5 text-violet-600" />
                          ) : (
                            <Bot className="h-3.5 w-3.5 text-blue-600" />
                          )}
                          <span className="text-sm font-medium">
                            {step.step_number}. {step.name}
                          </span>
                          {step.duration_ms !== null && (
                            <span className="ml-auto flex items-center gap-1 text-xs text-slate-400">
                              <Clock3 className="h-3 w-3" />
                              {step.duration_ms.toFixed(0)} ms
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
