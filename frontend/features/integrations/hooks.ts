import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createIntegration,
  deleteIntegration,
  getIntegration,
  getIntegrations,
  updateIntegration,
} from "./api";

import type {
  CreateIntegrationRequest,
  UpdateIntegrationRequest,
} from "./types";


export function useIntegrations(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "integrations",
    ],

    queryFn:
      getIntegrations,

    enabled,
  });
}


export function useIntegration(
  id: string | null,
) {
  return useQuery({
    queryKey: [
      "integrations",
      id,
    ],

    queryFn: () =>
      getIntegration(
        id!,
      ),

    enabled:
      Boolean(id),
  });
}


export function useCreateIntegration() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateIntegrationRequest,
    ) =>
      createIntegration(
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "integrations",
        ],
      });
    },
  });
}


export function useUpdateIntegration() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;

      data:
        UpdateIntegrationRequest;
    }) =>
      updateIntegration(
        id,
        data,
      ),

    onSuccess(
      updatedIntegration,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "integrations",
        ],
      });

      queryClient.setQueryData(
        [
          "integrations",
          updatedIntegration.id,
        ],
        updatedIntegration,
      );
    },
  });
}


export function useDeleteIntegration() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteIntegration,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "integrations",
        ],
      });
    },
  });
}