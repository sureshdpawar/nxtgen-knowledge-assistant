"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Check,
  Copy,
  Power,
  ShieldCheck,
  Trash2,
} from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  Input,
} from "@/components/ui/input";

import {
  Label,
} from "@/components/ui/label";

import {
  useAgents,
} from "@/features/agents/hooks";

import {
  useTools,
} from "@/features/tools/hooks";

import {
  useDeleteChatChannel,
  useUpdateChatChannel,
} from "../hooks";

import type {
  ChatChannel,
  WebsiteExecutionMode,
} from "../types";


type Props = {
  channel: ChatChannel;
  knowledgeBaseId: string;
};


const CONTACT_FIELDS = [
  {
    name: "first_name",
    label: "First name",
    required: true,
    input_type: "text" as const,
    placeholder: "First name",
  },
  {
    name: "last_name",
    label: "Last name",
    required: true,
    input_type: "text" as const,
    placeholder: "Last name",
  },
  {
    name: "phone",
    label: "Phone",
    required: true,
    input_type: "tel" as const,
    placeholder: "Phone number",
  },
  {
    name: "email",
    label: "Email",
    required: false,
    input_type: "email" as const,
    placeholder: "Email (optional)",
  },
];


export default function ManageWebsiteChannelDialog({
  channel,
  knowledgeBaseId,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    name,
    setName,
  ] = useState(channel.name);

  const [
    origins,
    setOrigins,
  ] = useState(
    (
      channel.configuration
        .allowed_origins
      || []
    ).join("\n"),
  );

  const [
    widgetTitle,
    setWidgetTitle,
  ] = useState(
    channel.configuration
      .widget_title
    || channel.name,
  );

  const [
    welcomeMessage,
    setWelcomeMessage,
  ] = useState(
    channel.configuration
      .welcome_message
    || "Hi! How can I help?",
  );

  const [
    placeholder,
    setPlaceholder,
  ] = useState(
    channel.configuration
      .placeholder
    || "Ask me anything...",
  );

  const [
    showSources,
    setShowSources,
  ] = useState(
    channel.configuration
      .show_sources
    ?? true,
  );

  const [
    executionMode,
    setExecutionMode,
  ] = useState<WebsiteExecutionMode>(
    channel.configuration.execution_mode ?? "KNOWLEDGE"
  );

  const [
    agentId,
    setAgentId,
  ] = useState(
    channel.configuration
      .agent_id
    || "",
  );

  const [
    preChatEnabled,
    setPreChatEnabled,
  ] = useState(
    channel.configuration
      .pre_chat
      ?.enabled
    ?? false,
  );

  const [
    sessionStartTool,
    setSessionStartTool,
  ] = useState<string>(
    channel.configuration.session_start_action?.tool_name ?? ""
  );

  const [
    autoExecuteTools,
    setAutoExecuteTools,
  ] = useState<string[]>(
    channel.configuration
      .auto_execute_tools
    || [],
  );

  const [
    copied,
    setCopied,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(null);

  const agentsQuery =
    useAgents(open);

  const toolsQuery =
    useTools(
      open
      && executionMode
        === "AGENT",
    );

  const activeAgents =
    (
      agentsQuery.data
      || []
    ).filter(
      (agent) =>
        agent.status
        === "ACTIVE",
    );

  const selectedAgent =
    activeAgents.find(
      (agent) =>
        agent.id
        === agentId,
    )
    ?? null;

  const assignedWriteTools =
    (
      toolsQuery.data
      || []
    ).filter(
      (tool) =>
        tool.is_active
        && tool.risk_level
          === "WRITE"
        && (
          selectedAgent
            ?.tool_ids
            ?? []
        ).includes(
          tool.id,
        ),
    );

  const updateMutation =
    useUpdateChatChannel(
      knowledgeBaseId,
    );

  const deleteMutation =
    useDeleteChatChannel(
      knowledgeBaseId,
    );


  useEffect(() => {
    if (!open) {
      return;
    }

    setName(channel.name);

    setOrigins(
      (
        channel.configuration
          .allowed_origins
        || []
      ).join("\n"),
    );

    setWidgetTitle(
      channel.configuration
        .widget_title
      || channel.name,
    );

    setWelcomeMessage(
      channel.configuration
        .welcome_message
      || "Hi! How can I help?",
    );

    setPlaceholder(
      channel.configuration
        .placeholder
      || "Ask me anything...",
    );

    setShowSources(
      channel.configuration
        .show_sources
      ?? true,
    );

    setExecutionMode(
      channel.configuration.execution_mode ?? "KNOWLEDGE"
    );

    setAgentId(
      channel.configuration
        .agent_id
      || "",
    );

    setPreChatEnabled(
      channel.configuration
        .pre_chat
        ?.enabled
      ?? false,
    );

    setSessionStartTool(
      channel.configuration.session_start_action?.tool_name ?? ""
    );

    setAutoExecuteTools(
      channel.configuration
        .auto_execute_tools
      || [],
    );

    setError(null);
    setCopied(false);

  }, [
    open,
    channel,
  ]);


  useEffect(() => {
    if (
      !open
      || executionMode
        !== "AGENT"
      || !selectedAgent
      || toolsQuery.isLoading
    ) {
      return;
    }

    const assignedWriteToolNames =
      new Set(
        assignedWriteTools.map(
          (tool) =>
            tool.name,
        ),
      );

    setAutoExecuteTools(
      (current) =>
        current.filter(
          (name) =>
            assignedWriteToolNames.has(
              name,
            ),
        ),
    );
  }, [
    open,
    executionMode,
    selectedAgent,
    toolsQuery.isLoading,
    assignedWriteTools,
  ]);


  const embedCode =
    useMemo(() => {
      if (
        typeof window
        === "undefined"
      ) {
        return "";
      }

      const frontendBase =
        window.location.origin;

      const configuredApiBase =
        process.env
          .NEXT_PUBLIC_API_URL
        || "http://localhost:8000";

      const apiBase =
        configuredApiBase
          .replace(
            /\/api\/v1\/?$/,
            "",
          )
          .replace(
            /\/$/,
            "",
          );

      return [
        "<script",
        "  defer",
        `  src="${frontendBase}/nxtgen-widget.js"`,
        `  data-channel-id="${channel.id}"`,
        `  data-api-base="${apiBase}"`,
        "></script>",
      ].join("\n");
    }, [
      channel.id,
      open,
    ]);


  function parsedLines(
    value: string,
  ) {
    return value
      .split("\n")
      .map(
        (item) =>
          item.trim(),
      )
      .filter(Boolean);
  }


  function toggleAutoExecuteTool(
    toolName: string,
  ) {
    setAutoExecuteTools(
      (current) => {
        if (
          current.includes(
            toolName,
          )
        ) {
          return current.filter(
            (name) =>
              name !== toolName,
          );
        }

        return [
          ...current,
          toolName,
        ];
      },
    );
  }


  async function save() {
    const normalizedName =
      name.trim();

    const allowedOrigins =
      parsedLines(origins);

    if (!normalizedName) {
      setError(
        "Channel name is required.",
      );
      return;
    }

    if (
      allowedOrigins.length
      === 0
    ) {
      setError(
        "At least one allowed website is required.",
      );
      return;
    }

    if (
      executionMode
      === "AGENT"
      && !agentId
    ) {
      setError(
        "Select an active agent for Agent execution.",
      );
      return;
    }

    if (
      executionMode
      === "AGENT"
      && preChatEnabled
      && !sessionStartTool.trim()
    ) {
      setError(
        "Session-start tool is required when contact capture is enabled.",
      );
      return;
    }

    setError(null);

    const assignedWriteToolNames =
      new Set(
        assignedWriteTools.map(
          (tool) =>
            tool.name,
        ),
      );

    const validAutoExecuteTools =
      autoExecuteTools.filter(
        (toolName) =>
          assignedWriteToolNames.has(
            toolName,
          ),
      );

    const nextConfiguration = {
      ...channel.configuration,

      allowed_origins:
        allowedOrigins,

      widget_title:
        widgetTitle.trim()
        || normalizedName,

      welcome_message:
        welcomeMessage.trim(),

      placeholder:
        placeholder.trim()
        || "Ask a question...",

      show_sources:
        showSources,

      execution_mode:
        executionMode,

      agent_id:
        executionMode
        === "AGENT"
          ? agentId
          : null,

      pre_chat:
        executionMode
        === "AGENT"
          ? {
              enabled:
                preChatEnabled,
              title:
                "Before we start",
              submit_label:
                "Start chat",
              fields:
                CONTACT_FIELDS,
            }
          : {
              enabled:
                false,
              title:
                "Before we start",
              submit_label:
                "Start chat",
              fields:
                [],
            },

      session_start_action:
        (
          executionMode
          === "AGENT"
          && preChatEnabled
        )
          ? {
              tool_name:
                sessionStartTool.trim(),

              arguments: {
                name: {
                  template:
                    "{first_name} {last_name}",
                },
                phone: {
                  field:
                    "phone",
                },
                email: {
                  field:
                    "email",
                  omit_if_empty:
                    true,
                },
              },

              context: {
                enquiry_id:
                  "enquiry_id",
              },
            }
          : null,

      auto_execute_tools:
        executionMode
        === "AGENT"
          ? validAutoExecuteTools
          : [],
    };

    try {
      await updateMutation
        .mutateAsync({
          id:
            channel.id,

          data: {
            name:
              normalizedName,

            configuration:
              nextConfiguration,
          },
        });

      setOpen(false);

    } catch (
      saveError
    ) {
      console.error(
        saveError,
      );

      setError(
        "Unable to update channel.",
      );
    }
  }


  async function toggleStatus() {
    try {
      await updateMutation
        .mutateAsync({
          id:
            channel.id,

          data: {
            status:
              (
                channel.status
                === "ACTIVE"
              )
                ? "INACTIVE"
                : "ACTIVE",
          },
        });

    } catch (
      statusError
    ) {
      console.error(
        statusError,
      );

      setError(
        "Unable to update channel status.",
      );
    }
  }


  async function copyEmbed() {
    if (!embedCode) {
      return;
    }

    try {
      await navigator
        .clipboard
        .writeText(
          embedCode,
        );

      setCopied(true);

      window.setTimeout(
        () =>
          setCopied(false),
        2000,
      );

    } catch (
      copyError
    ) {
      console.error(
        copyError,
      );

      setError(
        "Unable to copy embed code.",
      );
    }
  }


  async function deleteChannel() {
    const confirmed =
      window.confirm(
        `Delete "${channel.name}"? This will also remove its channel conversations.`,
      );

    if (!confirmed) {
      return;
    }

    try {
      await deleteMutation
        .mutateAsync(
          channel.id,
        );

      setOpen(false);

    } catch (
      deleteError
    ) {
      console.error(
        deleteError,
      );

      setError(
        "Unable to delete channel.",
      );
    }
  }


  const busy =
    updateMutation.isPending
    || deleteMutation.isPending;


  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(true)
        }
        className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Manage
      </button>


      <Dialog
        open={open}
        onOpenChange={setOpen}
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              Manage Website Channel
            </DialogTitle>
          </DialogHeader>


          <div className="space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border bg-slate-50 p-4">
              <div>
                <p className="text-sm font-medium text-slate-900">
                  Channel Status
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  {
                    channel.status
                    === "ACTIVE"
                      ? "Visitors can currently use this widget."
                      : "This widget is currently disabled."
                  }
                </p>
              </div>

              <button
                type="button"
                onClick={toggleStatus}
                disabled={busy}
                className="inline-flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
              >
                <Power className="h-4 w-4" />

                {
                  channel.status
                  === "ACTIVE"
                    ? "Disable"
                    : "Enable"
                }
              </button>
            </div>


            <div className="space-y-2">
              <Label>
                Name
              </Label>

              <Input
                value={name}
                onChange={(event) => {
                  setName(event.currentTarget.value);
                }}
              />
            </div>


            <div className="space-y-2">
              <Label>
                Allowed Websites
              </Label>

              <textarea
                value={origins}
                onChange={(event) => {
                  setOrigins(event.currentTarget.value);
                }}
                rows={4}
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500"
                placeholder={
                  "https://example.com\nhttps://www.example.com"
                }
              />
            </div>


            <div className="rounded-xl border p-4">
              <p className="text-sm font-semibold text-slate-900">
                Execution
              </p>

              <p className="mt-1 text-xs text-slate-500">
                WEBSITE is the delivery channel. Choose what processes the conversation.
              </p>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>
                    Execution Mode
                  </Label>

                  <select
                    value={executionMode}
                    onChange={(event) => {
                      const mode =
                        event.currentTarget.value as WebsiteExecutionMode;

                      setExecutionMode(mode);

                      if (
                        mode !== "AGENT"
                      ) {
                        setAutoExecuteTools(
                          [],
                        );
                      }
                    }}
                    className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                  >
                    <option value="KNOWLEDGE">
                      Knowledge Assistant
                    </option>

                    <option value="AGENT">
                      Agent
                    </option>
                  </select>
                </div>


                {
                  executionMode
                  === "AGENT"
                  && (
                    <div className="space-y-2">
                      <Label>
                        Agent
                      </Label>

                      <select
                        value={agentId}
                        onChange={(event) => {
                          setAgentId(
                            event.currentTarget.value,
                          );
                          setAutoExecuteTools(
                            [],
                          );
                        }}
                        className="h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                      >
                        <option value="">
                          Select an active agent
                        </option>

                        {
                          activeAgents.map(
                            (agent) => (
                              <option
                                key={agent.id}
                                value={agent.id}
                              >
                                {agent.name}
                              </option>
                            ),
                          )
                        }
                      </select>
                    </div>
                  )
                }
              </div>
            </div>


            {
              executionMode
              === "AGENT"
              && (
                <div className="space-y-5 rounded-xl border p-4">
                  <div>
                    <p className="text-sm font-semibold text-slate-900">
                      Website Agent Governance
                    </p>

                    <p className="mt-1 text-xs leading-5 text-slate-500">
                      Tool risk and execution policy are separate.
                      READ / WRITE describes what a tool can do.
                      AUTO / HUMAN_APPROVAL is resolved for this website execution context.
                    </p>
                  </div>


                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
                    <div className="flex items-start gap-2">
                      <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-slate-600" />

                      <div>
                        <p className="text-sm font-medium text-slate-900">
                          Auto-execution policy for this website
                        </p>

                        <p className="mt-1 text-xs leading-5 text-slate-500">
                          Select only assigned WRITE tools that this channel is explicitly
                          allowed to execute automatically. Unselected WRITE tools continue
                          through the runtime approval path.
                        </p>
                      </div>
                    </div>
                  </div>


                  {!agentId ? (
                    <p className="text-sm text-slate-500">
                      Select an active agent to configure its website execution policy.
                    </p>
                  ) : toolsQuery.isLoading ? (
                    <p className="text-sm text-slate-500">
                      Loading assigned WRITE tools...
                    </p>
                  ) : toolsQuery.isError ? (
                    <p className="text-sm text-red-600">
                      Failed to load tools.
                    </p>
                  ) : assignedWriteTools.length === 0 ? (
                    <p className="text-sm text-slate-500">
                      This agent has no active WRITE tools assigned.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {assignedWriteTools.map(
                        (tool) => {
                          const isAuto =
                            autoExecuteTools.includes(
                              tool.name,
                            );

                          return (
                            <label
                              key={tool.id}
                              className="flex cursor-pointer items-start gap-3 rounded-lg border border-slate-200 p-3 hover:bg-slate-50"
                            >
                              <input
                                type="checkbox"
                                checked={isAuto}
                                onChange={() =>
                                  toggleAutoExecuteTool(
                                    tool.name,
                                  )
                                }
                                className="mt-1 h-4 w-4"
                              />

                              <div className="min-w-0 flex-1">
                                <div className="flex flex-wrap items-center gap-2">
                                  <p className="text-sm font-medium text-slate-900">
                                    {tool.name}
                                  </p>

                                  <span className="rounded-full bg-blue-50 px-2 py-0.5 text-[11px] font-medium text-blue-700">
                                    {tool.tool_type}
                                  </span>

                                  <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[11px] font-medium text-amber-700">
                                    WRITE
                                  </span>

                                  <span
                                    className={
                                      isAuto
                                        ? "rounded-full bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700"
                                        : "rounded-full bg-slate-100 px-2 py-0.5 text-[11px] font-semibold text-slate-700"
                                    }
                                  >
                                    {isAuto
                                      ? "AUTO"
                                      : "HUMAN_APPROVAL"}
                                  </span>
                                </div>

                                <p className="mt-1 text-xs text-slate-500">
                                  {tool.description}
                                </p>

                                <p className="mt-2 text-xs text-slate-500">
                                  {isAuto
                                    ? "This website channel may execute this WRITE tool without a human interrupt."
                                    : "This website channel does not grant auto-execution for this WRITE tool."}
                                </p>
                              </div>
                            </label>
                          );
                        },
                      )}
                    </div>
                  )}


                  <div className="border-t border-slate-200 pt-4">
                    <p className="text-sm font-semibold text-slate-900">
                      Contact Capture MVP
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      First name, last name, phone and optional email before chat.
                    </p>
                  </div>

                  <label className="flex items-start gap-3">
                    <input
                      type="checkbox"
                      checked={preChatEnabled}
                      onChange={(event) => {
                        setPreChatEnabled(event.currentTarget.checked);
                      }}
                      className="mt-1 h-4 w-4"
                    />

                    <div>
                      <p className="text-sm font-medium text-slate-900">
                        Require contact capture before chat
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        Session creation invokes the configured tool deterministically.
                      </p>
                    </div>
                  </label>

                  {
                    preChatEnabled
                    && (
                      <div className="space-y-2">
                        <Label>
                          Session-start tool
                        </Label>

                        <Input
                          value={sessionStartTool}
                          onChange={(event) => {
                            setSessionStartTool(event.currentTarget.value);
                          }}
                          placeholder="create_enquiry"
                        />

                        <p className="text-xs text-slate-500">
                          Session-start execution is deterministic and separate from
                          LLM-proposed tool execution policy.
                        </p>
                      </div>
                    )
                  }
                </div>
              )
            }


            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label>
                  Widget Title
                </Label>

                <Input
                  value={widgetTitle}
                  onChange={(event) => {
                    setWidgetTitle(event.currentTarget.value);
                  }}
                />
              </div>

              <div className="space-y-2">
                <Label>
                  Input Placeholder
                </Label>

                <Input
                  value={placeholder}
                  onChange={(event) => {
                    setPlaceholder(event.currentTarget.value);
                  }}
                />
              </div>
            </div>


            <div className="space-y-2">
              <Label>
                Welcome Message
              </Label>

              <Input
                value={welcomeMessage}
                onChange={(event) => {
                  setWelcomeMessage(event.currentTarget.value);
                }}
              />
            </div>


            <label className="flex items-start gap-3 rounded-xl border p-4">
              <input
                type="checkbox"
                checked={showSources}
                onChange={(event) => {
                  setShowSources(event.currentTarget.checked);
                }}
                className="mt-1 h-4 w-4"
              />

              <div>
                <p className="text-sm font-medium text-slate-900">
                  Show sources
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Existing Knowledge Assistant source behavior is preserved.
                </p>
              </div>
            </label>


            <div className="rounded-xl border bg-slate-50 p-4">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    Embed Code
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Same embed supports Knowledge and Agent execution.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={copyEmbed}
                  className="inline-flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm font-medium text-slate-700"
                >
                  {
                    copied
                      ? (
                        <Check className="h-4 w-4 text-green-600" />
                      )
                      : (
                        <Copy className="h-4 w-4" />
                      )
                  }

                  {
                    copied
                      ? "Copied"
                      : "Copy Embed"
                  }
                </button>
              </div>

              <pre className="mt-4 overflow-x-auto whitespace-pre-wrap break-all rounded-lg bg-slate-950 p-4 text-xs leading-5 text-slate-100">
                {embedCode}
              </pre>
            </div>


            {
              error
              && (
                <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {error}
                </div>
              )
            }


            <div className="rounded-xl border border-red-100 bg-red-50 p-4">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium text-red-900">
                    Delete Channel
                  </p>

                  <p className="mt-1 text-xs text-red-700">
                    Permanently removes this channel.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={deleteChannel}
                  disabled={busy}
                  className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white disabled:opacity-50"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </button>
              </div>
            </div>
          </div>


          <DialogFooter>
            <button
              type="button"
              onClick={() =>
                setOpen(false)
              }
              disabled={busy}
              className="rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="button"
              onClick={save}
              disabled={busy}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
            >
              {
                updateMutation.isPending
                  ? "Saving..."
                  : "Save"
              }
            </button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
