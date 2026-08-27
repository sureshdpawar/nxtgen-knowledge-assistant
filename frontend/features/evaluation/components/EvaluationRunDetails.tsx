"use client";

import {
  useMemo,
  useState,
} from "react";

import {
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  ExternalLink,
  Loader2,
  Search,
  XCircle,
} from "lucide-react";

import {
  useEvaluationResults,
} from "@/features/evaluation/hooks";

import type {
  EvalCase,
  EvalResult,
} from "@/features/evaluation/types";


type Props = {
  experimentId: string;

  cases: EvalCase[];
};


type Filter =
  | "all"
  | "passed"
  | "failed"
  | "unscored";


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


function getMetricReason(
  result: EvalResult,
  metricName: string,
) {
  const metric =
    result.metrics[
      metricName
    ];

  if (
    typeof metric
    !== "object"
    || metric === null
    || Array.isArray(
      metric,
    )
  ) {
    return null;
  }

  const reason = (
    metric as
      Record<
        string,
        unknown
      >
  ).reason;

  return (
    typeof reason
    === "string"
      ? reason
      : null
  );
}


function getRetrievedSources(
  result: EvalResult,
) {
  const sources:
    {
      rank:
        | number
        | null;

      url: string;

      documentName:
        | string
        | null;
    }[] = [];

  for (
    const item
    of result.retrieval_context
  ) {
    const externalId =
      item[
        "document_external_id"
      ];

    if (
      typeof externalId
      !== "string"
      || !externalId
    ) {
      continue;
    }

    const rank =
      item[
        "rank"
      ];

    const documentName =
      item[
        "document_name"
      ];

    sources.push({
      rank:
        typeof rank
        === "number"
          ? rank
          : null,

      url:
        externalId,

      documentName:
        typeof documentName
        === "string"
          ? documentName
          : null,
    });
  }

  return sources;
}


function ResultBadge({
  passed,
}: {
  passed:
    | boolean
    | null;
}) {
  if (
    passed === true
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" />

        Passed
      </span>
    );
  }

  if (
    passed === false
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
        <XCircle className="h-3.5 w-3.5" />

        Failed
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
      <CircleHelp className="h-3.5 w-3.5" />

      Unscored
    </span>
  );
}


function SmallMetric({
  label,
  value,
}: {
  label: string;

  value:
    | number
    | null;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-sm font-bold text-slate-900">
        {
          formatScore(
            value,
          )
        }
      </p>
    </div>
  );
}


function JudgeReason({
  label,
  reason,
}: {
  label: string;

  reason:
    | string
    | null;
}) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-xs font-semibold text-slate-700">
        {label}
      </p>

      <p className="mt-1 text-sm leading-5 text-slate-600">
        {
          reason
          || "Not scored."
        }
      </p>
    </div>
  );
}


