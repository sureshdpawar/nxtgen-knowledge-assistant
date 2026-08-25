"use client";

import {
  ChangeEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  CheckCircle2,
  ClipboardCheck,
  FileJson,
  GitCompareArrows,
  Loader2,
  Play,
  RefreshCw,
  Upload,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";

import EvaluationCompareRuns from "@/features/evaluation/components/EvaluationCompareRuns";
import EvaluationRunDetails from "@/features/evaluation/components/EvaluationRunDetails";

import {
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  useEvaluationCases,
  useEvaluationDatasets,
  useEvaluationRuns,
  useImportEvaluationDataset,
  useRunRAGEvaluation,
} from "@/features/evaluation/hooks";

import type {
  EvalExperiment,
} from "@/features/evaluation/types";


type ViewMode =
  | "run"
  | "compare";


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


function formatMilliseconds(
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


function getNestedNumber(
  object:
    Record<
      string,
      unknown
    >,
  path: string[],
):
  | number
  | null {
  let current:
    unknown = object;

  for (
    const key
    of path
  ) {
    if (
      typeof current
      !== "object"
      || current === null
      || Array.isArray(
        current,
      )
    ) {
      return null;
    }

    current = (
      current as
        Record<
          string,
          unknown
        >
    )[key];
  }

  return (
    typeof current
    === "number"
      ? current
      : null
  );
}


function getMetricAverage(
  experiment:
    EvalExperiment,
  metric: string,
) {
  return getNestedNumber(
    experiment.metrics,
    [
      "generation",
      metric,
      "average_score",
    ],
  );
}


function getAverageLatency(
  experiment:
    EvalExperiment,
) {
  return getNestedNumber(
    experiment.metrics,
    [
      "latency",
      "average_rag_ms",
    ],
  );
}


function getTotalTokens(
  experiment:
    EvalExperiment,
) {
  const total =
    getNestedNumber(
      experiment.metrics,
      [
        "usage",
        "total_evaluation_tokens",
      ],
    );

  if (
    total !== null
  ) {
    return total;
  }

  return getNestedNumber(
    experiment.metrics,
    [
      "usage",
      "generation",
      "total_tokens",
    ],
  );
}


function getPassRate(
  experiment:
    EvalExperiment,
) {
  return getNestedNumber(
    experiment.metrics,
    [
      "cases",
      "pass_rate",
    ],
  );
}


function StatusBadge({
  status,
}: {
  status: string;
}) {
  const normalized =
    status.toLowerCase();

  if (
    normalized
    === "completed"
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
        <CheckCircle2 className="h-3.5 w-3.5" />

        Completed
      </span>
    );
  }

  if (
    normalized
    === "failed"
  ) {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
        <XCircle className="h-3.5 w-3.5" />

        Failed
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1.5 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">
      <Loader2 className="h-3.5 w-3.5 animate-spin" />

      {status}
    </span>
  );
}


function MetricCard({
  label,
  value,
  subtitle,
}: {
  label: string;

  value: string;

  subtitle?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold text-slate-900">
        {value}
      </p>

      {subtitle && (
        <p className="mt-1 text-xs text-slate-500">
          {subtitle}
        </p>
      )}
    </div>
  );
}


export default function EvaluationDashboard() {
  const fileInputRef =
    useRef<
      HTMLInputElement
      | null
    >(
      null,
    );

  const [
    viewMode,
    setViewMode,
  ] = useState<ViewMode>(
    "run",
  );

  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] = useState(
    "",
  );

  const [
    datasetId,
    setDatasetId,
  ] = useState(
    "",
  );

  const [
    selectedRunId,
    setSelectedRunId,
  ] = useState(
    "",
  );

  const [
    runName,
    setRunName,
  ] = useState(
    "",
  );

  const [
    topK,
    setTopK,
  ] = useState(
    5,
  );

  const [
    runJudges,
    setRunJudges,
  ] = useState(
    true,
  );


  const {
    data:
      knowledgeBases = [],
    isLoading:
      knowledgeBasesLoading,
  } = useKnowledgeBases();


  const {
    data:
      datasets = [],
    isLoading:
      datasetsLoading,
    refetch:
      refetchDatasets,
  } = useEvaluationDatasets(
    knowledgeBaseId
      || null,
  );


  const {
    data:
      cases = [],
    isLoading:
      casesLoading,
  } = useEvaluationCases(
    datasetId
      || null,
  );


  const {
    data:
      runs = [],
    isLoading:
      runsLoading,
    refetch:
      refetchRuns,
  } = useEvaluationRuns(
    datasetId
      || null,
  );


  const importMutation =
    useImportEvaluationDataset();

  const runMutation =
    useRunRAGEvaluation();


  useEffect(
    () => {
      if (
        !knowledgeBaseId
        && knowledgeBases
          .length > 0
      ) {
        setKnowledgeBaseId(
          knowledgeBases[
            0
          ].id,
        );
      }
    },
    [
      knowledgeBases,
      knowledgeBaseId,
    ],
  );


  useEffect(
    () => {
      setDatasetId(
        "",
      );

      setSelectedRunId(
        "",
      );

      setViewMode(
        "run",
      );
    },
    [
      knowledgeBaseId,
    ],
  );


  useEffect(
    () => {
      if (
        !datasetId
        && datasets.length
        > 0
      ) {
        setDatasetId(
          datasets[
            0
          ].id,
        );
      }
    },
    [
      datasets,
      datasetId,
    ],
  );


  useEffect(
    () => {
      if (
        runs.length
        === 0
      ) {
        setSelectedRunId(
          "",
        );

        return;
      }

      const exists =
        runs.some(
          (
            run,
          ) =>
            run.id
            === selectedRunId,
        );

      if (
        !exists
      ) {
        setSelectedRunId(
          runs[
            runs.length
            - 1
          ].id,
        );
      }
    },
    [
      runs,
      selectedRunId,
    ],
  );


  const selectedDataset =
    useMemo(
      () =>
        datasets.find(
          (
            dataset,
          ) =>
            dataset.id
            === datasetId,
        )
        ?? null,
      [
        datasets,
        datasetId,
      ],
    );


  const selectedRun =
    useMemo(
      () =>
        runs.find(
          (
            run,
          ) =>
            run.id
            === selectedRunId,
        )
        ?? null,
      [
        runs,
        selectedRunId,
      ],
    );


  function handleFileChange(
    event:
      ChangeEvent<
        HTMLInputElement
      >,
  ) {
    const file =
      event
        .target
        .files?.[0];

    if (
      !file
    ) {
      return;
    }

    if (
      !file.name
        .toLowerCase()
        .endsWith(
          ".json",
        )
    ) {
      toast.error(
        "Please select a JSON evaluation dataset.",
      );

      event.target.value =
        "";

      return;
    }

    importMutation.mutate(
      file,
      {
        onSuccess(
          response,
        ) {
          toast.success(
            `Imported ${response.case_count} evaluation cases.`,
          );

          setKnowledgeBaseId(
            response
              .dataset
              .knowledge_base_id,
          );

          setDatasetId(
            response
              .dataset
              .id,
          );

          setSelectedRunId(
            "",
          );

          setViewMode(
            "run",
          );

          refetchDatasets();
        },

        onError(
          error,
        ) {
          console.error(
            error,
          );

          toast.error(
            "Unable to import evaluation dataset.",
          );
        },

        onSettled() {
          if (
            fileInputRef
              .current
          ) {
            fileInputRef
              .current
              .value = "";
          }
        },
      },
    );
  }


  function handleRun() {
    if (
      !knowledgeBaseId
    ) {
      toast.error(
        "Select a Knowledge Base.",
      );

      return;
    }

    if (
      !datasetId
    ) {
      toast.error(
        "Select an evaluation dataset.",
      );

      return;
    }

    const name =
      runName.trim()
      || `Evaluation ${new Date().toLocaleString()}`;

    runMutation.mutate(
      {
        dataset_id:
          datasetId,

        knowledge_base_id:
          knowledgeBaseId,

        name,

        top_k:
          topK,

        evaluator_llm_configuration_id:
          null,

        run_judges:
          runJudges,
      },
      {
        onSuccess(
          experiment,
        ) {
          toast.success(
            "Evaluation run completed.",
          );

          setSelectedRunId(
            experiment.id,
          );

          setRunName(
            "",
          );

          setViewMode(
            "run",
          );

          refetchRuns();
        },

        onError(
          error,
        ) {
          console.error(
            error,
          );

          toast.error(
            "Evaluation run failed.",
          );
        },
      },
    );
  }


  const running =
    runMutation.isPending;


  return (
    <div className="mx-auto max-w-[1600px] space-y-6">
      <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
        <div>
          <div className="flex items-center gap-2">
            <ClipboardCheck className="h-6 w-6 text-blue-600" />

            <h1 className="text-2xl font-bold text-slate-900">
              Evaluation
            </h1>
          </div>

          <p className="mt-1 max-w-3xl text-sm text-slate-600">
            Measure retrieval quality,
            generation quality,
            latency and cost against
            reusable golden datasets.
          </p>
        </div>


        <button
          type="button"
          onClick={() =>
            fileInputRef
              .current
              ?.click()
          }
          disabled={
            importMutation
              .isPending
          }
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-60"
        >
          {
            importMutation
              .isPending
              ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              )
              : (
                <Upload className="h-4 w-4" />
              )
          }

          Import Golden Dataset
        </button>


        <input
          ref={
            fileInputRef
          }
          type="file"
          accept=".json,application/json"
          className="hidden"
          onChange={
            handleFileChange
          }
        />
      </div>


      <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:grid-cols-3">
        <div>
          <label className="mb-1.5 block text-sm font-semibold text-slate-700">
            Knowledge Base
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
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
          >
            <option value="">
              Select Knowledge Base
            </option>

            {
              knowledgeBases.map(
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
              )
            }
          </select>
        </div>


        <div>
          <label className="mb-1.5 block text-sm font-semibold text-slate-700">
            Evaluation Dataset
          </label>

          <select
            value={
              datasetId
            }
            onChange={(
              event,
            ) => {
              setDatasetId(
                event
                  .target
                  .value,
              );

              setSelectedRunId(
                "",
              );

              setViewMode(
                "run",
              );
            }}
            disabled={
              !knowledgeBaseId
              || datasetsLoading
            }
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
          >
            <option value="">
              Select Dataset
            </option>

            {
              datasets.map(
                (
                  dataset,
                ) => (
                  <option
                    key={
                      dataset.id
                    }
                    value={
                      dataset.id
                    }
                  >
                    {
                      dataset.name
                    }{" "}
                    ({
                      dataset.version
                    })
                  </option>
                ),
              )
            }
          </select>
        </div>


        <div className="flex items-end">
          <button
            type="button"
            onClick={() => {
              refetchDatasets();

              if (
                datasetId
              ) {
                refetchRuns();
              }
            }}
            className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <RefreshCw className="h-4 w-4" />

            Refresh
          </button>
        </div>
      </div>


      {selectedDataset && (
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex flex-col justify-between gap-3 md:flex-row md:items-center">
            <div>
              <div className="flex items-center gap-2">
                <FileJson className="h-5 w-5 text-slate-500" />

                <h2 className="font-semibold text-slate-900">
                  {
                    selectedDataset
                      .name
                  }
                </h2>

                <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600">
                  {
                    selectedDataset
                      .version
                  }
                </span>
              </div>

              {
                selectedDataset
                  .description && (
                  <p className="mt-2 text-sm text-slate-600">
                    {
                      selectedDataset
                        .description
                    }
                  </p>
                )
              }
            </div>

            <div className="rounded-lg bg-slate-50 px-4 py-2 text-center">
              <p className="text-xl font-bold text-slate-900">
                {
                  casesLoading
                    ? "..."
                    : cases.length
                }
              </p>

              <p className="text-xs font-medium text-slate-500">
                Golden Cases
              </p>
            </div>
          </div>
        </div>
      )}


      {datasetId && (
        <>
          <div className="flex gap-2 rounded-xl border border-slate-200 bg-white p-2 shadow-sm">
            <button
              type="button"
              onClick={() =>
                setViewMode(
                  "run",
                )
              }
              className={`rounded-lg px-4 py-2 text-sm font-semibold transition ${
                viewMode === "run"
                  ? "bg-blue-600 text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              Runs
            </button>

            <button
              type="button"
              onClick={() =>
                setViewMode(
                  "compare",
                )
              }
              className={`inline-flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition ${
                viewMode === "compare"
                  ? "bg-blue-600 text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              <GitCompareArrows className="h-4 w-4" />

              Compare
            </button>
          </div>


          {viewMode === "compare" && (
            <EvaluationCompareRuns
              runs={
                runs
              }
            />
          )}


          {viewMode === "run" && (
            <div className="grid gap-6 xl:grid-cols-[380px_minmax(0,1fr)]">
              <div className="space-y-6">
                <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                  <h2 className="text-lg font-semibold text-slate-900">
                    Run Evaluation
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Execute the golden set
                    using the current RAG
                    configuration.
                  </p>


                  <div className="mt-5 space-y-4">
                    <div>
                      <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                        Run Name
                      </label>

                      <input
                        value={
                          runName
                        }
                        onChange={(
                          event,
                        ) =>
                          setRunName(
                            event
                              .target
                              .value,
                          )
                        }
                        placeholder="e.g. Prompt v8 candidate"
                        className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm"
                      />
                    </div>


                    <div>
                      <label className="mb-1.5 block text-sm font-semibold text-slate-700">
                        Top K
                      </label>

                      <input
                        type="number"
                        min={1}
                        max={100}
                        value={
                          topK
                        }
                        onChange={(
                          event,
                        ) =>
                          setTopK(
                            Math.max(
                              1,
                              Math.min(
                                100,
                                Number(
                                  event
                                    .target
                                    .value,
                                )
                                || 1,
                              ),
                            ),
                          )
                        }
                        className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm"
                      />
                    </div>


                    <label className="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 p-3">
                      <input
                        type="checkbox"
                        checked={
                          runJudges
                        }
                        onChange={(
                          event,
                        ) =>
                          setRunJudges(
                            event
                              .target
                              .checked,
                          )
                        }
                        className="mt-1 h-4 w-4"
                      />

                      <span>
                        <span className="block text-sm font-semibold text-slate-800">
                          LLM-as-a-Judge
                        </span>

                        <span className="mt-0.5 block text-xs text-slate-500">
                          Faithfulness,
                          relevancy,
                          correctness and
                          refusal behavior.
                        </span>
                      </span>
                    </label>


                    <button
                      type="button"
                      onClick={
                        handleRun
                      }
                      disabled={
                        running
                      }
                      className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white disabled:opacity-60"
                    >
                      {
                        running
                          ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          )
                          : (
                            <Play className="h-4 w-4" />
                          )
                      }

                      {
                        running
                          ? "Running Evaluation..."
                          : "Run Evaluation"
                      }
                    </button>
                  </div>
                </div>


                <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
                  <div className="border-b border-slate-200 px-5 py-4">
                    <h2 className="font-semibold text-slate-900">
                      Run History
                    </h2>
                  </div>

                  <div className="max-h-[500px] overflow-y-auto">
                    {
                      runsLoading && (
                        <div className="p-5 text-sm text-slate-500">
                          Loading runs...
                        </div>
                      )
                    }

                    {
                      !runsLoading
                      && runs.length
                      === 0 && (
                        <div className="p-5 text-sm text-slate-500">
                          No evaluation runs yet.
                        </div>
                      )
                    }

                    {
                      runs.map(
                        (
                          run,
                        ) => (
                          <button
                            key={
                              run.id
                            }
                            type="button"
                            onClick={() =>
                              setSelectedRunId(
                                run.id,
                              )
                            }
                            className={`block w-full border-b border-slate-100 px-5 py-4 text-left ${
                              selectedRunId
                              === run.id
                                ? "bg-blue-50"
                                : "hover:bg-slate-50"
                            }`}
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="min-w-0">
                                <p className="truncate text-sm font-semibold text-slate-900">
                                  {
                                    run.name
                                  }
                                </p>

                                <p className="mt-1 text-xs text-slate-500">
                                  {
                                    run.llm_model
                                    || "No model"
                                  }{" "}
                                  · Top K{" "}
                                  {
                                    run.top_k
                                  }
                                </p>
                              </div>

                              <StatusBadge
                                status={
                                  run.status
                                }
                              />
                            </div>
                          </button>
                        ),
                      )
                    }
                  </div>
                </div>
              </div>


              <div>
                {!selectedRun && (
                  <div className="flex min-h-[400px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-white">
                    <div className="text-center">
                      <ClipboardCheck className="mx-auto h-10 w-10 text-slate-300" />

                      <p className="mt-3 text-sm font-semibold text-slate-700">
                        Select or run an evaluation
                      </p>
                    </div>
                  </div>
                )}


                {selectedRun && (
                  <div className="space-y-5">
                    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                      <div className="flex justify-between gap-3">
                        <div>
                          <h2 className="text-lg font-semibold text-slate-900">
                            {
                              selectedRun.name
                            }
                          </h2>

                          <p className="mt-1 text-sm text-slate-500">
                            {
                              selectedRun
                                .llm_model
                              || "No generator model"
                            }
                          </p>
                        </div>

                        <StatusBadge
                          status={
                            selectedRun.status
                          }
                        />
                      </div>
                    </div>


                    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                      <MetricCard
                        label="Hit@K"
                        value={
                          formatScore(
                            selectedRun
                              .hit_rate,
                          )
                        }
                      />

                      <MetricCard
                        label="MRR"
                        value={
                          formatScore(
                            selectedRun
                              .mrr,
                          )
                        }
                      />

                      <MetricCard
                        label="Faithfulness"
                        value={
                          formatScore(
                            getMetricAverage(
                              selectedRun,
                              "faithfulness",
                            ),
                          )
                        }
                      />

                      <MetricCard
                        label="Answer Relevancy"
                        value={
                          formatScore(
                            getMetricAverage(
                              selectedRun,
                              "answer_relevancy",
                            ),
                          )
                        }
                      />

                      <MetricCard
                        label="Correctness"
                        value={
                          formatScore(
                            getMetricAverage(
                              selectedRun,
                              "correctness",
                            ),
                          )
                        }
                      />

                      <MetricCard
                        label="Refusal"
                        value={
                          formatScore(
                            getMetricAverage(
                              selectedRun,
                              "refusal_correctness",
                            ),
                          )
                        }
                      />

                      <MetricCard
                        label="Pass Rate"
                        value={
                          formatScore(
                            getPassRate(
                              selectedRun,
                            ),
                          )
                        }
                      />

                      <MetricCard
                        label="Avg RAG Latency"
                        value={
                          formatMilliseconds(
                            getAverageLatency(
                              selectedRun,
                            ),
                          )
                        }
                      />
                    </div>


                    <div className="grid gap-4 md:grid-cols-2">
                      <MetricCard
                        label="Total Evaluation Tokens"
                        value={
                          formatNumber(
                            getTotalTokens(
                              selectedRun,
                            ),
                          )
                        }
                        subtitle="Generator + judge"
                      />

                      <MetricCard
                        label="Dataset Cases"
                        value={
                          formatNumber(
                            cases.length,
                          )
                        }
                      />
                    </div>


                    <EvaluationRunDetails
                      experimentId={
                        selectedRun.id
                      }
                      cases={
                        cases
                      }
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}