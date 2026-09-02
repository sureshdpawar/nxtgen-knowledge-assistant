export type CurrencyCostTotal = {
  currency: string;
  total_cost: number;
};

export type CostAnalyticsOverview = {
  request_count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;

  costed_request_count: number;
  uncosted_request_count: number;

  cost_totals: CurrencyCostTotal[];
};

export type CostAnalyticsDailyPoint = {
  date: string;

  request_count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;

  costed_request_count: number;
  uncosted_request_count: number;

  cost_totals: CurrencyCostTotal[];
};

export type CostAnalyticsKnowledgeBaseBreakdown = {
  knowledge_base_id: string | null;
  knowledge_base_name: string | null;

  request_count: number;
  total_tokens: number;

  costed_request_count: number;
  uncosted_request_count: number;

  cost_totals: CurrencyCostTotal[];
};

export type CostAnalyticsModelBreakdown = {
  provider: string;
  model: string;

  request_count: number;
  total_tokens: number;

  costed_request_count: number;
  uncosted_request_count: number;

  cost_totals: CurrencyCostTotal[];
};

export type CostAnalyticsWorkloadBreakdown = {
  request_type: string;

  request_count: number;
  total_tokens: number;

  costed_request_count: number;
  uncosted_request_count: number;

  cost_totals: CurrencyCostTotal[];
};

export type CostAnalyticsResponse = {
  start_date: string;
  end_date: string;
  timezone: string;

  knowledge_base_id: string | null;
  request_type: string | null;

  overview: CostAnalyticsOverview;

  daily: CostAnalyticsDailyPoint[];

  by_knowledge_base:
    CostAnalyticsKnowledgeBaseBreakdown[];

  by_model:
    CostAnalyticsModelBreakdown[];

  by_workload:
    CostAnalyticsWorkloadBreakdown[];
};

export type CostAnalyticsFilters = {
  startDate: string;
  endDate: string;

  knowledgeBaseId?: string;
  requestType?: string;
};
