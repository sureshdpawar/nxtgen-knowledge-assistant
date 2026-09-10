"use client";

import {
  useState,
} from "react";

import {
  Activity,
  CheckCircle2,
  Clock3,
  RefreshCw,
  ShieldCheck,
  XCircle,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  useAgentOnlineEvalResults,
  useAgentOnlineEvalSummary,
  useProcessPendingAgentOnlineEvals,
} from "../hooks";


function percent(
  value: number | null | undefined,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return `${(
    value * 100
  ).toFixed(1)}%`;
}


function score(
  value: number | null | undefined,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return value.toFixed(3);
}


export default function AgentOnlineEvaluationDashboard() {
  const summaryQuery =
    useAgentOnlineEvalSummary();

  const resultsQuery =
    useAgentOnlineEvalResults();

  const processMutation =
    useProcessPendingAgentOnlineEvals();

  const [
    message,
    setMessage,
  ] = useState<
    string | null
  >(null);


  async function processPending() {
    setMessage(
      null,
    );

    try {
      const result =
        await processMutation
          .mutateAsync({
            limit: 20,
            task_quality_threshold:
              0.8,
          });

      setMessage(
        `Processed ${result.processed} sample(s): `
        + `${result.completed} completed, `
        + `${result.failed} failed.`,
      );

    } catch {
      setMessage(
        "Unable to process pending Agent evaluations.",
      );
    }
  }


  const summary =
    summaryQuery.data;

  const results =
    resultsQuery.data
    ?? [];


  return (
    <div className="space-y-6">

      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">

        <div>
          <div className="flex items-center gap-2 text-sm font-medium text-blue-700">
            <Activity className="h-4 w-4" />
            Agent Online Evaluation
          </div>

          <h1 className="mt-1 text-2xl font-semibold text-slate-900">
            Agent Production Quality
          </h1>

          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Evaluate sampled production and staging AgentRuns without
            replaying the agent or executing tools. Task quality is judged
            against the observed request and response; execution health is
            derived from the persisted run trace.
          </p>
        </div>


        <Button
          type="button"
          onClick={
            processPending
          }
          disabled={
            processMutation
              .isPending
            || !summary
            || summary.pending === 0
          }
        >
          <RefreshCw
            className={
              `mr-2 h-4 w-4 ${
                processMutation.isPending
                  ? "animate-spin"
                  : ""
              }`
            }
          />

          {processMutation.isPending
            ? "Evaluating..."
            : `Evaluate Pending${
                summary?.pending
                  ? ` (${summary.pending})`
                  : ""
              }`}
        </Button>

      </div>


      {message && (
        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
          {message}
        </div>
      )}


      {summaryQuery.isLoading && (
        <div className="rounded-xl border bg-white p-6 text-sm text-slate-500">
          Loading Agent production quality...
        </div>
      )}


      {summaryQuery.isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load Agent production quality summary.
        </div>
      )}


      {summary && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">

          <div className="rounded-xl border bg-white p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">
                Pass Rate
              </p>
              <ShieldCheck className="h-4 w-4 text-slate-400" />
            </div>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {percent(
                summary.pass_rate,
              )}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              {summary.passed} passed / {summary.completed} completed
            </p>
          </div>


          <div className="rounded-xl border bg-white p-5">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium text-slate-500">
                Pending
              </p>
              <Clock3 className="h-4 w-4 text-slate-400" />
            </div>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {summary.pending}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Sampled runs awaiting evaluation
            </p>
          </div>


          <div className="rounded-xl border bg-white p-5">
            <p className="text-sm font-medium text-slate-500">
              Task Quality
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {score(
                summary.average_task_quality,
              )}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Average judge score
            </p>
          </div>


          <div className="rounded-xl border bg-white p-5">
            <p className="text-sm font-medium text-slate-500">
              Execution Health
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {score(
                summary.average_execution_health,
              )}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Persisted runtime health
            </p>
          </div>


          <div className="rounded-xl border bg-white p-5">
            <p className="text-sm font-medium text-slate-500">
              Overall
            </p>
            <p className="mt-2 text-2xl font-semibold text-slate-900">
              {score(
                summary.average_overall_score,
              )}
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Mean applicable quality signals
            </p>
          </div>

        </div>
      )}


      <div className="overflow-hidden rounded-xl border bg-white">

        <div className="border-b px-5 py-4">
          <h2 className="font-semibold text-slate-900">
            Recent Agent Quality Results
          </h2>
          <p className="mt-1 text-sm text-slate-500">
            The source AgentRun remains the execution record. Evaluation does
            not replay the run.
          </p>
        </div>


        {resultsQuery.isLoading && (
          <div className="p-6 text-sm text-slate-500">
            Loading results...
          </div>
        )}


        {resultsQuery.isError && (
          <div className="p-6 text-sm text-red-700">
            Failed to load Agent quality results.
          </div>
        )}


        {!resultsQuery.isLoading
          && !resultsQuery.isError
          && results.length === 0 && (
          <div className="p-8 text-center">
            <Activity className="mx-auto h-8 w-8 text-slate-300" />
            <p className="mt-3 text-sm font-medium text-slate-700">
              No Agent quality samples yet
            </p>
            <p className="mt-1 text-sm text-slate-500">
              New completed AgentRuns will be sampled when Online Evaluation
              is enabled.
            </p>
          </div>
        )}


        {results.length > 0 && (
          <div className="overflow-x-auto">

            <table className="w-full text-left text-sm">

              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">
                    Outcome
                  </th>
                  <th className="px-4 py-3 font-medium">
                    Request
                  </th>
                  <th className="px-4 py-3 font-medium">
                    Task
                  </th>
                  <th className="px-4 py-3 font-medium">
                    Execution
                  </th>
                  <th className="px-4 py-3 font-medium">
                    Overall
                  </th>
                  <th className="px-4 py-3 font-medium">
                    Tools
                  </th>
                  <th className="px-4 py-3 font-medium">
                    Evaluated
                  </th>
                </tr>
              </thead>


              <tbody className="divide-y">

                {results.map(
                  (result) => (
                    <tr
                      key={result.id}
                      className="align-top"
                    >
                      <td className="px-4 py-4">
                        {result.status === "pending" ? (
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700">
                            <Clock3 className="h-3.5 w-3.5" />
                            Pending
                          </span>
                        ) : result.passed === true ? (
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700">
                            <CheckCircle2 className="h-3.5 w-3.5" />
                            Pass
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700">
                            <XCircle className="h-3.5 w-3.5" />
                            Fail
                          </span>
                        )}
                      </td>

                      <td className="max-w-lg px-4 py-4">
                        <p className="line-clamp-2 text-slate-800">
                          {result.question}
                        </p>
                        <p className="mt-1 font-mono text-[11px] text-slate-400">
                          Run {result.agent_run_id}
                        </p>
                      </td>

                      <td className="px-4 py-4 font-medium text-slate-700">
                        {score(
                          result.task_quality_score,
                        )}
                      </td>

                      <td className="px-4 py-4 font-medium text-slate-700">
                        {score(
                          result.execution_health_score,
                        )}
                      </td>

                      <td className="px-4 py-4 font-medium text-slate-900">
                        {score(
                          result.overall_score,
                        )}
                      </td>

                      <td className="px-4 py-4 text-slate-600">
                        {result.tools_used.length > 0
                          ? result.tools_used.join(", ")
                          : "—"}
                      </td>

                      <td className="px-4 py-4 text-slate-500">
                        {result.evaluated_at
                          ? new Date(
                              result.evaluated_at,
                            ).toLocaleString()
                          : "—"}
                      </td>
                    </tr>
                  ),
                )}

              </tbody>

            </table>

          </div>
        )}

      </div>

    </div>
  );
}
