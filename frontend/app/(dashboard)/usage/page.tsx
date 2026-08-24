"use client";

import {
  FormEvent,
  useState,
} from "react";

import {
  AlertTriangle,
  CheckCircle2,
  Database,
  Gauge,
  MessageSquare,
  Save,
} from "lucide-react";

import {
  useAuth,
} from "@/hooks/useAuth";

import {
  useChatChannels,
} from "@/features/chat-channels/hooks";

import {
  useKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  useChatChannelUsageLimit,
  useChatChannelUsageStatus,
  useKnowledgeBaseUsageLimit,
  useKnowledgeBaseUsageStatus,
  useTenantUsageLimit,
  useTenantUsageStatus,
  useUpdateChatChannelUsageLimit,
  useUpdateKnowledgeBaseUsageLimit,
  useUpdateTenantUsageLimit,
} from "@/features/usage/hooks";

import type {
  UsageLimit,
  UsageLimitUpdate,
  UsageMetricStatus,
  UsagePeriodStatus,
  UsageScopeStatus,
} from "@/features/usage/types";


type ScopeType =
  | "tenant"
  | "knowledge_base"
  | "chat_channel";


type FormState = {
  daily_message_limit: string;

  daily_input_token_limit: string;

  daily_output_token_limit: string;

  daily_total_token_limit: string;

  monthly_message_limit: string;

  monthly_input_token_limit: string;

  monthly_output_token_limit: string;

  monthly_total_token_limit: string;

  max_input_tokens_per_request:
    string;

  max_output_tokens_per_request:
    string;

  timezone: string;

  enabled: boolean;
};


const emptyForm: FormState = {
  daily_message_limit: "",

  daily_input_token_limit: "",

  daily_output_token_limit: "",

  daily_total_token_limit: "",

  monthly_message_limit: "",

  monthly_input_token_limit: "",

  monthly_output_token_limit: "",

  monthly_total_token_limit: "",

  max_input_tokens_per_request: "",

  max_output_tokens_per_request: "",

  timezone: "UTC",

  enabled: true,
};


function createFormState(
  limit: UsageLimit | null,
): FormState {
  if (!limit) {
    return {
      ...emptyForm,
    };
  }

  return {
    daily_message_limit:
      limit.daily_message_limit
        ?.toString()
      ?? "",

    daily_input_token_limit:
      limit.daily_input_token_limit
        ?.toString()
      ?? "",

    daily_output_token_limit:
      limit.daily_output_token_limit
        ?.toString()
      ?? "",

    daily_total_token_limit:
      limit.daily_total_token_limit
        ?.toString()
      ?? "",

    monthly_message_limit:
      limit.monthly_message_limit
        ?.toString()
      ?? "",

    monthly_input_token_limit:
      limit.monthly_input_token_limit
        ?.toString()
      ?? "",

    monthly_output_token_limit:
      limit.monthly_output_token_limit
        ?.toString()
      ?? "",

    monthly_total_token_limit:
      limit.monthly_total_token_limit
        ?.toString()
      ?? "",

    max_input_tokens_per_request:
      limit.max_input_tokens_per_request
        ?.toString()
      ?? "",

    max_output_tokens_per_request:
      limit.max_output_tokens_per_request
        ?.toString()
      ?? "",

    timezone:
      limit.timezone
      || "UTC",

    enabled:
      limit.enabled,
  };
}


function parseLimit(
  value: string,
): number | null {
  const trimmed =
    value.trim();

  if (!trimmed) {
    return null;
  }

  return Number(
    trimmed,
  );
}


function buildPayload(
  form: FormState,
): UsageLimitUpdate {
  return {
    daily_message_limit:
      parseLimit(
        form.daily_message_limit,
      ),

    daily_input_token_limit:
      parseLimit(
        form.daily_input_token_limit,
      ),

    daily_output_token_limit:
      parseLimit(
        form.daily_output_token_limit,
      ),

    daily_total_token_limit:
      parseLimit(
        form.daily_total_token_limit,
      ),

    monthly_message_limit:
      parseLimit(
        form.monthly_message_limit,
      ),

    monthly_input_token_limit:
      parseLimit(
        form.monthly_input_token_limit,
      ),

    monthly_output_token_limit:
      parseLimit(
        form.monthly_output_token_limit,
      ),

    monthly_total_token_limit:
      parseLimit(
        form.monthly_total_token_limit,
      ),

    max_input_tokens_per_request:
      parseLimit(
        form
          .max_input_tokens_per_request,
      ),

    max_output_tokens_per_request:
      parseLimit(
        form
          .max_output_tokens_per_request,
      ),

    timezone:
      form.timezone,

    enabled:
      form.enabled,
  };
}


