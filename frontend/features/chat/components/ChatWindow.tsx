"use client";

import {
  useRef,
  useState,
} from "react";

import {
  MessageSquare,
} from "lucide-react";

import {
  useAccessibleKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  streamChat,
} from "../api";

import type {
  ChatMessage,
} from "../types";

import ChatComposer from "./ChatComposer";
import ChatMessageComponent from "./ChatMessage";


export default function ChatWindow() {
  const {
    data:
      knowledgeBases,
    isLoading:
      knowledgeBasesLoading,
  } =
    useAccessibleKnowledgeBases();


  const [
    knowledgeBaseId,
    setKnowledgeBaseId,
  ] =
    useState("");


  const [
    conversationId,
    setConversationId,
  ] =
    useState<
      string | null
    >(null);


  const [
    messages,
    setMessages,
  ] =
    useState<
      ChatMessage[]
    >([]);


  const [
    streaming,
    setStreaming,
  ] =
    useState(false);


  const [
    error,
    setError,
  ] =
    useState<
      string | null
    >(null);


  const messageCounter =
    useRef(0);


  function nextMessageId() {
    messageCounter.current += 1;

    return (
      `chat-${messageCounter.current}`
    );
  }


  function changeKnowledgeBase(
    id: string,
  ) {
    setKnowledgeBaseId(
      id,
    );

    /*
     * A conversation should
     * stay scoped to one KB.
     */
    setConversationId(
      null,
    );

    setMessages([]);

    setError(null);
  }


  async function handleSend(
    query: string,
  ) {
    if (
      !knowledgeBaseId ||
      streaming
    ) {
      return;
    }


    setError(null);


    const userMessage:
      ChatMessage = {
        id:
          nextMessageId(),

        role:
          "user",

        content:
          query,
      };


    const assistantId =
      nextMessageId();


    const assistantMessage:
      ChatMessage = {
        id:
          assistantId,

        role:
          "assistant",

        content:
          "",
      };


    setMessages(
      (current) => [
        ...current,
        userMessage,
        assistantMessage,
      ],
    );


    setStreaming(true);


    try {
      await streamChat(
        {
          knowledge_base_id:
            knowledgeBaseId,

          conversation_id:
            conversationId,

          query,
        },

        {
          onToken(token) {
            setMessages(
              (
                current,
              ) =>
                current.map(
                  (
                    message,
                  ) =>
                    message.id ===
                    assistantId
                      ? {
                          ...message,
                          content:
                            message.content +
                            token,
                        }
                      : message,
                ),
            );
          },


          onMetadata(
            metadata,
          ) {
            setConversationId(
              metadata
                .conversation_id,
            );


            setMessages(
              (
                current,
              ) =>
                current.map(
                  (
                    message,
                  ) =>
                    message.id ===
                    assistantId
                      ? {
                          ...message,
                          sources:
                            metadata.sources,
                        }
                      : message,
                ),
            );
          },
        },
      );
    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Chat failed.";


      setError(
        message,
      );


      setMessages(
        (current) =>
          current.filter(
            (message) =>
              message.id !==
              assistantId,
          ),
      );

    } finally {
      setStreaming(false);
    }
  }


  return (
    <div className="flex min-h-[calc(100vh-9rem)] flex-col overflow-hidden rounded-xl border bg-white shadow-sm">

      {/* Chat Header */}
      <div className="border-b p-5">

        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">

          <div>

            <div className="flex items-center gap-2">

              <MessageSquare className="h-5 w-5 text-blue-600" />

              <h2 className="text-lg font-semibold">
                Knowledge Chat
              </h2>

            </div>

            <p className="mt-1 text-sm text-slate-500">
              Ask questions grounded in
              your knowledge base.
            </p>

          </div>


          <div className="w-full lg:w-72">

            <label
              htmlFor="chat-kb"
              className="text-xs font-medium text-slate-600"
            >
              Knowledge Base
            </label>


            <select
              id="chat-kb"
              value={
                knowledgeBaseId
              }
              onChange={(event) =>
                changeKnowledgeBase(
                  event.target
                    .value,
                )
              }
              disabled={
                knowledgeBasesLoading ||
                streaming
              }
              className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm outline-none focus:border-blue-500"
            >

              <option value="">
                Select knowledge base
              </option>


              {knowledgeBases?.map(
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
              )}

            </select>

          </div>

        </div>

      </div>


      {/* Messages */}
      <div className="flex-1 space-y-5 overflow-y-auto bg-slate-50 p-6">

        {messages.length ===
          0 && (
          <div className="flex h-full min-h-80 items-center justify-center">

            <div className="max-w-md text-center">

              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-blue-100">
                <MessageSquare className="h-6 w-6 text-blue-600" />
              </div>

              <h3 className="mt-4 font-semibold text-slate-900">
                Start a conversation
              </h3>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Select a knowledge
                base and ask a question
                about its documents.
              </p>

            </div>

          </div>
        )}


        {messages.map(
          (message) => (
            <ChatMessageComponent
              key={
                message.id
              }
              message={
                message
              }
            />
          ),
        )}


        {streaming && (
          <p className="text-xs text-slate-400">
            Generating response...
          </p>
        )}


        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {error}
          </div>
        )}

      </div>


      {/* Composer */}
      <ChatComposer
        onSend={
          handleSend
        }
        disabled={
          !knowledgeBaseId ||
          streaming
        }
      />

    </div>
  );
}