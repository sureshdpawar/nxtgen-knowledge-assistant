import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createTenant,
  createTenantAdmin,
  deleteTenant,
  getTenant,
  getTenantAdmins,
  getTenants,
  updateTenant,
  updateTenantAdmin,
} from "./api";

import type {
  CreateTenantAdminRequest,
  UpdateTenantAdminRequest,
  UpdateTenantRequest,
} from "./types";


export function useTenants(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "tenants",
    ],

    queryFn:
      getTenants,

    enabled,
  });
}


export function useTenant(
  id: string,
) {
  return useQuery({
    queryKey: [
      "tenants",
      id,
    ],

    queryFn: () =>
      getTenant(
        id,
      ),

    enabled:
      !!id,
  });
}


export function useTenantAdmins(
  tenantId: string,
) {
  return useQuery({
    queryKey: [
      "tenant-admins",
      tenantId,
    ],

    queryFn: () =>
      getTenantAdmins(
        tenantId,
      ),

    enabled:
      !!tenantId,
  });
}


export function useCreateTenant() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      createTenant,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "tenants",
        ],
      });
    },
  });
}


export function useUpdateTenant() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data:
        UpdateTenantRequest;
    }) =>
      updateTenant(
        id,
        data,
      ),

    onSuccess(
      _data,
      variables,
    ) {
      queryClient.invalidateQueries({
        queryKey: [
          "tenants",
        ],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "tenants",
          variables.id,
        ],
      });
    },
  });
}


export function useDeleteTenant() {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn:
      deleteTenant,

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "tenants",
        ],
      });
    },
  });
}


export function useCreateTenantAdmin(
  tenantId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: (
      payload:
        CreateTenantAdminRequest,
    ) =>
      createTenantAdmin(
        tenantId,
        payload,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "tenant-admins",
          tenantId,
        ],
      });
    },
  });
}


export function useUpdateTenantAdmin(
  tenantId: string,
) {
  const queryClient =
    useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      data,
    }: {
      userId: string;
      data:
        UpdateTenantAdminRequest;
    }) =>
      updateTenantAdmin(
        tenantId,
        userId,
        data,
      ),

    onSuccess() {
      queryClient.invalidateQueries({
        queryKey: [
          "tenant-admins",
          tenantId,
        ],
      });
    },
  });
}