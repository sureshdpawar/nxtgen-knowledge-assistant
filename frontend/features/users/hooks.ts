// features/users/hooks.ts

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createUser,
  getUser,
  getUsers,
  updateUser,
} from "./api";

import type {
  CreateUserRequest,
  UpdateUserRequest,
} from "./types";


export function useUsers() {
  return useQuery({
    queryKey: [
      "users",
    ],
    queryFn:
      getUsers,
  });
}


export function useUser(
  id: string,
) {
  return useQuery({
    queryKey: [
      "users",
      id,
    ],

    queryFn: () =>
      getUser(id),

    enabled:
      !!id,
  });
}


export function useCreateUser() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateUserRequest,
    ) =>
      createUser(
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "users",
        ],
      });
    },
  });
}


export function useUpdateUser() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data:
        UpdateUserRequest;
    }) =>
      updateUser(
        id,
        data,
      ),

    onSuccess(
      _data,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "users",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "users",
          variables.id,
        ],
      });
    },
  });
}