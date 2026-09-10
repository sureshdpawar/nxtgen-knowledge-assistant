"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  AlertCircle,
  Beaker,
  CheckCircle2,
} from "lucide-react";

import {
  Button,
} from "@/components/ui/button";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  getAgentEvalDatasets,
  promoteAgentRunToEvalCase,
} from "@/features/agent-evaluation/api";

import type {
  AgentEvalDataset,
} from "@/features/agent-evaluation/types";

import type {
  Agent,
  AgentRun,
} from "@/features/agents/types";


type Props = {
  agent: Agent;
  run: AgentRun | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};


function parseCsv(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}


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

  return "Failed to promote Agent Run.";
}


export default function PromoteAgentRunDialog({
  agent,
  run,
  open,
  onOpenChange,
}: Props) {
  const [datasets, setDatasets] =
    useState<AgentEvalDataset[]>([]);

  const [datasetId, setDatasetId] =
    useState("");

  const [name, setName] =
    useState("");

  const [expectedOutcome, setExpectedOutcome] =
    useState("");

  const [expectedTools, setExpectedTools] =
    useState("");

  const [forbiddenTools, setForbiddenTools] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [error, setError] =
    useState("");

  const [success, setSuccess] =
    useState("");


  useEffect(() => {
    if (!open || !run) {
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError("");
      setSuccess("");
      setExpectedOutcome("");
      setExpectedTools("");
      setForbiddenTools("");
      setName(
        run.query
          ? `Regression: ${run.query.slice(0, 80)}`
          : "Promoted Agent Run",
      );

      try {
        const data =
          await getAgentEvalDatasets(
            agent.id,
          );

        if (cancelled) {
          return;
        }

        setDatasets(data);
        setDatasetId(
          data[0]?.id ?? "",
        );
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
  }, [
    open,
    run,
    agent.id,
  ]);


  async function handlePromote(
    event: React.FormEvent,
  ) {
    event.preventDefault();

    if (!run) {
      return;
    }

    if (!datasetId) {
      setError(
        "Select an Agent Evaluation dataset.",
      );
      return;
    }

    setSaving(true);
    setError("");
    setSuccess("");

    try {
      await promoteAgentRunToEvalCase(
        datasetId,
        {
          agent_run_id: run.id,
          name: name.trim(),
          expected_outcome:
            expectedOutcome.trim(),
          expected_tools:
            parseCsv(
              expectedTools,
            ).map((toolName) => ({
              name: toolName,
              input_parameters: {},
            })),
          forbidden_tools:
            parseCsv(
              forbiddenTools,
            ),
          enabled: true,
        },
      );

      setSuccess(
        "Agent Run promoted to the regression dataset.",
      );
    } catch (err) {
      setError(
        errorMessage(err),
      );
    } finally {
      setSaving(false);
    }
  }


  return (
    <Dialog
      open={open}
      onOpenChange={
        onOpenChange
      }
    >
      <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">

        <DialogHeader>
          <DialogTitle>
            Promote to Evaluation
          </DialogTitle>

          <DialogDescription>
            Turn this real Agent Run into a reusable regression case.
            The original user query becomes the evaluation input;
            define the desired behavior instead of copying the production answer.
          </DialogDescription>
        </DialogHeader>


        {!run ? null : loading ? (
          <div className="rounded-lg border bg-slate-50 p-5 text-sm text-slate-500">
            Loading evaluation datasets...
          </div>
        ) : (
          <form
            onSubmit={
              handlePromote
            }
            className="space-y-4"
          >
            {error && (
              <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
                <span>
                  {error}
                </span>
              </div>
            )}

            {success && (
              <div className="flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">
                <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0" />
                <span>
                  {success}
                </span>
              </div>
            )}


            <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Original Agent Run input
              </p>

              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                {run.query}
              </p>

              <p className="mt-2 break-all text-[11px] text-slate-400">
                Run ID: {run.id}
              </p>
            </div>


            <label className="block">
              <span className="text-sm font-medium text-slate-700">
                Target regression dataset
              </span>

              <select
                required
                value={datasetId}
                onChange={(event) =>
                  setDatasetId(
                    event.target.value,
                  )
                }
                className="mt-1.5 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              >
                {datasets.length === 0 && (
                  <option value="">
                    No datasets available for this agent
                  </option>
                )}

                {datasets.map(
                  (dataset) => (
                    <option
                      key={
                        dataset.id
                      }
                      value={
                        dataset.id
                      }
                    >
                      {dataset.name} · {dataset.version}
                    </option>
                  ),
                )}
              </select>

              {datasets.length === 0 && (
                <p className="mt-1.5 text-xs text-amber-700">
                  Create an Agent Evaluation dataset for this agent first.
                </p>
              )}
            </label>


            <label className="block">
              <span className="text-sm font-medium text-slate-700">
                Case name
              </span>

              <input
                required
                value={name}
                onChange={(event) =>
                  setName(
                    event.target.value,
                  )
                }
                className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />
            </label>


            <label className="block">
              <span className="text-sm font-medium text-slate-700">
                Expected outcome
              </span>

              <textarea
                required
                rows={5}
                value={
                  expectedOutcome
                }
                onChange={(event) =>
                  setExpectedOutcome(
                    event.target.value,
                  )
                }
                placeholder="Describe what the agent should correctly do or say when this scenario is replayed."
                className="mt-1.5 w-full resize-y rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <p className="mt-1.5 text-xs text-slate-500">
                This is intentionally operator-defined. The previous production answer is not treated as the gold answer.
              </p>
            </label>


            <div className="grid gap-4 md:grid-cols-2">

              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Expected tools
                </span>

                <input
                  value={
                    expectedTools
                  }
                  onChange={(event) =>
                    setExpectedTools(
                      event.target.value,
                    )
                  }
                  placeholder="create_enquiry, update_enquiry"
                  className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

                <p className="mt-1.5 text-xs text-slate-500">
                  Optional, comma-separated. Use JSON dataset import when exact argument expectations are needed.
                </p>
              </label>


              <label className="block">
                <span className="text-sm font-medium text-slate-700">
                  Forbidden tools
                </span>

                <input
                  value={
                    forbiddenTools
                  }
                  onChange={(event) =>
                    setForbiddenTools(
                      event.target.value,
                    )
                  }
                  placeholder="delete_all, schedule_consultation"
                  className="mt-1.5 w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                />

                <p className="mt-1.5 text-xs text-slate-500">
                  Optional deterministic capability-boundary checks.
                </p>
              </label>

            </div>


            <div className="flex justify-end gap-2 pt-2">

              <Button
                type="button"
                variant="outline"
                onClick={() =>
                  onOpenChange(
                    false,
                  )
                }
              >
                Close
              </Button>

              <Button
                type="submit"
                disabled={
                  saving
                  || Boolean(success)
                  || !datasetId
                  || !name.trim()
                  || !expectedOutcome.trim()
                }
              >
                <Beaker className="mr-2 h-4 w-4" />

                {saving
                  ? "Promoting..."
                  : success
                    ? "Promoted"
                    : "Promote Run"}
              </Button>

            </div>

          </form>
        )}

      </DialogContent>
    </Dialog>
  );
}
