import type {
  ChatSource,
} from "@/features/chat/types";

export interface ConversationSummary {
  id: string;
  knowledge_base_id: string;

  title: string;

  created_at: string;
  updated_at: string;
}

export interface ConversationMessage {
  id: string;

  role:
    | "user"
    | "assistant";

  content: string;

  citations: ChatSource[];

  token_usage: Record<
    string,
    unknown
  >;

  created_at: string;
}

export interface Conversation {
  id: string;
  knowledge_base_id: string;

  title: string;

  created_at: string;
  updated_at: string;

  messages:
    ConversationMessage[];
}

export interface ConversationListResponse {
  conversations:
    ConversationSummary[];
}