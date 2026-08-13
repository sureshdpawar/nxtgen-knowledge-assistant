"use client";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  MessageSquare,
} from "lucide-react";

import {
  useQueryClient,
} from "@tanstack/react-query";

import {
  useAccessibleKnowledgeBases,
} from "@/features/knowledge-bases/hooks";

import {
  getConversation,
} from "@/features/conversations/api";

import {
  useConversations,
} from "@/features/conversations/hooks";

import ConversationList from "@/features/conversations/components/ConversationList";

import {
  streamChat,
} from "../api";

import type {
  ChatMessage,
} from "../types";

import ChatComposer from "./ChatComposer";
import ChatMessageComponent from "./ChatMessage";


export default function ChatWindow() {
  const queryClient =
    useQueryClient();


  const {
    data:
      knowledgeBases,
    isLoading:
      knowledgeBasesLoading,
  } =
    useAccessibleKnowledgeBases();


  const {
    data:
      conversationResponse,
    isLoading:
      conversationsLoading,
  } =
    useConversations();


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
    loadingConversation,
    setLoadingConversation,
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


  const conversationList =
    conversationResponse
      ?.conversations ?? [];


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

    setConversationId(
      null,
    );

    setMessages([]);

    setError(null);
  }


  function handleNewChat() {
    setConversationId(
      null,
    );

    setKnowledgeBaseId(
      "",
    );

    setMessages([]);

    setError(null);
  }


  async function handleSelectConversation(
    selectedConversationId:
      string,
  ) {
    if (
      streaming ||
      loadingConversation
    ) {
      return;
    }

    setError(null);

    setLoadingConversation(
      true,
    );

    try {
      const conversation =
        await getConversation(
          selectedConversationId,
        );

      setConversationId(
        conversation.id,
      );

      setKnowledgeBaseId(
        conversation
          .knowledge_base_id,
      );

      const loadedMessages:
        ChatMessage[] =
        conversation.messages.map(
          (message) => ({
            id:
              message.id,

            role:
              message.role,

            content:
              message.content,

            sources:
              message.role ===
                "assistant"
                ? message.citations
                : undefined,
          }),
        );

      setMessages(
        loadedMessages,
      );

    } catch (err) {
      const message =
        err instanceof Error
          ? err.message
          : "Failed to load conversation.";

      setError(
        message,
      );

    } finally {
      setLoadingConversation(
        false,
      );
    }
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


      await queryClient
        .invalidateQueries({
          queryKey: [
            "conversations",
          ],
        });

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
    <div className="grid min-h-[calc(100vh-9rem)] overflow-hidden rounded-xl border bg-white shadow-sm lg:grid-cols-[280px_1fr]">

      {/* Conversation History */}
      <aside className="border-b bg-slate-50 lg:border-r lg:border-b-0">

        {conversationsLoading ? (
          <div className="p-4 text-sm text-slate-500">
            Loading conversations...
          </div>
        ) : (
          <ConversationList
            conversations={
              conversationList
            }
            selectedId={
              conversationId
            }
            onSelect={
              handleSelectConversation
            }
            onNewChat={
              handleNewChat
            }
          />
        )}

      </aside>


      {/* Chat Area */}
      <div className="flex min-w-0 flex-col">

        {/* Header */}
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
                Ask questions grounded
                in your knowledge base.
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
                  streaming ||
                  loadingConversation ||
                  conversationId !==
                    null
                }
                className="mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm outline-none focus:border-blue-500 disabled:bg-slate-50"
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

          {loadingConversation && (
            <p className="text-sm text-slate-500">
              Loading conversation...
            </p>
          )}


          {!loadingConversation &&
            messages.length ===
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
            streaming ||
            loadingConversation
          }
        />

      </div>

    </div>
  );
}