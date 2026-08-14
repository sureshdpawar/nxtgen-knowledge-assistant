import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createKnowledgeBase,
  deleteKnowledgeBase,
  getAccessibleKnowledgeBases,
  getKnowledgeBase,
  getKnowledgeBases,
  updateKnowledgeBase,
  updateKnowledgeBaseLLMProfile,
} from "./api";

import type {
  UpdateKnowledgeBaseLLMProfileRequest,
  UpdateKnowledgeBaseRequest,
} from "./types";


export function useKnowledgeBases(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "knowledge-bases",
    ],

    queryFn:
      getKnowledgeBases,

    enabled,
  });
}


export function useCreateKnowledgeBase() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      createKnowledgeBase,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
        ],
      });
    },
  });
}


export function useUpdateKnowledgeBase() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;

      data:
        UpdateKnowledgeBaseRequest;
    }) =>
      updateKnowledgeBase(
        id,
        data,
      ),

    onSuccess(
      _data,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
          variables.id,
        ],
      });
    },
  });
}


export function useDeleteKnowledgeBase() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteKnowledgeBase,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
        ],
      });
    },
  });
}


export function useKnowledgeBase(
  id: string,
) {
  return useQuery({
    queryKey: [
      "knowledge-bases",
      id,
    ],

    queryFn: () =>
      getKnowledgeBase(
        id,
      ),

    enabled:
      !!id,
  });
}


export function useAccessibleKnowledgeBases(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "knowledge-bases",
      "accessible",
    ],

    queryFn:
      getAccessibleKnowledgeBases,

    enabled,
  });
}


export function useUpdateKnowledgeBaseLLMProfile() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      knowledgeBaseId,
      data,
    }: {
      knowledgeBaseId: string;

      data:
        UpdateKnowledgeBaseLLMProfileRequest;
    }) =>
      updateKnowledgeBaseLLMProfile(
        knowledgeBaseId,
        data,
      ),

    onSuccess(
      _data,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
          variables.knowledgeBaseId,
        ],
      });
    },
  });
}