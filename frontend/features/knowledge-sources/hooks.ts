import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createKnowledgeSource,
  deleteKnowledgeSource,
  getKnowledgeSource,
  getKnowledgeSources,
  getKnowledgeSourceSyncs,
  syncKnowledgeSource,
  updateKnowledgeSource,
} from "./api";

import type {
  CreateKnowledgeSourceRequest,
  UpdateKnowledgeSourceRequest,
} from "./types";


export function useKnowledgeSources(
  knowledgeBaseId: string,
) {
  return useQuery({
    queryKey: [
      "knowledge-sources",
      knowledgeBaseId,
    ],

    queryFn: () =>
      getKnowledgeSources(
        knowledgeBaseId,
      ),

    enabled: !!knowledgeBaseId,
  });
}


export function useKnowledgeSource(
  knowledgeSourceId: string,
) {
  return useQuery({
    queryKey: [
      "knowledge-source",
      knowledgeSourceId,
    ],

    queryFn: () =>
      getKnowledgeSource(
        knowledgeSourceId,
      ),

    enabled: !!knowledgeSourceId,
  });
}


export function useKnowledgeSourceSyncs(
  knowledgeSourceId: string,
) {
  return useQuery({
    queryKey: [
      "knowledge-source-syncs",
      knowledgeSourceId,
    ],

    queryFn: () =>
      getKnowledgeSourceSyncs(
        knowledgeSourceId,
      ),

    enabled: !!knowledgeSourceId,
  });
}


export function useCreateKnowledgeSource(
  knowledgeBaseId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateKnowledgeSourceRequest,
    ) =>
      createKnowledgeSource(
        knowledgeBaseId,
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-sources",
          knowledgeBaseId,
        ],
      });
    },
  });
}


export function useUpdateKnowledgeSource(
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
        UpdateKnowledgeSourceRequest;
    }) =>
      updateKnowledgeSource(
        id,
        data,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-sources",
          knowledgeBaseId,
        ],
      });
    },
  });
}


export function useDeleteKnowledgeSource(
  knowledgeBaseId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteKnowledgeSource,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-sources",
          knowledgeBaseId,
        ],
      });
    },
  });
}


export function useSyncKnowledgeSource(
  knowledgeBaseId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      knowledgeSourceId: string,
    ) =>
      syncKnowledgeSource(
        knowledgeSourceId,
      ),

    async onSuccess(
      syncResult,
    ) {
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: [
            "knowledge-sources",
            knowledgeBaseId,
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "knowledge-source-syncs",
            syncResult
              .knowledge_source_id,
          ],
        }),

        queryClient.invalidateQueries({
          queryKey: [
            "knowledge-source",
            syncResult
              .knowledge_source_id,
          ],
        }),
      ]);
    },
  });
}