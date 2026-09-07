"use client";

import {
  Activity,
  ChevronDown,
  ChevronRight,
  Copy,
  Loader2,
  X,
} from "lucide-react";
import {
  useMemo,
  useState,
} from "react";
import { toast } from "sonner";

import {
  useTraceDebugTrace,
} from "@/features/online-evaluation/hooks";

import type {
  TraceDebugSpan,
} from "@/features/online-evaluation/types";


type TraceDebugDetailsProps = {
  traceId:
    | string
    | null;

  onClose: () => void;
};


function formatDuration(
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
    value < 1
  ) {
    return `${value.toFixed(2)} ms`;
  }

  if (
    value < 1000
  ) {
    return `${value.toFixed(1)} ms`;
  }

  return `${(
    value / 1000
  ).toFixed(
    2,
  )} s`;
}


function shortId(
  value: string,
) {
  if (
    value.length <= 16
  ) {
    return value;
  }

  return `${value.slice(
    0,
    8,
  )}…${value.slice(
    -8,
  )}`;
}


function getHttpStatusCode(
  span: TraceDebugSpan,
) {
  const value =
    span.attributes[
      "http.status_code"
    ]
    ?? span.attributes[
      "http.response.status_code"
    ];

  return (
    typeof value === "number"
    || typeof value === "string"
  )
    ? String(value)
    : null;
}


function getImportantAttributes(
  span: TraceDebugSpan,
) {
  const preferredKeys = [
    "knowgentiq.tenant.id",
    "knowgentiq.knowledge_base.id",
    "gen_ai.system",
    "gen_ai.request.model",
    "gen_ai.usage.input_tokens",
    "gen_ai.usage.output_tokens",
    "knowgentiq.llm.total_tokens",
    "knowgentiq.cost.total",
    "knowgentiq.cost.currency",
    "knowgentiq.retrieval.candidate_count",
    "knowgentiq.retrieval.top_k",
    "knowgentiq.reranker.candidate_count",
    "http.request.method",
    "http.route",
    "http.response.status_code",
  ];

  return preferredKeys
    .filter(
      (key) =>
        span.attributes[
          key
        ] !== undefined,
    )
    .map(
      (key) => ({
        key,
        value:
          span.attributes[
            key
          ],
      }),
    );
}


