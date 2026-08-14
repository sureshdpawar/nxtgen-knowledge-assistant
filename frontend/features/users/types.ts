// features/users/types.ts

export interface User {
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


export interface CreateUserRequest {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
}


export interface UpdateUserRequest {
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
}