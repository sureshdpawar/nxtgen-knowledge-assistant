"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  Check,
  Copy,
  KeyRound,
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
  useChatChannelApiKeys,
  useCreateChatChannelApiKey,
  useDeleteChatChannel,
  useRevokeChatChannelApiKey,
  useUpdateChatChannel,
} from "../hooks";

import type {
  ChatChannel,
  CreatedChatChannelApiKey,
} from "../types";


type Props = {
  channel: ChatChannel;

  knowledgeBaseId: string;
};


export default function ManagePublicApiChannelDialog({
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
    newKeyName,
    setNewKeyName,
  ] = useState(
    "",
  );

  const [
    createdKey,
    setCreatedKey,
  ] = useState<
    CreatedChatChannelApiKey
    | null
  >(
    null,
  );

  const [
    copiedSecret,
    setCopiedSecret,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<
    string | null
  >(
    null,
  );


  const {
    data:
      apiKeys = [],

    isLoading:
      keysLoading,

  } = useChatChannelApiKeys(
    open
      ? channel.id
      : "",
  );


  const createKeyMutation =
    useCreateChatChannelApiKey(
      channel.id,
    );


  const revokeKeyMutation =
    useRevokeChatChannelApiKey(
      channel.id,
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

    setNewKeyName(
      "",
    );

    setCreatedKey(
      null,
    );

    setCopiedSecret(
      false,
    );

    setError(
      null,
    );
  }, [
    open,
    channel,
  ]);


  const busy =
    createKeyMutation.isPending
    || revokeKeyMutation.isPending
    || updateMutation.isPending
    || deleteMutation.isPending;


  function formatDate(
    value:
      string | null,
  ) {
    if (!value) {
      return "Never";
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
      return value;
    }

    return date
      .toLocaleString();
  }


  async function saveName() {
    const normalizedName =
      name.trim();

    if (!normalizedName) {
      setError(
        "Channel name is required.",
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

    setError(
      null,
    );

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


  async function createApiKey() {
    const normalizedName =
      newKeyName.trim();

    if (!normalizedName) {
      setError(
        "API key name is required.",
      );

      return;
    }

    setError(
      null,
    );

    setCreatedKey(
      null,
    );

    try {
      const result =
        await createKeyMutation
          .mutateAsync(
            normalizedName,
          );

      setCreatedKey(
        result,
      );

      setNewKeyName(
        "",
      );

      setCopiedSecret(
        false,
      );

    } catch (
      createError
    ) {
      console.error(
        createError,
      );

      setError(
        "Unable to create API key.",
      );
    }
  }


  async function copySecret() {
    if (
      !createdKey
      ?.api_key
    ) {
      return;
    }

    try {
      await navigator
        .clipboard
        .writeText(
          createdKey.api_key,
        );

      setCopiedSecret(
        true,
      );

      window.setTimeout(
        () => {
          setCopiedSecret(
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
        "Unable to copy API key.",
      );
    }
  }


  async function revokeKey(
    keyId: string,
    keyName: string,
  ) {
    const confirmed =
      window.confirm(
        `Revoke API key "${keyName}"? Applications using this key will immediately stop working.`,
      );

    if (!confirmed) {
      return;
    }

    setError(
      null,
    );

    try {
      await revokeKeyMutation
        .mutateAsync(
          keyId,
        );

    } catch (
      revokeError
    ) {
      console.error(
        revokeError,
      );

      setError(
        "Unable to revoke API key.",
      );
    }
  }


  async function deleteChannel() {
    const confirmed =
      window.confirm(
        `Delete "${channel.name}"? All API keys and channel conversations will also be removed.`,
      );

    if (!confirmed) {
      return;
    }

    setError(
      null,
    );

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
        Manage API
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
              Manage Public API Channel
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
                      ? "API requests using active keys are currently allowed."
                      : "All API access through this channel is currently disabled."
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
                htmlFor={`public-api-name-${channel.id}`}
              >
                Name
              </Label>

              <Input
                id={`public-api-name-${channel.id}`}
                value={
                  name
                }
                onChange={(event) =>
                  setName(
                    event
                      .currentTarget
                      .value,
                  )
                }
              />

            </div>


            <div className="rounded-xl border p-4">

              <div className="flex items-start gap-3">

                <div className="rounded-lg bg-blue-100 p-2">

                  <KeyRound className="h-5 w-5 text-blue-700" />

                </div>


                <div>

                  <p className="text-sm font-medium text-slate-900">
                    Create API Key
                  </p>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    The secret key is shown
                    only once. Store it
                    securely before closing
                    this dialog.
                  </p>

                </div>

              </div>


              <div className="mt-4 flex flex-col gap-2 sm:flex-row">

                <Input
                  value={
                    newKeyName
                  }
                  onChange={(event) =>
                    setNewKeyName(
                      event
                        .currentTarget
                        .value,
                    )
                  }
                  placeholder="Example: Production"
                  disabled={
                    busy
                  }
                />


                <button
                  type="button"
                  onClick={
                    createApiKey
                  }
                  disabled={
                    busy
                  }
                  className="shrink-0 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {
                    createKeyMutation
                      .isPending
                      ? "Creating..."
                      : "Generate Key"
                  }
                </button>

              </div>

            </div>


            {createdKey && (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">

                <p className="text-sm font-semibold text-amber-900">
                  Copy this key now
                </p>


                <p className="mt-1 text-xs text-amber-800">
                  This secret will not be
                  displayed again after you
                  close or refresh this page.
                </p>


                <div className="mt-4 flex items-start gap-2">

                  <code className="min-w-0 flex-1 break-all rounded-lg bg-slate-950 p-3 text-xs leading-5 text-slate-100">
                    {
                      createdKey.api_key
                    }
                  </code>


                  <button
                    type="button"
                    onClick={
                      copySecret
                    }
                    className="inline-flex shrink-0 items-center gap-2 rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm font-medium text-amber-900 hover:bg-amber-100"
                  >
                    {
                      copiedSecret
                        ? (
                          <Check className="h-4 w-4 text-green-600" />
                        )
                        : (
                          <Copy className="h-4 w-4" />
                        )
                    }

                    {
                      copiedSecret
                        ? "Copied"
                        : "Copy"
                    }
                  </button>

                </div>

              </div>
            )}


            <div>

              <div className="flex items-center justify-between gap-4">

                <div>

                  <h3 className="text-sm font-semibold text-slate-900">
                    API Keys
                  </h3>

                  <p className="mt-1 text-xs text-slate-500">
                    Existing secret values
                    cannot be retrieved.
                  </p>

                </div>

              </div>


              {keysLoading && (
                <div className="mt-4 rounded-lg border p-4 text-sm text-slate-500">
                  Loading API keys...
                </div>
              )}


              {!keysLoading
                && apiKeys.length
                === 0
                && (
                  <div className="mt-4 rounded-lg border border-dashed bg-slate-50 p-5 text-center">

                    <p className="text-sm font-medium text-slate-800">
                      No API keys
                    </p>

                    <p className="mt-1 text-xs text-slate-500">
                      Generate a key above
                      to start using this
                      Public API channel.
                    </p>

                  </div>
                )}


              {!keysLoading
                && apiKeys.length
                > 0
                && (
                  <div className="mt-4 space-y-3">

                    {apiKeys.map(
                      (
                        apiKey,
                      ) => (
                        <div
                          key={
                            apiKey.id
                          }
                          className="flex flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between"
                        >

                          <div className="min-w-0">

                            <div className="flex flex-wrap items-center gap-2">

                              <p className="font-medium text-slate-900">
                                {
                                  apiKey.name
                                }
                              </p>


                              <span
                                className={
                                  apiKey.active
                                    ? "rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700"
                                    : "rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600"
                                }
                              >
                                {
                                  apiKey.active
                                    ? "ACTIVE"
                                    : "REVOKED"
                                }
                              </span>

                            </div>


                            <p className="mt-2 font-mono text-xs text-slate-500">
                              {
                                apiKey.key_prefix
                              }
                              ...
                            </p>


                            <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-xs text-slate-400">

                              <span>
                                Last used:{" "}
                                {
                                  formatDate(
                                    apiKey
                                      .last_used_at,
                                  )
                                }
                              </span>


                              <span>
                                Created:{" "}
                                {
                                  formatDate(
                                    apiKey
                                      .created_at,
                                  )
                                }
                              </span>

                            </div>

                          </div>


                          {apiKey.active && (
                            <button
                              type="button"
                              onClick={() =>
                                revokeKey(
                                  apiKey.id,
                                  apiKey.name,
                                )
                              }
                              disabled={
                                busy
                              }
                              className="shrink-0 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100 disabled:opacity-50"
                            >
                              Revoke
                            </button>
                          )}

                        </div>
                      ),
                    )}

                  </div>
                )}

            </div>


            <div className="rounded-xl border bg-slate-50 p-4">

              <p className="text-sm font-medium text-slate-900">
                Authentication
              </p>


              <p className="mt-2 text-xs leading-5 text-slate-600">
                Send the API key as a Bearer
                token on requests to the
                Public API.
              </p>


              <pre className="mt-3 overflow-x-auto rounded-lg bg-slate-950 p-4 text-xs leading-5 text-slate-100">
{`Authorization: Bearer nxtgen_pk_...

POST /public/v1/chat

{
  "message": "Your question"
}`}
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
                    This permanently removes
                    the channel, its API keys,
                    and its channel
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
                  className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg bg-red-600 px-3 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
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
              Close
            </button>


            <button
              type="button"
              onClick={
                saveName
              }
              disabled={
                busy
              }
              className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {
                updateMutation
                  .isPending
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