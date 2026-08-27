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
  CircleHelp,
  GitCompareArrows,
  Loader2,
  Minus,
} from "lucide-react";

import {
  useCompareEvaluationRuns,
} from "@/features/evaluation/hooks";

import type {
  EvalComparison,
  EvalComparisonCase,
  EvalComparisonDimension,
  EvalComparisonMetric,
  EvalComparisonOutcome,
  EvalExperiment,
} from "@/features/evaluation/types";


type Props = {
  runs: EvalExperiment[];
};


type CaseTab =
  | "regressed"
  | "improved"
  | "unchanged"
  | "not_comparable";


type DimensionName =
  | "retrieval"
  | "generation"
  | "performance";


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
  maximumFractionDigits = 0,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return value.toLocaleString(
    undefined,
    {
      maximumFractionDigits,
    },
  );
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


function formatBoolean(
  value:
    | boolean
    | null
    | undefined,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return value
    ? "Yes"
    : "No";
}


function isScoreMetric(
  metric: string,
) {
  return [
    "hit_rate",
    "precision_at_k",
    "recall_at_k",
    "mrr",
    "faithfulness",
    "answer_relevancy",
    "correctness",
    "refusal_correctness",
    "pass_rate",
  ].includes(
    metric,
  );
}


function isLatencyMetric(
  metric: string,
) {
  return [
    "average_retrieval_ms",
    "average_generation_ms",
    "average_rag_ms",
    "retrieval_ms",
    "generation_ms",
    "total_ms",
  ].includes(
    metric,
  );
}


function formatMetricValue(
  metric: string,
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
    isScoreMetric(
      metric,
    )
  ) {
    return formatScore(
      value,
    );
  }

  if (
    isLatencyMetric(
      metric,
    )
  ) {
    return formatLatency(
      value,
    );
  }

  return formatNumber(
    value,
    1,
  );
}


