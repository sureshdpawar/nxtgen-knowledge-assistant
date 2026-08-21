"use client";

import {
  useState,
} from "react";

import {
  ChevronLeft,
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
  useChannelConversation,
  useChannelConversations,
  useDeleteChannelConversation,
} from "../hooks";

import type {
  ChannelConversationSummary,
  ChatChannel,
} from "../types";


type Props = {
  channel: ChatChannel;
};


export default function ChannelConversationsDialog({
  channel,
}: Props) {
  const [
    open,
    setOpen,
  ] = useState(false);

  const [
    selectedConversationId,
    setSelectedConversationId,
  ] = useState("");

  const [
    conversationToDelete,
    setConversationToDelete,
  ] = useState<
    ChannelConversationSummary | null
  >(null);


  const {
    data:
      conversations = [],

    isLoading:
      conversationsLoading,

    error:
      conversationsError,

  } = useChannelConversations(
    channel.id,
    open,
  );


  const {
    data:
      conversation,

    isLoading:
      conversationLoading,

    error:
      conversationError,

  } = useChannelConversation(
    channel.id,
    selectedConversationId,
    open
      && !!selectedConversationId,
  );


  const deleteMutation =
    useDeleteChannelConversation(
      channel.id,
    );


  function formatDate(
    value: string,
  ) {
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


  function requestDelete(
    item:
      ChannelConversationSummary,
  ) {
    setConversationToDelete(
      item,
    );
  }


  function cancelDelete() {
    if (
      deleteMutation.isPending
    ) {
      return;
    }

    setConversationToDelete(
      null,
    );
  }


  async function confirmDelete() {
    if (
      !conversationToDelete
    ) {
      return;
    }

    const conversationId =
      conversationToDelete.id;

    try {
      await deleteMutation
        .mutateAsync(
          conversationId,
        );

      if (
        selectedConversationId
        === conversationId
      ) {
        setSelectedConversationId(
          "",
        );
      }

      setConversationToDelete(
        null,
      );

    } catch (
      error
    ) {
      console.error(
        "Unable to delete conversation.",
        error,
      );
    }
  }


  function closeDialog() {
    if (
      deleteMutation.isPending
    ) {
      return;
    }

    setOpen(
      false,
    );

    setSelectedConversationId(
      "",
    );

    setConversationToDelete(
      null,
    );
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
        className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <MessageSquare className="h-4 w-4" />

        Conversations
      </button>


      <Dialog
        open={
          open
        }
        onOpenChange={(
          nextOpen,
        ) => {
          if (!nextOpen) {
            closeDialog();

            return;
          }

          setOpen(
            true,
          );
        }}
      >
        <DialogContent className="max-h-[90vh] overflow-hidden sm:max-w-4xl">

          <DialogHeader>
            <DialogTitle>
              {
                selectedConversationId
                  ? "Conversation"
                  : `Conversations · ${channel.name}`
              }
            </DialogTitle>
          </DialogHeader>


          {!selectedConversationId && (
            <div className="max-h-[70vh] overflow-y-auto pr-1">

              {conversationsLoading && (
                <div className="rounded-xl border bg-slate-50 p-5 text-sm text-slate-500">
                  Loading conversations...
                </div>
              )}


              {conversationsError && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
                  Unable to load conversations.
                </div>
              )}


              {!conversationsLoading
                && !conversationsError
                && conversations.length
                === 0
                && (
                  <div className="rounded-xl border border-dashed bg-slate-50 p-8 text-center">

                    <MessageSquare className="mx-auto h-6 w-6 text-slate-400" />

                    <p className="mt-3 font-medium text-slate-900">
                      No conversations yet
                    </p>

                    <p className="mt-1 text-sm text-slate-500">
                      Conversations will appear
                      here after this channel
                      is used.
                    </p>

                  </div>
                )}


              {conversations.length
                > 0
                && (
                  <div className="space-y-3">

                    {conversations.map(
                      (
                        item,
                      ) => (
                        <div
                          key={
                            item.id
                          }
                          className="flex flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between"
                        >

                          <button
                            type="button"
                            onClick={() =>
                              setSelectedConversationId(
                                item.id,
                              )
                            }
                            className="min-w-0 flex-1 text-left"
                          >

                            <p className="truncate font-medium text-slate-900">
                              {
                                item.title
                              }
                            </p>


                            <p className="mt-1 text-xs text-slate-500">
                              Updated{" "}
                              {
                                formatDate(
                                  item.updated_at,
                                )
                              }
                            </p>


                            <p className="mt-1 font-mono text-[11px] text-slate-400">
                              {
                                item.id
                              }
                            </p>

                          </button>


                          <button
                            type="button"
                            onClick={() =>
                              requestDelete(
                                item,
                              )
                            }
                            disabled={
                              deleteMutation
                                .isPending
                            }
                            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm font-medium text-red-700 hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50"
                          >
                            <Trash2 className="h-4 w-4" />

                            Delete
                          </button>

                        </div>
                      ),
                    )}

                  </div>
                )}

            </div>
          )}


          {selectedConversationId && (
            <div className="flex max-h-[70vh] min-h-0 flex-col">

              <div className="mb-4">

                <button
                  type="button"
                  onClick={() =>
                    setSelectedConversationId(
                      "",
                    )
                  }
                  className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900"
                >
                  <ChevronLeft className="h-4 w-4" />

                  Back to conversations
                </button>

              </div>


              {conversationLoading && (
                <div className="rounded-xl border bg-slate-50 p-5 text-sm text-slate-500">
                  Loading conversation...
                </div>
              )}


              {conversationError && (
                <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700">
                  Unable to load conversation.
                </div>
              )}


              {conversation && (
                <div className="min-h-0 flex-1 overflow-y-auto pr-1">

                  <div className="mb-5 rounded-xl border bg-slate-50 p-4">

                    <p className="font-medium text-slate-900">
                      {
                        conversation.title
                      }
                    </p>


                    <p className="mt-2 text-xs text-slate-500">
                      Started{" "}
                      {
                        formatDate(
                          conversation.created_at,
                        )
                      }
                    </p>


                    <p className="mt-1 text-xs text-slate-500">
                      Last activity{" "}
                      {
                        formatDate(
                          conversation.updated_at,
                        )
                      }
                    </p>


                    <p className="mt-2 break-all font-mono text-[11px] text-slate-400">
                      {
                        conversation.id
                      }
                    </p>

                  </div>


                  {conversation.messages.length
                    === 0
                    && (
                      <div className="rounded-xl border border-dashed bg-slate-50 p-6 text-center text-sm text-slate-500">
                        This conversation has
                        no messages.
                      </div>
                    )}


                  <div className="space-y-4">

                    {conversation.messages.map(
                      (
                        message,
                      ) => {
                        const isUser =
                          message.role
                          === "user";

                        return (
                          <div
                            key={
                              message.id
                            }
                            className={
                              isUser
                                ? "ml-auto max-w-[85%] rounded-2xl rounded-br-md bg-blue-600 p-4 text-white"
                                : "mr-auto max-w-[90%] rounded-2xl rounded-bl-md border bg-white p-4 text-slate-900"
                            }
                          >

                            <div className="mb-2 flex items-center justify-between gap-3">

                              <span
                                className={
                                  isUser
                                    ? "text-xs font-semibold uppercase tracking-wide text-blue-100"
                                    : "text-xs font-semibold uppercase tracking-wide text-slate-400"
                                }
                              >
                                {
                                  isUser
                                    ? "User"
                                    : "Assistant"
                                }
                              </span>


                              <span
                                className={
                                  isUser
                                    ? "text-[11px] text-blue-100"
                                    : "text-[11px] text-slate-400"
                                }
                              >
                                {
                                  formatDate(
                                    message.created_at,
                                  )
                                }
                              </span>

                            </div>


                            <p className="whitespace-pre-wrap break-words text-sm leading-6">
                              {
                                message.content
                              }
                            </p>


                            {!isUser
                              && message.citations
                              && message.citations.length
                              > 0
                              && (
                                <details className="mt-4 border-t pt-3">

                                  <summary className="cursor-pointer text-xs font-semibold text-slate-500">
                                    Citations (
                                    {
                                      message
                                        .citations
                                        .length
                                    }
                                    )
                                  </summary>


                                  <div className="mt-2 space-y-2">

                                    {message.citations.map(
                                      (
                                        citation,
                                        index,
                                      ) => (
                                        <pre
                                          key={
                                            index
                                          }
                                          className="overflow-x-auto whitespace-pre-wrap break-all rounded-md bg-slate-50 p-2 text-[11px] text-slate-500"
                                        >
                                          {
                                            JSON.stringify(
                                              citation,
                                              null,
                                              2,
                                            )
                                          }
                                        </pre>
                                      ),
                                    )}

                                  </div>

                                </details>
                              )}


                            {!isUser
                              && message.token_usage
                              && Object.keys(
                                message.token_usage,
                              ).length
                              > 0
                              && (
                                <details className="mt-3">

                                  <summary className="cursor-pointer text-xs text-slate-400">
                                    Token usage
                                  </summary>


                                  <pre className="mt-2 overflow-x-auto rounded-md bg-slate-50 p-2 text-[11px] text-slate-500">
                                    {
                                      JSON.stringify(
                                        message.token_usage,
                                        null,
                                        2,
                                      )
                                    }
                                  </pre>

                                </details>
                              )}

                          </div>
                        );
                      },
                    )}

                  </div>

                </div>
              )}

            </div>
          )}

        </DialogContent>
      </Dialog>


      <Dialog
        open={
          !!conversationToDelete
        }
        onOpenChange={(
          nextOpen,
        ) => {
          if (
            !nextOpen
          ) {
            cancelDelete();
          }
        }}
      >
        <DialogContent className="sm:max-w-md">

          <DialogHeader>

            <DialogTitle>
              Delete conversation?
            </DialogTitle>


            <DialogDescription>
              This will permanently
              delete this conversation
              and all of its messages.
              This action cannot be
              undone.
            </DialogDescription>

          </DialogHeader>


          {conversationToDelete && (
            <div className="rounded-xl border bg-slate-50 p-4">

              <p className="font-medium text-slate-900">
                {
                  conversationToDelete
                    .title
                }
              </p>


              <p className="mt-1 text-xs text-slate-500">
                Last activity{" "}
                {
                  formatDate(
                    conversationToDelete
                      .updated_at,
                  )
                }
              </p>


              <p className="mt-2 break-all font-mono text-[11px] text-slate-400">
                {
                  conversationToDelete
                    .id
                }
              </p>

            </div>
          )}


          {deleteMutation.isError && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              Unable to delete the
              conversation. Please try
              again.
            </div>
          )}


          <DialogFooter>

            <button
              type="button"
              onClick={
                cancelDelete
              }
              disabled={
                deleteMutation
                  .isPending
              }
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Cancel
            </button>


            <button
              type="button"
              onClick={
                confirmDelete
              }
              disabled={
                deleteMutation
                  .isPending
              }
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Trash2 className="h-4 w-4" />

              {
                deleteMutation
                  .isPending
                  ? "Deleting..."
                  : "Delete conversation"
              }
            </button>

          </DialogFooter>

        </DialogContent>
      </Dialog>
    </>
  );
}