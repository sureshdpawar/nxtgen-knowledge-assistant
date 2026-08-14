import {
  useQuery,
} from "@tanstack/react-query";

import {
  getDashboardStats,
  getPlatformDashboardStats,
} from "./api";


export function useDashboardStats(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "dashboard",
      "stats",
    ],

    queryFn:
      getDashboardStats,

    enabled,
  });
}


export function usePlatformDashboardStats(
  enabled = true,
) {
  return useQuery({
    queryKey: [
      "dashboard",
      "platform-stats",
    ],

    queryFn:
      getPlatformDashboardStats,

    enabled,
  });
}