function CaseResult({
  evalCase,
  result,
}: {
  evalCase: EvalCase;

  result: EvalResult;
}) {
  const [
    expanded,
    setExpanded,
  ] = useState(
    false,
  );

  const sources =
    getRetrievedSources(
      result,
    );

  const expectedSources =
    evalCase.expected_sources
    ?? [];

  const faithfulnessReason =
    getMetricReason(
      result,
      "faithfulness",
    );

  const relevancyReason =
    getMetricReason(
      result,
      "answer_relevancy",
    );

  const correctnessReason =
    getMetricReason(
      result,
      "correctness",
    );

  const refusalReason =
    getMetricReason(
      result,
      "refusal_correctness",
    );


  return (
    <div className="border-b border-slate-200 last:border-b-0">
      <button
        type="button"
        onClick={() =>
          setExpanded(
            (
              current,
            ) =>
              !current,
          )
        }
        className="flex w-full items-start gap-3 px-5 py-4 text-left transition hover:bg-slate-50"
      >
        <div className="mt-1 shrink-0 text-slate-400">
          {
            expanded
              ? (
                <ChevronDown className="h-4 w-4" />
              )
              : (
                <ChevronRight className="h-4 w-4" />
              )
          }
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-col justify-between gap-2 lg:flex-row lg:items-start">
            <div className="min-w-0">
              <p className="font-semibold text-slate-900">
                {
                  evalCase
                    .question
                }
              </p>

              <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
                <span>
                  {
                    evalCase
                      .answerable
                      ? "Answerable"
                      : "Unanswerable"
                  }
                </span>

                <span>
                  ·
                </span>

                <span>
                  Hit@K:{" "}
                  {
                    result.hit_at_k
                    === null
                      ? "—"
                      : result.hit_at_k
                        ? "Yes"
                        : "No"
                  }
                </span>

                <span>
                  ·
                </span>

                <span>
                  Rank:{" "}
                  {
                    result
                      .expected_rank
                    ?? "—"
                  }
                </span>
              </div>
            </div>

            <ResultBadge
              passed={
                result.passed
              }
            />
          </div>
        </div>
      </button>


      {expanded && (
        <div className="bg-slate-50 px-5 pb-5 pt-1">
          <div className="ml-7 space-y-5">
            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
              <SmallMetric
                label="MRR"
                value={
                  result
                    .reciprocal_rank
                }
              />

              <SmallMetric
                label="Faithfulness"
                value={
                  result
                    .faithfulness_score
                }
              />

              <SmallMetric
                label="Relevancy"
                value={
                  result
                    .relevancy_score
                }
              />

              <SmallMetric
                label="Correctness"
                value={
                  result
                    .correctness_score
                }
              />

              <SmallMetric
                label="Refusal"
                value={
                  result
                    .refusal_score
                }
              />
            </div>


            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Expected Answer
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {
                    evalCase
                      .expected_answer
                    || (
                      evalCase
                        .answerable
                        ? "No expected answer configured."
                        : "Question is intentionally unanswerable."
                    )
                  }
                </p>
              </div>


              <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Actual Answer
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {
                    result
                      .actual_answer
                    || "No answer generated."
                  }
                </p>
              </div>
            </div>


            <div className="grid gap-4 xl:grid-cols-2">
              <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Expected Sources
                </p>

                {
                  expectedSources
                    .length
                  === 0 && (
                    <p className="mt-2 text-sm text-slate-500">
                      No retrieval ground truth configured.
                    </p>
                  )
                }

                {
                  expectedSources
                    .length
                  > 0 && (
                    <div className="mt-3 space-y-2">
                      {
                        expectedSources.map(
                          (
                            source,
                            index,
                          ) => (
                            <div
                              key={
                                `${source.type}-${source.value}-${index}`
                              }
                              className="rounded-md border border-slate-200 bg-slate-50 p-3"
                            >
                              <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                                {
                                  source.type
                                }
                              </p>

                              {
                                source.value
                                  .startsWith(
                                    "http",
                                  )
                                  ? (
                                    <a
                                      href={
                                        source.value
                                      }
                                      target="_blank"
                                      rel="noreferrer"
                                      className="mt-1 flex break-all text-sm font-medium text-blue-600 hover:underline"
                                    >
                                      {
                                        source.value
                                      }

                                      <ExternalLink className="ml-1 mt-0.5 h-3.5 w-3.5 shrink-0" />
                                    </a>
                                  )
                                  : (
                                    <p className="mt-1 break-all text-sm text-slate-700">
                                      {
                                        source.value
                                      }
                                    </p>
                                  )
                              }
                            </div>
                          ),
                        )
                      }
                    </div>
                  )
                }
              </div>


              <div className="rounded-lg border border-slate-200 bg-white p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Retrieved Sources
                </p>

                {
                  sources.length
                  === 0 && (
                    <p className="mt-2 text-sm text-slate-500">
                      No retrieved source identities recorded.
                    </p>
                  )
                }

                {
                  sources.length
                  > 0 && (
                    <div className="mt-3 space-y-2">
                      {
                        sources.map(
                          (
                            source,
                            index,
                          ) => (
                            <div
                              key={
                                `${source.url}-${index}`
                              }
                              className="rounded-md border border-slate-200 bg-slate-50 p-3"
                            >
                              <div className="flex gap-3">
                                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-200 text-xs font-bold text-slate-600">
                                  {
                                    source.rank
                                    ?? (
                                      index
                                      + 1
                                    )
                                  }
                                </span>

                                <div className="min-w-0">
                                  {
                                    source.documentName && (
                                      <p className="truncate text-xs font-medium text-slate-500">
                                        {
                                          source.documentName
                                        }
                                      </p>
                                    )
                                  }

                                  <a
                                    href={
                                      source.url
                                    }
                                    target="_blank"
                                    rel="noreferrer"
                                    className="mt-1 flex break-all text-sm font-medium text-blue-600 hover:underline"
                                  >
                                    {
                                      source.url
                                    }

                                    <ExternalLink className="ml-1 mt-0.5 h-3.5 w-3.5 shrink-0" />
                                  </a>
                                </div>
                              </div>
                            </div>
                          ),
                        )
                      }
                    </div>
                  )
                }
              </div>
            </div>


            <div className="rounded-lg border border-slate-200 bg-white p-4">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Judge Reasons
              </p>

              <div className="mt-3 grid gap-3 lg:grid-cols-2">
                <JudgeReason
                  label="Faithfulness"
                  reason={
                    faithfulnessReason
                  }
                />

                <JudgeReason
                  label="Answer Relevancy"
                  reason={
                    relevancyReason
                  }
                />

                <JudgeReason
                  label="Correctness"
                  reason={
                    correctnessReason
                  }
                />

                <JudgeReason
                  label="Refusal Correctness"
                  reason={
                    refusalReason
                  }
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


function FilterButton({
  label,
  count,
  active,
  onClick,
}: {
  label: string;

  count: number;

  active: boolean;

  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={
        onClick
      }
      className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
        active
          ? "bg-blue-600 text-white"
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


export default function EvaluationRunDetails({
  experimentId,
  cases,
}: Props) {
  const [
    filter,
    setFilter,
  ] = useState<Filter>(
    "all",
  );

  const [
    search,
    setSearch,
  ] = useState(
    "",
  );

  const {
    data:
      results = [],
    isLoading,
    isError,
  } = useEvaluationResults(
    experimentId,
  );


  const caseById =
    useMemo(
      () =>
        new Map(
          cases.map(
            (
              evalCase,
            ) => [
              evalCase.id,
              evalCase,
            ],
          ),
        ),
      [
        cases,
      ],
    );


  const joined =
    useMemo(
      () =>
        results
          .map(
            (
              result,
            ) => ({
              result,

              evalCase:
                caseById.get(
                  result
                    .eval_case_id,
                )
                ?? null,
            }),
          )
          .filter(
            (
              item,
            ) =>
              item.evalCase
              !== null,
          ),
      [
        results,
        caseById,
      ],
    );


  const counts =
    useMemo(
      () => ({
        all:
          joined.length,

        passed:
          joined.filter(
            (
              item,
            ) =>
              item.result
                .passed
              === true,
          ).length,

        failed:
          joined.filter(
            (
              item,
            ) =>
              item.result
                .passed
              === false,
          ).length,

        unscored:
          joined.filter(
            (
              item,
            ) =>
              item.result
                .passed
              === null,
          ).length,
      }),
      [
        joined,
      ],
    );


  const filtered =
    useMemo(
      () => {
        const normalizedSearch =
          search
            .trim()
            .toLowerCase();

        return joined.filter(
          (
            item,
          ) => {
            const evalCase =
              item.evalCase!;

            const result =
              item.result;

            if (
              filter === "passed"
              && result.passed
              !== true
            ) {
              return false;
            }

            if (
              filter === "failed"
              && result.passed
              !== false
            ) {
              return false;
            }

            if (
              filter === "unscored"
              && result.passed
              !== null
            ) {
              return false;
            }

            if (
              normalizedSearch
            ) {
              const haystack = [
                evalCase.question,

                evalCase
                  .expected_answer
                  ?? "",

                result
                  .actual_answer
                  ?? "",
              ]
                .join(
                  " ",
                )
                .toLowerCase();

              if (
                !haystack.includes(
                  normalizedSearch,
                )
              ) {
                return false;
              }
            }

            return true;
          },
        );
      },
      [
        joined,
        filter,
        search,
      ],
    );


  if (
    isLoading
  ) {
    return (
      <div className="flex min-h-[220px] items-center justify-center rounded-xl border border-slate-200 bg-white">
        <Loader2 className="h-5 w-5 animate-spin text-blue-600" />

        <span className="ml-2 text-sm text-slate-600">
          Loading test-case results...
        </span>
      </div>
    );
  }


  if (
    isError
  ) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
        Unable to load evaluation results.
      </div>
    );
  }


  return (
    <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <div className="border-b border-slate-200 p-5">
        <div className="flex flex-col justify-between gap-4 xl:flex-row xl:items-center">
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Test Case Results
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Inspect retrieval,
              generation and judge
              results for every golden case.
            </p>
          </div>


          <div className="relative w-full xl:w-80">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />

            <input
              value={
                search
              }
              onChange={(
                event,
              ) =>
                setSearch(
                  event
                    .target
                    .value,
                )
              }
              placeholder="Search questions or answers..."
              className="w-full rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            />
          </div>
        </div>


        <div className="mt-4 flex flex-wrap gap-2">
          <FilterButton
            label="All"
            count={
              counts.all
            }
            active={
              filter
              === "all"
            }
            onClick={() =>
              setFilter(
                "all",
              )
            }
          />

          <FilterButton
            label="Passed"
            count={
              counts.passed
            }
            active={
              filter
              === "passed"
            }
            onClick={() =>
              setFilter(
                "passed",
              )
            }
          />

          <FilterButton
            label="Failed"
            count={
              counts.failed
            }
            active={
              filter
              === "failed"
            }
            onClick={() =>
              setFilter(
                "failed",
              )
            }
          />

          <FilterButton
            label="Unscored"
            count={
              counts.unscored
            }
            active={
              filter
              === "unscored"
            }
            onClick={() =>
              setFilter(
                "unscored",
              )
            }
          />
        </div>
      </div>


      {
        filtered.length
        === 0 && (
          <div className="p-10 text-center text-sm text-slate-500">
            No evaluation cases match
            the current filter.
          </div>
        )
      }


      {
        filtered.map(
          (
            item,
          ) => (
            <CaseResult
              key={
                item.result.id
              }
              evalCase={
                item.evalCase!
              }
              result={
                item.result
              }
            />
          ),
        )
      }
    </div>
  );
}