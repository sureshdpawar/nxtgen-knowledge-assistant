import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createChatChannel,
  createChatChannelApiKey,
  deleteChannelConversation,
  deleteChatChannel,
  getChannelConversation,
  getChannelConversations,
  getChatChannel,
  getChatChannelApiKeys,
  getChatChannelMetrics,
  getChatChannels,
  revokeChatChannelApiKey,
  updateChatChannel,
} from "./api";

import type {
  CreateChatChannelRequest,
  UpdateChatChannelRequest,
} from "./types";


export function useChatChannels(
  knowledgeBaseId: string,
) {
  return useQuery({
    queryKey: [
      "chat-channels",
      knowledgeBaseId,
    ],

    queryFn: () =>
      getChatChannels(
        knowledgeBaseId,
      ),

    enabled:
      !!knowledgeBaseId,
  });
}


export function useChatChannel(
  channelId: string,
) {
  return useQuery({
    queryKey: [
      "chat-channel",
      channelId,
    ],

    queryFn: () =>
      getChatChannel(
        channelId,
      ),

    enabled:
      !!channelId,
  });
}


export function useCreateChatChannel(
  knowledgeBaseId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateChatChannelRequest,
    ) =>
      createChatChannel(
        payload,
      ),

    onSuccess() {
      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channels",
            knowledgeBaseId,
          ],
        });
    },
  });
}


export function useUpdateChatChannel(
  knowledgeBaseId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;

      data:
        UpdateChatChannelRequest;
    }) =>
      updateChatChannel(
        id,
        data,
      ),

    onSuccess(
      channel,
    ) {
      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channels",
            knowledgeBaseId,
          ],
        });

      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel",
            channel.id,
          ],
        });

      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel-metrics",
            channel.id,
          ],
        });
    },
  });
}


export function useDeleteChatChannel(
  knowledgeBaseId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteChatChannel,

    onSuccess(
      _data,
      channelId,
    ) {
      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channels",
            knowledgeBaseId,
          ],
        });

      queryClient
        .removeQueries({
          queryKey: [
            "chat-channel",
            channelId,
          ],
        });

      queryClient
        .removeQueries({
          queryKey: [
            "chat-channel-metrics",
            channelId,
          ],
        });

      queryClient
        .removeQueries({
          queryKey: [
            "channel-conversations",
            channelId,
          ],
        });
    },
  });
}


export function useChatChannelApiKeys(
  channelId: string,
) {
  return useQuery({
    queryKey: [
      "chat-channel-api-keys",
      channelId,
    ],

    queryFn: () =>
      getChatChannelApiKeys(
        channelId,
      ),

    enabled:
      !!channelId,
  });
}


export function useCreateChatChannelApiKey(
  channelId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      name: string,
    ) =>
      createChatChannelApiKey(
        channelId,
        name,
      ),

    onSuccess() {
      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel-api-keys",
            channelId,
          ],
        });

      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel-metrics",
            channelId,
          ],
        });
    },
  });
}


export function useRevokeChatChannelApiKey(
  channelId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      keyId: string,
    ) =>
      revokeChatChannelApiKey(
        channelId,
        keyId,
      ),

    onSuccess() {
      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel-api-keys",
            channelId,
          ],
        });

      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel-metrics",
            channelId,
          ],
        });
    },
  });
}


export function useChannelConversations(
  channelId: string,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "channel-conversations",
      channelId,
    ],

    queryFn: () =>
      getChannelConversations(
        channelId,
      ),

    enabled:
      !!channelId
      && enabled,
  });
}


export function useChannelConversation(
  channelId: string,
  conversationId: string,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "channel-conversation",
      channelId,
      conversationId,
    ],

    queryFn: () =>
      getChannelConversation(
        channelId,
        conversationId,
      ),

    enabled:
      !!channelId
      && !!conversationId
      && enabled,
  });
}


export function useDeleteChannelConversation(
  channelId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      conversationId: string,
    ) =>
      deleteChannelConversation(
        channelId,
        conversationId,
      ),

    onSuccess(
      _data,
      conversationId,
    ) {
      queryClient
        .invalidateQueries({
          queryKey: [
            "channel-conversations",
            channelId,
          ],
        });

      queryClient
        .invalidateQueries({
          queryKey: [
            "chat-channel-metrics",
            channelId,
          ],
        });

      queryClient
        .removeQueries({
          queryKey: [
            "channel-conversation",
            channelId,
            conversationId,
          ],
        });
    },
  });
}


export function useChatChannelMetrics(
  channelId: string,
) {
  return useQuery({
    queryKey: [
      "chat-channel-metrics",
      channelId,
    ],

    queryFn: () =>
      getChatChannelMetrics(
        channelId,
      ),

    enabled:
      !!channelId,

    refetchInterval:
      30000,
  });
}