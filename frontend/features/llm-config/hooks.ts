import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createLLMProfile,
  deleteLLMProfile,
  getLLMProfiles,
  setDefaultLLMProfile,
  updateLLMProfile,
} from "./api";

import type {
  CreateLLMProfileRequest,
  UpdateLLMProfileRequest,
} from "./types";


export function useLLMProfiles(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "llm-profiles",
    ],

    queryFn:
      getLLMProfiles,

    enabled,
  });
}


export function useCreateLLMProfile() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateLLMProfileRequest,
    ) =>
      createLLMProfile(
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "llm-profiles",
        ],
      });
    },
  });
}


export function useUpdateLLMProfile() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data:
        UpdateLLMProfileRequest;
    }) =>
      updateLLMProfile(
        id,
        data,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "llm-profiles",
        ],
      });
    },
  });
}


export function useSetDefaultLLMProfile() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      setDefaultLLMProfile,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "llm-profiles",
        ],
      });
    },
  });
}


export function useDeleteLLMProfile() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteLLMProfile,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "llm-profiles",
        ],
      });
    },
  });
}