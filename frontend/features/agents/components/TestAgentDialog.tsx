"use client";

import {
  type FormEvent,
  useState,
} from "react";

import {
  Bot,
  CheckCircle2,
  Clock3,
  LoaderCircle,
  Play,
  Search,
  Wrench,
  XCircle,
} from "lucide-react";

import {
  useQueryClient,
} from "@tanstack/react-query";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  runAgentStream,
} from "../api";

import {
  useAgentRun,
} from "../hooks";

import type {
  Agent,
  AgentProgressEvent,
  AgentProgressItem,
  AgentRunResponse,
} from "../types";


type Props = {
  agent: Agent;
};


export default function TestAgentDialog({
  agent,
}: Props) {
  const queryClient =
    useQueryClient();

  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    query,
    setQuery,
  ] = useState("");

  const [
    runId,
    setRunId,
  ] = useState<
    string | null
  >(null);

  const [
    running,
    setRunning,
  ] = useState(false);

  const [
    result,
    setResult,
  ] = useState<
    AgentRunResponse | null
  >(null);

  const [
    progress,
    setProgress,
  ] = useState<
    AgentProgressItem[]
  >([]);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const runDetailsQuery =
    useAgentRun(
      runId,
    );


  function resetState() {
    setQuery("");
    setRunId(null);
    setRunning(false);
    setResult(null);
    setProgress([]);
    setError(null);
  }


  function handleOpenChange(
    nextOpen: boolean,
  ) {
    setOpen(
      nextOpen,
    );

    if (!nextOpen) {
      resetState();
    }
  }


  function handleProgressEvent(
    event:
      AgentProgressEvent,
  ) {
    if (
      event.type ===
      "run_started"
    ) {
      setRunId(
        event.run_id,
      );

      return;
    }


    if (
      event.type ===
      "llm_started"
    ) {
      setProgress(
        (current) => [
          ...current,
          {
            id:
              `llm-${event.iteration}`,

            type:
              "LLM",

            name:
              event.iteration === 1
                ? "Thinking"
                : "Generating response",

            status:
              "RUNNING",
          },
        ],
      );

      return;
    }


    if (
      event.type ===
      "llm_completed"
    ) {
      setProgress(
        (current) =>
          current.map(
            (item) =>
              item.id ===
              `llm-${event.iteration}`
                ? {
                    ...item,

                    status:
                      "COMPLETED",

                    duration_ms:
                      event.duration_ms,
                  }
                : item,
          ),
      );

      return;
    }


    if (
      event.type ===
      "tool_started"
    ) {
      setProgress(
        (current) => [
          ...current,
          {
            id:
              `tool-${event.name}-${Date.now()}`,

            type:
              "TOOL",

            name:
              event.name,

            status:
              "RUNNING",
          },
        ],
      );

      return;
    }


    if (
      event.type ===
      "tool_completed"
    ) {
      setProgress(
        (current) => {
          const next = [
            ...current,
          ];

          const index =
            next.findLastIndex(
              (item) =>
                item.type ===
                  "TOOL"
                && item.name ===
                  event.name
                && item.status ===
                  "RUNNING",
            );

          if (
            index !== -1
          ) {
            next[index] = {
              ...next[index],

              status:
                "COMPLETED",

              duration_ms:
                event.duration_ms,
            };
          }

          return next;
        },
      );

      return;
    }


    if (
      event.type ===
      "completed"
    ) {
      setResult(
        event.result,
      );

      setRunId(
        event.result.run_id,
      );

      setRunning(false);

      queryClient.invalidateQueries({
        queryKey: [
          "agent-runs",
          agent.id,
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "agent-run",
          event.result.run_id,
        ],
      });

      return;
    }


    if (
      event.type ===
      "failed"
    ) {
      setError(
        event.message,
      );

      setRunning(false);
    }
  }


  async function submit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const cleanQuery =
      query.trim();

    if (
      !cleanQuery
      || running
    ) {
      return;
    }

    setRunId(null);
    setResult(null);
    setProgress([]);
    setError(null);
    setRunning(true);

    try {
      await runAgentStream(
        agent.id,
        {
          query:
            cleanQuery,
        },
        handleProgressEvent,
      );

    } catch {
      setError(
        "Agent execution failed.",
      );

      setRunning(false);
    }
  }


  return (
    <>
      <Button
        type="button"
        disabled={
          agent.status !==
          "ACTIVE"
        }
        onClick={() =>
          setOpen(true)
        }
      >
        <Play className="mr-2 h-4 w-4" />

        Test Agent
      </Button>


      <Dialog
        open={open}
        onOpenChange={
          handleOpenChange
        }
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-4xl">

          <DialogHeader>

            <DialogTitle className="flex items-center gap-2">

              <Bot className="h-5 w-5 text-violet-600" />

              Test Agent

            </DialogTitle>


            <DialogDescription>
              Run{" "}
              <span className="font-medium text-slate-700">
                {agent.name}
              </span>{" "}
              and inspect the execution
              trace.
            </DialogDescription>

          </DialogHeader>


          <div className="grid gap-6 lg:grid-cols-2">

            <div className="space-y-5">

              <form
                onSubmit={submit}
                className="space-y-4"
              >

                <div>

                  <label className="text-sm font-medium text-slate-700">
                    Query
                  </label>

                  <textarea
                    value={query}
                    onChange={(event) =>
                      setQuery(
                        event.target.value,
                      )
                    }
                    rows={6}
                    disabled={running}
                    placeholder="Ask the agent something..."
                    className="mt-2 w-full rounded-md border border-slate-200 px-3 py-2 text-sm outline-none focus:border-blue-500 disabled:bg-slate-50"
                  />

                </div>


                <Button
                  type="submit"
                  disabled={
                    running
                    || !query.trim()
                  }
                >

                  {running ? (
                    <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Play className="mr-2 h-4 w-4" />
                  )}

                  {running
                    ? "Running..."
                    : "Run Agent"}

                </Button>

              </form>


              {(running
                || progress.length >
                  0) && (
                <div className="rounded-xl border bg-white p-5">

                  <div className="flex items-center justify-between">

                    <h3 className="font-semibold text-slate-900">
                      Live Execution
                    </h3>


                    {running && (
                      <span className="flex items-center gap-2 text-xs font-medium text-blue-600">

                        <span className="h-2 w-2 animate-pulse rounded-full bg-blue-600" />

                        Running

                      </span>
                    )}

                  </div>


                  <div className="mt-4 space-y-3">

                    {progress.map(
                      (item) => (
                        <div
                          key={
                            item.id
                          }
                          className="flex items-start gap-3"
                        >

                          <div className="mt-0.5">

                            {item.status ===
                            "RUNNING" ? (
                              <LoaderCircle className="h-4 w-4 animate-spin text-blue-600" />
                            ) : (
                              <CheckCircle2 className="h-4 w-4 text-green-600" />
                            )}

                          </div>


                          <div className="min-w-0 flex-1">

                            <div className="flex items-center gap-2">

                              {item.type ===
                              "TOOL" ? (
                                <Wrench className="h-3.5 w-3.5 text-violet-600" />
                              ) : (
                                <Bot className="h-3.5 w-3.5 text-blue-600" />
                              )}


                              <p className="text-sm font-medium text-slate-700">
                                {item.name}
                              </p>

                            </div>


                            {item.duration_ms !==
                              undefined && (
                              <p className="mt-1 text-xs text-slate-400">
                                {item.duration_ms.toFixed(
                                  2,
                                )}{" "}
                                ms
                              </p>
                            )}

                          </div>

                        </div>
                      ),
                    )}

                  </div>

                </div>
              )}


              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">

                  <div className="flex items-center gap-2">

                    <XCircle className="h-4 w-4" />

                    {error}

                  </div>

                </div>
              )}


              {result && (
                <div className="space-y-4 rounded-xl border bg-white p-5">

                  <div className="flex items-center justify-between">

                    <h3 className="font-semibold text-slate-900">
                      Result
                    </h3>


                    <span className="rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700">
                      {result.status}
                    </span>

                  </div>


                  <div className="rounded-lg bg-slate-50 p-4">

                    <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">
                      {result.answer}
                    </p>

                  </div>


                  <div className="grid gap-3 sm:grid-cols-3">

                    <div className="rounded-lg border p-3">

                      <p className="text-xs uppercase tracking-wide text-slate-400">
                        LLM Calls
                      </p>

                      <p className="mt-1 text-lg font-semibold text-slate-900">
                        {result.llm_calls}
                      </p>

                    </div>


                    <div className="rounded-lg border p-3">

                      <p className="text-xs uppercase tracking-wide text-slate-400">
                        Tools
                      </p>

                      <p className="mt-1 text-lg font-semibold text-slate-900">
                        {
                          result.tools_used
                            .length
                        }
                      </p>

                    </div>


                    <div className="rounded-lg border p-3">

                      <p className="text-xs uppercase tracking-wide text-slate-400">
                        Duration
                      </p>

                      <p className="mt-1 text-lg font-semibold text-slate-900">
                        {(
                          result.duration_ms
                          / 1000
                        ).toFixed(
                          2,
                        )}
                        s
                      </p>

                    </div>

                  </div>


                  {result.tools_used.length >
                    0 && (
                    <div>

                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Tools Used
                      </p>

                      <div className="mt-2 flex flex-wrap gap-2">

                        {result.tools_used.map(
                          (tool) => (
                            <span
                              key={
                                tool
                              }
                              className="rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700"
                            >
                              {tool}
                            </span>
                          ),
                        )}

                      </div>

                    </div>
                  )}


                  <div>

                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Run ID
                    </p>

                    <p className="mt-1 break-all font-mono text-xs text-slate-500">
                      {result.run_id}
                    </p>

                  </div>

                </div>
              )}

            </div>


            <div>

              <div className="rounded-xl border bg-slate-50 p-5">

                <div className="flex items-center justify-between">

                  <h3 className="font-semibold text-slate-900">
                    Execution Trace
                  </h3>


                  {runDetailsQuery.isFetching && (
                    <span className="text-xs text-slate-400">
                      Loading...
                    </span>
                  )}

                </div>


                {!runId && (
                  <div className="mt-6 rounded-lg border border-dashed bg-white p-6 text-center">

                    {running ? (
                      <LoaderCircle className="mx-auto h-8 w-8 animate-spin text-blue-400" />
                    ) : (
                      <Search className="mx-auto h-8 w-8 text-slate-300" />
                    )}

                    <p className="mt-3 text-sm text-slate-500">
                      {running
                        ? "Execution is in progress..."
                        : "Run the agent to see LLM and tool execution steps."}
                    </p>

                  </div>
                )}


                {runDetailsQuery.isError && (
                  <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                    Failed to load run
                    details.
                  </div>
                )}


                {runDetailsQuery.data && (
                  <div className="mt-5 space-y-3">

                    {runDetailsQuery.data.steps.map(
                      (step) => (
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

                                      {step.duration_ms.toFixed(
                                        2,
                                      )}{" "}
                                      ms

                                    </span>
                                  )}

                                </div>

                              </div>

                            </div>

                          </div>


                          {step.step_type ===
                            "TOOL"
                            && step.input_data && (
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
                            "TOOL"
                            && step.output_data && (
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
                )}

              </div>

            </div>

          </div>

        </DialogContent>
      </Dialog>
    </>
  );
}