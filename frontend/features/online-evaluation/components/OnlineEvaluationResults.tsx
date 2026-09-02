"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  CircleMinus,
  Copy,
  Loader2,
  Search,
  ShieldCheck,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";

import {
  useOnlineEvalResults,
} from "@/features/online-evaluation/hooks";

import type {
  OnlineEvalFilters,
  OnlineEvalOutcome,
  OnlineEvalResultSummary,
  OnlineEvalStatus,
  OnlineEvalSummaryFilters,
} from "@/features/online-evaluation/types";


type PassedFilter =
  | "all"
  | "passed"
  | "failed";


type OnlineEvaluationResultsProps = {
  baseFilters?: OnlineEvalSummaryFilters;
  onSelectResult?: (
    result: OnlineEvalResultSummary,
  ) => void;
};


function formatScore(
  value: number | null | undefined,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return `${(value * 100).toFixed(1)}%`;
}


function formatDateTime(
  value: string | null | undefined,
) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(date);
}


function shortenTrace(
  traceId: string,
) {
  if (traceId.length <= 16) {
    return traceId;
  }

  return `${traceId.slice(0, 8)}…${traceId.slice(-8)}`;
}


function StatusBadge({
  status,
}: {
  status: OnlineEvalStatus;
}) {
  if (status === "completed") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" />
        Completed
      </span>
    );
  }

  if (status === "failed") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
        <XCircle className="h-3.5 w-3.5" />
        Failed
      </span>
    );
  }

  if (status === "running") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
        <Loader2 className="h-3.5 w-3.5 animate-spin" />
        Running
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
      <CircleMinus className="h-3.5 w-3.5" />
      Pending
    </span>
  );
}


