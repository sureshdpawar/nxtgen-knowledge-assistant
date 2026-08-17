import api from "@/services/api";

import type {
  ChangePasswordRequest,
  ChangePasswordResponse,
} from "./types";


export async function changePassword(
  payload: ChangePasswordRequest,
) {
  const response =
    await api.put<
      ChangePasswordResponse
    >(
      "/account/change-password",
      payload,
    );

  return response.data;
}