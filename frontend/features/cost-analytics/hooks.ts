import {
  useQuery,
} from "@tanstack/react-query";

import {
  getCostAnalytics,
} from "./api";

import type {
  CostAnalyticsFilters,
} from "./types";


export function useCostAnalytics(
  filters: CostAnalyticsFilters,
) {
  return useQuery({
    queryKey: [
      "cost-analytics",
      filters,
    ],

    queryFn: () =>
      getCostAnalytics(
        filters,
      ),
  });
}
