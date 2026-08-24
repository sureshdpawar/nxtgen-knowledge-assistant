import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  getChatChannelUsageLimit,
  getChatChannelUsageStatus,
  getKnowledgeBaseUsageLimit,
  getKnowledgeBaseUsageStatus,
  getTenantUsageLimit,
  getTenantUsageStatus,
  updateChatChannelUsageLimit,
  updateKnowledgeBaseUsageLimit,
  updateTenantUsageLimit,
} from "./api";

import type {
  UsageLimitUpdate,
} from "./types";


export function useTenantUsageStatus(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "usage",
      "tenant",
      "status",
    ],

    queryFn:
      getTenantUsageStatus,

    enabled,
  });
}


export function useTenantUsageLimit(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "usage",
      "tenant",
      "limit",
    ],

    queryFn:
      getTenantUsageLimit,

    enabled,
  });
}


export function useUpdateTenantUsageLimit() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        UsageLimitUpdate,
    ) =>
      updateTenantUsageLimit(
        payload,
      ),

    async onSuccess() {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "tenant",
            "limit",
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "tenant",
            "status",
          ],
        }),
      ]);
    },
  });
}


export function useKnowledgeBaseUsageStatus(
  knowledgeBaseId:
    string | null,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "usage",
      "knowledge-base",
      knowledgeBaseId,
      "status",
    ],

    queryFn: () =>
      getKnowledgeBaseUsageStatus(
        knowledgeBaseId!,
      ),

    enabled:
      enabled
      && Boolean(
        knowledgeBaseId,
      ),
  });
}


export function useKnowledgeBaseUsageLimit(
  knowledgeBaseId:
    string | null,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "usage",
      "knowledge-base",
      knowledgeBaseId,
      "limit",
    ],

    queryFn: () =>
      getKnowledgeBaseUsageLimit(
        knowledgeBaseId!,
      ),

    enabled:
      enabled
      && Boolean(
        knowledgeBaseId,
      ),
  });
}


export function useUpdateKnowledgeBaseUsageLimit() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      knowledgeBaseId,
      payload,
    }: {
      knowledgeBaseId: string;

      payload:
        UsageLimitUpdate;
    }) =>
      updateKnowledgeBaseUsageLimit(
        knowledgeBaseId,
        payload,
      ),

    async onSuccess(
      _data,
      variables,
    ) {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "knowledge-base",
            variables
              .knowledgeBaseId,
            "limit",
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "knowledge-base",
            variables
              .knowledgeBaseId,
            "status",
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "tenant",
            "status",
          ],
        }),
      ]);
    },
  });
}


export function useChatChannelUsageStatus(
  knowledgeBaseId:
    string | null,
  chatChannelId:
    string | null,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "usage",
      "chat-channel",
      chatChannelId,
      knowledgeBaseId,
      "status",
    ],

    queryFn: () =>
      getChatChannelUsageStatus(
        knowledgeBaseId!,
        chatChannelId!,
      ),

    enabled:
      enabled
      && Boolean(
        knowledgeBaseId,
      )
      && Boolean(
        chatChannelId,
      ),
  });
}


export function useChatChannelUsageLimit(
  chatChannelId:
    string | null,
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "usage",
      "chat-channel",
      chatChannelId,
      "limit",
    ],

    queryFn: () =>
      getChatChannelUsageLimit(
        chatChannelId!,
      ),

    enabled:
      enabled
      && Boolean(
        chatChannelId,
      ),
  });
}


export function useUpdateChatChannelUsageLimit() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      knowledgeBaseId,
      chatChannelId,
      payload,
    }: {
      knowledgeBaseId: string;

      chatChannelId: string;

      payload:
        UsageLimitUpdate;
    }) =>
      updateChatChannelUsageLimit(
        knowledgeBaseId,
        chatChannelId,
        payload,
      ),

    async onSuccess(
      _data,
      variables,
    ) {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "chat-channel",
            variables
              .chatChannelId,
            "limit",
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "chat-channel",
            variables
              .chatChannelId,
            variables
              .knowledgeBaseId,
            "status",
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "knowledge-base",
            variables
              .knowledgeBaseId,
            "status",
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "usage",
            "tenant",
            "status",
          ],
        }),
      ]);
    },
  });
}