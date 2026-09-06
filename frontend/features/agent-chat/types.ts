import type {
  AgentInterrupt,
  AgentRunStatus,
} from "@/features/agents/types";

export interface AgentChatStreamRequest {
  agent_id: string;
  conversation_id?: string | null;
  query: string;
}

export interface AgentChatResult {
  conversation_id: string;
  agent_id: string;
  run_id: string;
  thread_id: string;
  checkpoint_id: string | null;
  answer: string | null;
  status: AgentRunStatus;
  llm_calls: number;
  tools_used: string[];
  duration_ms: number;
  interrupts: AgentInterrupt[];
}

export type AgentChatProgressEvent =
  Record<string, unknown> & {
    type?: string;
  };

export interface AgentChatStreamCallbacks {
  onProgress?: (
    event: AgentChatProgressEvent,
  ) => void;

  onCompleted: (
    result: AgentChatResult,
  ) => void;

  onApprovalRequired: (
    result: AgentChatResult,
  ) => void;
}
