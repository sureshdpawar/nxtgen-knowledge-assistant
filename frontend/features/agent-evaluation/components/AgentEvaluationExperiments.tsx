"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  AlertCircle,
  CheckCircle2,
  FlaskConical,
  Play,
  RefreshCw,
} from "lucide-react";

import {
  createAgentEvalExperiment,
  getAgentEvalCases,
  getAgentEvalDatasets,
  getAgentEvalExperiments,
  getAgentEvalResults,
  runAgentEvalExperiment,
} from "@/features/agent-evaluation/api";

import type {
  AgentEvalCase,
  AgentEvalDataset,
  AgentEvalExperiment,
  AgentEvalResult,
} from "@/features/agent-evaluation/types";

import { getAgents } from "@/features/agents/api";
import type { Agent } from "@/features/agents/types";
import { useLLMProfiles } from "@/features/llm-config/hooks";


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


function statusClass(status: string) {
  if (status === "passed") {
    return "bg-emerald-50 text-emerald-700 ring-emerald-200";
  }

  if (status === "failed") {
    return "bg-red-50 text-red-700 ring-red-200";
  }

  if (status === "running") {
    return "bg-blue-50 text-blue-700 ring-blue-200";
  }

  return "bg-slate-100 text-slate-600 ring-slate-200";
}


