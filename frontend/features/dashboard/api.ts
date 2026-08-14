import api from "@/services/api";

import type {
  DashboardStats,
  PlatformDashboardStats,
} from "./types";


export async function getDashboardStats() {
  const response =
    await api.get<DashboardStats>(
      "/dashboard/stats",
    );

  return response.data;
}


export async function getPlatformDashboardStats() {
  const response =
    await api.get<PlatformDashboardStats>(
      "/dashboard/platform-stats",
    );

  return response.data;
}