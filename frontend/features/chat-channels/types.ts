export type ChatChannelType =
  | "PUBLIC_API"
  | "WEBSITE"
  | "SLACK"
  | "TEAMS";


export type ChatChannelStatus =
  | "ACTIVE"
  | "INACTIVE";


export type ChatChannelConfiguration = {
  allowed_origins?: string[];

  widget_title?: string;

  welcome_message?: string;

  placeholder?: string;

  show_sources?: boolean;

  [key: string]: unknown;
};


export type ChatChannel = {
  id: string;

  tenant_id: string;

  knowledge_base_id: string;

  name: string;

  type: ChatChannelType;

  status: ChatChannelStatus;

  configuration:
    ChatChannelConfiguration;

  created_at: string;

  updated_at: string;
};


export type CreateChatChannelRequest = {
  knowledge_base_id: string;

  name: string;

  type: ChatChannelType;

  configuration:
    ChatChannelConfiguration;
};


export type UpdateChatChannelRequest = {
  name?: string;

  status?: ChatChannelStatus;

  configuration?:
    ChatChannelConfiguration;
};


export type ChatChannelApiKey = {
  id: string;

  name: string;

  key_prefix: string;

  active: boolean;

  last_used_at:
    string | null;

  created_at: string;
};


export type CreatedChatChannelApiKey = {
  id: string;

  name: string;

  key_prefix: string;

  api_key: string;
};


export type ChannelConversationSummary = {
  id: string;

  knowledge_base_id: string;

  chat_channel_id: string;

  title: string;

  created_at: string;

  updated_at: string;
};


export type ChannelConversationMessage = {
  id: string;

  role: string;

  content: string;

  citations: Array<
    Record<string, unknown>
  >;

  token_usage:
    Record<string, unknown>;

  created_at: string;
};


export type ChannelConversation = {
  id: string;

  knowledge_base_id: string;

  chat_channel_id: string;

  title: string;

  created_at: string;

  updated_at: string;

  messages:
    ChannelConversationMessage[];
};


export type ChannelConversationListResponse = {
  conversations:
    ChannelConversationSummary[];
};


export type ChatChannelMetrics = {
  conversation_count: number;

  message_count: number;

  user_message_count: number;

  assistant_message_count: number;

  last_activity_at:
    string | null;

  active_api_key_count: number;

  revoked_api_key_count: number;
};