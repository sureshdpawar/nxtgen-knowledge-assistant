export const TOOL_TYPES = [
  "NATIVE",
  "REST",
  "MCP",
] as const;


export type ToolType =
  (typeof TOOL_TYPES)[number];


export const TOOL_RISK_LEVELS = [
  "READ",
  "WRITE",
] as const;


export type ToolRiskLevel =
  (typeof TOOL_RISK_LEVELS)[number];


export interface ToolDefinition {
  id: string;

  tenant_id: string;

  integration_id:
    string | null;

  name: string;

  description: string;

  tool_type: ToolType;

  risk_level:
    ToolRiskLevel;

  input_schema:
    Record<string, unknown>;

  configuration:
    Record<string, unknown>
    | null;

  is_active: boolean;

  created_at: string;

  updated_at: string;
}


export interface CreateToolRequest {
  integration_id:
    string | null;

  name: string;

  description: string;

  tool_type: ToolType;

  risk_level:
    ToolRiskLevel;

  input_schema:
    Record<string, unknown>;

  configuration:
    Record<string, unknown>
    | null;

  is_active: boolean;
}


export interface UpdateToolRequest {
  integration_id?:
    string | null;

  name?:
    string;

  description?:
    string;

  risk_level?:
    ToolRiskLevel;

  input_schema?:
    Record<string, unknown>;

  configuration?:
    Record<string, unknown>
    | null;

  is_active?:
    boolean;
}