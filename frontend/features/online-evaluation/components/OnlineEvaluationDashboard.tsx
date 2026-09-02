"use client";

import {
  useMemo,
  useState,
} from "react";

import {
  Activity,
  CircleDollarSign,
  Gauge,
  Loader2,
  Play,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";

import {
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  useOnlineEvalSummary,
  useProcessPendingOnlineEvals,
} from "@/features/online-evaluation/hooks";

import type {
  OnlineEvalSummaryFilters,
} from "@/features/online-evaluation/types";


function formatScore(
  value:
    | number
    | null
    | undefined,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return `${(
    value * 100
  ).toFixed(
    1,
  )}%`;
}


function formatCost(
  total:
    | number
    | null
    | undefined,
  currency:
    | string
    | null
    | undefined,
) {
  if (
    total === null
    || total === undefined
    || !currency
  ) {
    return "—";
  }

  return new Intl.NumberFormat(
    undefined,
    {
      style:
        "currency",
      currency,
      maximumFractionDigits:
        6,
    },
  ).format(
    total,
  );
}


function MetricCard({
  label,
  value,
  subtitle,
  icon,
}: {
  label: string;

  value: string;

  subtitle: string;

  icon:
    React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {label}
          </p>

          <p className="mt-2 text-2xl font-bold text-slate-900">
            {value}
          </p>
        </div>

        <div className="rounded-lg bg-slate-100 p-2 text-slate-600">
          {icon}
        </div>
      </div>

      <p className="mt-2 text-xs text-slate-500">
        {subtitle}
      </p>
    </div>
  );
}


export default function OnlineEvaluationDashboard() {
  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] = useState(
    "",
  );

  const [
    generatorProvider,
    setGeneratorProvider,
  ] = useState(
    "",
  );

  const [
    generatorModel,
    setGeneratorModel,
  ] = useState(
    "",
  );

  const [
    createdFrom,
    setCreatedFrom,
  ] = useState(
    "",
  );

  const [
    createdTo,
    setCreatedTo,
  ] = useState(
    "",
  );

  const [
    processLimit,
    setProcessLimit,
  ] = useState(
    10,
  );


  const {
    data:
      knowledgeBases = [],
    isLoading:
      knowledgeBasesLoading,
  } = useKnowledgeBases();


  const summaryFilters =
    useMemo<
      OnlineEvalSummaryFilters
    >(
      () => ({
        knowledge_base_id:
          knowledgeBaseId
          || null,

        generator_provider:
          generatorProvider
            .trim()
          || null,

        generator_model:
          generatorModel
            .trim()
          || null,

        created_from:
          createdFrom
            ? new Date(
                `${createdFrom}T00:00:00`,
              )
                .toISOString()
            : null,

        created_to:
          createdTo
            ? new Date(
                `${createdTo}T23:59:59.999`,
              )
                .toISOString()
            : null,
      }),
      [
        knowledgeBaseId,
        generatorProvider,
        generatorModel,
        createdFrom,
        createdTo,
      ],
    );


  const {
    data:
      summary,
    isLoading:
      summaryLoading,
    isFetching:
      summaryFetching,
    error:
      summaryError,
    refetch:
      refetchSummary,
  } = useOnlineEvalSummary(
    summaryFilters,
  );


  const processMutation =
    useProcessPendingOnlineEvals();


  async function handleProcessPending() {
    try {
      const response =
        await processMutation
          .mutateAsync({
            limit:
              processLimit,

            evaluator_llm_configuration_id:
              null,
          });

      toast.success(
        `Processed ${response.selected} online evaluation sample${
          response.selected
          === 1
            ? ""
            : "s"
        }. ${response.completed} completed, ${response.failed} failed.`,
      );
    } catch (
      error
    ) {
      toast.error(
        error instanceof Error
          ? error.message
          : "Unable to process pending online evaluations.",
      );
    }
  }


  function clearFilters() {
    setKnowledgeBaseId(
      "",
    );

    setGeneratorProvider(
      "",
    );

    setGeneratorModel(
      "",
    );

    setCreatedFrom(
      "",
    );

    setCreatedTo(
      "",
    );
  }


  const pricedEvaluations =
    summary
      ?.evaluation_cost
      .priced_evaluations
    ?? 0;

  const unpricedEvaluations =
    summary
      ?.evaluation_cost
      .unpriced_evaluations
    ?? 0;


  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="h-6 w-6 text-slate-700" />

            <h1 className="text-2xl font-bold text-slate-900">
              Online Evaluation
            </h1>
          </div>

          <p className="mt-1 max-w-3xl text-sm text-slate-600">
            Monitor sampled production RAG responses using reference-free quality evaluation linked back to the original request trace.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <label className="sr-only">
            Process limit
          </label>

          <select
            className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 shadow-sm outline-none transition focus:border-slate-500"
            value={
              processLimit
            }
            onChange={(
              event,
            ) =>
              setProcessLimit(
                Number(
                  event
                    .target
                    .value,
                ),
              )
            }
            disabled={
              processMutation
                .isPending
            }
          >
            <option value={5}>
              5 samples
            </option>

            <option value={10}>
              10 samples
            </option>

            <option value={25}>
              25 samples
            </option>

            <option value={50}>
              50 samples
            </option>

            <option value={100}>
              100 samples
            </option>
          </select>

          <button
            type="button"
            onClick={
              handleProcessPending
            }
            disabled={
              processMutation
                .isPending
            }
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-slate-900 px-4 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {processMutation
              .isPending
              ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              )
              : (
                <Play className="h-4 w-4" />
              )}

            Process pending
          </button>

          <button
            type="button"
            onClick={() =>
              refetchSummary()
            }
            disabled={
              summaryFetching
            }
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <RefreshCw
              className={`h-4 w-4 ${
                summaryFetching
                  ? "animate-spin"
                  : ""
              }`}
            />

            Refresh
          </button>
        </div>
      </div>


      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">
          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Knowledge base
            </label>

            <select
              value={
                knowledgeBaseId
              }
              onChange={(
                event,
              ) =>
                setKnowledgeBaseId(
                  event
                    .target
                    .value,
                )
              }
              disabled={
                knowledgeBasesLoading
              }
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-slate-500"
            >
              <option value="">
                All knowledge bases
              </option>

              {knowledgeBases.map(
                (
                  knowledgeBase,
                ) => (
                  <option
                    key={
                      knowledgeBase.id
                    }
                    value={
                      knowledgeBase.id
                    }
                  >
                    {
                      knowledgeBase.name
                    }
                  </option>
                ),
              )}
            </select>
          </div>


          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Provider
            </label>

            <input
              value={
                generatorProvider
              }
              onChange={(
                event,
              ) =>
                setGeneratorProvider(
                  event
                    .target
                    .value,
                )
              }
              placeholder="All providers"
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-500"
            />
          </div>


          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Model
            </label>

            <input
              value={
                generatorModel
              }
              onChange={(
                event,
              ) =>
                setGeneratorModel(
                  event
                    .target
                    .value,
                )
              }
              placeholder="All models"
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-slate-500"
            />
          </div>


          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              From
            </label>

            <input
              type="date"
              value={
                createdFrom
              }
              onChange={(
                event,
              ) =>
                setCreatedFrom(
                  event
                    .target
                    .value,
                )
              }
              className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-slate-500"
            />
          </div>


          <div>
            <label className="mb-1.5 block text-xs font-semibold uppercase tracking-wide text-slate-500">
              To
            </label>

            <div className="flex gap-2">
              <input
                type="date"
                value={
                  createdTo
                }
                onChange={(
                  event,
                ) =>
                  setCreatedTo(
                    event
                      .target
                      .value,
                  )
                }
                className="h-10 min-w-0 flex-1 rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-slate-500"
              />

              <button
                type="button"
                onClick={
                  clearFilters
                }
                className="h-10 rounded-lg border border-slate-300 bg-white px-3 text-xs font-semibold text-slate-600 transition hover:bg-slate-50"
              >
                Clear
              </button>
            </div>
          </div>
        </div>
      </div>


      {summaryError ? (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Unable to load online evaluation summary.
        </div>
      ) : null}


      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricCard
          label="Pass rate"
          value={
            summaryLoading
              ? "…"
              : formatScore(
                  summary
                    ?.pass_rate,
                )
          }
          subtitle={
            summary
              ? `${summary.passed} passed / ${summary.completed} completed`
              : "Completed evaluations"
          }
          icon={
            <ShieldCheck className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Faithfulness"
          value={
            summaryLoading
              ? "…"
              : formatScore(
                  summary
                    ?.average_scores
                    .faithfulness,
                )
          }
          subtitle="Average completed score"
          icon={
            <Gauge className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Answer relevancy"
          value={
            summaryLoading
              ? "…"
              : formatScore(
                  summary
                    ?.average_scores
                    .answer_relevancy,
                )
          }
          subtitle="Average completed score"
          icon={
            <Gauge className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Context relevancy"
          value={
            summaryLoading
              ? "…"
              : formatScore(
                  summary
                    ?.average_scores
                    .contextual_relevancy,
                )
          }
          subtitle="Average completed score"
          icon={
            <Gauge className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Evaluation cost"
          value={
            summaryLoading
              ? "…"
              : formatCost(
                  summary
                    ?.evaluation_cost
                    .total,
                  summary
                    ?.evaluation_cost
                    .currency,
                )
          }
          subtitle={
            summary
              ? `${pricedEvaluations} priced${
                  unpricedEvaluations > 0
                    ? ` · ${unpricedEvaluations} incomplete`
                    : ""
                }`
              : "Judge cost"
          }
          icon={
            <CircleDollarSign className="h-5 w-5" />
          }
        />
      </div>


      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          label="Sampled"
          value={
            summaryLoading
              ? "…"
              : (
                  summary
                    ?.total
                  ?? 0
                ).toLocaleString()
          }
          subtitle="Total captured samples"
          icon={
            <Activity className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Pending"
          value={
            summaryLoading
              ? "…"
              : (
                  summary
                    ?.pending
                  ?? 0
                ).toLocaleString()
          }
          subtitle="Waiting for manual evaluation"
          icon={
            <Loader2 className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Running"
          value={
            summaryLoading
              ? "…"
              : (
                  summary
                    ?.running
                  ?? 0
                ).toLocaleString()
          }
          subtitle="Currently being processed"
          icon={
            <Loader2 className="h-5 w-5" />
          }
        />

        <MetricCard
          label="Failed"
          value={
            summaryLoading
              ? "…"
              : (
                  summary
                    ?.failed
                  ?? 0
                ).toLocaleString()
          }
          subtitle="Evaluation execution failures"
          icon={
            <Activity className="h-5 w-5" />
          }
        />
      </div>


      <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center">
        <p className="text-sm font-semibold text-slate-700">
          Online evaluation results
        </p>

        <p className="mt-1 text-sm text-slate-500">
          The results table and evaluation detail view will be added here next.
        </p>
      </div>
    </div>
  );
}
