"use client";

import {
  Braces,
  Copy,
  Globe2,
  Hash,
} from "lucide-react";

import {
  useState,
} from "react";

import {
  useChatChannels,
  useCreateChatChannel,
} from "../hooks";

import type {
  ChatChannel,
  CreateChatChannelRequest,
} from "../types";

import ChannelConversationsDialog from "./ChannelConversationsDialog";
import ChannelMetricsPanel from "./ChannelMetricsPanel";
import CreateChatChannelDialog from "./CreateChatChannelDialog";
import ManagePublicApiChannelDialog from "./ManagePublicApiChannelDialog";
import ManageSlackChannelDialog from "./ManageSlackChannelDialog";
import ManageWebsiteChannelDialog from "./ManageWebsiteChannelDialog";


type Props = {
  knowledgeBaseId: string;
};


export default function ChatChannelList({
  knowledgeBaseId,
}: Props) {
  const {
    data:
      channels = [],

    isLoading,

    error,

  } = useChatChannels(
    knowledgeBaseId,
  );

  const createMutation =
    useCreateChatChannel(
      knowledgeBaseId,
    );

  const [
    copiedChannelId,
    setCopiedChannelId,
  ] = useState<
    string | null
  >(
    null,
  );


  async function handleCreate(
    payload:
      CreateChatChannelRequest,
  ) {
    await createMutation
      .mutateAsync(
        payload,
      );
  }


  function buildEmbedCode(
    channel:
      ChatChannel,
  ) {
    if (
      typeof window
      === "undefined"
    ) {
      return "";
    }

    const frontendBase =
      window.location.origin;

    const apiBase =
      process.env
        .NEXT_PUBLIC_API_URL
      || "http://localhost:8000";

    return [
      "<script",
      `  src="${frontendBase}/nxtgen-widget.js"`,
      `  data-channel-id="${channel.id}"`,
      `  data-api-base="${apiBase}"`,
      "></script>",
    ].join("\n");
  }


  async function copyEmbed(
    channel:
      ChatChannel,
  ) {
    const embedCode =
      buildEmbedCode(
        channel,
      );

    if (!embedCode) {
      return;
    }

    try {
      await navigator
        .clipboard
        .writeText(
          embedCode,
        );

      setCopiedChannelId(
        channel.id,
      );

      window.setTimeout(
        () => {
          setCopiedChannelId(
            null,
          );
        },
        2000,
      );

    } catch (
      error
    ) {
      console.error(
        "Unable to copy embed code.",
        error,
      );
    }
  }


  return (
    <div className="space-y-4">

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

        <div>

          <h2 className="text-xl font-semibold text-slate-900">
            Channels
          </h2>

          <p className="mt-1 text-sm text-slate-500">
            Control where users can
            interact with this knowledge
            base.
          </p>

        </div>


        <CreateChatChannelDialog
          knowledgeBaseId={
            knowledgeBaseId
          }
          onCreate={
            handleCreate
          }
        />

      </div>


      {isLoading && (
        <div className="rounded-xl border bg-white p-6 text-sm text-slate-500">
          Loading channels...
        </div>
      )}


      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">
          Failed to load channels.
        </div>
      )}


      {!isLoading
        && !error
        && channels.length
        === 0
        && (
          <div className="rounded-2xl border border-dashed bg-slate-50 p-8 text-center">

            <p className="font-medium text-slate-900">
              No channels yet
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Create a Website chatbot,
              Public API, or Slack
              channel for this knowledge
              base.
            </p>

          </div>
        )}


      {!isLoading
        && !error
        && channels.length
        > 0
        && (
          <div className="grid gap-4 md:grid-cols-2">

            {channels.map(
              (
                channel,
              ) => {
                const isWebsite =
                  channel.type
                  === "WEBSITE";

                const isPublicApi =
                  channel.type
                  === "PUBLIC_API";

                const isSlack =
                  channel.type
                  === "SLACK";

                const Icon =
                  isWebsite
                    ? Globe2
                    : (
                      isSlack
                        ? Hash
                        : Braces
                    );

                const channelLabel =
                  isWebsite
                    ? "WEBSITE"
                    : (
                      isPublicApi
                        ? "PUBLIC API"
                        : (
                          isSlack
                            ? "SLACK"
                            : channel.type
                        )
                    );

                return (
                  <div
                    key={
                      channel.id
                    }
                    className="rounded-2xl border bg-white p-5 shadow-sm"
                  >

                    <div className="flex items-start justify-between gap-4">

                      <div className="flex min-w-0 items-start gap-3">

                        <div className="rounded-xl bg-slate-100 p-2.5">

                          <Icon className="h-5 w-5 text-slate-700" />

                        </div>


                        <div className="min-w-0">

                          <h3 className="truncate font-semibold text-slate-900">
                            {
                              channel.name
                            }
                          </h3>


                          <div className="mt-2 flex flex-wrap gap-2">

                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                              {
                                channelLabel
                              }
                            </span>


                            <span
                              className={
                                channel.status
                                === "ACTIVE"
                                  ? "rounded-full bg-green-100 px-2.5 py-1 text-xs font-medium text-green-700"
                                  : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600"
                              }
                            >
                              {
                                channel.status
                              }
                            </span>

                          </div>

                        </div>

                      </div>

                    </div>


                    <ChannelMetricsPanel
                      channel={
                        channel
                      }
                    />


                    {isWebsite && (
                      <div className="mt-4 border-t pt-4">

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Allowed websites
                        </p>


                        <div className="mt-2 space-y-1">

                          {(
                            channel
                              .configuration
                              .allowed_origins
                            || []
                          ).length
                            > 0
                            ? (
                              (
                                channel
                                  .configuration
                                  .allowed_origins
                                || []
                              ).map(
                                (
                                  origin,
                                ) => (
                                  <p
                                    key={
                                      origin
                                    }
                                    className="break-all text-sm text-slate-600"
                                  >
                                    {
                                      origin
                                    }
                                  </p>
                                ),
                              )
                            )
                            : (
                              <p className="text-sm text-slate-400">
                                No websites configured
                              </p>
                            )}

                        </div>


                        <div className="mt-5 flex flex-wrap gap-2">

                          <ManageWebsiteChannelDialog
                            channel={
                              channel
                            }
                            knowledgeBaseId={
                              knowledgeBaseId
                            }
                          />


                          <ChannelConversationsDialog
                            channel={
                              channel
                            }
                          />


                          <button
                            type="button"
                            onClick={() =>
                              copyEmbed(
                                channel,
                              )
                            }
                            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                          >
                            <Copy className="h-4 w-4" />

                            {
                              copiedChannelId
                              === channel.id
                                ? "Copied"
                                : "Copy Embed"
                            }
                          </button>

                        </div>

                      </div>
                    )}


                    {isPublicApi && (
                      <div className="mt-4 border-t pt-4">

                        <p className="text-sm text-slate-500">
                          Server-to-server
                          access using
                          revocable API keys.
                        </p>


                        <div className="mt-5 flex flex-wrap gap-2">

                          <ManagePublicApiChannelDialog
                            channel={
                              channel
                            }
                            knowledgeBaseId={
                              knowledgeBaseId
                            }
                          />


                          <ChannelConversationsDialog
                            channel={
                              channel
                            }
                          />

                        </div>

                      </div>
                    )}


                    {isSlack && (
                      <div className="mt-4 border-t pt-4">

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Slack
                        </p>


                        <p className="mt-2 text-sm text-slate-500">
                          Connect this knowledge
                          base to a Slack
                          workspace so users can
                          ask questions directly
                          from Slack.
                        </p>


                        {channel.configuration
                          .respond_to_mentions
                          !== undefined
                          && (
                            <div className="mt-3 flex flex-wrap gap-2">

                              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                                {
                                  channel
                                    .configuration
                                    .respond_to_mentions
                                    ? "Mentions enabled"
                                    : "Mentions disabled"
                                }
                              </span>


                              <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                                {
                                  channel
                                    .configuration
                                    .respond_to_direct_messages
                                    ? "DMs enabled"
                                    : "DMs disabled"
                                }
                              </span>

                            </div>
                          )}


                        {(
                          channel
                            .configuration
                            .allowed_slack_channel_ids
                          || []
                        ).length
                          > 0
                          && (
                            <div className="mt-4">

                              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                Allowed Slack channels
                              </p>


                              <div className="mt-2 flex flex-wrap gap-2">

                                {(
                                  channel
                                    .configuration
                                    .allowed_slack_channel_ids
                                  || []
                                ).map(
                                  (
                                    slackChannelId,
                                  ) => (
                                    <span
                                      key={
                                        slackChannelId
                                      }
                                      className="rounded-md bg-slate-100 px-2 py-1 font-mono text-xs text-slate-600"
                                    >
                                      {
                                        slackChannelId
                                      }
                                    </span>
                                  ),
                                )}

                              </div>

                            </div>
                          )}


                        <div className="mt-5 flex flex-wrap gap-2">

                          <ManageSlackChannelDialog
                            channel={
                              channel
                            }
                          />


                          <ChannelConversationsDialog
                            channel={
                              channel
                            }
                          />

                        </div>

                      </div>
                    )}


                    {!isWebsite
                      && !isPublicApi
                      && !isSlack
                      && (
                        <div className="mt-4 border-t pt-4">

                          <p className="text-sm text-slate-500">
                            This channel type
                            is not yet managed
                            from this UI.
                          </p>

                        </div>
                      )}

                  </div>
                );
              },
            )}

          </div>
        )}

    </div>
  );
}