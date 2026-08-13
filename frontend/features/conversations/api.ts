import api from "@/services/api";

import type {
  Conversation,
  ConversationListResponse,
} from "./types";


export async function getConversations() {
  const response =
    await api.get<ConversationListResponse>(
      "/conversations",
    );

  return response.data;
}


export async function getConversation(
  conversationId: string,
) {
  const response =
    await api.get<Conversation>(
      `/conversations/${conversationId}`,
    );

  return response.data;
}