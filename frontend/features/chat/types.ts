export type ChatRole =
  | "user"
  | "assistant";

export interface ChatSource {
  knowledge_source_id: string;
  knowledge_source_name: string;

  document_id: string;
  document_name: string;

  chunk_index: number;
  page: number;
  similarity: number;
}

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  sources?: ChatSource[];
}

export interface ChatStreamRequest {
  knowledge_base_id: string;
  conversation_id?: string | null;
  query: string;
}

export interface ChatStreamMetadata {
  conversation_id: string;
  sources: ChatSource[];
}

export type ChatStreamCallbacks = {
  onToken: (
    token: string,
  ) => void;

  onMetadata: (
    metadata:
      ChatStreamMetadata,
  ) => void;
};