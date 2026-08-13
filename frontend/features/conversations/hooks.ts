import {
  useQuery,
} from "@tanstack/react-query";

import {
  getConversation,
  getConversations,
} from "./api";


export function useConversations() {
  return useQuery({
    queryKey: [
      "conversations",
    ],

    queryFn:
      getConversations,
  });
}


export function useConversation(
  conversationId: string,
) {
  return useQuery({
    queryKey: [
      "conversation",
      conversationId,
    ],

    queryFn: () =>
      getConversation(
        conversationId,
      ),

    enabled:
      !!conversationId,
  });
}