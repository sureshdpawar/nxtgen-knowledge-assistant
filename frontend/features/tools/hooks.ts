import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createTool,
  deleteTool,
  getTools,
  updateTool,
} from "./api";

import type {
  CreateToolRequest,
  UpdateToolRequest,
} from "./types";


export function useTools(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "tools",
    ],

    queryFn:
      getTools,

    enabled,
  });
}


export function useCreateTool() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateToolRequest,
    ) =>
      createTool(
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "tools",
        ],
      });
    },
  });
}


export function useUpdateTool() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;

      data:
        UpdateToolRequest;
    }) =>
      updateTool(
        id,
        data,
      ),

    onSuccess(
      updatedTool,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "tools",
        ],
      });

      queryClient.setQueryData(
        [
          "tools",
          updatedTool.id,
        ],
        updatedTool,
      );
    },
  });
}


export function useDeleteTool() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteTool,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "tools",
        ],
      });
    },
  });
}