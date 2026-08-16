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
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-4xl">

        <DialogHeader>

          <DialogTitle>
            Agent Run Details
          </DialogTitle>

          <DialogDescription>
            Inspect the persisted
            execution trace for this
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
          <div className="space-y-6">

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
                  Tools
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {
                    runQuery.data.tools_used.length
                  }
                </p>

              </div>


              <div className="rounded-lg border p-3">

                <p className="text-xs uppercase tracking-wide text-slate-400">
                  Duration
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-900">
                  {
                    runQuery.data.duration_ms
                      ? `${(
                          runQuery.data.duration_ms
                          / 1000
                        ).toFixed(
                          2,
                        )}s`
                      : "-"
                  }
                </p>

              </div>

            </div>


            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Query
              </p>

              <div className="mt-2 rounded-lg bg-slate-50 p-4">

                <p className="whitespace-pre-wrap text-sm text-slate-700">
                  {
                    runQuery.data.query
                  }
                </p>

              </div>

            </div>


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


            {runQuery.data.error_message && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-4">

                <p className="text-xs font-medium uppercase tracking-wide text-red-500">
                  Error
                </p>

                <p className="mt-2 text-sm text-red-700">
                  {
                    runQuery.data.error_message
                  }
                </p>

              </div>
            )}


            <div>

              <h3 className="font-semibold text-slate-900">
                Execution Trace
              </h3>


              <div className="mt-4 space-y-3">

                {runQuery.data.steps.length ===
                  0 && (
                  <div className="rounded-lg border border-dashed p-5 text-sm text-slate-500">
                    No execution steps
                    recorded.
                  </div>
                )}


                {runQuery.data.steps.map(
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
                                    step.duration_ms.toFixed(
                                      2,
                                    )
                                  }{" "}
                                  ms

                                </span>
                              )}

                            </div>

                          </div>

                        </div>

                      </div>


                      {step.step_type ===
                        "TOOL" &&
                        step.input_data && (
                        <div className="mt-4">

                          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                            Input
                          </p>

                          <pre className="mt-2 max-h-40 overflow-auto rounded-md bg-slate-950 p-3 text-xs text-slate-100">
                            {JSON.stringify(
                              step.input_data,
                              null,
                              2,
                            )}
                          </pre>

                        </div>
                      )}


                      {step.step_type ===
                        "TOOL" &&
                        step.output_data && (
                        <div className="mt-4">

                          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                            Output
                          </p>

                          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-slate-950 p-3 text-xs text-slate-100">
                            {JSON.stringify(
                              step.output_data,
                              null,
                              2,
                            )}
                          </pre>

                        </div>
                      )}

                    </div>
                  ),
                )}

              </div>

            </div>


            <div>

              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Run ID
              </p>

              <p className="mt-1 break-all font-mono text-xs text-slate-500">
                {
                  runQuery.data.id
                }
              </p>

            </div>

          </div>
        )}

      </DialogContent>
    </Dialog>
  );
}