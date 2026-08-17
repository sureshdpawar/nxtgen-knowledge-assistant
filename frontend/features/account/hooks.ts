import {
  useMutation,
} from "@tanstack/react-query";

import {
  changePassword,
} from "./api";

import type {
  ChangePasswordRequest,
} from "./types";


export function useChangePassword() {
  return useMutation({
    mutationFn: (
      payload:
        ChangePasswordRequest,
    ) =>
      changePassword(
        payload,
      ),
  });
}