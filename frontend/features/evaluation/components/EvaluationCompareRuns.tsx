"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  ArrowDown,
  ArrowRight,
  ArrowUp,
  CheckCircle2,
  GitCompareArrows,
  Loader2,
  Minus,
  XCircle,
} from "lucide-react";

import {
  useCompareEvaluationRuns,
} from "@/features/evaluation/hooks";

import type {
  EvalComparison,
  EvalComparisonCase,
  EvalComparisonMetric,
  EvalExperiment,
} from "@/features/evaluation/types";


type Props = {
  runs: EvalExperiment[];
};


type CaseTab =
  | "regressed"
  | "improved"
  | "unchanged";


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


function formatNumber(
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

  return value.toLocaleString();
}


function formatLatency(
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

  if (
    value >= 1000
  ) {
    return `${(
      value / 1000
    ).toFixed(
      2,
    )}s`;
  }

  return `${value.toFixed(
    0,
  )}ms`;
}


function formatMetricValue(
  metric: string,
  value:
    | number
    | null,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  if (
    [
      "hit_rate",
      "mrr",
      "faithfulness",
      "answer_relevancy",
      "correctness",
      "refusal_correctness",
      "pass_rate",
    ].includes(
      metric,
    )
  ) {
    return formatScore(
      value,
    );
  }

  if (
    metric
    === "average_rag_ms"
  ) {
    return formatLatency(
      value,
    );
  }

  return formatNumber(
    value,
  );
}


function formatDelta(
  metric:
    EvalComparisonMetric,
) {
  if (
    metric.delta
    === null
  ) {
    return "—";
  }

  if (
    [
      "hit_rate",
      "mrr",
      "faithfulness",
      "answer_relevancy",
      "correctness",
      "refusal_correctness",
      "pass_rate",
    ].includes(
      metric.metric,
    )
  ) {
    const percentage =
      metric.delta
      * 100;

    return `${
      percentage > 0
        ? "+"
        : ""
    }${percentage.toFixed(
      1,
    )} pts`;
  }

  if (
    metric.metric
    === "average_rag_ms"
  ) {
    return `${
      metric.delta > 0
        ? "+"
        : ""
    }${metric.delta.toFixed(
      0,
    )} ms`;
  }

  return `${
    metric.delta > 0
      ? "+"
      : ""
  }${metric.delta.toLocaleString()}`;
}


function metricLabel(
  metric: string,
) {
  const labels:
    Record<
      string,
      string
    > = {
      hit_rate:
        "Hit@K",

      mrr:
        "MRR",

      faithfulness:
        "Faithfulness",

      answer_relevancy:
        "Answer Relevancy",

      correctness:
        "Correctness",

      refusal_correctness:
        "Refusal Correctness",

      pass_rate:
        "Pass Rate",

      average_rag_ms:
        "Avg RAG Latency",

      generation_tokens:
        "Generation Tokens",

      judge_tokens:
        "Judge Tokens",

      total_evaluation_tokens:
        "Total Tokens",
    };

  return (
    labels[
      metric
    ]
    ?? metric
  );
}


function OutcomeIcon({
  outcome,
}: {
  outcome: string;
}) {
  if (
    outcome
    === "improved"
  ) {
    return (
      <ArrowUp className="h-4 w-4 text-emerald-600" />
    );
  }

  if (
    outcome
    === "regressed"
  ) {
    return (
      <ArrowDown className="h-4 w-4 text-red-600" />
    );
  }

  return (
    <Minus className="h-4 w-4 text-slate-400" />
  );
}


function OutcomeBadge({
  outcome,
}: {
  outcome: string;
}) {
  if (
    outcome
    === "improved"
  ) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <ArrowUp className="h-3.5 w-3.5" />

        Improved
      </span>
    );
  }

  if (
    outcome
    === "regressed"
  ) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
        <ArrowDown className="h-3.5 w-3.5" />

        Regressed
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
      <Minus className="h-3.5 w-3.5" />

      Unchanged
    </span>
  );
}


function MetricComparisonCard({
  metric,
}: {
  metric:
    EvalComparisonMetric;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            {
              metricLabel(
                metric.metric,
              )
            }
          </p>

          <div className="mt-3 flex items-center gap-3">
            <span className="text-sm font-medium text-slate-500">
              {
                formatMetricValue(
                  metric.metric,
                  metric.baseline,
                )
              }
            </span>

            <ArrowRight className="h-4 w-4 text-slate-300" />

            <span className="text-lg font-bold text-slate-900">
              {
                formatMetricValue(
                  metric.metric,
                  metric.candidate,
                )
              }
            </span>
          </div>
        </div>

        <OutcomeIcon
          outcome={
            metric.outcome
          }
        />
      </div>

      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-slate-500">
          Delta
        </span>

        <span
          className={`text-xs font-semibold ${
            metric.outcome
            === "improved"
              ? "text-emerald-600"
              : metric.outcome
                === "regressed"
                ? "text-red-600"
                : "text-slate-500"
          }`}
        >
          {
            formatDelta(
              metric,
            )
          }
        </span>
      </div>
    </div>
  );
}


