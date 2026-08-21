import api from "@/services/api";

import type {
  ChannelConversation,
  ChannelConversationListResponse,
  ChatChannel,
  ChatChannelApiKey,
  ChatChannelMetrics,
  CreateChatChannelRequest,
  CreatedChatChannelApiKey,
  UpdateChatChannelRequest,
} from "./types";


export async function getChatChannels(
  knowledgeBaseId: string,
) {
  const response =
    await api.get<ChatChannel[]>(
      "/channels",
      {
        params: {
          knowledge_base_id:
            knowledgeBaseId,
        },
      },
    );

  return response.data;
}


export async function getChatChannel(
  channelId: string,
) {
  const response =
    await api.get<ChatChannel>(
      `/channels/${channelId}`,
    );

  return response.data;
}


export async function createChatChannel(
  payload:
    CreateChatChannelRequest,
) {
  const response =
    await api.post<ChatChannel>(
      "/channels",
      payload,
    );

  return response.data;
}


export async function updateChatChannel(
  channelId: string,
  payload:
    UpdateChatChannelRequest,
) {
  const response =
    await api.patch<ChatChannel>(
      `/channels/${channelId}`,
      payload,
    );

  return response.data;
}


export async function deleteChatChannel(
  channelId: string,
) {
  await api.delete(
    `/channels/${channelId}`,
  );
}


export async function getChatChannelApiKeys(
  channelId: string,
) {
  const response =
    await api.get<
      ChatChannelApiKey[]
    >(
      `/channels/${channelId}/api-keys`,
    );

  return response.data;
}


export async function createChatChannelApiKey(
  channelId: string,
  name: string,
) {
  const response =
    await api.post<
      CreatedChatChannelApiKey
    >(
      `/channels/${channelId}/api-keys`,
      {
        name,
      },
    );

  return response.data;
}


export async function revokeChatChannelApiKey(
  channelId: string,
  keyId: string,
) {
  const response =
    await api.delete<
      ChatChannelApiKey
    >(
      `/channels/${channelId}/api-keys/${keyId}`,
    );

  return response.data;
}


export async function getChannelConversations(
  channelId: string,
) {
  const response =
    await api.get<
      ChannelConversationListResponse
    >(
      `/channels/${channelId}/conversations`,
    );

  return response
    .data
    .conversations;
}


export async function getChannelConversation(
  channelId: string,
  conversationId: string,
) {
  const response =
    await api.get<
      ChannelConversation
    >(
      `/channels/${channelId}/conversations/${conversationId}`,
    );

  return response.data;
}


export async function deleteChannelConversation(
  channelId: string,
  conversationId: string,
) {
  await api.delete(
    `/channels/${channelId}/conversations/${conversationId}`,
  );
}


export async function getChatChannelMetrics(
  channelId: string,
) {
  const response =
    await api.get<
      ChatChannelMetrics
    >(
      `/channels/${channelId}/metrics`,
    );

  return response.data;
}