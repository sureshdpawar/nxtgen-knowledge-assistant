"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  ArrowRight,
  GitCompareArrows,
  Minus,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

import {
  compareAgentEvalExperiments,
  getAgentEvalDatasets,
  getAgentEvalExperiments,
} from "@/features/agent-evaluation/api";

import type {
  AgentEvalDataset,
  AgentEvalExperiment,
  AgentEvalExperimentComparison,
  AgentEvalMetricDelta,
} from "@/features/agent-evaluation/types";

import { getAgents } from "@/features/agents/api";
import type { Agent } from "@/features/agents/types";


function errorMessage(error: unknown) {
  if (
    typeof error === "object"
    && error !== null
    && "response" in error
  ) {
    const response = (
      error as {
        response?: {
          data?: {
            detail?: string;
          };
        };
      }
    ).response;

    if (
      response?.data?.detail
      && typeof response.data.detail === "string"
    ) {
      return response.data.detail;
    }
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong.";
}


function score(value: number | null) {
  return value === null
    ? "—"
    : value.toFixed(3);
}


function percent(value: number | null) {
  return value === null
    ? "—"
    : `${(value * 100).toFixed(1)}%`;
}


function signed(
  value: number | null,
  asPercent = false,
) {
  if (value === null) {
    return "—";
  }

  if (asPercent) {
    const p = value * 100;
    return `${p >= 0 ? "+" : ""}${p.toFixed(1)} pp`;
  }

  return `${value >= 0 ? "+" : ""}${value.toFixed(3)}`;
}


function completed(
  experiment: AgentEvalExperiment,
) {
  return (
    experiment.status === "passed"
    || experiment.status === "failed"
  );
}


function classificationClass(
  value: string,
) {
  if (value === "regression") {
    return "bg-red-50 text-red-700 ring-red-200";
  }

  if (value === "improvement") {
    return "bg-emerald-50 text-emerald-700 ring-emerald-200";
  }

  if (value === "missing_result") {
    return "bg-amber-50 text-amber-700 ring-amber-200";
  }

  return "bg-slate-100 text-slate-600 ring-slate-200";
}


export default function AgentEvaluationCompare() {
  const [agents, setAgents] =
    useState<Agent[]>([]);
  const [datasets, setDatasets] =
    useState<AgentEvalDataset[]>([]);
  const [experiments, setExperiments] =
    useState<AgentEvalExperiment[]>([]);

  const [selectedAgentId, setSelectedAgentId] =
    useState("");
  const [selectedDatasetId, setSelectedDatasetId] =
    useState("");
  const [baselineId, setBaselineId] =
    useState("");
  const [candidateId, setCandidateId] =
    useState("");

  const [comparison, setComparison] =
    useState<AgentEvalExperimentComparison | null>(
      null,
    );

  const [loading, setLoading] =
    useState(true);
  const [comparing, setComparing] =
    useState(false);
  const [error, setError] =
    useState("");

  const comparableExperiments =
    useMemo(
      () =>
        experiments.filter(completed),
      [experiments],
    );

  async function loadForAgent(
    agentId: string,
  ) {
    const data =
      await getAgentEvalDatasets(
        agentId || undefined,
      );

    setDatasets(data);

    const datasetId =
      data[0]?.id ?? "";

    setSelectedDatasetId(datasetId);
    setComparison(null);

    if (!datasetId) {
      setExperiments([]);
      setBaselineId("");
      setCandidateId("");
      return;
    }

    await loadForDataset(datasetId);
  }

  async function loadForDataset(
    datasetId: string,
  ) {
    const data =
      await getAgentEvalExperiments(
        datasetId,
      );

    setExperiments(data);
    setComparison(null);

    const comparable =
      data.filter(completed);

    setBaselineId(
      comparable.length >= 2
        ? comparable[1].id
        : comparable[0]?.id ?? "",
    );

    setCandidateId(
      comparable[0]?.id ?? "",
    );
  }

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError("");

      try {
        const agentData =
          await getAgents();

        if (cancelled) {
          return;
        }

        setAgents(agentData);

        const agentId =
          agentData[0]?.id ?? "";

        setSelectedAgentId(agentId);

        if (agentId) {
          await loadForAgent(agentId);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            errorMessage(err),
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  async function handleAgentChange(
    agentId: string,
  ) {
    setSelectedAgentId(agentId);
    setError("");

    try {
      await loadForAgent(agentId);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function handleDatasetChange(
    datasetId: string,
  ) {
    setSelectedDatasetId(datasetId);
    setError("");

    if (!datasetId) {
      setExperiments([]);
      setBaselineId("");
      setCandidateId("");
      setComparison(null);
      return;
    }

    try {
      await loadForDataset(datasetId);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function handleCompare() {
    if (!baselineId || !candidateId) {
      setError(
        "Choose both a baseline and a candidate experiment.",
      );
      return;
    }

    if (baselineId === candidateId) {
      setError(
        "Baseline and candidate experiments must be different.",
      );
      return;
    }

    setComparing(true);
    setError("");

    try {
      const data =
        await compareAgentEvalExperiments({
          baseline_experiment_id:
            baselineId,
          candidate_experiment_id:
            candidateId,
        });

      setComparison(data);
    } catch (err) {
      setError(errorMessage(err));
      setComparison(null);
    } finally {
      setComparing(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        Loading comparison workspace...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <GitCompareArrows className="h-5 w-5 text-blue-600" />
          <div>
            <h2 className="font-semibold text-slate-900">
              Compare experiments
            </h2>
            <p className="mt-1 text-xs text-slate-500">
              Compare two fully evaluated runs over the same regression dataset.
            </p>
          </div>
        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <SelectField
            label="Agent"
            value={selectedAgentId}
            onChange={(value) =>
              void handleAgentChange(
                value,
              )
            }
          >
            {agents.map(
              (agent) => (
                <option
                  key={agent.id}
                  value={agent.id}
                >
                  {agent.name} · {agent.status}
                </option>
              ),
            )}
          </SelectField>

          <SelectField
            label="Regression dataset"
            value={selectedDatasetId}
            onChange={(value) =>
              void handleDatasetChange(
                value,
              )
            }
          >
            {datasets.length === 0 && (
              <option value="">
                No datasets available
              </option>
            )}

            {datasets.map(
              (dataset) => (
                <option
                  key={dataset.id}
                  value={dataset.id}
                >
                  {dataset.name} · {dataset.version}
                </option>
              ),
            )}
          </SelectField>

          <SelectField
            label="Baseline"
            value={baselineId}
            onChange={(value) => {
              setBaselineId(value);
              setComparison(null);
            }}
          >
            {comparableExperiments.length === 0 && (
              <option value="">
                No completed experiments
              </option>
            )}

            {comparableExperiments.map(
              (experiment) => (
                <option
                  key={experiment.id}
                  value={experiment.id}
                >
                  {experiment.name} · {experiment.status}
                </option>
              ),
            )}
          </SelectField>

          <SelectField
            label="Candidate"
            value={candidateId}
            onChange={(value) => {
              setCandidateId(value);
              setComparison(null);
            }}
          >
            {comparableExperiments.length === 0 && (
              <option value="">
                No completed experiments
              </option>
            )}

            {comparableExperiments.map(
              (experiment) => (
                <option
                  key={experiment.id}
                  value={experiment.id}
                >
                  {experiment.name} · {experiment.status}
                </option>
              ),
            )}
          </SelectField>
        </div>

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-slate-500">
            Comparison uses persisted evaluation results only; it does not run the agent or invoke DeepEval again.
          </p>

          <button
            type="button"
            onClick={() =>
              void handleCompare()
            }
            disabled={
              comparing
              || !baselineId
              || !candidateId
              || baselineId === candidateId
            }
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <GitCompareArrows className="h-4 w-4" />
            {comparing
              ? "Comparing..."
              : "Compare"}
          </button>
        </div>
      </section>

      {!comparison ? (
        <section className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
          <GitCompareArrows className="mx-auto h-8 w-8 text-slate-400" />
          <p className="mt-3 font-medium text-slate-800">
            Choose a baseline and candidate
          </p>
          <p className="mt-1 text-sm text-slate-500">
            Two completed experiments are required to identify regressions and improvements.
          </p>
        </section>
      ) : (
        <>
          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <MetricDeltaCard
              label="Pass rate"
              metric={
                comparison.pass_rate
              }
              asPercent
            />
            <MetricDeltaCard
              label="Outcome"
              metric={
                comparison.outcome_correctness
              }
            />
            <MetricDeltaCard
              label="Tool"
              metric={
                comparison.tool_correctness
              }
            />
            <MetricDeltaCard
              label="Arguments"
              metric={
                comparison.argument_correctness
              }
            />
          </section>

          <section className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <SummaryCard
              label="Regressions"
              value={
                comparison.regressions
              }
              tone="regression"
            />
            <SummaryCard
              label="Improvements"
              value={
                comparison.improvements
              }
              tone="improvement"
            />
            <SummaryCard
              label="Unchanged"
              value={
                comparison.unchanged
              }
              tone="neutral"
            />
            <SummaryCard
              label="Missing results"
              value={
                comparison.missing_results
              }
              tone="warning"
            />
          </section>

          <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-200 px-5 py-4">
              <div className="flex flex-wrap items-center gap-2 text-sm">
                <span className="font-semibold text-slate-900">
                  {
                    comparison
                      .baseline_experiment
                      .name
                  }
                </span>
                <ArrowRight className="h-4 w-4 text-slate-400" />
                <span className="font-semibold text-slate-900">
                  {
                    comparison
                      .candidate_experiment
                      .name
                  }
                </span>
              </div>

              <p className="mt-1 text-xs text-slate-500">
                PASS → FAIL is a regression. FAIL → PASS is an improvement.
              </p>
            </div>

            {comparison.cases.length === 0 ? (
              <div className="p-8 text-center text-sm text-slate-500">
                No comparable case results were returned.
              </div>
            ) : (
              <div className="divide-y divide-slate-200">
                {comparison.cases.map(
                  (item) => (
                    <article
                      key={item.eval_case_id}
                      className="p-5"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <h3 className="font-semibold text-slate-900">
                            {item.case_name}
                          </h3>

                          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                            <PassState
                              label="Baseline"
                              passed={
                                item.baseline_passed
                              }
                            />
                            <ArrowRight className="h-3.5 w-3.5" />
                            <PassState
                              label="Candidate"
                              passed={
                                item.candidate_passed
                              }
                            />
                          </div>
                        </div>

                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold uppercase ring-1 ${classificationClass(
                            item.classification,
                          )}`}
                        >
                          {item.classification.replace(
                            "_",
                            " ",
                          )}
                        </span>
                      </div>

                      <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        <MetricDeltaCard
                          label="Outcome"
                          metric={
                            item.outcome_correctness
                          }
                          compact
                        />
                        <MetricDeltaCard
                          label="Tool"
                          metric={
                            item.tool_correctness
                          }
                          compact
                        />
                        <MetricDeltaCard
                          label="Arguments"
                          metric={
                            item.argument_correctness
                          }
                          compact
                        />
                      </div>

                      {(
                        item.baseline_forbidden_tool_violations.length > 0
                        || item.candidate_forbidden_tool_violations.length > 0
                      ) && (
                        <div className="mt-4 grid gap-3 md:grid-cols-2">
                          <ViolationBox
                            label="Baseline violations"
                            items={
                              item.baseline_forbidden_tool_violations
                            }
                          />
                          <ViolationBox
                            label="Candidate violations"
                            items={
                              item.candidate_forbidden_tool_violations
                            }
                          />
                        </div>
                      )}
                    </article>
                  ),
                )}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}


function SelectField({
  label,
  value,
  onChange,
  children,
}: {
  label: string;
  value: string;
  onChange: (
    value: string,
  ) => void;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </span>

      <select
        value={value}
        onChange={(event) =>
          onChange(
            event.target.value,
          )
        }
        className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      >
        {children}
      </select>
    </label>
  );
}


function MetricDeltaCard({
  label,
  metric,
  asPercent = false,
  compact = false,
}: {
  label: string;
  metric: AgentEvalMetricDelta;
  asPercent?: boolean;
  compact?: boolean;
}) {
  const deltaPositive =
    metric.delta !== null
    && metric.delta > 0;

  const deltaNegative =
    metric.delta !== null
    && metric.delta < 0;

  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white ${
        compact
          ? "p-3"
          : "p-4 shadow-sm"
      }`}
    >
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <div className="mt-2 flex items-center gap-2 text-sm text-slate-700">
        <span>
          {asPercent
            ? percent(metric.baseline)
            : score(metric.baseline)}
        </span>

        <ArrowRight className="h-3.5 w-3.5 text-slate-400" />

        <span className="font-semibold text-slate-900">
          {asPercent
            ? percent(metric.candidate)
            : score(metric.candidate)}
        </span>
      </div>

      <div
        className={`mt-2 inline-flex items-center gap-1 text-xs font-semibold ${
          deltaPositive
            ? "text-emerald-700"
            : deltaNegative
              ? "text-red-700"
              : "text-slate-500"
        }`}
      >
        {deltaPositive ? (
          <TrendingUp className="h-3.5 w-3.5" />
        ) : deltaNegative ? (
          <TrendingDown className="h-3.5 w-3.5" />
        ) : (
          <Minus className="h-3.5 w-3.5" />
        )}

        {signed(
          metric.delta,
          asPercent,
        )}
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
    | "regression"
    | "improvement"
    | "warning"
    | "neutral";
}) {
  const cls =
    tone === "regression"
      ? "border-red-200 bg-red-50 text-red-800"
      : tone === "improvement"
        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
        : tone === "warning"
          ? "border-amber-200 bg-amber-50 text-amber-800"
          : "border-slate-200 bg-white text-slate-800";

  return (
    <div
      className={`rounded-xl border p-4 shadow-sm ${cls}`}
    >
      <p className="text-xs font-semibold uppercase tracking-wide opacity-70">
        {label}
      </p>
      <p className="mt-1 text-2xl font-semibold">
        {value}
      </p>
    </div>
  );
}


function PassState({
  label,
  passed,
}: {
  label: string;
  passed: boolean | null;
}) {
  const value =
    passed === true
      ? "PASS"
      : passed === false
        ? "FAIL"
        : "MISSING";

  return (
    <span>
      {label}:{" "}
      <strong
        className={
          passed === true
            ? "text-emerald-700"
            : passed === false
              ? "text-red-700"
              : "text-amber-700"
        }
      >
        {value}
      </strong>
    </span>
  );
}


function ViolationBox({
  label,
  items,
}: {
  label: string;
  items: string[];
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-3">
      <p className="text-xs font-semibold text-red-800">
        {label}
      </p>

      {items.length === 0 ? (
        <p className="mt-1 text-xs text-red-700/70">
          None
        </p>
      ) : (
        <div className="mt-2 flex flex-wrap gap-2">
          {items.map(
            (item) => (
              <span
                key={item}
                className="rounded-full bg-white px-2 py-0.5 text-xs font-semibold text-red-700 ring-1 ring-red-200"
              >
                {item}
              </span>
            ),
          )}
        </div>
      )}
    </div>
  );
}
