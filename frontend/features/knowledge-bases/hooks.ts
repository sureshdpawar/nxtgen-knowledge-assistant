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
} from "./api";

import type {
  UpdateKnowledgeBaseRequest,
} from "./types";


export function useKnowledgeBases() {
  return useQuery({
    queryKey: [
      "knowledge-bases",
    ],
    queryFn:
      getKnowledgeBases,
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

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "knowledge-bases",
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
        getKnowledgeBase(id),
      enabled: !!id,
    });
  }

 export function useAccessibleKnowledgeBases() {
  return useQuery({
    queryKey: [
      "knowledge-bases",
      "accessible",
    ],
    queryFn:
      getAccessibleKnowledgeBases,
  });
} 

  