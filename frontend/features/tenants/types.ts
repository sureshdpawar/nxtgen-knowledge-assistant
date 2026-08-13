export interface Tenant {
  id: string;

  name: string;
  slug: string;

  plan: string;
  status: string;

  created_at: string;
  updated_at: string;
}


export interface CreateTenantRequest {
  name: string;
  slug: string;
}


export interface UpdateTenantRequest {
  name?: string;
  plan?: string;
  status?: string;
}


export interface CreateTenantAdminRequest {
  first_name: string;
  last_name: string;

  email: string;
  password: string;
}


export interface UpdateTenantAdminRequest {
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
}


export interface TenantAdmin {
  id: string;

  tenant_id: string | null;

  first_name: string;
  last_name: string;

  email: string;

  role:
    | "SUPERADMIN"
    | "ADMIN"
    | "USER";

  is_active: boolean;

  created_at: string;
  updated_at: string;
}