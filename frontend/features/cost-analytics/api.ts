import api from "@/services/api";

import type {
  CostAnalyticsFilters,
  CostAnalyticsResponse,
} from "./types";


export async function getCostAnalytics(
  filters: CostAnalyticsFilters,
) {
  const response =
    await api.get<CostAnalyticsResponse>(
      "/cost-analytics",
      {
        params: {
          start_date:
            filters.startDate,

          end_date:
            filters.endDate,

          knowledge_base_id:
            filters.knowledgeBaseId
            || undefined,

          request_type:
            filters.requestType
            || undefined,
        },
      },
    );

  return response.data;
}