export default function AgentEvaluationExperiments() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [datasets, setDatasets] = useState<AgentEvalDataset[]>([]);
  const [experiments, setExperiments] = useState<AgentEvalExperiment[]>([]);
  const [cases, setCases] = useState<AgentEvalCase[]>([]);
  const [results, setResults] = useState<AgentEvalResult[]>([]);

  const [selectedAgentId, setSelectedAgentId] = useState("");
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [selectedExperimentId, setSelectedExperimentId] = useState("");

  const [name, setName] = useState("");
  const [
    evaluatorLLMConfigurationId,
    setEvaluatorLLMConfigurationId,
  ] = useState("");
  const [passRate, setPassRate] = useState("0.80");
  const [outcomeThreshold, setOutcomeThreshold] = useState("0.80");
  const [toolThreshold, setToolThreshold] = useState("1.00");
  const [argumentThreshold, setArgumentThreshold] = useState("0.80");

  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const {
    data: llmProfiles = [],
    isLoading: llmProfilesLoading,
  } = useLLMProfiles();

  const activeLLMProfiles = useMemo(
    () =>
      llmProfiles.filter(
        (profile) => profile.is_active,
      ),
    [llmProfiles],
  );

  const selectedExperiment = useMemo(
    () =>
      experiments.find(
        (item) => item.id === selectedExperimentId,
      ) ?? null,
    [experiments, selectedExperimentId],
  );

  const caseById = useMemo(
    () =>
      new Map(
        cases.map((item) => [item.id, item]),
      ),
    [cases],
  );

  async function loadDatasetContext(
    agentId: string,
  ) {
    const data = await getAgentEvalDatasets(
      agentId || undefined,
    );

    setDatasets(data);

    const datasetId = data[0]?.id ?? "";
    setSelectedDatasetId(datasetId);

    if (!datasetId) {
      setExperiments([]);
      setCases([]);
      setResults([]);
      setSelectedExperimentId("");
      return;
    }

    const [experimentData, caseData] =
      await Promise.all([
        getAgentEvalExperiments(datasetId),
        getAgentEvalCases(datasetId),
      ]);

    setExperiments(experimentData);
    setCases(caseData);
    setSelectedExperimentId(
      experimentData[0]?.id ?? "",
    );
  }

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError("");

      try {
        const agentData = await getAgents();

        if (cancelled) {
          return;
        }

        setAgents(agentData);

        const agentId = agentData[0]?.id ?? "";
        setSelectedAgentId(agentId);

        if (agentId) {
          await loadDatasetContext(agentId);
        }
      } catch (err) {
        if (!cancelled) {
          setError(errorMessage(err));
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

  useEffect(() => {
    if (!selectedExperimentId) {
      setResults([]);
      return;
    }

    let cancelled = false;

    async function load() {
      try {
        const data = await getAgentEvalResults(
          selectedExperimentId,
        );

        if (!cancelled) {
          setResults(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(errorMessage(err));
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [selectedExperimentId]);

  async function handleAgentChange(
    agentId: string,
  ) {
    setSelectedAgentId(agentId);
    setSelectedExperimentId("");
    setResults([]);
    setError("");
    setMessage("");

    try {
      await loadDatasetContext(agentId);
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function handleDatasetChange(
    datasetId: string,
  ) {
    setSelectedDatasetId(datasetId);
    setSelectedExperimentId("");
    setResults([]);
    setError("");
    setMessage("");

    if (!datasetId) {
      setExperiments([]);
      setCases([]);
      return;
    }

    try {
      const [experimentData, caseData] =
        await Promise.all([
          getAgentEvalExperiments(datasetId),
          getAgentEvalCases(datasetId),
        ]);

      setExperiments(experimentData);
      setCases(caseData);
      setSelectedExperimentId(
        experimentData[0]?.id ?? "",
      );
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function refreshExperiments(
    selectId?: string,
  ) {
    if (!selectedDatasetId) {
      return;
    }

    const data = await getAgentEvalExperiments(
      selectedDatasetId,
    );

    setExperiments(data);

    if (selectId) {
      setSelectedExperimentId(selectId);
      return;
    }

    if (
      selectedExperimentId
      && data.some(
        (item) =>
          item.id === selectedExperimentId,
      )
    ) {
      return;
    }

    setSelectedExperimentId(
      data[0]?.id ?? "",
    );
  }

  async function handleCreate(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!selectedDatasetId) {
      setError("Select a dataset first.");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");

    try {
      const created =
        await createAgentEvalExperiment({
          dataset_id: selectedDatasetId,
          name: name.trim(),
          evaluator_llm_configuration_id:
            evaluatorLLMConfigurationId || null,
          pass_rate_threshold: Number(passRate),
          outcome_threshold: Number(outcomeThreshold),
          tool_threshold: Number(toolThreshold),
          argument_threshold: Number(argumentThreshold),
        });

      setName("");
      await refreshExperiments(created.id);
      setMessage("Experiment created. It is ready to run.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function handleRun() {
    if (!selectedExperiment) {
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");

    try {
      const finished =
        await runAgentEvalExperiment(
          selectedExperiment.id,
        );

      await refreshExperiments(finished.id);

      setResults(
        await getAgentEvalResults(finished.id),
      );

      setMessage(
        finished.status === "passed"
          ? "Experiment completed. Quality gate PASS."
          : "Experiment completed. Quality gate FAIL.",
      );
    } catch (err) {
      setError(errorMessage(err));

      try {
        await refreshExperiments(
          selectedExperiment.id,
        );
        setResults(
          await getAgentEvalResults(
            selectedExperiment.id,
          ),
        );
      } catch {
        // Preserve the original run error.
      }
    } finally {
      setBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        Loading experiments...
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

      {message && (
        <div className="flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">
          <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      <div className="grid gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-2">
        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Agent
          </label>
          <select
            value={selectedAgentId}
            onChange={(event) =>
              void handleAgentChange(event.target.value)
            }
            className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
          >
            {agents.map((agent) => (
              <option key={agent.id} value={agent.id}>
                {agent.name} · {agent.status}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Regression dataset
          </label>
          <select
            value={selectedDatasetId}
            onChange={(event) =>
              void handleDatasetChange(event.target.value)
            }
            className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm"
          >
            {datasets.length === 0 && (
              <option value="">No datasets available</option>
            )}
            {datasets.map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.name} · {dataset.version}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[23rem_minmax(0,1fr)]">
        <div className="space-y-4">
          <form
            onSubmit={handleCreate}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center gap-2">
              <FlaskConical className="h-4 w-4 text-blue-600" />
              <h2 className="font-semibold text-slate-900">
                New experiment
              </h2>
            </div>

            <div className="mt-4 space-y-3">
              <input
                required
                value={name}
                onChange={(event) =>
                  setName(event.target.value)
                }
                placeholder="Experiment name"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm"
              />

              <label className="block">
                <span className="text-xs font-semibold text-slate-600">
                  Evaluator / Judge LLM
                </span>
                <select
                  value={evaluatorLLMConfigurationId}
                  onChange={(event) =>
                    setEvaluatorLLMConfigurationId(
                      event.target.value,
                    )
                  }
                  disabled={llmProfilesLoading}
                  className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm disabled:opacity-50"
                >
                  <option value="">
                    Tenant default
                  </option>
                  {activeLLMProfiles.map((profile) => (
                    <option
                      key={profile.id}
                      value={profile.id}
                    >
                      {profile.name} · {profile.model_name}
                      {profile.is_default ? " (default)" : ""}
                    </option>
                  ))}
                </select>
                <span className="mt-1 block text-[11px] leading-4 text-slate-500">
                  Independent from the agent runtime model.
                </span>
              </label>

              <div className="grid grid-cols-2 gap-3">
                <Threshold
                  label="Pass rate"
                  value={passRate}
                  onChange={setPassRate}
                />
                <Threshold
                  label="Outcome"
                  value={outcomeThreshold}
                  onChange={setOutcomeThreshold}
                />
                <Threshold
                  label="Tool"
                  value={toolThreshold}
                  onChange={setToolThreshold}
                />
                <Threshold
                  label="Arguments"
                  value={argumentThreshold}
                  onChange={setArgumentThreshold}
                />
              </div>

              <button
                type="submit"
                disabled={
                  busy
                  || !selectedDatasetId
                  || !name.trim()
                }
                className="w-full rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
              >
                Create experiment
              </button>
            </div>
          </form>

          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div>
                <h2 className="font-semibold text-slate-900">
                  Experiments
                </h2>
                <p className="text-xs text-slate-500">
                  {experiments.length} run definition
                  {experiments.length === 1 ? "" : "s"}
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  void refreshExperiments()
                }
                className="rounded-lg p-2 text-slate-500 hover:bg-slate-100"
                aria-label="Refresh experiments"
              >
                <RefreshCw className="h-4 w-4" />
              </button>
            </div>

            <div className="max-h-[32rem] overflow-y-auto p-2">
              {experiments.length === 0 ? (
                <p className="p-4 text-sm text-slate-500">
                  No experiments for this dataset yet.
                </p>
              ) : (
                <div className="space-y-1">
                  {experiments.map((item) => (
                    <button
                      type="button"
                      key={item.id}
                      onClick={() =>
                        setSelectedExperimentId(item.id)
                      }
                      className={`w-full rounded-lg p-3 text-left ${
                        item.id === selectedExperimentId
                          ? "bg-blue-50 ring-1 ring-blue-200"
                          : "hover:bg-slate-50"
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="truncate text-sm font-semibold text-slate-900">
                            {item.name}
                          </p>
                          <p className="mt-1 text-xs text-slate-500">
                            Pass rate: {percent(item.pass_rate)}
                          </p>
                        </div>

                        <span
                          className={`rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase ring-1 ${statusClass(item.status)}`}
                        >
                          {item.status}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="min-w-0 space-y-4">
          {!selectedExperiment ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">
              Create or select an experiment.
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">
                      {selectedExperiment.name}
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                      Judge: {selectedExperiment.judge_model ?? "Tenant profile"}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => void handleRun()}
                    disabled={
                      busy
                      || selectedExperiment.status === "running"
                      || selectedExperiment.status === "passed"
                      || (
                        selectedExperiment.status === "failed"
                        && selectedExperiment.case_count > 0
                      )
                    }
                    className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Play className="h-4 w-4" />
                    {busy ? "Running..." : "Run experiment"}
                  </button>
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                  <MetricCard
                    label="Pass rate"
                    value={percent(selectedExperiment.pass_rate)}
                  />
                  <MetricCard
                    label="Outcome"
                    value={score(selectedExperiment.outcome_correctness)}
                  />
                  <MetricCard
                    label="Tool"
                    value={score(selectedExperiment.tool_correctness)}
                  />
                  <MetricCard
                    label="Arguments"
                    value={score(selectedExperiment.argument_correctness)}
                  />
                </div>

                <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
                  <span>
                    Cases: {selectedExperiment.case_count}
                  </span>
                  <span>
                    Passed: {selectedExperiment.passed_count}
                  </span>
                  <span>
                    Required pass rate:{" "}
                    {percent(selectedExperiment.pass_rate_threshold)}
                  </span>
                </div>
              </div>

              <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-200 px-5 py-4">
                  <h3 className="font-semibold text-slate-900">
                    Case results
                  </h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Actual agent behavior scored against the regression dataset.
                  </p>
                </div>

                {results.length === 0 ? (
                  <div className="p-8 text-center text-sm text-slate-500">
                    No results yet. Run the experiment to execute the real agent workflow.
                  </div>
                ) : (
                  <div className="divide-y divide-slate-200">
                    {results.map((result) => {
                      const evalCase =
                        caseById.get(result.eval_case_id);

                      return (
                        <article
                          key={result.id}
                          className="p-5"
                        >
                          <div className="flex flex-wrap items-start justify-between gap-3">
                            <div>
                              <h4 className="font-semibold text-slate-900">
                                {evalCase?.name ?? result.eval_case_id}
                              </h4>
                              {result.agent_run_id && (
                                <p className="mt-1 break-all text-[11px] text-slate-400">
                                  Agent run: {result.agent_run_id}
                                </p>
                              )}
                            </div>

                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${
                                result.passed === true
                                  ? "bg-emerald-50 text-emerald-700 ring-emerald-200"
                                  : result.passed === false
                                    ? "bg-red-50 text-red-700 ring-red-200"
                                    : "bg-slate-100 text-slate-600 ring-slate-200"
                              }`}
                            >
                              {result.passed === true
                                ? "PASS"
                                : result.passed === false
                                  ? "FAIL"
                                  : "PENDING"}
                            </span>
                          </div>

                          <div className="mt-4 grid gap-3 sm:grid-cols-3">
                            <MetricCard
                              label="Outcome"
                              value={score(result.outcome_correctness)}
                            />
                            <MetricCard
                              label="Tool"
                              value={score(result.tool_correctness)}
                            />
                            <MetricCard
                              label="Arguments"
                              value={score(result.argument_correctness)}
                            />
                          </div>

                          <div className="mt-4 rounded-lg bg-slate-50 p-3">
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                              Actual answer
                            </p>
                            <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                              {result.actual_answer || "No answer recorded."}
                            </p>
                          </div>

                          <div className="mt-3 flex flex-wrap gap-2">
                            {result.tools_called.map(
                              (tool, index) => (
                                <span
                                  key={`${tool.name ?? "tool"}-${index}`}
                                  className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700 ring-1 ring-blue-200"
                                >
                                  Tool: {tool.name ?? "unknown"}
                                </span>
                              ),
                            )}

                            {result.forbidden_tool_violations.map(
                              (tool) => (
                                <span
                                  key={`violation-${tool}`}
                                  className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700 ring-1 ring-red-200"
                                >
                                  Forbidden tool executed: {tool}
                                </span>
                              ),
                            )}
                          </div>
                        </article>
                      );
                    })}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}


function Threshold({
  label,
  value,
  onChange,
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="text-xs font-semibold text-slate-600">
        {label}
      </span>
      <input
        type="number"
        min="0"
        max="1"
        step="0.01"
        required
        value={value}
        onChange={(event) =>
          onChange(event.target.value)
        }
        className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
    </label>
  );
}


function MetricCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>
      <p className="mt-1 text-lg font-semibold text-slate-900">
        {value}
      </p>
    </div>
  );
}
