import api from "./api";

import {
  AuthUser,
  LoginRequest,
  LoginResponse,
} from "@/types/auth";

class AuthService {

  async login(
    payload: LoginRequest,
  ): Promise<LoginResponse> {

    const response =
      await api.post<LoginResponse>(
        "/auth/login",
        payload,
      );

    return response.data;
  }

  async me(): Promise<AuthUser> {

    const response =
      await api.get<AuthUser>(
        "/auth/me",
      );

    return response.data;
  }

  logout() {
    localStorage.removeItem(
      "access_token",
    );
  }

}

export default new AuthService();