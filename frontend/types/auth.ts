export type UserRole =
  | "SUPERADMIN"
  | "ADMIN"
  | "USER";


export interface LoginRequest {
  email: string;
  password: string;
}


export interface LoginResponse {
  access_token: string;
  token_type: string;
}


export interface AuthUser {
  id: string;

  tenant_id:
    | string
    | null;

  first_name: string;
  last_name: string;

  email: string;

  role: UserRole;

  is_active: boolean;

  created_at: string;
  updated_at: string;
}