function SpanCard({
  span,
  depth,
}: {
  span: TraceDebugSpan;
  depth: number;
}) {
  const [
    expanded,
    setExpanded,
  ] = useState(
    false,
  );

  const importantAttributes =
    getImportantAttributes(
      span,
    );

  const statusCode =
    getHttpStatusCode(
      span,
    );

  const hasAttributes =
    Object.keys(
      span.attributes,
    ).length > 0;

  return (
    <div
      style={{
        marginLeft:
          Math.min(
            depth * 20,
            80,
          ),
      }}
      className="rounded-lg border border-slate-200 bg-white"
    >
      <button
        type="button"
        onClick={() =>
          setExpanded(
            (value) =>
              !value,
          )
        }
        className="flex w-full items-start gap-3 p-3 text-left transition hover:bg-slate-50"
      >
        <div className="mt-0.5 text-slate-400">
          {expanded ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-sm font-semibold text-slate-900">
              {span.name}
            </span>

            <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
              {span.kind}
            </span>

            {span.status !== "UNSET" ? (
              <span
                className={
                  span.status === "ERROR"
                    ? "rounded-full bg-red-50 px-2 py-0.5 text-[11px] font-semibold text-red-700"
                    : "rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700"
                }
              >
                {span.status}
              </span>
            ) : null}

            {statusCode ? (
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-600">
                HTTP {statusCode}
              </span>
            ) : null}
          </div>

          <div className="mt-1 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-500">
            <span>
              {formatDuration(
                span.duration_ms,
              )}
            </span>

            <span>
              span {shortId(
                span.span_id,
              )}
            </span>
          </div>
        </div>
      </button>

      {expanded ? (
        <div className="border-t border-slate-200 bg-slate-50 p-3">
          {importantAttributes.length > 0 ? (
            <div className="grid gap-2 sm:grid-cols-2">
              {importantAttributes.map(
                ({
                  key,
                  value,
                }) => (
                  <div
                    key={key}
                    className="rounded border border-slate-200 bg-white p-2"
                  >
                    <p className="break-all font-mono text-[10px] text-slate-400">
                      {key}
                    </p>

                    <p className="mt-1 break-all text-xs font-medium text-slate-700">
                      {String(
                        value,
                      )}
                    </p>
                  </div>
                ),
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500">
              No highlighted debugging attributes on this span.
            </p>
          )}

          {hasAttributes ? (
            <details className="mt-3">
              <summary className="cursor-pointer text-xs font-semibold text-slate-600">
                All span attributes
              </summary>

              <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-950 p-3 text-[11px] leading-5 text-slate-100">
                {JSON.stringify(
                  span.attributes,
                  null,
                  2,
                )}
              </pre>
            </details>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}


function buildSpanDepths(
  spans: TraceDebugSpan[],
) {
  const spanById =
    new Map(
      spans.map(
        (span) => [
          span.span_id,
          span,
        ],
      ),
    );

  const depthCache =
    new Map<
      string,
      number
    >();

  function depthFor(
    span: TraceDebugSpan,
    seen =
      new Set<string>(),
  ): number {
    const cached =
      depthCache.get(
        span.span_id,
      );

    if (
      cached !== undefined
    ) {
      return cached;
    }

    if (
      !span.parent_span_id
      || seen.has(
        span.span_id,
      )
    ) {
      depthCache.set(
        span.span_id,
        0,
      );

      return 0;
    }

    const parent =
      spanById.get(
        span.parent_span_id,
      );

    if (
      !parent
    ) {
      depthCache.set(
        span.span_id,
        0,
      );

      return 0;
    }

    const nextSeen =
      new Set(
        seen,
      );

    nextSeen.add(
      span.span_id,
    );

    const depth =
      depthFor(
        parent,
        nextSeen,
      ) + 1;

    depthCache.set(
      span.span_id,
      depth,
    );

    return depth;
  }

  return new Map(
    spans.map(
      (span) => [
        span.span_id,
        depthFor(
          span,
        ),
      ],
    ),
  );
}


export default function TraceDebugDetails({
  traceId,
  onClose,
}: TraceDebugDetailsProps) {
  const {
    data:
      trace,
    isLoading,
    error,
  } = useTraceDebugTrace(
    traceId,
  );

  const spanDepths =
    useMemo(
      () =>
        buildSpanDepths(
          trace?.spans
          ?? [],
        ),
      [
        trace,
      ],
    );

  async function copyTraceId() {
    if (
      !traceId
    ) {
      return;
    }

    try {
      await navigator
        .clipboard
        .writeText(
          traceId,
        );

      toast.success(
        "Trace ID copied.",
      );
    } catch {
      toast.error(
        "Unable to copy trace ID.",
      );
    }
  }

  if (
    !traceId
  ) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-[60]">
      <button
        type="button"
        aria-label="Close trace details"
        onClick={
          onClose
        }
        className="absolute inset-0 bg-slate-950/40"
      />

      <aside className="absolute right-0 top-0 h-full w-full max-w-4xl overflow-y-auto border-l border-slate-200 bg-slate-50 shadow-2xl">
        <div className="sticky top-0 z-10 border-b border-slate-200 bg-white px-5 py-4">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Activity className="h-5 w-5 text-slate-500" />

                <h2 className="text-lg font-bold text-slate-900">
                  Production trace
                </h2>
              </div>

              <p className="mt-1 text-sm text-slate-500">
                OpenTelemetry execution path for the original production request
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

          <div className="mt-3 flex items-center gap-2">
            <code className="min-w-0 flex-1 break-all rounded bg-slate-100 px-2 py-1.5 text-xs text-slate-700">
              {traceId}
            </code>

            <button
              type="button"
              onClick={
                copyTraceId
              }
              className="rounded-lg border border-slate-300 bg-white p-2 text-slate-500 transition hover:bg-slate-50 hover:text-slate-800"
              aria-label="Copy trace ID"
            >
              <Copy className="h-4 w-4" />
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="flex min-h-[400px] items-center justify-center">
            <div className="inline-flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" />

              Loading production trace…
            </div>
          </div>
        ) : error || !trace ? (
          <div className="m-5 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm font-semibold text-amber-900">
              Production trace is not available in local trace storage.
            </p>

            <p className="mt-2 text-sm leading-6 text-amber-800">
              The production trace ID was captured successfully with this request.
              Local trace debugging only retains span details produced while the
              backend is running with OTEL_TRACE_EXPORTER=memory. Those in-memory
              spans are lost when the backend restarts.
            </p>

            <p className="mt-2 text-xs leading-5 text-amber-700">
              The persisted trace ID remains valid correlation data and can be used
              with a durable OpenTelemetry backend when one is configured.
            </p>
          </div>
        ) : (
          <div className="space-y-4 p-5">
            <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Execution path
                  </p>

                  <p className="mt-1 text-sm text-slate-700">
                    Parent/child indentation shows how the request moved through the system.
                  </p>
                </div>

                <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                  {trace.span_count} span{
                    trace.span_count === 1
                      ? ""
                      : "s"
                  }
                </span>
              </div>
            </section>

            <section className="space-y-2">
              {trace.spans.map(
                (span) => (
                  <SpanCard
                    key={
                      span.span_id
                    }
                    span={
                      span
                    }
                    depth={
                      spanDepths.get(
                        span.span_id,
                      )
                      ?? 0
                    }
                  />
                ),
              )}
            </section>

            <section className="rounded-xl border border-blue-200 bg-blue-50 p-4">
              <p className="text-sm font-semibold text-blue-900">
                How to debug a bad RAG answer
              </p>

              <p className="mt-2 text-sm leading-6 text-blue-800">
                Follow the request from retrieval → embedding → vector search →
                reranking → LLM generation. A failed context-relevancy score tells
                you where to start; this trace shows how the request actually ran.
              </p>
            </section>
          </div>
        )}
      </aside>
    </div>
  );
}
