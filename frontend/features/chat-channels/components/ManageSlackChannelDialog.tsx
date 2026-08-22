"use client";

import {
  useEffect,
  useState,
} from "react";

import {
  MessageSquare,
  Trash2,
} from "lucide-react";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import {
  useChatChannelSlackConfiguration,
  useConnectChatChannelSlack,
  useDisconnectChatChannelSlack,
} from "../hooks";

import type {
  ChatChannel,
} from "../types";


type Props = {
  channel: ChatChannel;
};


export default function ManageSlackChannelDialog({
  channel,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    disconnectOpen,
    setDisconnectOpen,
  ] = useState(false);

  const [
    slackTeamId,
    setSlackTeamId,
  ] = useState("");

  const [
    slackTeamName,
    setSlackTeamName,
  ] = useState("");

  const [
    botUserId,
    setBotUserId,
  ] = useState("");

  const [
    botToken,
    setBotToken,
  ] = useState("");

  const [
    signingSecret,
    setSigningSecret,
  ] = useState("");

  const [
    respondToMentions,
    setRespondToMentions,
  ] = useState(true);

  const [
    respondToDirectMessages,
    setRespondToDirectMessages,
  ] = useState(false);

  const [
    allowedChannelsText,
    setAllowedChannelsText,
  ] = useState("");

  const [
    formError,
    setFormError,
  ] = useState<
    string | null
  >(null);


  const {
    data:
      configuration,

    isLoading,

    error,

  } = useChatChannelSlackConfiguration(
    channel.id,
    open,
  );


  const connectMutation =
    useConnectChatChannelSlack(
      channel.id,
    );


  const disconnectMutation =
    useDisconnectChatChannelSlack(
      channel.id,
    );


  useEffect(
    () => {
      if (!configuration) {
        return;
      }

      setSlackTeamId(
        configuration.slack_team_id
        || "",
      );

      setSlackTeamName(
        configuration.slack_team_name
        || "",
      );

      setBotUserId(
        configuration.bot_user_id
        || "",
      );

      setRespondToMentions(
        configuration
          .respond_to_mentions,
      );

      setRespondToDirectMessages(
        configuration
          .respond_to_direct_messages,
      );

      setAllowedChannelsText(
        configuration
          .allowed_slack_channel_ids
          .join("\n"),
      );

      /*
       * Secrets are intentionally
       * not returned by the backend.
       */
      setBotToken("");
      setSigningSecret("");
    },
    [
      configuration,
    ],
  );


  function resetForm() {
    setSlackTeamId("");
    setSlackTeamName("");
    setBotUserId("");
    setBotToken("");
    setSigningSecret("");
    setRespondToMentions(
      true,
    );
    setRespondToDirectMessages(
      false,
    );
    setAllowedChannelsText("");
    setFormError(
      null,
    );
  }


  function parseAllowedChannels() {
    const rawValues =
      allowedChannelsText
        .split(
          /[\n,]+/,
        )
        .map(
          (
            value,
          ) =>
            value.trim(),
        )
        .filter(
          Boolean,
        );

    return Array.from(
      new Set(
        rawValues,
      ),
    );
  }


  async function save() {
    setFormError(
      null,
    );

    const teamId =
      slackTeamId.trim();

    const token =
      botToken.trim();

    const secret =
      signingSecret.trim();

    if (!teamId) {
      setFormError(
        "Slack Team ID is required.",
      );

      return;
    }

    /*
     * Because secrets are never
     * returned by GET, they must be
     * entered whenever saving.
     *
     * Later we can add a PATCH-style
     * backend endpoint so existing
     * secrets do not need re-entry.
     */
    if (!token) {
      setFormError(
        "Slack bot token is required.",
      );

      return;
    }

    if (!secret) {
      setFormError(
        "Slack signing secret is required.",
      );

      return;
    }

    try {
      await connectMutation
        .mutateAsync({
          slack_team_id:
            teamId,

          slack_team_name:
            slackTeamName.trim()
            || null,

          bot_user_id:
            botUserId.trim()
            || null,

          bot_token:
            token,

          signing_secret:
            secret,

          respond_to_mentions:
            respondToMentions,

          respond_to_direct_messages:
            respondToDirectMessages,

          allowed_slack_channel_ids:
            parseAllowedChannels(),
        });

      setBotToken("");
      setSigningSecret("");

    } catch (
      error
    ) {
      console.error(
        "Unable to save Slack configuration.",
        error,
      );

      setFormError(
        "Unable to save Slack configuration.",
      );
    }
  }


  async function disconnect() {
    try {
      await disconnectMutation
        .mutateAsync();

      setDisconnectOpen(
        false,
      );

      setOpen(
        false,
      );

      resetForm();

    } catch (
      error
    ) {
      console.error(
        "Unable to disconnect Slack.",
        error,
      );
    }
  }


  const isConfigured =
    !!configuration
    && configuration.configured;


  return (
    <>
      <button
        type="button"
        onClick={() =>
          setOpen(
            true,
          )
        }
        className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <MessageSquare className="h-4 w-4" />

        Manage Slack
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={(
          nextOpen,
        ) => {
          setOpen(
            nextOpen,
          );

          if (
            !nextOpen
          ) {
            setFormError(
              null,
            );

            setBotToken("");
            setSigningSecret("");
          }
        }}
      >
        <DialogContent className="max-h-[90vh] overflow-y-auto sm:max-w-2xl">

          <DialogHeader>

            <DialogTitle>
              Manage Slack
            </DialogTitle>

            <DialogDescription>
              Connect this NXTGEN
              knowledge base to a Slack
              workspace.
            </DialogDescription>

          </DialogHeader>


          {isLoading && (
            <div className="rounded-xl border bg-slate-50 p-4 text-sm text-slate-500">
              Loading Slack configuration...
            </div>
          )}


          {!isLoading && (
            <div className="space-y-5">

              {isConfigured && (
                <div className="rounded-xl border border-green-200 bg-green-50 p-4">

                  <p className="text-sm font-semibold text-green-800">
                    Slack workspace connected
                  </p>

                  <p className="mt-1 text-sm text-green-700">
                    {
                      configuration
                        .slack_team_name
                      || configuration
                        .slack_team_id
                    }
                  </p>

                </div>
              )}


              {error && !configuration && (
                <div className="rounded-xl border bg-slate-50 p-4 text-sm text-slate-500">
                  Slack has not been
                  configured yet.
                </div>
              )}


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Slack Team ID
                </label>

                <input
                  type="text"
                  value={
                    slackTeamId
                  }
                  onChange={(
                    event,
                  ) =>
                    setSlackTeamId(
                      event
                        .target
                        .value,
                    )
                  }
                  placeholder="T0123456789"
                  className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400"
                />

                <p className="mt-1 text-xs text-slate-400">
                  The Slack workspace
                  identifier.
                </p>

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Workspace name
                </label>

                <input
                  type="text"
                  value={
                    slackTeamName
                  }
                  onChange={(
                    event,
                  ) =>
                    setSlackTeamName(
                      event
                        .target
                        .value,
                    )
                  }
                  placeholder="ACME Engineering"
                  className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400"
                />

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Bot User ID
                </label>

                <input
                  type="text"
                  value={
                    botUserId
                  }
                  onChange={(
                    event,
                  ) =>
                    setBotUserId(
                      event
                        .target
                        .value,
                    )
                  }
                  placeholder="U0123456789"
                  className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400"
                />

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Bot token
                </label>

                <input
                  type="password"
                  value={
                    botToken
                  }
                  onChange={(
                    event,
                  ) =>
                    setBotToken(
                      event
                        .target
                        .value,
                    )
                  }
                  placeholder="xoxb-..."
                  autoComplete="off"
                  className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400"
                />

                {isConfigured && (
                  <p className="mt-1 text-xs text-slate-400">
                    Secret is not displayed.
                    Re-enter it when saving.
                  </p>
                )}

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Signing secret
                </label>

                <input
                  type="password"
                  value={
                    signingSecret
                  }
                  onChange={(
                    event,
                  ) =>
                    setSigningSecret(
                      event
                        .target
                        .value,
                    )
                  }
                  placeholder="Slack signing secret"
                  autoComplete="off"
                  className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm outline-none focus:border-slate-400"
                />

                {isConfigured && (
                  <p className="mt-1 text-xs text-slate-400">
                    Secret is not displayed.
                    Re-enter it when saving.
                  </p>
                )}

              </div>


              <div className="rounded-xl border p-4">

                <label className="flex items-start gap-3">

                  <input
                    type="checkbox"
                    checked={
                      respondToMentions
                    }
                    onChange={(
                      event,
                    ) =>
                      setRespondToMentions(
                        event
                          .target
                          .checked,
                      )
                    }
                    className="mt-1 h-4 w-4"
                  />

                  <span>

                    <span className="block text-sm font-medium text-slate-800">
                      Respond to mentions
                    </span>

                    <span className="mt-1 block text-xs text-slate-500">
                      Respond when users
                      mention the NXTGEN bot
                      in Slack channels.
                    </span>

                  </span>

                </label>


                <label className="mt-4 flex items-start gap-3">

                  <input
                    type="checkbox"
                    checked={
                      respondToDirectMessages
                    }
                    onChange={(
                      event,
                    ) =>
                      setRespondToDirectMessages(
                        event
                          .target
                          .checked,
                      )
                    }
                    className="mt-1 h-4 w-4"
                  />

                  <span>

                    <span className="block text-sm font-medium text-slate-800">
                      Respond to direct messages
                    </span>

                    <span className="mt-1 block text-xs text-slate-500">
                      Allow users to message
                      the NXTGEN bot directly.
                    </span>

                  </span>

                </label>

              </div>


              <div>

                <label className="text-sm font-medium text-slate-700">
                  Allowed Slack channels
                </label>

                <textarea
                  value={
                    allowedChannelsText
                  }
                  onChange={(
                    event,
                  ) =>
                    setAllowedChannelsText(
                      event
                        .target
                        .value,
                    )
                  }
                  rows={
                    5
                  }
                  placeholder={
                    [
                      "C0123456789",
                      "C9876543210",
                    ].join("\n")
                  }
                  className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 font-mono text-sm outline-none focus:border-slate-400"
                />

                <p className="mt-1 text-xs text-slate-400">
                  One Slack channel ID per
                  line. Leave empty to allow
                  all channels permitted by
                  the Slack app.
                </p>

              </div>


              {formError && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                  {
                    formError
                  }
                </div>
              )}

            </div>
          )}


          <DialogFooter className="mt-5 flex-col gap-2 sm:flex-row sm:justify-between">

            <div>

              {isConfigured && (
                <button
                  type="button"
                  onClick={() =>
                    setDisconnectOpen(
                      true,
                    )
                  }
                  className="inline-flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
                >
                  <Trash2 className="h-4 w-4" />

                  Disconnect Slack
                </button>
              )}

            </div>


            <div className="flex gap-2">

              <button
                type="button"
                onClick={() =>
                  setOpen(
                    false,
                  )
                }
                className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                Cancel
              </button>


              <button
                type="button"
                onClick={
                  save
                }
                disabled={
                  connectMutation
                    .isPending
                }
                className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {
                  connectMutation
                    .isPending
                    ? "Saving..."
                    : (
                      isConfigured
                        ? "Update Slack"
                        : "Connect Slack"
                    )
                }
              </button>

            </div>

          </DialogFooter>

        </DialogContent>
      </Dialog>


      <Dialog
        open={
          disconnectOpen
        }
        onOpenChange={(
          nextOpen,
        ) => {
          if (
            disconnectMutation
              .isPending
          ) {
            return;
          }

          setDisconnectOpen(
            nextOpen,
          );
        }}
      >
        <DialogContent className="sm:max-w-md">

          <DialogHeader>

            <DialogTitle>
              Disconnect Slack?
            </DialogTitle>

            <DialogDescription>
              This removes the Slack
              workspace credentials from
              this channel. Existing
              conversation history will
              remain.
            </DialogDescription>

          </DialogHeader>


          {configuration && (
            <div className="rounded-xl border bg-slate-50 p-4">

              <p className="font-medium text-slate-900">
                {
                  configuration
                    .slack_team_name
                  || "Slack workspace"
                }
              </p>

              <p className="mt-1 font-mono text-xs text-slate-500">
                {
                  configuration
                    .slack_team_id
                }
              </p>

            </div>
          )}


          {disconnectMutation
            .isError
            && (
              <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                Unable to disconnect Slack.
              </div>
            )}


          <DialogFooter>

            <button
              type="button"
              onClick={() =>
                setDisconnectOpen(
                  false,
                )
              }
              disabled={
                disconnectMutation
                  .isPending
              }
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>


            <button
              type="button"
              onClick={
                disconnect
              }
              disabled={
                disconnectMutation
                  .isPending
              }
              className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4" />

              {
                disconnectMutation
                  .isPending
                  ? "Disconnecting..."
                  : "Disconnect Slack"
              }
            </button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}