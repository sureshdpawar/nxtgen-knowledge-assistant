"use client";

import {
  CheckCircle2,
  Copy,
  ExternalLink,
  Info,
  Loader2,
  ShieldCheck,
  X,
  XCircle,
} from "lucide-react";
import {
  useState,
} from "react";
import type {
  ReactNode,
} from "react";
import { toast } from "sonner";

import TraceDebugDetails from "@/features/online-evaluation/components/TraceDebugDetails";
import {
  useOnlineEvalResult,
} from "@/features/online-evaluation/hooks";


type OnlineEvaluationDetailsProps = {
  resultId:
    | string
    | null;

  onClose: () => void;
};


type EvaluationMetricMetadata = {
  score?: number;
  passed?: boolean;
  reason?: string;
};


type EvaluationMetadataView = {
  evaluationPath:
    | string
    | null;

  evaluationOutcome:
    | string
    | null;

  contextAnswerable:
    | boolean
    | null;

  safeAbstention:
    | EvaluationMetricMetadata
    | null;

  contextAnswerability:
    | EvaluationMetricMetadata
    | null;
};


type ProductionMetadataView = {
  workload:
    | string
    | null;

  agentId:
    | string
    | null;

  agentName:
    | string
    | null;

  agentRunId:
    | string
    | null;

  agentThreadId:
    | string
    | null;

  actorType:
    | string
    | null;

  actorId:
    | string
    | null;
};


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


function formatDateTime(
  value:
    | string
    | null
    | undefined,
) {
  if (
    !value
  ) {
    return "—";
  }

  const date =
    new Date(
      value,
    );

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return "—";
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle:
        "medium",
      timeStyle:
        "short",
    },
  ).format(
    date,
  );
}


function formatMetadata(
  value:
    Record<
      string,
      unknown
    >,
) {
  try {
    return JSON.stringify(
      value,
      null,
      2,
    );
  } catch {
    return "{}";
  }
}


function asRecord(
  value: unknown,
): Record<
  string,
  unknown
> | null {
  if (
    typeof value !== "object"
    || value === null
    || Array.isArray(
      value,
    )
  ) {
    return null;
  }

  return value as Record<
    string,
    unknown
  >;
}


function asString(
  value: unknown,
) {
  return (
    typeof value === "string"
    && value.trim()
  )
    ? value.trim()
    : null;
}


function asMetricMetadata(
  value: unknown,
): EvaluationMetricMetadata | null {
  const record =
    asRecord(
      value,
    );

  if (
    !record
  ) {
    return null;
  }

  return {
    score:
      typeof record.score === "number"
        ? record.score
        : undefined,

    passed:
      typeof record.passed === "boolean"
        ? record.passed
        : undefined,

    reason:
      typeof record.reason === "string"
        ? record.reason
        : undefined,
  };
}


function readEvaluationMetadata(
  metadata:
    Record<
      string,
      unknown
    >,
): EvaluationMetadataView {
  const metrics =
    asRecord(
      metadata.metrics,
    );

  return {
    evaluationPath:
      asString(
        metadata.evaluation_path,
      ),

    evaluationOutcome:
      asString(
        metadata.evaluation_outcome,
      ),

    contextAnswerable:
      typeof metadata.context_answerable
        === "boolean"
        ? metadata.context_answerable
        : null,

    safeAbstention:
      asMetricMetadata(
        metrics
          ?.safe_abstention,
      ),

    contextAnswerability:
      asMetricMetadata(
        metrics
          ?.context_answerability,
      ),
  };
}


function readProductionMetadata(
  metadata:
    Record<
      string,
      unknown
    >,
): ProductionMetadataView {
  const workload =
    asString(
      metadata.workload,
    )
    ?? asString(
      metadata.capture_source,
    );

  return {
    workload,
    agentId:
      asString(
        metadata.agent_id,
      ),
    agentName:
      asString(
        metadata.agent_name,
      ),
    agentRunId:
      asString(
        metadata.agent_run_id,
      ),
    agentThreadId:
      asString(
        metadata.agent_thread_id,
      ),
    actorType:
      asString(
        metadata.actor_type,
      ),
    actorId:
      asString(
        metadata.actor_id,
      ),
  };
}