function SummaryCard({
  label,
  value,
  tone,
}: {
  label: string;

  value: number;

  tone:
    | "green"
    | "red"
    | "gray";
}) {
  const classes = {
    green:
      "border-emerald-200 bg-emerald-50 text-emerald-700",

    red:
      "border-red-200 bg-red-50 text-red-700",

    gray:
      "border-slate-200 bg-slate-50 text-slate-700",
  };

  return (
    <div
      className={`rounded-xl border p-4 ${classes[tone]}`}
    >
      <p className="text-xs font-semibold uppercase tracking-wide opacity-70">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold">
        {value}
      </p>
    </div>
  );
}


function CaseComparison({
  item,
}: {
  item:
    EvalComparisonCase;
}) {
  return (
    <div className="border-b border-slate-200 p-5 last:border-b-0">
      <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-start">
        <div className="min-w-0">
          <p className="font-semibold text-slate-900">
            {
              item.question
              || "Unknown question"
            }
          </p>

          <p className="mt-1 text-xs text-slate-500">
            {
              item.answerable
                ? "Answerable"
                : "Unanswerable"
            }
          </p>
        </div>

        <OutcomeBadge
          outcome={
            item.outcome
          }
        />
      </div>


      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Baseline
          </p>

          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <ComparisonValue
              label="Passed"
              value={
                item.baseline
                  .passed
                === null
                  ? "—"
                  : item.baseline
                    .passed
                    ? "Yes"
                    : "No"
              }
            />

            <ComparisonValue
              label="Hit@K"
              value={
                item.baseline
                  .hit_at_k
                === null
                  ? "—"
                  : item.baseline
                    .hit_at_k
                    ? "Yes"
                    : "No"
              }
            />

            <ComparisonValue
              label="Faithfulness"
              value={
                formatScore(
                  item.baseline
                    .faithfulness,
                )
              }
            />

            <ComparisonValue
              label="Relevancy"
              value={
                formatScore(
                  item.baseline
                    .answer_relevancy,
                )
              }
            />

            <ComparisonValue
              label="Correctness"
              value={
                formatScore(
                  item.baseline
                    .correctness,
                )
              }
            />

            <ComparisonValue
              label="Refusal"
              value={
                formatScore(
                  item.baseline
                    .refusal_correctness,
                )
              }
            />
          </div>

          <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
            Answer
          </p>

          <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
            {
              item.baseline
                .actual_answer
              || "No answer generated."
            }
          </p>
        </div>


        <div className="rounded-lg border border-blue-200 bg-blue-50/50 p-4">
          <p className="text-xs font-semibold uppercase tracking-wide text-blue-600">
            Candidate
          </p>

          <div className="mt-3 grid grid-cols-2 gap-2 text-sm">
            <ComparisonValue
              label="Passed"
              value={
                item.candidate
                  .passed
                === null
                  ? "—"
                  : item.candidate
                    .passed
                    ? "Yes"
                    : "No"
              }
            />

            <ComparisonValue
              label="Hit@K"
              value={
                item.candidate
                  .hit_at_k
                === null
                  ? "—"
                  : item.candidate
                    .hit_at_k
                    ? "Yes"
                    : "No"
              }
            />

            <ComparisonValue
              label="Faithfulness"
              value={
                formatScore(
                  item.candidate
                    .faithfulness,
                )
              }
            />

            <ComparisonValue
              label="Relevancy"
              value={
                formatScore(
                  item.candidate
                    .answer_relevancy,
                )
              }
            />

            <ComparisonValue
              label="Correctness"
              value={
                formatScore(
                  item.candidate
                    .correctness,
                )
              }
            />

            <ComparisonValue
              label="Refusal"
              value={
                formatScore(
                  item.candidate
                    .refusal_correctness,
                )
              }
            />
          </div>

          <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-blue-600">
            Answer
          </p>

          <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
            {
              item.candidate
                .actual_answer
              || "No answer generated."
            }
          </p>
        </div>
      </div>
    </div>
  );
}


