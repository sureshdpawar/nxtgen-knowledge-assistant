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
    useState(
      "",
    );


  const [
    conversationId,
    setConversationId,
  ] =
    useState<
      string | null
    >(
      null,
    );


  const [
    messages,
    setMessages,
  ] =
    useState<
      ChatMessage[]
    >(
      [],
    );


  const [
    streaming,
    setStreaming,
  ] =
    useState(
      false,
    );


  const [
    loadingConversation,
    setLoadingConversation,
  ] =
    useState(
      false,
    );


  const [
    error,
    setError,
  ] =
    useState<
      string | null
    >(
      null,
    );


  const messageCounter =
    useRef(
      0,
    );


  const messagesContainerRef =
    useRef<
      HTMLDivElement | null
    >(
      null,
    );


  const messagesEndRef =
    useRef<
      HTMLDivElement | null
    >(
      null,
    );


  const autoScrollRef =
    useRef(
      true,
    );


  const conversationList =
    conversationResponse
      ?.conversations
    ?? [];


  function nextMessageId() {
    messageCounter.current += 1;

    return (
      `chat-${messageCounter.current}`
    );
  }


  function scrollToBottom(
    behavior:
      ScrollBehavior = "smooth",
  ) {
    messagesEndRef.current
      ?.scrollIntoView({
        behavior,
        block: "end",
      });
  }


  function handleMessagesScroll() {
    const container =
      messagesContainerRef.current;

    if (!container) {
      return;
    }

    const distanceFromBottom =
      container.scrollHeight
      - container.scrollTop
      - container.clientHeight;

    autoScrollRef.current =
      distanceFromBottom
      < 120;
  }


  useEffect(() => {
    if (
      !autoScrollRef.current
    ) {
      return;
    }

    scrollToBottom(
      streaming
        ? "auto"
        : "smooth",
    );
  }, [
    messages,
    streaming,
  ]);


  function changeKnowledgeBase(
    id: string,
  ) {
    setKnowledgeBaseId(
      id,
    );

    setConversationId(
      null,
    );

    setMessages(
      [],
    );

    setError(
      null,
    );

    autoScrollRef.current =
      true;
  }


  function handleNewChat() {
    setConversationId(
      null,
    );

    setKnowledgeBaseId(
      "",
    );

    setMessages(
      [],
    );

    setError(
      null,
    );

    autoScrollRef.current =
      true;
  }


  async function handleSelectConversation(
    selectedConversationId:
      string,
  ) {
    if (
      streaming
      || loadingConversation
    ) {
      return;
    }

    setError(
      null,
    );

    setLoadingConversation(
      true,
    );

    autoScrollRef.current =
      true;

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
          (
            message,
          ) => ({
            id:
              message.id,

            role:
              message.role,

            content:
              message.content,

            sources:
              message.role
              === "assistant"
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
      !knowledgeBaseId
      || streaming
    ) {
      return;
    }

    setError(
      null,
    );

    autoScrollRef.current =
      true;


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
      (
        current,
      ) => [
        ...current,
        userMessage,
        assistantMessage,
      ],
    );


    setStreaming(
      true,
    );


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
          onToken(
            token,
          ) {
            setMessages(
              (
                current,
              ) =>
                current.map(
                  (
                    message,
                  ) =>
                    message.id
                    === assistantId
                      ? {
                          ...message,

                          content:
                            message.content
                            + token,
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
                    message.id
                    === assistantId
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
        (
          current,
        ) =>
          current.filter(
            (
              message,
            ) =>
              message.id
              !== assistantId,
          ),
      );

    } finally {
      setStreaming(
        false,
      );
    }
  }


  return (
    <div className="grid h-full min-h-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm grid-rows-[220px_minmax(0,1fr)] lg:grid-cols-[300px_minmax(0,1fr)] lg:grid-rows-1">

      {/* Conversations */}
      <aside className="min-h-0 overflow-hidden border-b bg-slate-50 lg:border-b-0 lg:border-r">

        {conversationsLoading
          ? (
            <div className="p-4 text-sm text-slate-500">
              Loading conversations...
            </div>
          )
          : (
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
          )
        }

      </aside>


      {/* Chat */}
      <section className="flex min-h-0 min-w-0 flex-col bg-white">

        {/* Compact chat header */}
        <header className="shrink-0 border-b border-slate-200 bg-white px-5 py-4">

          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">

            <div className="flex items-center gap-3">

              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50">

                <MessageSquare className="h-5 w-5 text-blue-600" />

              </div>


              <div>

                <h1 className="font-semibold text-slate-900">
                  Knowledge Chat
                </h1>

                <p className="text-xs text-slate-500">
                  Answers grounded in
                  your knowledge base
                </p>

              </div>

            </div>


            <div className="w-full xl:w-80">

              <label
                htmlFor="chat-kb"
                className="sr-only"
              >
                Knowledge Base
              </label>


              <select
                id="chat-kb"
                value={
                  knowledgeBaseId
                }
                onChange={(
                  event,
                ) =>
                  changeKnowledgeBase(
                    event.target.value,
                  )
                }
                disabled={
                  knowledgeBasesLoading
                  || streaming
                  || loadingConversation
                  || conversationId
                    !== null
                }
                className="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50 disabled:text-slate-500"
              >

                <option value="">
                  Select knowledge base
                </option>


                {knowledgeBases
                  ?.map(
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
                  )
                }

              </select>

            </div>

          </div>

        </header>


        {/* Messages */}
        <div
          ref={
            messagesContainerRef
          }
          onScroll={
            handleMessagesScroll
          }
          className="min-h-0 flex-1 overflow-y-auto bg-slate-50"
        >

          <div className="mx-auto flex min-h-full w-full max-w-4xl flex-col px-4 py-8 sm:px-6">

            {loadingConversation && (
              <div className="flex flex-1 items-center justify-center">

                <p className="text-sm text-slate-500">
                  Loading conversation...
                </p>

              </div>
            )}


            {!loadingConversation
              && messages.length
              === 0
              && (
                <div className="flex flex-1 items-center justify-center">

                  <div className="max-w-md text-center">

                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">

                      <MessageSquare className="h-6 w-6 text-blue-600" />

                    </div>


                    <h2 className="mt-4 text-lg font-semibold text-slate-900">
                      How can I help?
                    </h2>


                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      Select a knowledge
                      base and ask a
                      question about its
                      content.
                    </p>

                  </div>

                </div>
              )
            }


            {!loadingConversation
              && messages.length
              > 0
              && (
                <div className="space-y-7">

                  {messages.map(
                    (
                      message,
                    ) => (
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
                    <p className="pl-12 text-xs text-slate-400">
                      Generating response...
                    </p>
                  )}


                  {error && (
                    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                      {error}
                    </div>
                  )}

                </div>
              )
            }


            {!loadingConversation
              && messages.length
              === 0
              && error
              && (
                <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  {error}
                </div>
              )
            }


            <div
              ref={
                messagesEndRef
              }
              className="h-px"
            />

          </div>

        </div>


        {/* Composer */}
        <ChatComposer
          onSend={
            handleSend
          }
          disabled={
            !knowledgeBaseId
            || streaming
            || loadingConversation
          }
        />

      </section>

    </div>
  );
}