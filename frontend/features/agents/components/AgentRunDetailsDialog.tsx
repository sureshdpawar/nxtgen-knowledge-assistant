"use client";

import {
  Bot,
  CheckCircle2,
  Clock3,
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

import {
  useAgentRun,
} from "../hooks";


type Props = {
  runId: string | null;

  open: boolean;

  onOpenChange: (
    open: boolean,
  ) => void;
};


function formatDuration(
  durationMs:
    | number
    | null,
) {
  if (durationMs === null) {
    return "-";
  }

  if (durationMs < 1000) {
    return `${durationMs.toFixed(
      0,
    )} ms`;
  }

  return `${(
    durationMs / 1000
  ).toFixed(2)} s`;
}


function formatDate(
  value:
    | string
    | null,
) {
  if (!value) {
    return "-";
  }

  const parsed = new Date(
    value,
  );

  if (
    Number.isNaN(
      parsed.getTime(),
    )
  ) {
    return value;
  }

  return parsed.toLocaleString();
}


function JsonBlock({
  value,
}: {
  value: unknown;
}) {
  return (
    <pre className="mt-2 max-h-64 overflow-auto whitespace-pre-wrap break-words rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">
      {JSON.stringify(
        value,
        null,
        2,
      )}
    </pre>
  );
}


export default function AgentRunDetailsDialog({
  runId,
  open,
  onOpenChange,
}: Props) {
  const runQuery =
    useAgentRun(
      runId,
    );


  return (
    <Dialog
      open={open}
      onOpenChange={
        onOpenChange
      }
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-5xl">

        <DialogHeader>

          <DialogTitle>
            Agent Run Details
          </DialogTitle>

          <DialogDescription>
            Inspect the persisted
            execution audit for this
            agent run.
          </DialogDescription>

        </DialogHeader>


        {runQuery.isLoading && (
          <div className="rounded-lg border bg-slate-50 p-6 text-sm text-slate-500">
            Loading run details...
          </div>
        )}


        {runQuery.isError && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            Failed to load agent
            run details.
          </div>
        )}


        {runQuery.data && (
          <div className="space-y-7">

            {/* Summary */}

            <div className="grid gap-3 sm:grid-cols-4">

              <div className="rounded-lg border p-3">

                <p className="text-xs uppercase tracking-wide text-slate-400">
                  Status
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {
                    runQuery.data.status
                  }
                </p>

              </div>


              <div className="rounded-lg border p-3">

                <p className="text-xs uppercase tracking-wide text-slate-400">
                  LLM Calls
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {
                    runQuery.data.llm_calls
                  }
                </p>

              </div>


              <div className="rounded-lg border p-3">

                <p className="text-xs uppercase tracking-wide text-slate-400">
                  Executed Tools
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {
                    runQuery.data
                      .tools_used
                      .length
                  }
                </p>

              </div>


              <div className="rounded-lg border p-3">

                <p className="text-xs uppercase tracking-wide text-slate-400">
                  Duration
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {
                    formatDuration(
                      runQuery.data
                        .duration_ms,
                    )
                  }
                </p>

              </div>

            </div>


            {/* Execution identity */}

            <div>

              <h3 className="font-semibold text-slate-900">
                Execution Context
              </h3>


              <div className="mt-3 grid gap-3 sm:grid-cols-2">

                <div className="rounded-lg border bg-slate-50 p-3">

                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Actor Type
                  </p>

                  <p className="mt-1 text-sm font-medium text-slate-800">
                    {
                      runQuery.data
                        .actor_type
                    }
                  </p>

                </div>


                <div className="rounded-lg border bg-slate-50 p-3">

                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Actor ID
                  </p>

                  <p className="mt-1 break-all font-mono text-xs text-slate-700">
                    {
                      runQuery.data
                        .actor_id
                    }
                  </p>

                </div>


                <div className="rounded-lg border bg-slate-50 p-3">

                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Thread ID
                  </p>

                  <p className="mt-1 break-all font-mono text-xs text-slate-700">
                    {
                      runQuery.data
                        .thread_id
                      ?? "-"
                    }
                  </p>

                </div>


                <div className="rounded-lg border bg-slate-50 p-3">

                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Checkpoint ID
                  </p>

                  <p className="mt-1 break-all font-mono text-xs text-slate-700">
                    {
                      runQuery.data
                        .checkpoint_id
                      ?? "-"
                    }
                  </p>

                </div>


                <div className="rounded-lg border bg-slate-50 p-3">

                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Started
                  </p>

                  <p className="mt-1 text-sm text-slate-700">
                    {
                      formatDate(
                        runQuery.data
                          .started_at,
                      )
                    }
                  </p>

                </div>


                <div className="rounded-lg border bg-slate-50 p-3">

                  <p className="text-xs uppercase tracking-wide text-slate-400">
                    Completed
                  </p>

                  <p className="mt-1 text-sm text-slate-700">
                    {
                      formatDate(
                        runQuery.data
                          .completed_at,
                      )
                    }
                  </p>

                </div>

              </div>

            </div>


            {/* Business correlation */}

            {runQuery.data
              .context_metadata &&
              Object.keys(
                runQuery.data
                  .context_metadata,
              ).length > 0 && (

              <div>

                <h3 className="font-semibold text-slate-900">
                  Correlation Context
                </h3>

                <p className="mt-1 text-xs text-slate-500">
                  Platform and business
                  identifiers attached to
                  this run.
                </p>

                <JsonBlock
                  value={
                    runQuery.data
                      .context_metadata
                  }
                />

              </div>
            )}


            {/* Executed tools */}

            <div>

              <h3 className="font-semibold text-slate-900">
                Executed Tools
              </h3>

              {runQuery.data
                .tools_used
                .length === 0 ? (

                <div className="mt-3 rounded-lg border border-dashed p-4 text-sm text-slate-500">
                  No tools executed
                  during this run.
                </div>

              ) : (

                <div className="mt-3 flex flex-wrap gap-2">

                  {runQuery.data
                    .tools_used
                    .map(
                      (
                        toolName,
                      ) => (

                        <span
                          key={
                            toolName
                          }
                          className="rounded-full border border-violet-200 bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700"
                        >
                          {
                            toolName
                          }
                        </span>

                      ),
                    )}

                </div>

              )}

            </div>


            {/* Query */}

            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Query
              </p>

              <div className="mt-2 rounded-lg bg-slate-50 p-4">

                <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {
                    runQuery.data.query
                  }
                </p>

              </div>

            </div>


            {/* Answer */}

            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Answer
              </p>

              <div className="mt-2 rounded-lg bg-slate-50 p-4">

                <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {
                    runQuery.data.answer
                    ?? "No answer recorded."
                  }
                </p>

              </div>

            </div>


            {/* Error */}

            {runQuery.data
              .error_message && (

              <div className="rounded-lg border border-red-200 bg-red-50 p-4">

                <p className="text-xs font-medium uppercase tracking-wide text-red-500">
                  Error
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm text-red-700">
                  {
                    runQuery.data
                      .error_message
                  }
                </p>

              </div>
            )}


            {/* Trace */}

            <div>

              <div className="flex items-center justify-between gap-3">

                <div>

                  <h3 className="font-semibold text-slate-900">
                    Execution Trace
                  </h3>

                  <p className="mt-1 text-xs text-slate-500">
                    Persisted Knowgentiq
                    execution steps for
                    this run.
                  </p>

                </div>


                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                  {
                    runQuery.data.steps
                      .length
                  }{" "}
                  steps
                </span>

              </div>


              <div className="mt-4 space-y-3">

                {runQuery.data
                  .steps
                  .length === 0 && (

                  <div className="rounded-lg border border-dashed p-5 text-sm text-slate-500">
                    No execution steps
                    recorded.
                  </div>

                )}


                {runQuery.data
                  .steps
                  .map(
                    (
                      step,
                    ) => (

                    <div
                      key={
                        step.id
                      }
                      className="rounded-lg border bg-white p-4"
                    >

                      <div className="flex items-start justify-between gap-4">

                        <div className="flex items-start gap-3">

                          <div
                            className={
                              step.step_type ===
                              "TOOL"
                                ? "rounded-lg bg-violet-50 p-2"
                                : "rounded-lg bg-blue-50 p-2"
                            }
                          >

                            {step.step_type ===
                            "TOOL" ? (

                              <Wrench className="h-4 w-4 text-violet-600" />

                            ) : (

                              <Bot className="h-4 w-4 text-blue-600" />

                            )}

                          </div>


                          <div>

                            <div className="flex flex-wrap items-center gap-2">

                              <p className="text-sm font-semibold text-slate-900">
                                Step{" "}
                                {
                                  step.step_number
                                }
                                {" · "}
                                {
                                  step.name
                                }
                              </p>


                              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                                {
                                  step.step_type
                                }
                              </span>

                            </div>


                            <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-slate-500">

                              <span className="flex items-center gap-1">

                                {step.status ===
                                "COMPLETED" ? (

                                  <CheckCircle2 className="h-3.5 w-3.5 text-green-600" />

                                ) : (

                                  <XCircle className="h-3.5 w-3.5 text-red-600" />

                                )}

                                {
                                  step.status
                                }

                              </span>


                              {step.duration_ms !==
                                null && (

                                <span className="flex items-center gap-1">

                                  <Clock3 className="h-3.5 w-3.5" />

                                  {
                                    formatDuration(
                                      step.duration_ms,
                                    )
                                  }

                                </span>

                              )}

                            </div>

                          </div>

                        </div>

                      </div>


                      {step.input_data && (

                        <div className="mt-4">

                          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                            Input
                          </p>

                          <JsonBlock
                            value={
                              step.input_data
                            }
                          />

                        </div>

                      )}


                      {step.output_data && (

                        <div className="mt-4">

                          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                            Output
                          </p>

                          <JsonBlock
                            value={
                              step.output_data
                            }
                          />

                        </div>

                      )}

                    </div>

                  ),
                )}

              </div>

            </div>


            {/* IDs */}

            <div className="rounded-lg border bg-slate-50 p-4">

              <div className="grid gap-4 sm:grid-cols-2">

                <div>

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Run ID
                  </p>

                  <p className="mt-1 break-all font-mono text-xs text-slate-600">
                    {
                      runQuery.data.id
                    }
                  </p>

                </div>


                <div>

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Agent ID
                  </p>

                  <p className="mt-1 break-all font-mono text-xs text-slate-600">
                    {
                      runQuery.data
                        .agent_id
                    }
                  </p>

                </div>

              </div>

            </div>

          </div>
        )}

      </DialogContent>
    </Dialog>
  );
}