function OutcomeBadge({
  outcome,
  status,
}: {
  outcome: OnlineEvalOutcome | null;
  status: OnlineEvalStatus;
}) {
  if (
    status !== "completed"
    || outcome === null
  ) {
    return <span className="text-sm text-slate-400">—</span>;
  }

  if (outcome === "safe_abstention") {
    return (
      <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-blue-700">
        <ShieldCheck className="h-4 w-4" />
        Safe abstention
      </span>
    );
  }

  if (outcome === "pass") {
    return (
      <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-emerald-700">
        <CheckCircle2 className="h-4 w-4" />
        Answered
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-red-700">
      <XCircle className="h-4 w-4" />
      Failed
    </span>
  );
}


function ScoreCell({
  value,
}: {
  value: number | null;
}) {
  return (
    <span
      className={
        value === null
          ? "text-slate-400"
          : "font-medium text-slate-700"
      }
    >
      {formatScore(value)}
    </span>
  );
}


export default function OnlineEvaluationResults({
  baseFilters = {},
  onSelectResult,
}: OnlineEvaluationResultsProps) {
  const [status, setStatus] = useState<OnlineEvalStatus | "all">("all");
  const [passedFilter, setPassedFilter] = useState<PassedFilter>("all");
  const [traceInput, setTraceInput] = useState("");
  const [traceFilter, setTraceFilter] = useState("");
  const [limit, setLimit] = useState(25);
  const [offset, setOffset] = useState(0);

  useEffect(
    () => {
      setOffset(0);
    },
    [
      baseFilters.knowledge_base_id,
      baseFilters.generator_provider,
      baseFilters.generator_model,
      baseFilters.created_from,
      baseFilters.created_to,
      status,
      passedFilter,
      traceFilter,
      limit,
    ],
  );

  const filters = useMemo<OnlineEvalFilters>(
    () => ({
      ...baseFilters,
      status: status === "all" ? null : status,
      passed:
        passedFilter === "all"
          ? null
          : passedFilter === "passed",
      source_trace_id: traceFilter || null,
      limit,
      offset,
    }),
    [
      baseFilters,
      status,
      passedFilter,
      traceFilter,
      limit,
      offset,
    ],
  );

  const {
    data: results = [],
    isLoading,
    isFetching,
    error,
    refetch,
  } = useOnlineEvalResults(filters);

  function handleTraceSearch() {
    setTraceFilter(traceInput.trim());
  }

  function handleTraceKeyDown(
    event: React.KeyboardEvent<HTMLInputElement>,
  ) {
    if (event.key === "Enter") {
      handleTraceSearch();
    }
  }

  async function copyTrace(
    traceId: string,
  ) {
    try {
      await navigator.clipboard.writeText(traceId);
      toast.success("Trace ID copied.");
    } catch {
      toast.error("Unable to copy trace ID.");
    }
  }

  const pageNumber = Math.floor(offset / limit) + 1;
  const canGoPrevious = offset > 0;
  const canGoNext = results.length === limit;

  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-4">
        <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900">
              Production evaluation results
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              Separate successful answers, safe abstentions, and genuine failures.
            </p>
          </div>

          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex h-10 items-center justify-center rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isFetching ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : null}
            Refresh results
          </button>
        </div>

        <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-[180px_180px_minmax(260px,1fr)_120px]">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Status
            </label>
            <select
              value={status}
              onChange={(event) =>
                setStatus(
                  event.target.value as OnlineEvalStatus | "all",
                )
              }
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-slate-500"
            >
              <option value="all">All statuses</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Legacy result filter
            </label>
            <select
              value={passedFilter}
              onChange={(event) =>
                setPassedFilter(event.target.value as PassedFilter)
              }
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-slate-500"
            >
              <option value="all">All results</option>
              <option value="passed">Handled safely</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Source trace ID
            </label>
            <div className="flex gap-2">
              <input
                value={traceInput}
                onChange={(event) => setTraceInput(event.target.value)}
                onKeyDown={handleTraceKeyDown}
                placeholder="Search original production trace"
                className="h-10 min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-500"
              />
              <button
                type="button"
                onClick={handleTraceSearch}
                className="inline-flex h-10 items-center justify-center rounded-lg border border-slate-300 bg-white px-3 text-slate-700 transition hover:bg-slate-50"
                aria-label="Search trace ID"
              >
                <Search className="h-4 w-4" />
              </button>
            </div>
          </div>

          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Rows
            </label>
            <select
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value))}
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-slate-500"
            >
              <option value={10}>10</option>
              <option value={25}>25</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {traceFilter ? (
          <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
            <span>Filtering by trace:</span>
            <code className="rounded bg-slate-100 px-2 py-1 text-slate-700">
              {traceFilter}
            </code>
            <button
              type="button"
              onClick={() => {
                setTraceInput("");
                setTraceFilter("");
              }}
              className="font-semibold text-slate-700 hover:text-slate-900"
            >
              Clear
            </button>
          </div>
        ) : null}
      </div>

      {error ? (
        <div className="m-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Unable to load online evaluation results.
        </div>
      ) : null}

      <div className="overflow-x-auto">
        <table className="min-w-[1150px] w-full border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50 text-left">
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Status</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Outcome</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Faithfulness</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Answer relevancy</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Context relevancy</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Model</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Source trace</th>
              <th className="px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">Captured</th>
            </tr>
          </thead>

          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center">
                  <div className="inline-flex items-center gap-2 text-sm text-slate-500">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Loading online evaluations…
                  </div>
                </td>
              </tr>
            ) : results.length === 0 ? (
              <tr>
                <td colSpan={8} className="px-4 py-12 text-center">
                  <p className="text-sm font-semibold text-slate-700">
                    No online evaluation results
                  </p>
                  <p className="mt-1 text-sm text-slate-500">
                    No sampled production evaluations match the current filters.
                  </p>
                </td>
              </tr>
            ) : (
              results.map((result) => (
                <tr
                  key={result.id}
                  onClick={() => onSelectResult?.(result)}
                  className={`border-b border-slate-100 transition last:border-b-0 ${
                    onSelectResult
                      ? "cursor-pointer hover:bg-slate-50"
                      : ""
                  }`}
                >
                  <td className="whitespace-nowrap px-4 py-4">
                    <StatusBadge status={result.status} />
                  </td>

                  <td className="whitespace-nowrap px-4 py-4">
                    <OutcomeBadge
                      outcome={result.evaluation_outcome}
                      status={result.status}
                    />
                  </td>

                  <td className="whitespace-nowrap px-4 py-4 text-sm">
                    <ScoreCell value={result.faithfulness_score} />
                  </td>

                  <td className="whitespace-nowrap px-4 py-4 text-sm">
                    <ScoreCell value={result.answer_relevancy_score} />
                  </td>

                  <td className="whitespace-nowrap px-4 py-4 text-sm">
                    <ScoreCell value={result.contextual_relevancy_score} />
                  </td>

                  <td className="px-4 py-4">
                    <div className="max-w-[220px]">
                      <p className="truncate text-sm font-medium text-slate-800">
                        {result.generator_model ?? "—"}
                      </p>
                      {result.generator_provider ? (
                        <p className="mt-0.5 truncate text-xs text-slate-500">
                          {result.generator_provider}
                        </p>
                      ) : null}
                    </div>
                  </td>

                  <td className="whitespace-nowrap px-4 py-4">
                    <div className="flex items-center gap-2">
                      <code
                        className="text-xs text-slate-600"
                        title={result.source_trace_id}
                      >
                        {shortenTrace(result.source_trace_id)}
                      </code>
                      <button
                        type="button"
                        onClick={(event) => {
                          event.stopPropagation();
                          copyTrace(result.source_trace_id);
                        }}
                        className="rounded p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                        aria-label="Copy source trace ID"
                      >
                        <Copy className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>

                  <td className="whitespace-nowrap px-4 py-4 text-sm text-slate-600">
                    {formatDateTime(result.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="flex flex-col gap-3 border-t border-slate-200 p-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-slate-500">
          Page <span className="font-semibold text-slate-700">{pageNumber}</span>
          {" · "}{results.length} result{results.length === 1 ? "" : "s"} shown
        </p>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setOffset(Math.max(0, offset - limit))}
            disabled={!canGoPrevious || isFetching}
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </button>

          <button
            type="button"
            onClick={() => setOffset(offset + limit)}
            disabled={!canGoNext || isFetching}
            className="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    </section>
  );
}