function ComparisonValue({
  label,
  value,
}: {
  label: string;

  value: string;
}) {
  return (
    <div>
      <p className="text-xs text-slate-500">
        {label}
      </p>

      <p className="font-semibold text-slate-800">
        {value}
      </p>
    </div>
  );
}


export default function EvaluationCompareRuns({
  runs,
}: Props) {
  const completedRuns =
    useMemo(
      () =>
        runs.filter(
          (
            run,
          ) =>
            run.status
              .toLowerCase()
            === "completed",
        ),
      [
        runs,
      ],
    );


  const [
    baselineId,
    setBaselineId,
  ] = useState(
    "",
  );

  const [
    candidateId,
    setCandidateId,
  ] = useState(
    "",
  );

  const [
    activeTab,
    setActiveTab,
  ] = useState<CaseTab>(
    "regressed",
  );


  const comparisonMutation =
    useCompareEvaluationRuns();


  useEffect(
    () => {
      if (
        completedRuns.length
        < 2
      ) {
        setBaselineId(
          "",
        );

        setCandidateId(
          "",
        );

        return;
      }

      const baselineExists =
        completedRuns.some(
          (
            run,
          ) =>
            run.id
            === baselineId,
        );

      const candidateExists =
        completedRuns.some(
          (
            run,
          ) =>
            run.id
            === candidateId,
        );

      if (
        !baselineExists
      ) {
        setBaselineId(
          completedRuns[
            completedRuns.length
            - 2
          ].id,
        );
      }

      if (
        !candidateExists
      ) {
        setCandidateId(
          completedRuns[
            completedRuns.length
            - 1
          ].id,
        );
      }
    },
    [
      completedRuns,
      baselineId,
      candidateId,
    ],
  );


  function handleCompare() {
    if (
      !baselineId
      || !candidateId
    ) {
      return;
    }

    if (
      baselineId
      === candidateId
    ) {
      return;
    }

    comparisonMutation.mutate({
      baseline_experiment_id:
        baselineId,

      candidate_experiment_id:
        candidateId,
    });
  }


  const comparison:
    EvalComparison
    | undefined =
      comparisonMutation.data;


  const displayedCases =
    useMemo(
      () => {
        if (
          !comparison
        ) {
          return [];
        }

        if (
          activeTab
          === "improved"
        ) {
          return comparison
            .improved_cases;
        }

        if (
          activeTab
          === "unchanged"
        ) {
          return comparison
            .unchanged_cases;
        }

        return comparison
          .regressed_cases;
      },
      [
        comparison,
        activeTab,
      ],
    );


  return (
    <div className="space-y-5">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <GitCompareArrows className="h-5 w-5 text-blue-600" />

          <h2 className="text-lg font-semibold text-slate-900">
            Compare Runs
          </h2>
        </div>

        <p className="mt-1 text-sm text-slate-500">
          Compare a candidate configuration
          against a previously completed
          baseline run.
        </p>


        {completedRuns.length < 2 && (
          <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
            At least two completed runs
            are required for comparison.
          </div>
        )}


        {completedRuns.length >= 2 && (
          <>
            <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_auto_1fr_auto] lg:items-end">
              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                  Baseline
                </label>

                <select
                  value={
                    baselineId
                  }
                  onChange={(
                    event,
                  ) => {
                    setBaselineId(
                      event
                        .target
                        .value,
                    );

                    comparisonMutation.reset();
                  }}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  {
                    completedRuns.map(
                      (
                        run,
                      ) => (
                        <option
                          key={
                            run.id
                          }
                          value={
                            run.id
                          }
                        >
                          {
                            run.name
                          }{" "}
                          ·{" "}
                          {
                            run.llm_model
                            || "No model"
                          }
                        </option>
                      ),
                    )
                  }
                </select>
              </div>


              <div className="hidden pb-3 lg:block">
                <ArrowRight className="h-5 w-5 text-slate-300" />
              </div>


              <div>
                <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                  Candidate
                </label>

                <select
                  value={
                    candidateId
                  }
                  onChange={(
                    event,
                  ) => {
                    setCandidateId(
                      event
                        .target
                        .value,
                    );

                    comparisonMutation.reset();
                  }}
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                >
                  {
                    completedRuns.map(
                      (
                        run,
                      ) => (
                        <option
                          key={
                            run.id
                          }
                          value={
                            run.id
                          }
                        >
                          {
                            run.name
                          }{" "}
                          ·{" "}
                          {
                            run.llm_model
                            || "No model"
                          }
                        </option>
                      ),
                    )
                  }
                </select>
              </div>


              <button
                type="button"
                onClick={
                  handleCompare
                }
                disabled={
                  !baselineId
                  || !candidateId
                  || baselineId
                  === candidateId
                  || comparisonMutation
                    .isPending
                }
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {
                  comparisonMutation
                    .isPending
                    ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    )
                    : (
                      <GitCompareArrows className="h-4 w-4" />
                    )
                }

                Compare
              </button>
            </div>


            {
              baselineId
              === candidateId
              && baselineId && (
                <p className="mt-3 text-sm text-red-600">
                  Baseline and candidate
                  must be different runs.
                </p>
              )
            }
          </>
        )}
      </div>


      {comparisonMutation.isError && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
          Unable to compare the selected runs.
          Make sure both runs use the same
          dataset and Knowledge Base.
        </div>
      )}


      {comparison && (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <SummaryCard
              label="Improved Cases"
              value={
                comparison
                  .summary
                  .improved_case_count
              }
              tone="green"
            />

            <SummaryCard
              label="Regressed Cases"
              value={
                comparison
                  .summary
                  .regressed_case_count
              }
              tone="red"
            />

            <SummaryCard
              label="Unchanged Cases"
              value={
                comparison
                  .summary
                  .unchanged_case_count
              }
              tone="gray"
            />
          </div>


          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-col justify-between gap-3 md:flex-row md:items-start">
              <div>
                <h3 className="font-semibold text-slate-900">
                  Metric Comparison
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Quality, performance and
                  cost changes between runs.
                </p>
              </div>

              <div className="flex flex-wrap gap-2 text-xs">
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 font-semibold text-emerald-700">
                  {
                    comparison
                      .summary
                      .improved_metric_count
                  } improved
                </span>

                <span className="rounded-full bg-red-50 px-2.5 py-1 font-semibold text-red-700">
                  {
                    comparison
                      .summary
                      .regressed_metric_count
                  } regressed
                </span>
              </div>
            </div>


            <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {
                comparison.metrics.map(
                  (
                    metric,
                  ) => (
                    <MetricComparisonCard
                      key={
                        metric.metric
                      }
                      metric={
                        metric
                      }
                    />
                  ),
                )
              }
            </div>
          </div>


          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 p-5">
              <h3 className="font-semibold text-slate-900">
                Case-Level Changes
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                See exactly which golden
                cases improved or regressed.
              </p>


              <div className="mt-4 flex flex-wrap gap-2">
                <CaseTabButton
                  label="Regressed"
                  count={
                    comparison
                      .regressed_cases
                      .length
                  }
                  active={
                    activeTab
                    === "regressed"
                  }
                  tone="red"
                  onClick={() =>
                    setActiveTab(
                      "regressed",
                    )
                  }
                />

                <CaseTabButton
                  label="Improved"
                  count={
                    comparison
                      .improved_cases
                      .length
                  }
                  active={
                    activeTab
                    === "improved"
                  }
                  tone="green"
                  onClick={() =>
                    setActiveTab(
                      "improved",
                    )
                  }
                />

                <CaseTabButton
                  label="Unchanged"
                  count={
                    comparison
                      .unchanged_cases
                      .length
                  }
                  active={
                    activeTab
                    === "unchanged"
                  }
                  tone="gray"
                  onClick={() =>
                    setActiveTab(
                      "unchanged",
                    )
                  }
                />
              </div>
            </div>


            {displayedCases.length === 0 && (
              <div className="p-8 text-center text-sm text-slate-500">
                No cases in this category.
              </div>
            )}


            {
              displayedCases.map(
                (
                  item,
                ) => (
                  <CaseComparison
                    key={
                      item.eval_case_id
                    }
                    item={
                      item
                    }
                  />
                ),
              )
            }
          </div>
        </>
      )}
    </div>
  );
}


function CaseTabButton({
  label,
  count,
  active,
  tone,
  onClick,
}: {
  label: string;

  count: number;

  active: boolean;

  tone:
    | "red"
    | "green"
    | "gray";

  onClick: () => void;
}) {
  let activeClass =
    "bg-slate-700 text-white";

  if (
    tone === "red"
  ) {
    activeClass =
      "bg-red-600 text-white";
  }

  if (
    tone === "green"
  ) {
    activeClass =
      "bg-emerald-600 text-white";
  }

  return (
    <button
      type="button"
      onClick={
        onClick
      }
      className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
        active
          ? activeClass
          : "bg-slate-100 text-slate-600 hover:bg-slate-200"
      }`}
    >
      {label}

      <span className="ml-1.5 opacity-80">
        {count}
      </span>
    </button>
  );
}