function displayWorkload(
  workload:
    | string
    | null,
) {
  if (
    !workload
  ) {
    return "Chat";
  }

  const normalized =
    workload
      .trim()
      .toLowerCase();

  if (
    normalized === "agent"
  ) {
    return "Agent";
  }

  if (
    normalized === "chat"
  ) {
    return "Chat";
  }

  return (
    normalized
      .charAt(0)
      .toUpperCase()
    + normalized.slice(
      1,
    )
  );
}


function MetricCard({
  label,
  value,
  note,
}: {
  label: string;

  value:
    | number
    | null
    | undefined;

  note?: string;
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 text-xl font-bold text-slate-900">
        {formatScore(
          value,
        )}
      </p>

      {note ? (
        <p className="mt-1 text-xs leading-5 text-slate-500">
          {note}
        </p>
      ) : null}
    </div>
  );
}


function Field({
  label,
  value,
}: {
  label: string;

  value:
    ReactNode;
}) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <div className="mt-1 break-words text-sm text-slate-800">
        {value}
      </div>
    </div>
  );
}


export default function OnlineEvaluationDetails({
  resultId,
  onClose,
}: OnlineEvaluationDetailsProps) {
  const [
    selectedTraceId,
    setSelectedTraceId,
  ] = useState<
    string
    | null
  >(
    null,
  );

  const {
    data:
      result,
    isLoading,
    error,
  } = useOnlineEvalResult(
    resultId,
  );


  async function copyText(
    value: string,
    label: string,
  ) {
    try {
      await navigator
        .clipboard
        .writeText(
          value,
        );

      toast.success(
        `${label} copied.`,
      );
    } catch {
      toast.error(
        `Unable to copy ${label.toLowerCase()}.`,
      );
    }
  }


  if (
    !resultId
  ) {
    return null;
  }


  const evaluationView =
    result
      ? readEvaluationMetadata(
          result.evaluation_metadata,
        )
      : null;

  const productionView =
    result
      ? readProductionMetadata(
          result.evaluation_metadata,
        )
      : null;

  const isAgentWorkload =
    productionView
      ?.workload
      ?.toLowerCase()
      === "agent";

  const isSafeAbstention =
    evaluationView
      ?.evaluationOutcome
      === "safe_abstention";

  const isContextNotAnswerable =
    evaluationView
      ?.contextAnswerable
      === false;


  return (
    <>
      <div className="fixed inset-0 z-50">
        <button
          type="button"
          aria-label="Close online evaluation details"
          onClick={
            onClose
          }
          className="absolute inset-0 bg-slate-950/30"
        />

        <aside className="absolute right-0 top-0 h-full w-full max-w-3xl overflow-y-auto border-l border-slate-200 bg-slate-50 shadow-2xl">
          <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-5 py-4">
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Online evaluation details
              </h2>

              <p className="mt-0.5 text-sm text-slate-500">
                Production response quality and evaluation metadata
              </p>
            </div>

            <button
              type="button"
              onClick={
                onClose
              }
              className="rounded-lg p-2 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800"
              aria-label="Close"
            >
              <X className="h-5 w-5" />
            </button>
          </div>


          {isLoading ? (
            <div className="flex min-h-[400px] items-center justify-center">
              <div className="inline-flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="h-4 w-4 animate-spin" />

                Loading evaluation details…
              </div>
            </div>
          ) : error || !result ? (
            <div className="m-5 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              Unable to load online evaluation details.
            </div>
          ) : (
            <div className="space-y-5 p-5">
              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Evaluation
                    </p>

                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold capitalize text-slate-700">
                        {result.status}
                      </span>

                      {result.status === "completed"
                        && result.passed !== null ? (
                        isSafeAbstention ? (
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                            <ShieldCheck className="h-3.5 w-3.5" />

                            Safe abstention
                          </span>
                        ) : result.passed ? (
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">
                            <CheckCircle2 className="h-3.5 w-3.5" />

                            Passed
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1.5 rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-700">
                            <XCircle className="h-3.5 w-3.5" />

                            Failed
                          </span>
                        )
                      ) : null}
                    </div>
                  </div>

                  <div className="text-right">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Sample reason
                    </p>

                    <p className="mt-1 text-sm font-medium text-slate-800">
                      {result.sample_reason}
                    </p>
                  </div>
                </div>


                {isContextNotAnswerable ? (
                  <div className="mt-4 rounded-lg border border-blue-200 bg-blue-50 p-3">
                    <div className="flex gap-2">
                      <Info className="mt-0.5 h-4 w-4 shrink-0 text-blue-700" />

                      <div>
                        <p className="text-sm font-semibold text-blue-900">
                          Retrieved evidence was not sufficient to answer this question.
                        </p>

                        <p className="mt-1 text-xs leading-5 text-blue-700">
                          This does not prove the full knowledge base lacks the answer.
                          It means the retrieved context supplied to the generator was
                          not answerable.
                        </p>
                      </div>
                    </div>
                  </div>
                ) : null}


                <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
                  <MetricCard
                    label="Faithfulness"
                    value={
                      result
                        .faithfulness_score
                    }
                  />

                  <MetricCard
                    label="Answer relevancy"
                    value={
                      result
                        .answer_relevancy_score
                    }
                    note={
                      isContextNotAnswerable
                        ? "Not scored on the safe-abstention path."
                        : undefined
                    }
                  />

                  <MetricCard
                    label="Context relevancy"
                    value={
                      result
                        .contextual_relevancy_score
                    }
                    note={
                      isContextNotAnswerable
                        ? "Diagnostic only for this evaluation path."
                        : undefined
                    }
                  />

                  {evaluationView
                    ?.contextAnswerability ? (
                    <MetricCard
                      label="Context answerability"
                      value={
                        evaluationView
                          .contextAnswerability
                          .score
                      }
                    />
                  ) : null}

                  {evaluationView
                    ?.safeAbstention ? (
                    <MetricCard
                      label="Safe abstention"
                      value={
                        evaluationView
                          .safeAbstention
                          .score
                      }
                    />
                  ) : null}
                </div>
              </section>


              {evaluationView
                ?.contextAnswerability
                ?.reason ? (
                <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                  <h3 className="text-sm font-bold text-slate-900">
                    Answerability assessment
                  </h3>

                  <p className="mt-2 text-sm leading-6 text-slate-700">
                    {
                      evaluationView
                        .contextAnswerability
                        .reason
                    }
                  </p>

                  {evaluationView
                    ?.safeAbstention
                    ?.reason ? (
                    <div className="mt-4 border-t border-slate-200 pt-4">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                        Safe abstention assessment
                      </p>

                      <p className="mt-2 text-sm leading-6 text-slate-700">
                        {
                          evaluationView
                            .safeAbstention
                            .reason
                        }
                      </p>
                    </div>
                  ) : null}
                </section>
              ) : null}


              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <h3 className="text-sm font-bold text-slate-900">
                    Production request
                  </h3>

                  <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                    {displayWorkload(
                      productionView
                        ?.workload
                        ?? null,
                    )}
                  </span>
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  <Field
                    label="Provider"
                    value={
                      result.generator_provider
                      ?? "—"
                    }
                  />

                  <Field
                    label="Model"
                    value={
                      result.generator_model
                      ?? "—"
                    }
                  />

                  <Field
                    label="Knowledge base ID"
                    value={
                      result.knowledge_base_id
                      ?? "—"
                    }
                  />

                  {isAgentWorkload ? (
                    <>
                      <Field
                        label="Agent"
                        value={
                          productionView
                            ?.agentName
                          ?? productionView
                            ?.agentId
                          ?? "—"
                        }
                      />

                      <Field
                        label="Agent Run ID"
                        value={
                          productionView
                            ?.agentRunId
                          ?? "—"
                        }
                      />

                      <Field
                        label="Agent Thread ID"
                        value={
                          productionView
                            ?.agentThreadId
                          ?? "—"
                        }
                      />

                      <Field
                        label="Actor Type"
                        value={
                          productionView
                            ?.actorType
                          ?? "—"
                        }
                      />

                      <Field
                        label="Actor ID"
                        value={
                          productionView
                            ?.actorId
                          ?? "—"
                        }
                      />
                    </>
                  ) : (
                    <>
                      <Field
                        label="Conversation ID"
                        value={
                          result.conversation_id
                          ?? "—"
                        }
                      />

                      <Field
                        label="Message ID"
                        value={
                          result.message_id
                          ?? "—"
                        }
                      />
                    </>
                  )}

                  <Field
                    label="Captured"
                    value={
                      formatDateTime(
                        result.created_at,
                      )
                    }
                  />

                  <Field
                    label="Evaluated"
                    value={
                      formatDateTime(
                        result.evaluated_at,
                      )
                    }
                  />

                  <Field
                    label="Updated"
                    value={
                      formatDateTime(
                        result.updated_at,
                      )
                    }
                  />
                </div>


                <div className="mt-4">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Source trace ID
                  </p>

                  <div className="mt-1 flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() =>
                        setSelectedTraceId(
                          result.source_trace_id,
                        )
                      }
                      className="group min-w-0 max-w-full"
                      aria-label="Open production trace"
                    >
                      <code className="inline-flex max-w-full items-center gap-1.5 break-all rounded bg-blue-50 px-2 py-1.5 text-left text-xs font-semibold text-blue-700 transition group-hover:bg-blue-100 group-hover:text-blue-900">
                        {result.source_trace_id}

                        <ExternalLink className="h-3.5 w-3.5 shrink-0" />
                      </code>
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        copyText(
                          result.source_trace_id,
                          "Trace ID",
                        )
                      }
                      className="rounded-lg border border-slate-300 bg-white p-2 text-slate-500 transition hover:bg-slate-50 hover:text-slate-800"
                      aria-label="Copy source trace ID"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                  </div>

                  <p className="mt-2 text-xs text-slate-500">
                    The trace ID is persisted with this evaluation. Local span details
                    are available only while the configured trace-debug exporter retains them.
                  </p>
                </div>
              </section>


              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="text-sm font-bold text-slate-900">
                  Question
                </h3>

                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {result.question}
                </p>
              </section>


              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="text-sm font-bold text-slate-900">
                  Actual answer
                </h3>

                <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                  {result.actual_answer}
                </p>
              </section>


              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <h3 className="text-sm font-bold text-slate-900">
                    Retrieval context
                  </h3>

                  <span className="text-xs text-slate-500">
                    {result.retrieval_context.length} chunk{
                      result.retrieval_context.length === 1
                        ? ""
                        : "s"
                    }
                  </span>
                </div>

                {result.retrieval_context.length === 0 ? (
                  <p className="mt-3 text-sm text-slate-500">
                    No retrieval context was stored for this sample.
                  </p>
                ) : (
                  <div className="mt-3 space-y-3">
                    {result.retrieval_context.map(
                      (
                        context,
                        index,
                      ) => (
                        <div
                          key={`${result.id}-context-${index}`}
                          className="rounded-lg border border-slate-200 bg-slate-50 p-3"
                        >
                          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                            Context {index + 1}
                          </p>

                          <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">
                            {context}
                          </p>
                        </div>
                      ),
                    )}
                  </div>
                )}
              </section>


              {result.error_message ? (
                <section className="rounded-xl border border-red-200 bg-red-50 p-4">
                  <h3 className="text-sm font-bold text-red-800">
                    Evaluation error
                  </h3>

                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-red-700">
                    {result.error_message}
                  </p>
                </section>
              ) : null}


              <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                <h3 className="text-sm font-bold text-slate-900">
                  Evaluation metadata
                </h3>

                <pre className="mt-3 overflow-x-auto rounded-lg bg-slate-950 p-4 text-xs leading-5 text-slate-100">
                  {formatMetadata(
                    result.evaluation_metadata,
                  )}
                </pre>
              </section>
            </div>
          )}
        </aside>
      </div>

      <TraceDebugDetails
        traceId={
          selectedTraceId
        }
        onClose={() =>
          setSelectedTraceId(
            null,
          )
        }
      />
    </>
  );
}
