"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  Bot,
  ShieldAlert,
} from "lucide-react";

import {
  useQueryClient,
} from "@tanstack/react-query";

import {
  useAgents,
} from "@/features/agents/hooks";

import type {
  AgentInterrupt,
} from "@/features/agents/types";

import {
  getConversation,
} from "@/features/conversations/api";

import {
  useConversations,
} from "@/features/conversations/hooks";

import ConversationList from "@/features/conversations/components/ConversationList";

import ChatComposer from "@/features/chat/components/ChatComposer";
import ChatMessageComponent from "@/features/chat/components/ChatMessage";

import type {
  ChatMessage,
} from "@/features/chat/types";

import {
  resumeAgentChatStream,
  streamAgentChat,
} from "../api";

import type {
  AgentChatProgressEvent,
  AgentChatResult,
} from "../types";

export default function AgentChatWindow() {
  const queryClient =
    useQueryClient();

  const {
    data: agents,
    isLoading: agentsLoading,
  } = useAgents();

  const {
    data: conversationResponse,
    isLoading: conversationsLoading,
  } = useConversations();

  const activeAgents =
    useMemo(
      () =>
        (agents ?? []).filter(
          (agent) =>
            agent.status === "ACTIVE",
        ),
      [agents],
    );

  const conversationList =
    useMemo(
      () =>
        (
          conversationResponse
            ?.conversations
          ?? []
        ).filter(
          (conversation) =>
            conversation.agent_id
            !== null,
        ),
      [conversationResponse],
    );

  const [
    agentId,
    setAgentId,
  ] = useState("");

  const [
    conversationId,
    setConversationId,
  ] = useState<string | null>(
    null,
  );

  const [
    messages,
    setMessages,
  ] = useState<ChatMessage[]>(
    [],
  );

  const [
    pendingApproval,
    setPendingApproval,
  ] = useState<AgentChatResult | null>(
    null,
  );

  const [
    progressText,
    setProgressText,
  ] = useState<string | null>(
    null,
  );

  const [
    streaming,
    setStreaming,
  ] = useState(false);

  const [
    loadingConversation,
    setLoadingConversation,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState<string | null>(
    null,
  );

  const messageCounter =
    useRef(0);

  const messagesContainerRef =
    useRef<HTMLDivElement | null>(
      null,
    );

  const messagesEndRef =
    useRef<HTMLDivElement | null>(
      null,
    );

  const autoScrollRef =
    useRef(true);

  function nextMessageId() {
    messageCounter.current += 1;

    return `agent-chat-${messageCounter.current}`;
  }

  function scrollToBottom(
    behavior: ScrollBehavior =
      "smooth",
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
      distanceFromBottom < 120;
  }

  useEffect(() => {
    if (!autoScrollRef.current) {
      return;
    }

    scrollToBottom(
      streaming
        ? "auto"
        : "smooth",
    );
  }, [
    messages,
    pendingApproval,
    progressText,
    streaming,
  ]);

  function changeAgent(
    id: string,
  ) {
    setAgentId(id);
    setConversationId(null);
    setMessages([]);
    setPendingApproval(null);
    setProgressText(null);
    setError(null);
    autoScrollRef.current = true;
  }

  function handleNewChat() {
    setConversationId(null);
    setAgentId("");
    setMessages([]);
    setPendingApproval(null);
    setProgressText(null);
    setError(null);
    autoScrollRef.current = true;
  }

  async function handleSelectConversation(
    selectedConversationId: string,
  ) {
    if (
      streaming
      || loadingConversation
    ) {
      return;
    }

    setError(null);
    setPendingApproval(null);
    setProgressText(null);
    setLoadingConversation(true);
    autoScrollRef.current = true;

    try {
      const conversation =
        await getConversation(
          selectedConversationId,
        );

      if (!conversation.agent_id) {
        throw new Error(
          "This is not an agent conversation.",
        );
      }

      setConversationId(
        conversation.id,
      );

      setAgentId(
        conversation.agent_id,
      );

      setMessages(
        conversation.messages.map(
          (message) => ({
            id: message.id,
            role: message.role,
            content: message.content,
            sources:
              message.role
              === "assistant"
                ? message.citations
                : undefined,
          }),
        ),
      );
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load conversation.",
      );
    } finally {
      setLoadingConversation(false);
    }
  }

  async function handleSend(
    query: string,
  ) {
    if (
      !agentId
      || streaming
      || pendingApproval
    ) {
      return;
    }

    setError(null);
    setProgressText(
      "Starting agent...",
    );
    autoScrollRef.current = true;

    const userMessage:
      ChatMessage = {
        id: nextMessageId(),
        role: "user",
        content: query,
      };

    setMessages(
      (current) => [
        ...current,
        userMessage,
      ],
    );

    setStreaming(true);

    try {
      await streamAgentChat(
        {
          agent_id: agentId,
          conversation_id:
            conversationId,
          query,
        },
        {
          onProgress(
            event,
          ) {
            handleProgressEvent(
              event,
            );
          },
          onCompleted(
            result,
          ) {
            setConversationId(
              result.conversation_id,
            );

            setPendingApproval(null);
            setProgressText(null);

            if (result.answer) {
              setMessages(
                (current) => [
                  ...current,
                  {
                    id: nextMessageId(),
                    role: "assistant",
                    content: result.answer,
                  },
                ],
              );
            }
          },
          onApprovalRequired(
            result,
          ) {
            setConversationId(
              result.conversation_id,
            );
            setPendingApproval(result);
            setProgressText(null);
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
      setProgressText(null);
      setError(
        err instanceof Error
          ? err.message
          : "Agent chat failed.",
      );
    } finally {
      setStreaming(false);
    }
  }

  async function handleApprovalDecision(
    decision:
      | "approve"
      | "reject",
  ) {
    if (
      !pendingApproval
      || streaming
    ) {
      return;
    }

    const approval =
      pendingApproval;

    setError(null);
    setProgressText(
      decision === "approve"
        ? "Continuing approved action..."
        : "Continuing after rejection...",
    );
    setStreaming(true);

    try {
      await resumeAgentChatStream(
        {
          conversation_id:
            approval.conversation_id,
          run_id:
            approval.run_id,
          decision,
        },
        {
          onProgress(
            event,
          ) {
            handleProgressEvent(
              event,
            );
          },
          onCompleted(
            result,
          ) {
            setPendingApproval(null);
            setProgressText(null);

            if (result.answer) {
              setMessages(
                (current) => [
                  ...current,
                  {
                    id: nextMessageId(),
                    role: "assistant",
                    content: result.answer,
                  },
                ],
              );
            }
          },
          onApprovalRequired(
            result,
          ) {
            setPendingApproval(result);
            setProgressText(null);
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
      setProgressText(null);
      setError(
        err instanceof Error
          ? err.message
          : "Failed to resume agent run.",
      );
    } finally {
      setStreaming(false);
    }
  }

  function handleProgressEvent(
    event: AgentChatProgressEvent,
  ) {
    if (
      event.type === "conversation"
      && typeof event.conversation_id
        === "string"
    ) {
      setConversationId(
        event.conversation_id,
      );

      return;
    }

    if (
      event.type === "llm_started"
    ) {
      setProgressText(
        "Agent is thinking...",
      );

      return;
    }

    if (
      event.type === "tool_started"
      && typeof event.name
        === "string"
    ) {
      setProgressText(
        `Using ${event.name}...`,
      );

      return;
    }

    if (
      event.type === "tool_completed"
      && typeof event.name
        === "string"
    ) {
      setProgressText(
        `${event.name} completed.`,
      );

      return;
    }

    if (
      event.type === "run_started"
    ) {
      setProgressText(
        "Agent is working...",
      );
    }
  }

  const selectedAgent =
    activeAgents.find(
      (agent) =>
        agent.id === agentId,
    );

  return (
    <div className="grid h-full min-h-0 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm grid-rows-[220px_minmax(0,1fr)] lg:grid-cols-[300px_minmax(0,1fr)] lg:grid-rows-1">
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
          )}
      </aside>

      <section className="flex min-h-0 min-w-0 flex-col bg-white">
        <header className="shrink-0 border-b border-slate-200 bg-white px-5 py-4">
          <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50">
                <Bot className="h-5 w-5 text-blue-600" />
              </div>

              <div>
                <h1 className="font-semibold text-slate-900">
                  Agent Chat
                </h1>

                <p className="text-xs text-slate-500">
                  Chat with an agent using its configured knowledge and tools
                </p>
              </div>
            </div>

            <div className="w-full xl:w-80">
              <label
                htmlFor="agent-chat-agent"
                className="sr-only"
              >
                Agent
              </label>

              <select
                id="agent-chat-agent"
                value={agentId}
                onChange={(event) =>
                  changeAgent(
                    event.target.value,
                  )
                }
                disabled={
                  agentsLoading
                  || streaming
                  || loadingConversation
                  || conversationId
                    !== null
                }
                className="h-10 w-full rounded-lg border border-slate-200 bg-white px-3 text-sm text-slate-700 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50 disabled:text-slate-500"
              >
                <option value="">
                  Select agent
                </option>

                {activeAgents.map(
                  (agent) => (
                    <option
                      key={agent.id}
                      value={agent.id}
                    >
                      {agent.name}
                    </option>
                  ),
                )}
              </select>
            </div>
          </div>
        </header>

        <div
          ref={messagesContainerRef}
          onScroll={handleMessagesScroll}
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
              && messages.length === 0
              && !pendingApproval
              && (
                <div className="flex flex-1 items-center justify-center">
                  <div className="max-w-md text-center">
                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50">
                      <Bot className="h-6 w-6 text-blue-600" />
                    </div>

                    <h2 className="mt-4 text-lg font-semibold text-slate-900">
                      Start an agent conversation
                    </h2>

                    <p className="mt-2 text-sm leading-6 text-slate-500">
                      {activeAgents.length === 0
                        && !agentsLoading
                        ? "No active agents are available to you."
                        : "Select an agent and ask it to help using its configured knowledge and tools."}
                    </p>
                  </div>
                </div>
              )}

            {!loadingConversation
              && messages.length > 0
              && (
                <div className="space-y-7">
                  {messages.map(
                    (message) => (
                      <ChatMessageComponent
                        key={message.id}
                        message={message}
                      />
                    ),
                  )}

                  {pendingApproval && (
                    <ApprovalCard
                      result={pendingApproval}
                      disabled={streaming}
                      onApprove={() =>
                        handleApprovalDecision(
                          "approve",
                        )
                      }
                      onReject={() =>
                        handleApprovalDecision(
                          "reject",
                        )
                      }
                    />
                  )}

                  {progressText && (
                    <p className="pl-12 text-xs text-slate-400">
                      {progressText}
                    </p>
                  )}

                  {error && (
                    <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                      {error}
                    </div>
                  )}
                </div>
              )}

            {!loadingConversation
              && messages.length === 0
              && error
              && (
                <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
                  {error}
                </div>
              )}

            <div
              ref={messagesEndRef}
              className="h-px"
            />
          </div>
        </div>

        <ChatComposer
          onSend={handleSend}
          disabled={
            !agentId
            || streaming
            || loadingConversation
            || pendingApproval
              !== null
          }
        />

        {selectedAgent
          && conversationId === null
          && (
            <div className="shrink-0 border-t border-slate-100 bg-white px-5 py-2 text-center text-xs text-slate-400">
              New conversation with {selectedAgent.name}
            </div>
          )}
      </section>
    </div>
  );
}

type ApprovalCardProps = {
  result: AgentChatResult;
  disabled: boolean;
  onApprove: () => void;
  onReject: () => void;
};

function ApprovalCard({
  result,
  disabled,
  onApprove,
  onReject,
}: ApprovalCardProps) {
  const tools =
    approvalTools(
      result.interrupts,
    );

  return (
    <div className="ml-0 max-w-2xl rounded-xl border border-amber-200 bg-amber-50 p-4 sm:ml-12">
      <div className="flex items-start gap-3">
        <div className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-100">
          <ShieldAlert className="h-5 w-5 text-amber-700" />
        </div>

        <div className="min-w-0 flex-1">
          <h3 className="text-sm font-semibold text-slate-900">
            Approval required
          </h3>

          <p className="mt-1 text-sm leading-6 text-slate-600">
            The agent needs your approval before it can continue with this action.
          </p>

          {tools.length > 0 && (
            <div className="mt-3 space-y-2">
              {tools.map(
                (tool, index) => (
                  <div
                    key={`${tool.name}-${index}`}
                    className="rounded-lg border border-amber-200 bg-white px-3 py-2"
                  >
                    <p className="text-sm font-medium text-slate-800">
                      {tool.name}
                    </p>

                    {tool.args
                      && Object.keys(
                        tool.args,
                      ).length > 0
                      && (
                        <pre className="mt-2 overflow-x-auto whitespace-pre-wrap break-words text-xs leading-5 text-slate-500">
                          {JSON.stringify(
                            tool.args,
                            null,
                            2,
                          )}
                        </pre>
                      )}
                  </div>
                ),
              )}
            </div>
          )}

          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              onClick={onApprove}
              disabled={disabled}
              className="inline-flex h-9 items-center justify-center rounded-lg bg-blue-600 px-4 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Approve
            </button>

            <button
              type="button"
              onClick={onReject}
              disabled={disabled}
              className="inline-flex h-9 items-center justify-center rounded-lg border border-slate-300 bg-white px-4 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

function approvalTools(
  interrupts: AgentInterrupt[],
) {
  return interrupts.flatMap(
    (interrupt) =>
      (interrupt.tools ?? []).map(
        (tool) => ({
          name:
            tool.name
            ?? "Tool action",
          args: tool.args,
        }),
      ),
  );
}
