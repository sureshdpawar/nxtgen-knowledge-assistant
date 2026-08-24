"use client";

import {
  MessageSquare,
  Plus,
} from "lucide-react";

import type {
  ConversationSummary,
} from "../types";


type Props = {
  conversations:
    ConversationSummary[];

  selectedId:
    string | null;

  onSelect: (
    conversationId: string,
  ) => void;

  onNewChat: () => void;
};


export default function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onNewChat,
}: Props) {
  return (
    <div className="flex h-full min-h-0 flex-col">

      {/* Fixed top section */}
      <div className="shrink-0 border-b border-slate-200 bg-slate-50 p-3">

        <button
          type="button"
          onClick={
            onNewChat
          }
          className="flex h-10 w-full items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-100"
        >

          <Plus className="h-4 w-4" />

          New Chat

        </button>

      </div>


      {/* Scrollable conversation history */}
      <div className="min-h-0 flex-1 overflow-y-auto">

        <div className="px-3 pb-2 pt-4">

          <p className="px-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
            Conversations
          </p>

        </div>


        {conversations.length
          === 0
          ? (
            <div className="px-5 py-8 text-center text-sm text-slate-500">
              No conversations yet.
            </div>
          )
          : (
            <div className="space-y-1 px-2 pb-4">

              {conversations.map(
                (
                  conversation,
                ) => {
                  const selected =
                    conversation.id
                    === selectedId;


                  return (
                    <button
                      key={
                        conversation.id
                      }
                      type="button"
                      onClick={() =>
                        onSelect(
                          conversation.id,
                        )
                      }
                      className={`group flex w-full items-start gap-3 rounded-lg px-3 py-3 text-left transition ${
                        selected
                          ? "bg-blue-50"
                          : "hover:bg-slate-100"
                      }`}
                    >

                      <MessageSquare
                        className={`mt-0.5 h-4 w-4 shrink-0 ${
                          selected
                            ? "text-blue-600"
                            : "text-slate-400"
                        }`}
                      />


                      <div className="min-w-0 flex-1">

                        <p
                          className={`truncate text-sm ${
                            selected
                              ? "font-medium text-blue-700"
                              : "font-medium text-slate-700"
                          }`}
                        >
                          {
                            conversation.title
                          }
                        </p>


                        <p className="mt-1 truncate text-xs text-slate-400">
                          {new Date(
                            conversation
                              .updated_at,
                          ).toLocaleString()}
                        </p>

                      </div>

                    </button>
                  );
                },
              )}

            </div>
          )
        }

      </div>

    </div>
  );
}