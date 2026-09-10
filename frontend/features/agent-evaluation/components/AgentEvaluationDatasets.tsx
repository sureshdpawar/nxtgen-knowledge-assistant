"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  AlertCircle,
  Bot,
  CheckCircle2,
  FileUp,
  FlaskConical,
  Plus,
  Trash2,
} from "lucide-react";

import {
  createAgentEvalCase,
  createAgentEvalDataset,
  deleteAgentEvalCase,
  getAgentEvalCases,
  getAgentEvalDatasets,
  importAgentEvalDataset,
} from "@/features/agent-evaluation/api";

import type {
  AgentEvalCase,
  AgentEvalDataset,
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


function formatDate(value: string) {
  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(new Date(value));
}


function parseCsv(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}


export default function AgentEvaluationDatasets() {
  const fileInputRef =
    useRef<HTMLInputElement | null>(null);

  const [agents, setAgents] =
    useState<Agent[]>([]);
  const [datasets, setDatasets] =
    useState<AgentEvalDataset[]>([]);
  const [cases, setCases] =
    useState<AgentEvalCase[]>([]);

  const [selectedAgentId, setSelectedAgentId] =
    useState("");
  const [selectedDatasetId, setSelectedDatasetId] =
    useState("");

  const [loading, setLoading] =
    useState(true);
  const [loadingCases, setLoadingCases] =
    useState(false);
  const [saving, setSaving] =
    useState(false);
  const [message, setMessage] =
    useState("");
  const [error, setError] =
    useState("");

  const [datasetName, setDatasetName] =
    useState("");
  const [datasetVersion, setDatasetVersion] =
    useState("v1");
  const [datasetDescription, setDatasetDescription] =
    useState("");

  const [caseName, setCaseName] =
    useState("");
  const [caseInput, setCaseInput] =
    useState("");
  const [expectedOutcome, setExpectedOutcome] =
    useState("");
  const [expectedToolNames, setExpectedToolNames] =
    useState("");
  const [forbiddenToolNames, setForbiddenToolNames] =
    useState("");

  const selectedDataset = useMemo(
    () =>
      datasets.find(
        (dataset) =>
          dataset.id === selectedDatasetId,
      ) ?? null,
    [datasets, selectedDatasetId],
  );

  const selectedAgent = useMemo(
    () =>
      agents.find(
        (agent) =>
          agent.id === selectedAgentId,
      ) ?? null,
    [agents, selectedAgentId],
  );

  async function loadDatasets(
    agentId?: string,
    preserveDataset = false,
  ) {
    const data = await getAgentEvalDatasets(
      agentId || undefined,
    );

    setDatasets(data);

    if (
      preserveDataset
      && data.some(
        (item) =>
          item.id === selectedDatasetId,
      )
    ) {
      return;
    }

    setSelectedDatasetId(
      data[0]?.id ?? "",
    );
  }

  async function loadInitial() {
    setLoading(true);
    setError("");

    try {
      const agentData = await getAgents();
      setAgents(agentData);

      const firstAgentId =
        agentData[0]?.id ?? "";

      setSelectedAgentId(firstAgentId);
      await loadDatasets(
        firstAgentId || undefined,
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadInitial();
  }, []);

  useEffect(() => {
    if (!selectedDatasetId) {
      setCases([]);
      return;
    }

    let cancelled = false;

    async function load() {
      setLoadingCases(true);
      setError("");

      try {
        const data = await getAgentEvalCases(
          selectedDatasetId,
        );

        if (!cancelled) {
          setCases(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(errorMessage(err));
        }
      } finally {
        if (!cancelled) {
          setLoadingCases(false);
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [selectedDatasetId]);

  async function handleAgentChange(
    agentId: string,
  ) {
    setSelectedAgentId(agentId);
    setSelectedDatasetId("");
    setCases([]);
    setError("");
    setMessage("");

    try {
      await loadDatasets(
        agentId || undefined,
      );
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function handleCreateDataset(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!selectedAgentId) {
      setError(
        "Select an agent before creating a dataset.",
      );
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const created =
        await createAgentEvalDataset({
          agent_id: selectedAgentId,
          name: datasetName.trim(),
          version:
            datasetVersion.trim() || "v1",
          description:
            datasetDescription.trim()
            || null,
        });

      setDatasetName("");
      setDatasetVersion("v1");
      setDatasetDescription("");

      await loadDatasets(
        selectedAgentId,
      );

      setSelectedDatasetId(created.id);
      setMessage(
        "Evaluation dataset created.",
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleImportFile(
    file: File | undefined,
  ) {
    if (!file) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const imported =
        await importAgentEvalDataset(file);

      const importedAgentId =
        imported.dataset.agent_id;

      setSelectedAgentId(importedAgentId);

      const agentExists = agents.some(
        (agent) =>
          agent.id === importedAgentId,
      );

      if (!agentExists) {
        const refreshedAgents =
          await getAgents();
        setAgents(refreshedAgents);
      }

      await loadDatasets(
        importedAgentId,
      );

      setSelectedDatasetId(
        imported.dataset.id,
      );

      setMessage(
        `Imported ${imported.case_count} evaluation case${
          imported.case_count === 1
            ? ""
            : "s"
        }.`,
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  async function handleCreateCase(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!selectedDatasetId) {
      setError(
        "Select a dataset before creating a case.",
      );
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await createAgentEvalCase(
        selectedDatasetId,
        {
          name: caseName.trim(),
          input: caseInput.trim(),
          expected_outcome:
            expectedOutcome.trim(),
          expected_tools:
            parseCsv(
              expectedToolNames,
            ).map((name) => ({
              name,
              input_parameters: {},
            })),
          forbidden_tools:
            parseCsv(
              forbiddenToolNames,
            ),
          enabled: true,
        },
      );

      setCaseName("");
      setCaseInput("");
      setExpectedOutcome("");
      setExpectedToolNames("");
      setForbiddenToolNames("");

      setCases(
        await getAgentEvalCases(
          selectedDatasetId,
        ),
      );

      setMessage(
        "Evaluation case created.",
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteCase(
    item: AgentEvalCase,
  ) {
    const confirmed = window.confirm(
      `Delete evaluation case "${item.name}"?`,
    );

    if (!confirmed) {
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      await deleteAgentEvalCase(
        item.dataset_id,
        item.id,
      );

      setCases(
        await getAgentEvalCases(
          item.dataset_id,
        ),
      );

      setMessage(
        "Evaluation case deleted.",
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-600">
        Loading Agent Evaluation...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <FlaskConical className="h-6 w-6 text-blue-600" />
          <h1 className="text-2xl font-semibold text-slate-900">
            Agent Evaluation
          </h1>
        </div>

        <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
          Build tenant-owned regression datasets for governed agents.
          Curate scenarios manually, import JSON datasets, and preserve
          production provenance when runs are promoted into evaluation.
        </p>
      </div>

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

      <div className="grid gap-6 xl:grid-cols-[22rem_minmax(0,1fr)]">
        <section className="space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
            <label className="block text-xs font-semibold uppercase tracking-wide text-slate-500">
              Agent
            </label>

            <select
              value={selectedAgentId}
              onChange={(event) =>
                void handleAgentChange(
                  event.target.value,
                )
              }
              className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >
              {agents.length === 0 && (
                <option value="">
                  No agents available
                </option>
              )}

              {agents.map((agent) => (
                <option
                  key={agent.id}
                  value={agent.id}
                >
                  {agent.name} · {agent.status}
                </option>
              ))}
            </select>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
            <div className="flex items-center justify-between border-b border-slate-200 px-4 py-3">
              <div>
                <h2 className="font-semibold text-slate-900">
                  Datasets
                </h2>
                <p className="text-xs text-slate-500">
                  {datasets.length} dataset
                  {datasets.length === 1
                    ? ""
                    : "s"}
                </p>
              </div>

              <button
                type="button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                disabled={saving}
                className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 px-2.5 py-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 disabled:opacity-50"
              >
                <FileUp className="h-4 w-4" />
                Import
              </button>

              <input
                ref={fileInputRef}
                type="file"
                accept=".json,application/json"
                className="hidden"
                onChange={(event) =>
                  void handleImportFile(
                    event.target.files?.[0],
                  )
                }
              />
            </div>

            <div className="max-h-[26rem] overflow-y-auto p-2">
              {datasets.length === 0 ? (
                <div className="p-4 text-sm text-slate-500">
                  No Agent Evaluation datasets for this agent yet.
                </div>
              ) : (
                <div className="space-y-1">
                  {datasets.map((dataset) => {
                    const active =
                      dataset.id
                      === selectedDatasetId;

                    return (
                      <button
                        key={dataset.id}
                        type="button"
                        onClick={() =>
                          setSelectedDatasetId(
                            dataset.id,
                          )
                        }
                        className={`w-full rounded-lg px-3 py-3 text-left transition ${
                          active
                            ? "bg-blue-50 ring-1 ring-blue-200"
                            : "hover:bg-slate-50"
                        }`}
                      >
                        <div className="flex items-start gap-2">
                          <Bot className={`mt-0.5 h-4 w-4 shrink-0 ${
                            active
                              ? "text-blue-600"
                              : "text-slate-400"
                          }`} />

                          <div className="min-w-0">
                            <p className="truncate text-sm font-semibold text-slate-900">
                              {dataset.name}
                            </p>
                            <p className="mt-0.5 text-xs text-slate-500">
                              {dataset.version}
                            </p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          </div>

          <form
            onSubmit={handleCreateDataset}
            className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
          >
            <div className="flex items-center gap-2">
              <Plus className="h-4 w-4 text-blue-600" />
              <h2 className="font-semibold text-slate-900">
                New dataset
              </h2>
            </div>

            <div className="mt-4 space-y-3">
              <input
                required
                value={datasetName}
                onChange={(event) =>
                  setDatasetName(
                    event.target.value,
                  )
                }
                placeholder="Dataset name"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <input
                required
                value={datasetVersion}
                onChange={(event) =>
                  setDatasetVersion(
                    event.target.value,
                  )
                }
                placeholder="Version"
                className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <textarea
                value={datasetDescription}
                onChange={(event) =>
                  setDatasetDescription(
                    event.target.value,
                  )
                }
                rows={3}
                placeholder="Description (optional)"
                className="w-full resize-y rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <button
                type="submit"
                disabled={
                  saving
                  || !selectedAgentId
                  || !datasetName.trim()
                }
                className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-3 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Plus className="h-4 w-4" />
                Create dataset
              </button>
            </div>
          </form>
        </section>

        <section className="min-w-0 space-y-4">
          {!selectedDataset ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center">
              <FlaskConical className="mx-auto h-8 w-8 text-slate-400" />
              <p className="mt-3 font-medium text-slate-800">
                Select or create a dataset
              </p>
              <p className="mt-1 text-sm text-slate-500">
                Evaluation cases will appear here.
              </p>
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-900">
                      {selectedDataset.name}
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                      {selectedAgent?.name ?? "Agent"}
                      {" · "}
                      {selectedDataset.version}
                    </p>
                  </div>

                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-600">
                    {cases.length} case
                    {cases.length === 1
                      ? ""
                      : "s"}
                  </span>
                </div>

                {selectedDataset.description && (
                  <p className="mt-3 text-sm leading-6 text-slate-600">
                    {selectedDataset.description}
                  </p>
                )}
              </div>

              <form
                onSubmit={handleCreateCase}
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
              >
                <div className="flex items-center gap-2">
                  <Plus className="h-4 w-4 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">
                    Add regression case
                  </h3>
                </div>

                <div className="mt-4 grid gap-3 lg:grid-cols-2">
                  <div className="lg:col-span-2">
                    <label className="text-xs font-semibold text-slate-600">
                      Case name
                    </label>
                    <input
                      required
                      value={caseName}
                      onChange={(event) =>
                        setCaseName(
                          event.target.value,
                        )
                      }
                      className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-600">
                      Agent input
                    </label>
                    <textarea
                      required
                      rows={5}
                      value={caseInput}
                      onChange={(event) =>
                        setCaseInput(
                          event.target.value,
                        )
                      }
                      className="mt-1.5 w-full resize-y rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-600">
                      Expected outcome
                    </label>
                    <textarea
                      required
                      rows={5}
                      value={expectedOutcome}
                      onChange={(event) =>
                        setExpectedOutcome(
                          event.target.value,
                        )
                      }
                      className="mt-1.5 w-full resize-y rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-600">
                      Expected tools
                    </label>
                    <input
                      value={expectedToolNames}
                      onChange={(event) =>
                        setExpectedToolNames(
                          event.target.value,
                        )
                      }
                      placeholder="create_enquiry, ..."
                      className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                    <p className="mt-1 text-xs text-slate-400">
                      Comma-separated. Arguments can be refined through JSON import.
                    </p>
                  </div>

                  <div>
                    <label className="text-xs font-semibold text-slate-600">
                      Forbidden tools
                    </label>
                    <input
                      value={forbiddenToolNames}
                      onChange={(event) =>
                        setForbiddenToolNames(
                          event.target.value,
                        )
                      }
                      placeholder="delete_all, ..."
                      className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                    />
                    <p className="mt-1 text-xs text-slate-400">
                      Comma-separated deterministic governance checks.
                    </p>
                  </div>
                </div>

                <div className="mt-4 flex justify-end">
                  <button
                    type="submit"
                    disabled={
                      saving
                      || !caseName.trim()
                      || !caseInput.trim()
                      || !expectedOutcome.trim()
                    }
                    className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Plus className="h-4 w-4" />
                    Add case
                  </button>
                </div>
              </form>

              <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
                <div className="border-b border-slate-200 px-5 py-4">
                  <h3 className="font-semibold text-slate-900">
                    Regression cases
                  </h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Curated scenarios are replayed by future Agent Experiments.
                  </p>
                </div>

                {loadingCases ? (
                  <div className="p-5 text-sm text-slate-500">
                    Loading cases...
                  </div>
                ) : cases.length === 0 ? (
                  <div className="p-8 text-center text-sm text-slate-500">
                    No evaluation cases yet.
                  </div>
                ) : (
                  <div className="divide-y divide-slate-200">
                    {cases.map((item) => (
                      <article
                        key={item.id}
                        className="p-5"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="min-w-0">
                            <div className="flex flex-wrap items-center gap-2">
                              <h4 className="font-semibold text-slate-900">
                                {item.name}
                              </h4>

                              {item.source_agent_run_id && (
                                <span className="rounded-full bg-violet-50 px-2 py-0.5 text-[11px] font-semibold text-violet-700 ring-1 ring-violet-200">
                                  From Agent Run
                                </span>
                              )}

                              {!item.enabled && (
                                <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-500">
                                  Disabled
                                </span>
                              )}
                            </div>

                            <p className="mt-1 text-xs text-slate-400">
                              Added {formatDate(item.created_at)}
                            </p>
                          </div>

                          <button
                            type="button"
                            onClick={() =>
                              void handleDeleteCase(
                                item,
                              )
                            }
                            disabled={saving}
                            aria-label={`Delete ${item.name}`}
                            className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-slate-200 text-slate-500 hover:bg-slate-50 hover:text-red-600 disabled:opacity-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>

                        <div className="mt-4 grid gap-3 lg:grid-cols-2">
                          <div className="rounded-lg bg-slate-50 p-3">
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                              Input
                            </p>
                            <p className="mt-1 whitespace-pre-wrap text-sm leading-5 text-slate-700">
                              {item.input}
                            </p>
                          </div>

                          <div className="rounded-lg bg-slate-50 p-3">
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                              Expected outcome
                            </p>
                            <p className="mt-1 whitespace-pre-wrap text-sm leading-5 text-slate-700">
                              {item.expected_outcome}
                            </p>
                          </div>
                        </div>

                        <div className="mt-3 flex flex-wrap gap-2">
                          {item.expected_tools.map(
                            (tool) => (
                              <span
                                key={`expected-${tool.name}`}
                                className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700 ring-1 ring-emerald-200"
                              >
                                Expected: {tool.name}
                              </span>
                            ),
                          )}

                          {item.forbidden_tools.map(
                            (tool) => (
                              <span
                                key={`forbidden-${tool}`}
                                className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-medium text-red-700 ring-1 ring-red-200"
                              >
                                Forbidden: {tool}
                              </span>
                            ),
                          )}

                          {item.expected_tools.length === 0
                            && item.forbidden_tools.length === 0
                            && (
                              <span className="text-xs text-slate-400">
                                No explicit tool expectations.
                              </span>
                            )}
                        </div>

                        {item.source_agent_run_id && (
                          <p className="mt-3 break-all text-[11px] text-slate-400">
                            Source run: {item.source_agent_run_id}
                          </p>
                        )}
                      </article>
                    ))}
                  </div>
                )}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
