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
    <div className="flex h-full flex-col">

      <div className="border-b p-4">

        <button
          type="button"
          onClick={
            onNewChat
          }
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />

          New Chat
        </button>

      </div>


      <div className="flex-1 overflow-y-auto p-2">

        {conversations.length ===
        0 ? (
          <div className="p-4 text-center text-sm text-slate-500">
            No conversations yet.
          </div>
        ) : (
          <div className="space-y-1">

            {conversations.map(
              (
                conversation,
              ) => {
                const selected =
                  conversation.id ===
                  selectedId;

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
                    className={
                      selected
                        ? "flex w-full items-start gap-3 rounded-lg bg-blue-50 p-3 text-left"
                        : "flex w-full items-start gap-3 rounded-lg p-3 text-left hover:bg-slate-100"
                    }
                  >

                    <MessageSquare className="mt-0.5 h-4 w-4 shrink-0 text-slate-400" />

                    <div className="min-w-0">

                      <p
                        className={
                          selected
                            ? "truncate text-sm font-medium text-blue-700"
                            : "truncate text-sm font-medium text-slate-700"
                        }
                      >
                        {
                          conversation.title
                        }
                      </p>

                      <p className="mt-1 text-xs text-slate-400">
                        {new Date(
                          conversation.updated_at,
                        ).toLocaleString()}
                      </p>

                    </div>

                  </button>
                );
              },
            )}

          </div>
        )}

      </div>

    </div>
  );
}