export type UsageMetricStatus = {
  used: number;

  limit: number | null;

  remaining: number | null;

  percentage_used: number | null;
};


export type UsagePeriodStatus = {
  messages: UsageMetricStatus;

  input_tokens: UsageMetricStatus;

  output_tokens: UsageMetricStatus;

  total_tokens: UsageMetricStatus;

  reset_at: string;
};


export type UsageScopeStatus = {
  scope: string;

  source?: string;

  enabled: boolean;

  timezone: string;

  daily: UsagePeriodStatus;

  monthly: UsagePeriodStatus;
};


export type UsageStatus = {
  allowed: boolean;

  scopes: UsageScopeStatus[];
};


export type UsageLimit = {
  id: string;

  tenant_id: string;

  knowledge_base_id: string | null;

  chat_channel_id: string | null;

  daily_message_limit: number | null;

  daily_input_token_limit:
    number | null;

  daily_output_token_limit:
    number | null;

  daily_total_token_limit:
    number | null;

  monthly_message_limit:
    number | null;

  monthly_input_token_limit:
    number | null;

  monthly_output_token_limit:
    number | null;

  monthly_total_token_limit:
    number | null;

  max_input_tokens_per_request:
    number | null;

  max_output_tokens_per_request:
    number | null;

  timezone: string;

  enabled: boolean;
};


export type UsageLimitUpdate = {
  daily_message_limit?:
    number | null;

  daily_input_token_limit?:
    number | null;

  daily_output_token_limit?:
    number | null;

  daily_total_token_limit?:
    number | null;

  monthly_message_limit?:
    number | null;

  monthly_input_token_limit?:
    number | null;

  monthly_output_token_limit?:
    number | null;

  monthly_total_token_limit?:
    number | null;

  max_input_tokens_per_request?:
    number | null;

  max_output_tokens_per_request?:
    number | null;

  timezone?: string | null;

  enabled?: boolean | null;
};