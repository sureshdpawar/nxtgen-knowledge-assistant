import api from "@/services/api";

import type {
  UsageLimit,
  UsageLimitUpdate,
  UsageStatus,
} from "./types";


export async function getTenantUsageStatus() {
  const response =
    await api.get<UsageStatus>(
      "/usage-limits/status/tenant",
    );

  return response.data;
}


export async function getTenantUsageLimit() {
  const response =
    await api.get<
      UsageLimit | null
    >(
      "/usage-limits/tenant",
    );

  return response.data;
}


export async function updateTenantUsageLimit(
  payload: UsageLimitUpdate,
) {
  const response =
    await api.put<UsageLimit>(
      "/usage-limits/tenant",
      payload,
    );

  return response.data;
}


export async function getKnowledgeBaseUsageStatus(
  knowledgeBaseId: string,
) {
  const response =
    await api.get<UsageStatus>(
      `/usage-limits/status/knowledge-bases/${knowledgeBaseId}`,
    );

  return response.data;
}


export async function getKnowledgeBaseUsageLimit(
  knowledgeBaseId: string,
) {
  const response =
    await api.get<
      UsageLimit | null
    >(
      `/usage-limits/knowledge-bases/${knowledgeBaseId}`,
    );

  return response.data;
}


export async function updateKnowledgeBaseUsageLimit(
  knowledgeBaseId: string,
  payload: UsageLimitUpdate,
) {
  const response =
    await api.put<UsageLimit>(
      `/usage-limits/knowledge-bases/${knowledgeBaseId}`,
      payload,
    );

  return response.data;
}


export async function getChatChannelUsageStatus(
  knowledgeBaseId: string,
  chatChannelId: string,
) {
  const response =
    await api.get<UsageStatus>(
      `/usage-limits/status/chat-channels/${chatChannelId}/knowledge-bases/${knowledgeBaseId}`,
    );

  return response.data;
}


export async function getChatChannelUsageLimit(
  chatChannelId: string,
) {
  const response =
    await api.get<
      UsageLimit | null
    >(
      `/usage-limits/chat-channels/${chatChannelId}`,
    );

  return response.data;
}


export async function updateChatChannelUsageLimit(
  knowledgeBaseId: string,
  chatChannelId: string,
  payload: UsageLimitUpdate,
) {
  const response =
    await api.put<UsageLimit>(
      `/usage-limits/chat-channels/${chatChannelId}/knowledge-bases/${knowledgeBaseId}`,
      payload,
    );

  return response.data;
}