function formatDelta(
  metric:
    EvalComparisonMetric,
) {
  if (
    metric.delta === null
  ) {
    return "—";
  }

  if (
    isScoreMetric(
      metric.metric,
    )
  ) {
    const percentage =
      metric.delta * 100;

    return `${
      percentage > 0
        ? "+"
        : ""
    }${percentage.toFixed(
      1,
    )} pts`;
  }

  if (
    isLatencyMetric(
      metric.metric,
    )
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
  }${metric.delta.toLocaleString(
    undefined,
    {
      maximumFractionDigits:
        1,
    },
  )}`;
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

      precision_at_k:
        "Precision@K",

      recall_at_k:
        "Recall@K",

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

      average_retrieval_ms:
        "Retrieval Latency",

      average_generation_ms:
        "Generation Latency",

      average_rag_ms:
        "Total RAG Latency",

      average_generation_tokens:
        "Avg Generation Tokens",

      generation_tokens:
        "Generation Tokens",

      judge_tokens:
        "Judge Tokens",

      total_evaluation_tokens:
        "Total Evaluation Tokens",
    };

  return (
    labels[
      metric
    ]
    ?? metric
  );
}


function outcomeLabel(
  outcome:
    EvalComparisonOutcome,
) {
  if (
    outcome
    === "not_comparable"
  ) {
    return "Not Comparable";
  }

  return (
    outcome.charAt(
      0,
    ).toUpperCase()
    + outcome.slice(
      1,
    )
  );
}


function outcomeClasses(
  outcome:
    EvalComparisonOutcome,
) {
  if (
    outcome
    === "improved"
  ) {
    return (
      "border-emerald-200 "
      + "bg-emerald-50 "
      + "text-emerald-700"
    );
  }

  if (
    outcome
    === "regressed"
  ) {
    return (
      "border-red-200 "
      + "bg-red-50 "
      + "text-red-700"
    );
  }

  if (
    outcome
    === "not_comparable"
  ) {
    return (
      "border-amber-200 "
      + "bg-amber-50 "
      + "text-amber-700"
    );
  }

  return (
    "border-slate-200 "
    + "bg-slate-50 "
    + "text-slate-700"
  );
}


function OutcomeIcon({
  outcome,
}: {
  outcome:
    EvalComparisonOutcome;
}) {
  if (
    outcome === "improved"
  ) {
    return (
      <ArrowUp className="h-4 w-4" />
    );
  }

  if (
    outcome === "regressed"
  ) {
    return (
      <ArrowDown className="h-4 w-4" />
    );
  }

  if (
    outcome
    === "not_comparable"
  ) {
    return (
      <CircleHelp className="h-4 w-4" />
    );
  }

  return (
    <Minus className="h-4 w-4" />
  );
}


function OutcomeBadge({
  outcome,
}: {
  outcome:
    EvalComparisonOutcome;
}) {
  return (
    <span
      className={
        "inline-flex items-center "
        + "gap-1 rounded-full border "
        + "px-2.5 py-1 text-xs "
        + "font-semibold "
        + outcomeClasses(
          outcome,
        )
      }
    >
      <OutcomeIcon
        outcome={
          outcome
        }
      />

      {
        outcomeLabel(
          outcome,
        )
      }
    </span>
  );
}


function OverallComparison({
  comparison,
}: {
  comparison:
    EvalComparison;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Overall Comparison
          </p>

          <div className="mt-2 flex flex-wrap items-center gap-3">
            <h2 className="text-xl font-bold text-slate-900">
              {
                comparison
                  .baseline
                  .name
              }
            </h2>

            <ArrowRight className="h-5 w-5 text-slate-300" />

            <h2 className="text-xl font-bold text-slate-900">
              {
                comparison
                  .candidate
                  .name
              }
            </h2>
          </div>

          <p className="mt-2 text-sm text-slate-500">
            Overall status is based on
            retrieval, generation and
            performance changes.
          </p>
        </div>

        <OutcomeBadge
          outcome={
            comparison
              .overall
              .outcome
          }
        />
      </div>


      <div className="mt-5 grid gap-4 md:grid-cols-3">
        <DimensionOutcomeCard
          label="Retrieval"
          description={
            "Hit@K, Precision@K, "
            + "Recall@K and MRR"
          }
          outcome={
            comparison
              .overall
              .retrieval_outcome
          }
        />

        <DimensionOutcomeCard
          label="Generation"
          description={
            "Faithfulness, relevancy "
            + "and correctness"
          }
          outcome={
            comparison
              .overall
              .generation_outcome
          }
        />

        <DimensionOutcomeCard
          label="Performance"
          description={
            "Latency and token usage"
          }
          outcome={
            comparison
              .overall
              .performance_outcome
          }
        />
      </div>
    </div>
  );
}


function DimensionOutcomeCard({
  label,
  description,
  outcome,
}: {
  label: string;

  description: string;

  outcome:
    EvalComparisonOutcome;
}) {
  return (
    <div
      className={
        "rounded-xl border p-4 "
        + outcomeClasses(
          outcome,
        )
      }
    >
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="font-semibold">
            {label}
          </p>

          <p className="mt-1 text-xs opacity-75">
            {description}
          </p>
        </div>

        <OutcomeIcon
          outcome={
            outcome
          }
        />
      </div>

      <p className="mt-4 text-sm font-bold">
        {
          outcomeLabel(
            outcome,
          )
        }
      </p>
    </div>
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

        <OutcomeBadge
          outcome={
            metric.outcome
          }
        />
      </div>

      <div className="mt-3 flex items-center justify-between border-t border-slate-100 pt-3">
        <span className="text-xs text-slate-500">
          Delta
        </span>

        <span
          className={
            "text-xs font-semibold "
            + (
              metric.outcome
              === "improved"
                ? "text-emerald-600"
                : metric.outcome
                  === "regressed"
                  ? "text-red-600"
                  : "text-slate-500"
            )
          }
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


function MetricSection({
  title,
  description,
  dimension,
}: {
  title: string;

  description: string;

  dimension:
    EvalComparisonDimension;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-start">
        <div>
          <h3 className="font-semibold text-slate-900">
            {title}
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            {description}
          </p>
        </div>

        <OutcomeBadge
          outcome={
            dimension.outcome
          }
        />
      </div>

      {
        dimension
          .metrics
          .length === 0
          ? (
            <div className="mt-5 rounded-lg bg-slate-50 p-4 text-sm text-slate-500">
              No comparable metrics
              are available for this
              dimension.
            </div>
          )
          : (
            <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {
                dimension
                  .metrics
                  .map(
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
          )
      }
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
    | "gray"
    | "amber";
}) {
  const classes = {
    green:
      "border-emerald-200 bg-emerald-50 text-emerald-700",

    red:
      "border-red-200 bg-red-50 text-red-700",

    gray:
      "border-slate-200 bg-slate-50 text-slate-700",

    amber:
      "border-amber-200 bg-amber-50 text-amber-700",
  };

  return (
    <div
      className={
        `rounded-xl border p-4 ${
          classes[
            tone
          ]
        }`
      }
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


function DimensionStatusRow({
  item,
}: {
  item:
    EvalComparisonCase;
}) {
  return (
    <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
      <CaseDimensionStatus
        label="Overall"
        outcome={
          item.overall_outcome
        }
      />

      <CaseDimensionStatus
        label="Retrieval"
        outcome={
          item.retrieval_outcome
        }
      />

      <CaseDimensionStatus
        label="Generation"
        outcome={
          item.generation_outcome
        }
      />

      <CaseDimensionStatus
        label="Performance"
        outcome={
          item.performance_outcome
        }
      />
    </div>
  );
}


function CaseDimensionStatus({
  label,
  outcome,
}: {
  label: string;

  outcome:
    EvalComparisonOutcome;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2">
      <span className="text-xs font-semibold text-slate-500">
        {label}
      </span>

      <OutcomeBadge
        outcome={
          outcome
        }
      />
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

      <p className="mt-0.5 font-semibold text-slate-800">
        {value}
      </p>
    </div>
  );
}


function CaseRunPanel({
  title,
  candidate = false,
  item,
}: {
  title: string;

  candidate?: boolean;

  item:
    EvalComparisonCase["baseline"];
}) {
  return (
    <div
      className={
        candidate
          ? "rounded-lg border border-blue-200 bg-blue-50/50 p-4"
          : "rounded-lg border border-slate-200 bg-slate-50 p-4"
      }
    >
      <p
        className={
          candidate
            ? "text-xs font-semibold uppercase tracking-wide text-blue-600"
            : "text-xs font-semibold uppercase tracking-wide text-slate-500"
        }
      >
        {title}
      </p>


      <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Overall
      </p>

      <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
        <ComparisonValue
          label="Passed"
          value={
            formatBoolean(
              item.passed,
            )
          }
        />
      </div>


      <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Retrieval
      </p>

      <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
        <ComparisonValue
          label="Hit@K"
          value={
            formatBoolean(
              item.hit_at_k,
            )
          }
        />

        <ComparisonValue
          label="Precision@K"
          value={
            formatScore(
              item.precision_at_k,
            )
          }
        />

        <ComparisonValue
          label="Recall@K"
          value={
            formatScore(
              item.recall_at_k,
            )
          }
        />

        <ComparisonValue
          label="Expected Rank"
          value={
            formatNumber(
              item.expected_rank,
            )
          }
        />

        <ComparisonValue
          label="Reciprocal Rank"
          value={
            formatScore(
              item.reciprocal_rank,
            )
          }
        />
      </div>


      <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Generation
      </p>

      <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
        <ComparisonValue
          label="Faithfulness"
          value={
            formatScore(
              item.faithfulness,
            )
          }
        />

        <ComparisonValue
          label="Relevancy"
          value={
            formatScore(
              item.answer_relevancy,
            )
          }
        />

        <ComparisonValue
          label="Correctness"
          value={
            formatScore(
              item.correctness,
            )
          }
        />

        <ComparisonValue
          label="Refusal"
          value={
            formatScore(
              item.refusal_correctness,
            )
          }
        />
      </div>


      <p className="mt-5 text-xs font-semibold uppercase tracking-wide text-slate-400">
        Performance
      </p>

      <div className="mt-2 grid grid-cols-2 gap-3 text-sm sm:grid-cols-3">
        <ComparisonValue
          label="Retrieval"
          value={
            formatLatency(
              item.retrieval_ms,
            )
          }
        />

        <ComparisonValue
          label="Generation"
          value={
            formatLatency(
              item.generation_ms,
            )
          }
        />

        <ComparisonValue
          label="Total"
          value={
            formatLatency(
              item.total_ms,
            )
          }
        />

        <ComparisonValue
          label="Prompt Tokens"
          value={
            formatNumber(
              item.prompt_tokens,
            )
          }
        />

        <ComparisonValue
          label="Completion Tokens"
          value={
            formatNumber(
              item.completion_tokens,
            )
          }
        />

        <ComparisonValue
          label="Total Tokens"
          value={
            formatNumber(
              item.total_tokens,
            )
          }
        />
      </div>


      <p
        className={
          candidate
            ? "mt-5 text-xs font-semibold uppercase tracking-wide text-blue-600"
            : "mt-5 text-xs font-semibold uppercase tracking-wide text-slate-500"
        }
      >
        Answer
      </p>

      <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
        {
          item.actual_answer
          || "No answer generated."
        }
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
            item.overall_outcome
          }
        />
      </div>


      <DimensionStatusRow
        item={
          item
        }
      />


      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <CaseRunPanel
          title="Baseline"
          item={
            item.baseline
          }
        />

        <CaseRunPanel
          title="Candidate"
          candidate
          item={
            item.candidate
          }
        />
      </div>
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
    | "gray"
    | "amber";

  onClick: () => void;
}) {
  const activeClasses = {
    red:
      "bg-red-600 text-white",

    green:
      "bg-emerald-600 text-white",

    gray:
      "bg-slate-700 text-white",

    amber:
      "bg-amber-600 text-white",
  };

  return (
    <button
      type="button"
      onClick={
        onClick
      }
      className={
        "rounded-full px-3 py-1.5 "
        + "text-xs font-semibold "
        + "transition "
        + (
          active
            ? activeClasses[
                tone
              ]
            : (
              "bg-slate-100 "
              + "text-slate-600 "
              + "hover:bg-slate-200"
            )
        )
      }
    >
      {label}

      <span className="ml-1.5 opacity-80">
        {count}
      </span>
    </button>
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
      || baselineId
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

        if (
          activeTab
          === "not_comparable"
        ) {
          return comparison
            .not_comparable_cases;
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
          Compare retrieval quality,
          generation quality and
          performance against a
          completed baseline run.
        </p>


        {
          completedRuns.length
          < 2
          && (
            <div className="mt-5 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-700">
              At least two completed
              runs are required for
              comparison.
            </div>
          )
        }


        {
          completedRuns.length
          >= 2
          && (
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

                      comparisonMutation
                        .reset();
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
                            }
                            {" · "}
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

                      comparisonMutation
                        .reset();
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
                            }
                            {" · "}
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
                && baselineId
                && (
                  <p className="mt-3 text-sm text-red-600">
                    Baseline and
                    candidate must be
                    different runs.
                  </p>
                )
              }
            </>
          )
        }
      </div>


      {
        comparisonMutation
          .isError
        && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
            Unable to compare the
            selected runs. Make sure
            both runs use the same
            dataset and Knowledge Base.
          </div>
        )
      }


      {
        comparison
        && (
          <>
            <OverallComparison
              comparison={
                comparison
              }
            />


            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
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

              <SummaryCard
                label="Not Comparable"
                value={
                  comparison
                    .summary
                    .not_comparable_case_count
                }
                tone="amber"
              />
            </div>


            <MetricSection
              title="Retrieval"
              description={
                "Did the candidate retrieve "
                + "the right evidence?"
              }
              dimension={
                comparison
                  .metric_groups
                  .retrieval
              }
            />


            <MetricSection
              title="Generation"
              description={
                "Did the candidate produce "
                + "grounded, relevant and "
                + "correct answers?"
              }
              dimension={
                comparison
                  .metric_groups
                  .generation
              }
            />


            <MetricSection
              title="Performance"
              description={
                "Did latency or token "
                + "consumption improve?"
              }
              dimension={
                comparison
                  .metric_groups
                  .performance
              }
            />


            <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
              <div className="border-b border-slate-200 p-5">
                <div className="flex flex-col justify-between gap-3 lg:flex-row lg:items-start">
                  <div>
                    <h3 className="font-semibold text-slate-900">
                      Case-Level Analysis
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      Diagnose whether each
                      golden case changed
                      because of retrieval,
                      generation or
                      performance.
                    </p>
                  </div>

                  <p className="text-xs font-medium text-slate-500">
                    {
                      comparison
                        .summary
                        .compared_case_count
                    } cases compared
                  </p>
                </div>


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

                  <CaseTabButton
                    label="Not Comparable"
                    count={
                      comparison
                        .not_comparable_cases
                        .length
                    }
                    active={
                      activeTab
                      === "not_comparable"
                    }
                    tone="amber"
                    onClick={() =>
                      setActiveTab(
                        "not_comparable",
                      )
                    }
                  />
                </div>
              </div>


              {
                displayedCases.length
                === 0
                && (
                  <div className="p-8 text-center text-sm text-slate-500">
                    No cases in this
                    category.
                  </div>
                )
              }


              {
                displayedCases.map(
                  (
                    item,
                  ) => (
                    <CaseComparison
                      key={
                        item
                          .eval_case_id
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
        )
      }
    </div>
  );
}