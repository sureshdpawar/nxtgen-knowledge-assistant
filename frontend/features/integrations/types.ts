export const INTEGRATION_TYPES = [
  "REST",
  "MCP",
] as const;


export type IntegrationType =
  (typeof INTEGRATION_TYPES)[number];


export const INTEGRATION_AUTH_TYPES = [
  "NONE",
  "BEARER",
  "API_KEY",
] as const;


export type IntegrationAuthType =
  (typeof INTEGRATION_AUTH_TYPES)[number];


export interface Integration {
  id: string;
  tenant_id: string;

  name: string;

  integration_type:
    IntegrationType;

  base_url: string;

  auth_type:
    IntegrationAuthType;

  configuration:
    Record<string, unknown>
    | null;

  is_active: boolean;

  created_at: string;
  updated_at: string;
}


export interface CreateIntegrationRequest {
  name: string;

  integration_type:
    IntegrationType;

  base_url: string;

  auth_type:
    IntegrationAuthType;

  auth_config?:
    Record<string, unknown>
    | null;

  configuration?:
    Record<string, unknown>
    | null;

  is_active: boolean;
}


export interface UpdateIntegrationRequest {
  name?: string;

  base_url?: string;

  auth_type?:
    IntegrationAuthType;

  auth_config?:
    Record<string, unknown>
    | null;

  configuration?:
    Record<string, unknown>
    | null;

  is_active?: boolean;
}