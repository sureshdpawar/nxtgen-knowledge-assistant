"use client";

import {
  useState,
} from "react";

import {
  Beaker,
  CheckCircle2,
  ShieldCheck,
  XCircle,
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

import PromoteAgentRunDialog from "@/features/agent-evaluation/components/PromoteAgentRunDialog";

import {
  useAgent,
  useAgentRun,
} from "@/features/agents/hooks";

import {
  useAgentOnlineEvalResult,
} from "../hooks";


type Props = {
  resultId: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};


function score(
  value: number | null | undefined,
) {
  if (
    value === null
    || value === undefined
  ) {
    return "—";
  }

  return value.toFixed(3);
}


export default function AgentOnlineEvaluationDetails({
  resultId,
  open,
  onOpenChange,
}: Props) {
  const resultQuery =
    useAgentOnlineEvalResult(
      open
        ? resultId
        : null,
    );

  const result =
    resultQuery.data;

  const agentQuery =
    useAgent(
      result?.agent_id
      ?? null,
    );

  const runQuery =
    useAgentRun(
      result?.agent_run_id
      ?? null,
    );

  const [
    promoteOpen,
    setPromoteOpen,
  ] = useState(false);


  const taskQuality =
    result?.metrics
      .task_quality;

  const capabilityGrounding =
    result?.metrics
      .capability_grounding;

  const capabilities =
    capabilityGrounding
      ?.runtime_capabilities
    ?? [];

  const toolsExecuted =
    capabilityGrounding
      ?.tools_executed
    ?? [];

  const snapshotSource =
    capabilityGrounding
      ?.snapshot_source
    ?? "unknown";

  const judgeReason =
    taskQuality?.reason
    ?? "—";


  return (
    <>
      <Dialog
        open={open}
        onOpenChange={
          onOpenChange
        }
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-4xl">

          <DialogHeader>
            <DialogTitle>
              Agent Quality Result
            </DialogTitle>

            <DialogDescription>
              Capability-aware evaluation of the persisted AgentRun.
              No replay or tool execution occurs.
            </DialogDescription>
          </DialogHeader>


          {resultQuery.isLoading && (
            <div className="rounded-lg border bg-slate-50 p-6 text-sm text-slate-500">
              Loading evaluation...
            </div>
          )}


          {resultQuery.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              Failed to load evaluation details.
            </div>
          )}


          {result && (
            <div className="space-y-5">

              <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-slate-50 p-4">

                <div className="flex items-center gap-2">
                  {result.passed === true ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <XCircle className="h-5 w-5 text-red-600" />
                  )}

                  <div>
                    <p className="font-semibold text-slate-900">
                      {result.passed === true
                        ? "Passed"
                        : "Failed"}
                    </p>

                    <p className="text-xs text-slate-500">
                      Run {result.agent_run_id}
                    </p>
                  </div>
                </div>


                {agentQuery.data
                  && runQuery.data && (
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() =>
                      setPromoteOpen(
                        true,
                      )
                    }
                  >
                    <Beaker className="mr-2 h-4 w-4" />
                    Promote to Regression
                  </Button>
                )}

              </div>


              <div className="grid gap-4 sm:grid-cols-3">

                <div className="rounded-xl border p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Task Quality
                  </p>
                  <p className="mt-2 text-xl font-semibold text-slate-900">
                    {score(
                      result.task_quality_score,
                    )}
                  </p>
                </div>

                <div className="rounded-xl border p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Execution Health
                  </p>
                  <p className="mt-2 text-xl font-semibold text-slate-900">
                    {score(
                      result.execution_health_score,
                    )}
                  </p>
                </div>

                <div className="rounded-xl border p-4">
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Overall
                  </p>
                  <p className="mt-2 text-xl font-semibold text-slate-900">
                    {score(
                      result.overall_score,
                    )}
                  </p>
                </div>

              </div>


              <div className="rounded-xl border p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  User Request
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-800">
                  {result.question}
                </p>
              </div>


              <div className="rounded-xl border p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Agent Answer
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-800">
                  {result.actual_answer
                    || "—"}
                </p>
              </div>


              <div className="rounded-xl border p-4">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="h-4 w-4 text-slate-500" />

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Runtime Capabilities
                  </p>
                </div>

                <p className="mt-1 text-xs text-slate-400">
                  Snapshot source: {
                    snapshotSource
                  }
                </p>

                <div className="mt-3 space-y-2">
                  {capabilities.length === 0 ? (
                    <p className="text-sm text-slate-500">
                      No runtime capability snapshot is available.
                    </p>
                  ) : (
                    capabilities.map(
                      (
                        capability,
                        index,
                      ) => (
                        <div
                          key={`${capability.name ?? "unknown"}-${index}`}
                          className="rounded-lg bg-slate-50 p-3"
                        >
                          <p className="font-mono text-sm font-medium text-slate-800">
                            {capability.name
                              ?? "unknown"}
                          </p>

                          {Boolean(
                            capability.description,
                          ) && (
                            <p className="mt-1 text-sm text-slate-600">
                              {
                                capability.description
                              }
                            </p>
                          )}

                          <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
                            {Boolean(
                              capability.execution_policy,
                            ) && (
                              <span>
                                Policy: {
                                  capability.execution_policy
                                }
                              </span>
                            )}

                            {Boolean(
                              capability.risk_level,
                            ) && (
                              <span>
                                Risk: {
                                  capability.risk_level
                                }
                              </span>
                            )}
                          </div>
                        </div>
                      ),
                    )
                  )}
                </div>
              </div>


              <div className="rounded-xl border p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Tools Actually Executed
                </p>

                <p className="mt-2 text-sm text-slate-700">
                  {toolsExecuted.length > 0
                    ? toolsExecuted.join(", ")
                    : "None"}
                </p>
              </div>


              <div className="rounded-xl border p-4">
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  Judge Reason
                </p>

                <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {judgeReason}
                </p>
              </div>

            </div>
          )}

        </DialogContent>
      </Dialog>


      {agentQuery.data && (
        <PromoteAgentRunDialog
          agent={
            agentQuery.data
          }
          run={
            runQuery.data
            ?? null
          }
          open={
            promoteOpen
          }
          onOpenChange={
            setPromoteOpen
          }
        />
      )}
    </>
  );
}