function formatNumber(
  value: number | null,
) {
  if (value === null) {
    return "Unlimited";
  }

  return new Intl.NumberFormat(
    "en-US",
  ).format(
    value,
  );
}


function formatResetAt(
  value: string,
) {
  const date =
    new Date(
      value,
    );

  return new Intl.DateTimeFormat(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  ).format(
    date,
  );
}


function progressWidth(
  percentage:
    number | null,
) {
  if (percentage === null) {
    return 0;
  }

  return Math.min(
    Math.max(
      percentage,
      0,
    ),
    100,
  );
}


function UsageMetric({
  label,
  metric,
}: {
  label: string;

  metric: UsageMetricStatus;
}) {
  const percentage =
    metric.percentage_used;

  const atLimit =
    metric.limit !== null
    && metric.used
      >= metric.limit;

  const warning =
    percentage !== null
    && percentage >= 80
    && !atLimit;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">

      <div className="flex items-start justify-between gap-4">

        <div>

          <p className="text-sm font-medium text-slate-600">
            {label}
          </p>

          <p className="mt-1 text-xl font-bold text-slate-900">

            {formatNumber(
              metric.used,
            )}

            <span className="ml-1 text-sm font-normal text-slate-400">
              /{" "}
              {formatNumber(
                metric.limit,
              )}
            </span>

          </p>

        </div>


        {percentage !== null && (
          <span
            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
              atLimit
                ? "bg-red-100 text-red-700"
                : warning
                  ? "bg-amber-100 text-amber-700"
                  : "bg-slate-100 text-slate-600"
            }`}
          >
            {percentage.toFixed(
              2,
            )}
            %
          </span>
        )}

      </div>


      {metric.limit !== null && (
        <div className="mt-4">

          <div className="h-2 overflow-hidden rounded-full bg-slate-100">

            <div
              className={`h-full rounded-full transition-all ${
                atLimit
                  ? "bg-red-500"
                  : warning
                    ? "bg-amber-500"
                    : "bg-blue-600"
              }`}
              style={{
                width:
                  `${progressWidth(
                    percentage,
                  )}%`,
              }}
            />

          </div>


          <div className="mt-2 flex items-center justify-between text-xs text-slate-500">

            <span>
              Used{" "}
              {formatNumber(
                metric.used,
              )}
            </span>

            <span>
              Remaining{" "}
              {formatNumber(
                metric.remaining,
              )}
            </span>

          </div>

        </div>
      )}

    </div>
  );
}


function UsagePeriod({
  title,
  period,
}: {
  title: string;

  period: UsagePeriodStatus;
}) {
  return (
    <section className="rounded-2xl border bg-slate-50 p-5">

      <div className="mb-5 flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">

        <h2 className="text-lg font-semibold text-slate-900">
          {title}
        </h2>

        <p className="text-xs text-slate-500">
          Resets{" "}
          {formatResetAt(
            period.reset_at,
          )}
        </p>

      </div>


      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

        <UsageMetric
          label="Messages"
          metric={
            period.messages
          }
        />

        <UsageMetric
          label="Input tokens"
          metric={
            period.input_tokens
          }
        />

        <UsageMetric
          label="Output tokens"
          metric={
            period.output_tokens
          }
        />

        <UsageMetric
          label="Total tokens"
          metric={
            period.total_tokens
          }
        />

      </div>

    </section>
  );
}


function LimitInput({
  label,
  value,
  effectiveValue,
  inheritedLabel,
  onChange,
}: {
  label: string;

  value: string;

  effectiveValue:
    number | null;

  inheritedLabel: string;

  onChange:
    (
      value: string,
    ) => void;
}) {
  return (
    <div>

      <label className="text-sm font-medium text-slate-700">
        {label}
      </label>

      <input
        type="number"
        min="0"
        value={
          value
        }
        onChange={(
          event,
        ) =>
          onChange(
            event.target.value,
          )
        }
        placeholder={
          effectiveValue === null
            ? inheritedLabel
            : `${inheritedLabel}: ${formatNumber(
                effectiveValue,
              )}`
        }
        className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
      />

      <p className="mt-1 text-xs text-slate-400">
        Leave blank to inherit.
      </p>

    </div>
  );
}


type LimitEditorProps = {
  title: string;

  description: string;

  availabilityLabel: string;

  inheritedLabel: string;

  initialLimit:
    UsageLimit | null;

  effectiveScope:
    UsageScopeStatus | undefined;

  editorKey: string;

  saving: boolean;

  error: unknown;

  onSave:
    (
      payload:
        UsageLimitUpdate,
    ) => Promise<UsageLimit>;
};


function LimitEditor({
  title,
  description,
  availabilityLabel,
  inheritedLabel,
  initialLimit,
  effectiveScope,
  editorKey,
  saving,
  error,
  onSave,
}: LimitEditorProps) {
  return (
    <LimitEditorForm
      key={
        editorKey
      }
      title={
        title
      }
      description={
        description
      }
      availabilityLabel={
        availabilityLabel
      }
      inheritedLabel={
        inheritedLabel
      }
      initialLimit={
        initialLimit
      }
      effectiveScope={
        effectiveScope
      }
      saving={
        saving
      }
      error={
        error
      }
      onSave={
        onSave
      }
    />
  );
}


function LimitEditorForm({
  title,
  description,
  availabilityLabel,
  inheritedLabel,
  initialLimit,
  effectiveScope,
  saving,
  error,
  onSave,
}: Omit<
  LimitEditorProps,
  "editorKey"
>) {
  const [
    form,
    setForm,
  ] = useState<FormState>(
    () =>
      createFormState(
        initialLimit,
      ),
  );

  const [
    saved,
    setSaved,
  ] = useState(
    false,
  );


  function setField(
    field:
      keyof FormState,
    value:
      string | boolean,
  ) {
    setSaved(
      false,
    );

    setForm(
      (
        current,
      ) => ({
        ...current,

        [field]:
          value,
      }),
    );
  }


  async function handleSubmit(
    event:
      FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    setSaved(
      false,
    );

    try {
      const updatedLimit =
        await onSave(
          buildPayload(
            form,
          ),
        );

      setForm(
        createFormState(
          updatedLimit,
        ),
      );

      setSaved(
        true,
      );
    } catch {
      setSaved(
        false,
      );
    }
  }


  return (
    <form
      onSubmit={
        handleSubmit
      }
      className="rounded-2xl border bg-white p-6 shadow-sm"
    >

      <div className="border-b pb-5">

        <h2 className="text-xl font-semibold text-slate-900">
          {title}
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          {description}
        </p>

      </div>


      <div className="mt-6">

        <h3 className="font-semibold text-slate-900">
          Daily limits
        </h3>

        <div className="mt-4 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

          <LimitInput
            label="Messages"
            value={
              form.daily_message_limit
            }
            effectiveValue={
              effectiveScope
                ?.daily
                .messages
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "daily_message_limit",
                value,
              )
            }
          />

          <LimitInput
            label="Input tokens"
            value={
              form
                .daily_input_token_limit
            }
            effectiveValue={
              effectiveScope
                ?.daily
                .input_tokens
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "daily_input_token_limit",
                value,
              )
            }
          />

          <LimitInput
            label="Output tokens"
            value={
              form
                .daily_output_token_limit
            }
            effectiveValue={
              effectiveScope
                ?.daily
                .output_tokens
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "daily_output_token_limit",
                value,
              )
            }
          />

          <LimitInput
            label="Total tokens"
            value={
              form
                .daily_total_token_limit
            }
            effectiveValue={
              effectiveScope
                ?.daily
                .total_tokens
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "daily_total_token_limit",
                value,
              )
            }
          />

        </div>

      </div>


      <div className="mt-8">

        <h3 className="font-semibold text-slate-900">
          Monthly limits
        </h3>

        <div className="mt-4 grid gap-5 md:grid-cols-2 xl:grid-cols-4">

          <LimitInput
            label="Messages"
            value={
              form.monthly_message_limit
            }
            effectiveValue={
              effectiveScope
                ?.monthly
                .messages
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "monthly_message_limit",
                value,
              )
            }
          />

          <LimitInput
            label="Input tokens"
            value={
              form
                .monthly_input_token_limit
            }
            effectiveValue={
              effectiveScope
                ?.monthly
                .input_tokens
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "monthly_input_token_limit",
                value,
              )
            }
          />

          <LimitInput
            label="Output tokens"
            value={
              form
                .monthly_output_token_limit
            }
            effectiveValue={
              effectiveScope
                ?.monthly
                .output_tokens
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "monthly_output_token_limit",
                value,
              )
            }
          />

          <LimitInput
            label="Total tokens"
            value={
              form
                .monthly_total_token_limit
            }
            effectiveValue={
              effectiveScope
                ?.monthly
                .total_tokens
                .limit
              ?? null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "monthly_total_token_limit",
                value,
              )
            }
          />

        </div>

      </div>


      <div className="mt-8">

        <h3 className="font-semibold text-slate-900">
          Per request
        </h3>

        <div className="mt-4 grid gap-5 md:grid-cols-2">

          <LimitInput
            label="Max input tokens"
            value={
              form
                .max_input_tokens_per_request
            }
            effectiveValue={
              null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "max_input_tokens_per_request",
                value,
              )
            }
          />

          <LimitInput
            label="Max output tokens"
            value={
              form
                .max_output_tokens_per_request
            }
            effectiveValue={
              null
            }
            inheritedLabel={
              inheritedLabel
            }
            onChange={(
              value,
            ) =>
              setField(
                "max_output_tokens_per_request",
                value,
              )
            }
          />

        </div>

      </div>


      <div className="mt-8 grid gap-5 border-t pt-6 md:grid-cols-2">

        <div>

          <label className="text-sm font-medium text-slate-700">
            Quota timezone
          </label>

          <input
            value={
              form.timezone
            }
            onChange={(
              event,
            ) =>
              setField(
                "timezone",
                event.target.value,
              )
            }
            placeholder="UTC"
            className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          />

          <p className="mt-1 text-xs text-slate-400">
            Example: UTC,
            Asia/Kolkata,
            America/New_York
          </p>

        </div>


        <div>

          <p className="text-sm font-medium text-slate-700">
            Chat availability
          </p>

          <label className="mt-3 flex cursor-pointer items-center gap-3">

            <input
              type="checkbox"
              checked={
                form.enabled
              }
              onChange={(
                event,
              ) =>
                setField(
                  "enabled",
                  event.target.checked,
                )
              }
              className="h-4 w-4 rounded border-slate-300"
            />

            <span className="text-sm text-slate-600">
              {availabilityLabel}
            </span>

          </label>

        </div>

      </div>


      {Boolean(error) && (
        <div className="mt-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to update usage
          limits.
        </div>
      )}


      {saved && (
        <div className="mt-6 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          Usage limits updated
          successfully.
        </div>
      )}


      <div className="mt-6 flex justify-end">

        <button
          type="submit"
          disabled={
            saving
          }
          className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
        >

          <Save className="h-4 w-4" />

          {saving
            ? "Saving..."
            : "Save limits"
          }

        </button>

      </div>

    </form>
  );
}


function ScopeUsage({
  scope,
  title,
  allowed,
}: {
  scope:
    UsageScopeStatus | undefined;

  title: string;

  allowed:
    boolean | undefined;
}) {
  if (!scope) {
    return null;
  }

  return (
    <div className="space-y-5">

      <div className="rounded-xl border bg-white p-5 shadow-sm">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-blue-50 p-2 text-blue-600">

              <Gauge className="h-5 w-5" />

            </div>


            <div>

              <p className="font-semibold text-slate-900">
                {title}
              </p>

              <p className="mt-1 text-sm text-slate-500">

                Timezone:{" "}
                {
                  scope.timezone
                }

                {scope.source && (
                  <>
                    {" · "}
                    Source:{" "}
                    {
                      scope.source
                    }
                  </>
                )}

              </p>

            </div>

          </div>


          <div
            className={`flex w-fit items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold ${
              allowed
                ? "bg-emerald-100 text-emerald-700"
                : "bg-red-100 text-red-700"
            }`}
          >

            {allowed
              ? (
                <CheckCircle2 className="h-4 w-4" />
              )
              : (
                <AlertTriangle className="h-4 w-4" />
              )
            }

            {allowed
              ? "Chat available"
              : "Usage limit reached"
            }

          </div>

        </div>

      </div>


      <UsagePeriod
        title="Daily usage"
        period={
          scope.daily
        }
      />

      <UsagePeriod
        title="Monthly usage"
        period={
          scope.monthly
        }
      />

    </div>
  );
}


export default function UsagePage() {
  const {
    user,
  } = useAuth();

  const isAdmin =
    user?.role === "ADMIN";

  const [
    scopeType,
    setScopeType,
  ] = useState<ScopeType>(
    "tenant",
  );

  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] = useState(
    "",
  );

  const [
    chatChannelId,
    setChatChannelId,
  ] = useState(
    "",
  );


  const {
    data:
      knowledgeBases,

    isLoading:
      knowledgeBasesLoading,

    error:
      knowledgeBasesError,
  } =
    useKnowledgeBases(
      isAdmin,
    );


  const {
    data:
      chatChannels,

    isLoading:
      chatChannelsLoading,

    error:
      chatChannelsError,
  } =
    useChatChannels(
      knowledgeBaseId,
    );


  const tenantEnabled =
    isAdmin
    && scopeType === "tenant";


  const kbEnabled =
    isAdmin
    && scopeType
      === "knowledge_base"
    && Boolean(
      knowledgeBaseId,
    );


  const channelEnabled =
    isAdmin
    && scopeType
      === "chat_channel"
    && Boolean(
      knowledgeBaseId,
    )
    && Boolean(
      chatChannelId,
    );


  const {
    data:
      tenantStatusData,

    isLoading:
      tenantStatusLoading,

    error:
      tenantStatusError,
  } =
    useTenantUsageStatus(
      tenantEnabled,
    );


  const {
    data:
      tenantLimitData,

    isLoading:
      tenantLimitLoading,

    error:
      tenantLimitError,
  } =
    useTenantUsageLimit(
      tenantEnabled,
    );


  const {
    data:
      kbStatusData,

    isLoading:
      kbStatusLoading,

    error:
      kbStatusError,
  } =
    useKnowledgeBaseUsageStatus(
      knowledgeBaseId || null,
      kbEnabled,
    );


  const {
    data:
      kbLimitData,

    isLoading:
      kbLimitLoading,

    error:
      kbLimitError,
  } =
    useKnowledgeBaseUsageLimit(
      knowledgeBaseId || null,
      kbEnabled,
    );


  const {
    data:
      channelStatusData,

    isLoading:
      channelStatusLoading,

    error:
      channelStatusError,
  } =
    useChatChannelUsageStatus(
      knowledgeBaseId || null,
      chatChannelId || null,
      channelEnabled,
    );


  const {
    data:
      channelLimitData,

    isLoading:
      channelLimitLoading,

    error:
      channelLimitError,
  } =
    useChatChannelUsageLimit(
      chatChannelId || null,
      channelEnabled,
    );


  const updateTenantLimit =
    useUpdateTenantUsageLimit();

  const updateKnowledgeBaseLimit =
    useUpdateKnowledgeBaseUsageLimit();

  const updateChatChannelLimit =
    useUpdateChatChannelUsageLimit();


  if (!user) {
    return null;
  }


  if (!isAdmin) {
    return (
      <div className="rounded-xl border bg-white p-8 shadow-sm">

        <h1 className="text-2xl font-bold text-slate-900">
          Usage & Limits
        </h1>

        <p className="mt-2 text-slate-500">
          Usage administration is
          available to tenant
          administrators.
        </p>

      </div>
    );
  }


  const tenantScope =
    tenantStatusData
      ?.scopes
      .find(
        (scope) =>
          scope.scope
          === "tenant",
      );


  const kbScope =
    kbStatusData
      ?.scopes
      .find(
        (scope) =>
          scope.scope
          === "knowledge_base",
      );


  const channelScope =
    channelStatusData
      ?.scopes
      .find(
        (scope) =>
          scope.scope
          === "chat_channel",
      );


  const selectedKnowledgeBase =
    knowledgeBases
      ?.find(
        (
          knowledgeBase,
        ) =>
          knowledgeBase.id
          === knowledgeBaseId,
      );


  const selectedChatChannel =
    chatChannels
      ?.find(
        (
          channel,
        ) =>
          channel.id
          === chatChannelId,
      );


  let activeStatusLoading =
    false;

  let activeStatusError:
    unknown = null;

  let activeLimitLoading =
    false;

  let activeLimitError:
    unknown = null;


  if (scopeType === "tenant") {
    activeStatusLoading =
      tenantStatusLoading;

    activeStatusError =
      tenantStatusError;

    activeLimitLoading =
      tenantLimitLoading;

    activeLimitError =
      tenantLimitError;
  }


  if (
    scopeType
    === "knowledge_base"
  ) {
    activeStatusLoading =
      kbStatusLoading;

    activeStatusError =
      kbStatusError;

    activeLimitLoading =
      kbLimitLoading;

    activeLimitError =
      kbLimitError;
  }


  if (
    scopeType
    === "chat_channel"
  ) {
    activeStatusLoading =
      channelStatusLoading;

    activeStatusError =
      channelStatusError;

    activeLimitLoading =
      channelLimitLoading;

    activeLimitError =
      channelLimitError;
  }


  return (
    <div className="space-y-8">

      <div>

        <p className="text-sm font-medium text-slate-500">
          Tenant Administration
        </p>

        <h1 className="mt-1 text-3xl font-bold text-slate-900">
          Usage & Limits
        </h1>

        <p className="mt-2 max-w-3xl text-slate-500">
          Monitor AI usage and
          configure daily, monthly,
          and per-request limits at
          tenant, knowledge-base, and
          chat-channel scope.
        </p>

      </div>


      <section className="rounded-2xl border bg-white p-6 shadow-sm">

        <div>

          <h2 className="text-lg font-semibold text-slate-900">
            Scope
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Choose which quota level
            you want to inspect or
            configure.
          </p>

        </div>


        <div className="mt-5 grid gap-5 md:grid-cols-3">

          <div>

            <label className="text-sm font-medium text-slate-700">
              Usage scope
            </label>

            <select
              value={
                scopeType
              }
              onChange={(
                event,
              ) => {
                const nextScope =
                  event.target
                    .value as ScopeType;

                setScopeType(
                  nextScope,
                );

                if (
                  nextScope
                  !== "chat_channel"
                ) {
                  setChatChannelId(
                    "",
                  );
                }
              }}
              className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
            >

              <option value="tenant">
                Tenant
              </option>

              <option value="knowledge_base">
                Knowledge Base
              </option>

              <option value="chat_channel">
                Chat Channel
              </option>

            </select>

          </div>


          {(
            scopeType
              === "knowledge_base"
            || scopeType
              === "chat_channel"
          ) && (
            <div>

              <label className="text-sm font-medium text-slate-700">
                Knowledge base
              </label>

              <select
                value={
                  knowledgeBaseId
                }
                onChange={(
                  event,
                ) => {
                  setKnowledgeBaseId(
                    event.target.value,
                  );

                  setChatChannelId(
                    "",
                  );
                }}
                disabled={
                  knowledgeBasesLoading
                }
                className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100"
              >

                <option value="">
                  Select a knowledge base
                </option>

                {knowledgeBases
                  ?.map(
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


              {Boolean(
                knowledgeBasesError,
              ) && (
                <p className="mt-2 text-sm text-red-600">
                  Failed to load
                  knowledge bases.
                </p>
              )}

            </div>
          )}


          {scopeType
            === "chat_channel"
            && (
              <div>

                <label className="text-sm font-medium text-slate-700">
                  Chat channel
                </label>

                <select
                  value={
                    chatChannelId
                  }
                  onChange={(
                    event,
                  ) =>
                    setChatChannelId(
                      event.target.value,
                    )
                  }
                  disabled={
                    !knowledgeBaseId
                    || chatChannelsLoading
                  }
                  className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100"
                >

                  <option value="">
                    Select a chat channel
                  </option>

                  {chatChannels
                    ?.map(
                      (
                        channel,
                      ) => (
                        <option
                          key={
                            channel.id
                          }
                          value={
                            channel.id
                          }
                        >
                          {
                            channel.name
                          }
                          {" · "}
                          {
                            channel.type
                          }
                        </option>
                      ),
                    )
                  }

                </select>


                {Boolean(
                  chatChannelsError,
                ) && (
                  <p className="mt-2 text-sm text-red-600">
                    Failed to load
                    chat channels.
                  </p>
                )}

              </div>
            )
          }

        </div>


        {scopeType
          === "knowledge_base"
          && selectedKnowledgeBase
          && (
            <div className="mt-5 flex items-start gap-3 rounded-xl border border-blue-100 bg-blue-50 p-4">

              <Database className="mt-0.5 h-5 w-5 shrink-0 text-blue-600" />

              <div>

                <p className="text-sm font-semibold text-blue-900">
                  {
                    selectedKnowledgeBase.name
                  }
                </p>

                <p className="mt-1 text-sm text-blue-700">
                  Blank KB limits inherit
                  the effective tenant
                  quota.
                </p>

              </div>

            </div>
          )
        }


        {scopeType
          === "chat_channel"
          && selectedChatChannel
          && (
            <div className="mt-5 flex items-start gap-3 rounded-xl border border-violet-100 bg-violet-50 p-4">

              <MessageSquare className="mt-0.5 h-5 w-5 shrink-0 text-violet-600" />

              <div>

                <p className="text-sm font-semibold text-violet-900">
                  {
                    selectedChatChannel.name
                  }
                </p>

                <p className="mt-1 text-sm text-violet-700">
                  {
                    selectedChatChannel.type
                  }
                  {" · "}
                  {
                    selectedChatChannel.status
                  }
                  {" · "}
                  Blank channel limits
                  inherit the effective
                  KB quota.
                </p>

              </div>

            </div>
          )
        }

      </section>


      {scopeType
        === "knowledge_base"
        && !knowledgeBaseId
        && (
          <div className="rounded-xl border border-dashed bg-white p-8 text-center">

            <Database className="mx-auto h-8 w-8 text-slate-400" />

            <p className="mt-3 font-medium text-slate-700">
              Select a knowledge base
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Choose a KB above to view
              its usage and limits.
            </p>

          </div>
        )
      }


      {scopeType
        === "chat_channel"
        && !knowledgeBaseId
        && (
          <div className="rounded-xl border border-dashed bg-white p-8 text-center">

            <Database className="mx-auto h-8 w-8 text-slate-400" />

            <p className="mt-3 font-medium text-slate-700">
              Select a knowledge base
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Select a KB first, then
              choose one of its chat
              channels.
            </p>

          </div>
        )
      }


      {scopeType
        === "chat_channel"
        && Boolean(
          knowledgeBaseId,
        )
        && !chatChannelId
        && (
          <div className="rounded-xl border border-dashed bg-white p-8 text-center">

            <MessageSquare className="mx-auto h-8 w-8 text-slate-400" />

            <p className="mt-3 font-medium text-slate-700">
              Select a chat channel
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Choose a channel to view
              its usage and limits.
            </p>

          </div>
        )
      }


      {activeStatusLoading && (
        <div className="rounded-xl border bg-white p-6 text-sm text-slate-500">
          Loading usage...
        </div>
      )}


      {Boolean(
        activeStatusError,
      ) && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load usage
          information.
        </div>
      )}


      {scopeType
        === "tenant"
        && (
          <ScopeUsage
            scope={
              tenantScope
            }
            title="Effective tenant quota"
            allowed={
              tenantStatusData
                ?.allowed
            }
          />
        )
      }


      {scopeType
        === "knowledge_base"
        && Boolean(
          knowledgeBaseId,
        )
        && (
          <ScopeUsage
            scope={
              kbScope
            }
            title={
              selectedKnowledgeBase
                ? `Effective quota · ${selectedKnowledgeBase.name}`
                : "Effective knowledge-base quota"
            }
            allowed={
              kbStatusData
                ?.allowed
            }
          />
        )
      }


      {scopeType
        === "chat_channel"
        && Boolean(
          knowledgeBaseId,
        )
        && Boolean(
          chatChannelId,
        )
        && (
          <ScopeUsage
            scope={
              channelScope
            }
            title={
              selectedChatChannel
                ? `Effective quota · ${selectedChatChannel.name}`
                : "Effective chat-channel quota"
            }
            allowed={
              channelStatusData
                ?.allowed
            }
          />
        )
      }


      {activeLimitLoading && (
        <div className="rounded-xl border bg-white p-6 text-sm text-slate-500">
          Loading limits...
        </div>
      )}


      {Boolean(
        activeLimitError,
      ) && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Failed to load limit
          configuration.
        </div>
      )}


      {scopeType
        === "tenant"
        && !tenantLimitLoading
        && !Boolean(
          tenantLimitError,
        )
        && tenantLimitData
          !== undefined
        && (
          <LimitEditor
            editorKey="tenant"
            title="Tenant overrides"
            description="Blank values inherit the platform default. A value of 0 blocks that metric."
            availabilityLabel="Usage enabled for this tenant"
            inheritedLabel="Platform default"
            initialLimit={
              tenantLimitData
            }
            effectiveScope={
              tenantScope
            }
            saving={
              updateTenantLimit
                .isPending
            }
            error={
              updateTenantLimit
                .error
            }
            onSave={(
              payload,
            ) =>
              updateTenantLimit
                .mutateAsync(
                  payload,
                )
            }
          />
        )
      }


      {scopeType
        === "knowledge_base"
        && Boolean(
          knowledgeBaseId,
        )
        && !kbLimitLoading
        && !Boolean(
          kbLimitError,
        )
        && kbLimitData
          !== undefined
        && (
          <LimitEditor
            editorKey={
              `kb-${knowledgeBaseId}`
            }
            title="Knowledge Base overrides"
            description="Blank values inherit the effective tenant quota. A value of 0 blocks that metric for this KB."
            availabilityLabel="Usage enabled for this knowledge base"
            inheritedLabel="Inherited from tenant"
            initialLimit={
              kbLimitData
            }
            effectiveScope={
              kbScope
            }
            saving={
              updateKnowledgeBaseLimit
                .isPending
            }
            error={
              updateKnowledgeBaseLimit
                .error
            }
            onSave={(
              payload,
            ) =>
              updateKnowledgeBaseLimit
                .mutateAsync({
                  knowledgeBaseId,
                  payload,
                })
            }
          />
        )
      }


      {scopeType
        === "chat_channel"
        && Boolean(
          knowledgeBaseId,
        )
        && Boolean(
          chatChannelId,
        )
        && !channelLimitLoading
        && !Boolean(
          channelLimitError,
        )
        && channelLimitData
          !== undefined
        && (
          <LimitEditor
            editorKey={
              `channel-${chatChannelId}`
            }
            title="Chat Channel overrides"
            description="Blank values inherit the effective knowledge-base quota. A value of 0 blocks that metric for this channel."
            availabilityLabel="Usage enabled for this chat channel"
            inheritedLabel="Inherited from knowledge base"
            initialLimit={
              channelLimitData
            }
            effectiveScope={
              channelScope
            }
            saving={
              updateChatChannelLimit
                .isPending
            }
            error={
              updateChatChannelLimit
                .error
            }
            onSave={(
              payload,
            ) =>
              updateChatChannelLimit
                .mutateAsync({
                  knowledgeBaseId,
                  chatChannelId,
                  payload,
                })
            }
          />
        )
      }

    </div>
  );
}