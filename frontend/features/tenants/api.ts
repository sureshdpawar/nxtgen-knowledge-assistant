import api from "@/services/api";

import type {
  CreateTenantAdminRequest,
  CreateTenantRequest,
  Tenant,
  TenantAdmin,
  UpdateTenantAdminRequest,
  UpdateTenantRequest,
} from "./types";


export async function getTenants() {
  const response =
    await api.get<Tenant[]>(
      "/tenants",
    );

  return response.data;
}


export async function getTenant(
  id: string,
) {
  const response =
    await api.get<Tenant>(
      `/tenants/${id}`,
    );

  return response.data;
}


export async function getTenantAdmins(
  tenantId: string,
) {
  const response =
    await api.get<TenantAdmin[]>(
      `/tenants/${tenantId}/admins`,
    );

  return response.data;
}


export async function createTenant(
  payload: CreateTenantRequest,
) {
  const response =
    await api.post<Tenant>(
      "/tenants",
      payload,
    );

  return response.data;
}


export async function updateTenant(
  id: string,
  payload: UpdateTenantRequest,
) {
  const response =
    await api.put<Tenant>(
      `/tenants/${id}`,
      payload,
    );

  return response.data;
}


export async function deleteTenant(
  id: string,
) {
  await api.delete(
    `/tenants/${id}`,
  );
}


export async function createTenantAdmin(
  tenantId: string,
  payload:
    CreateTenantAdminRequest,
) {
  const response =
    await api.post<TenantAdmin>(
      `/tenants/${tenantId}/admins`,
      payload,
    );

  return response.data;
}


export async function updateTenantAdmin(
  tenantId: string,
  userId: string,
  payload:
    UpdateTenantAdminRequest,
) {
  const response =
    await api.put<TenantAdmin>(
      `/tenants/${tenantId}/admins/${userId}`,
      payload,
    );

  return response.data;
}