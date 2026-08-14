export const LLM_PROVIDERS = [
  "OPENAI",
  "AZURE_OPENAI",
  "VLLM",
] as const;


export type LLMProvider =
  (typeof LLM_PROVIDERS)[number];


export interface LLMProfile {
  id: string;
  name: string;
  provider: LLMProvider;
  model_name: string;
  base_url: string;
  temperature: number;
  max_tokens: number;
  is_active: boolean;
  is_default: boolean;
}


export interface CreateLLMProfileRequest {
  name: string;
  provider: LLMProvider;
  model_name: string;
  base_url: string;
  api_key: string;
  temperature: number;
  max_tokens: number;
  is_active: boolean;
  is_default: boolean;
}


export interface UpdateLLMProfileRequest {
  name?: string;
  provider?: LLMProvider;
  model_name?: string;
  base_url?: string;
  api_key?: string;
  temperature?: number;
  max_tokens?: number;
  is_active?: boolean;
}