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
  useDeleteChatChannel,
  useUpdateChatChannel,
} from "../hooks";

import type {
  ChatChannel,
} from "../types";


type Props = {
  channel: ChatChannel;

  knowledgeBaseId: string;
};


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
  ] = useState(
    channel.name,
  );

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
    copied,
    setCopied,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(
    null,
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

    setName(
      channel.name,
    );

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

    setError(
      null,
    );

    setCopied(
      false,
    );
  }, [
    open,
    channel,
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


  function getAllowedOrigins() {
    return origins
      .split("\n")
      .map(
        (value) =>
          value.trim(),
      )
      .filter(
        Boolean,
      );
  }


  async function save() {
    const normalizedName =
      name.trim();

    if (!normalizedName) {
      setError(
        "Channel name is required.",
      );

      return;
    }

    const allowedOrigins =
      getAllowedOrigins();

    if (
      allowedOrigins.length
      === 0
    ) {
      setError(
        "At least one allowed website is required.",
      );

      return;
    }

    setError(
      null,
    );

    try {
      await updateMutation
        .mutateAsync({
          id:
            channel.id,

          data: {
            name:
              normalizedName,

            configuration: {
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
            },
          },
        });

      setOpen(
        false,
      );

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
    const nextStatus =
      channel.status
      === "ACTIVE"
        ? "INACTIVE"
        : "ACTIVE";

    try {
      await updateMutation
        .mutateAsync({
          id:
            channel.id,

          data: {
            status:
              nextStatus,
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

      setCopied(
        true,
      );

      window.setTimeout(
        () => {
          setCopied(
            false,
          );
        },
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

      setOpen(
        false,
      );

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
          setOpen(
            true,
          )
        }
        className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        Manage
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={
          setOpen
        }
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
                      ? "Visitors can currently use this chatbot."
                      : "This chatbot is currently disabled."
                  }
                </p>
              </div>


              <button
                type="button"
                onClick={
                  toggleStatus
                }
                disabled={
                  busy
                }
                className={
                  channel.status
                  === "ACTIVE"
                    ? "inline-flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm font-medium text-amber-700 hover:bg-amber-100 disabled:opacity-50"
                    : "inline-flex items-center gap-2 rounded-lg border border-green-200 bg-green-50 px-3 py-2 text-sm font-medium text-green-700 hover:bg-green-100 disabled:opacity-50"
                }
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

              <Label
                htmlFor={`channel-name-${channel.id}`}
              >
                Name
              </Label>

              <Input
                id={`channel-name-${channel.id}`}
                value={
                  name
                }
                onChange={(event) =>
                  setName(
                    event.currentTarget.value,
                  )
                }
              />

            </div>


            <div className="space-y-2">

              <Label
                htmlFor={`channel-origins-${channel.id}`}
              >
                Allowed Websites
              </Label>

              <textarea
                id={`channel-origins-${channel.id}`}
                value={
                  origins
                }
                onChange={(event) =>
                  setOrigins(
                    event.currentTarget.value,
                  )
                }
                rows={
                  4
                }
                className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-blue-500"
                placeholder={
                  "https://example.com\nhttps://www.example.com"
                }
              />

              <p className="text-xs text-slate-500">
                One origin per line.
                Changes take effect
                immediately and do not
                require an API restart.
              </p>

            </div>


            <div className="grid gap-4 md:grid-cols-2">

              <div className="space-y-2">

                <Label
                  htmlFor={`widget-title-${channel.id}`}
                >
                  Widget Title
                </Label>

                <Input
                  id={`widget-title-${channel.id}`}
                  value={
                    widgetTitle
                  }
                  onChange={(event) =>
                    setWidgetTitle(
                      event.currentTarget.value,
                    )
                  }
                />

              </div>


              <div className="space-y-2">

                <Label
                  htmlFor={`widget-placeholder-${channel.id}`}
                >
                  Input Placeholder
                </Label>

                <Input
                  id={`widget-placeholder-${channel.id}`}
                  value={
                    placeholder
                  }
                  onChange={(event) =>
                    setPlaceholder(
                      event.currentTarget.value,
                    )
                  }
                />

              </div>

            </div>


            <div className="space-y-2">

              <Label
                htmlFor={`welcome-${channel.id}`}
              >
                Welcome Message
              </Label>

              <Input
                id={`welcome-${channel.id}`}
                value={
                  welcomeMessage
                }
                onChange={(event) =>
                  setWelcomeMessage(
                    event.currentTarget.value,
                  )
                }
              />

            </div>


            <label className="flex items-start gap-3 rounded-xl border p-4">

              <input
                type="checkbox"
                checked={
                  showSources
                }
                onChange={(event) =>
                  setShowSources(
                    event.currentTarget.checked,
                  )
                }
                className="mt-1 h-4 w-4"
              />

              <div>
                <p className="text-sm font-medium text-slate-900">
                  Show sources
                </p>

                <p className="mt-1 text-xs text-slate-500">
                  Display supporting
                  document names under
                  chatbot answers.
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
                    Paste this before the
                    closing body tag on an
                    allowed website.
                  </p>
                </div>


                <button
                  type="button"
                  onClick={
                    copyEmbed
                  }
                  className="inline-flex items-center gap-2 rounded-lg border bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
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
                {
                  embedCode
                }
              </pre>

            </div>


            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {
                  error
                }
              </div>
            )}


            <div className="rounded-xl border border-red-100 bg-red-50 p-4">

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

                <div>
                  <p className="text-sm font-medium text-red-900">
                    Delete Channel
                  </p>

                  <p className="mt-1 text-xs text-red-700">
                    Permanently removes this
                    channel and its channel
                    conversations.
                  </p>
                </div>


                <button
                  type="button"
                  onClick={
                    deleteChannel
                  }
                  disabled={
                    busy
                  }
                  className="inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
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
                setOpen(
                  false,
                )
              }
              disabled={
                busy
              }
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>


            <button
              type="button"
              onClick={
                save
              }
              disabled={
                busy
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {
                updateMutation.isPending
                  ? "Saving..."
                  : "Save Changes"
              }
            </button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}