// features/users/api.ts

import api from "@/services/api";

import type {
  CreateUserRequest,
  UpdateUserRequest,
  User,
} from "./types";


export async function getUsers() {
  const response =
    await api.get<User[]>(
      "/users",
    );

  return response.data;
}


export async function getUser(
  id: string,
) {
  const response =
    await api.get<User>(
      `/users/${id}`,
    );

  return response.data;
}


export async function createUser(
  payload: CreateUserRequest,
) {
  const response =
    await api.post<User>(
      "/users",
      payload,
    );

  return response.data;
}


export async function updateUser(
  id: string,
  payload: UpdateUserRequest,
) {
  const response =
    await api.put<User>(
      `/users/${id}`,
      payload,
    );

  return response.data;
}