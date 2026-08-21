export type KnowledgeSourceType =
  | "UPLOAD"
  | "WEBSITE"
  | "GOOGLE_DRIVE";

export type KnowledgeSourceStatus =
  | "ACTIVE"
  | "PAUSED"
  | "ERROR";

export type KnowledgeSourceSyncStatus =
  | "PENDING"
  | "RUNNING"
  | "COMPLETED"
  | "COMPLETED_WITH_ERRORS"
  | "FAILED";

export interface WebsiteSourceConfiguration {
  base_url: string;
  max_pages: number;
  max_depth: number;
  include_patterns: string[];
  exclude_patterns: string[];
}

export interface KnowledgeSource {
  id: string;
  knowledge_base_id: string;
  created_by: string;

  name: string;
  type: KnowledgeSourceType;
  status: KnowledgeSourceStatus;

  configuration: Record<
    string,
    unknown
  >;

  last_sync_at: string | null;

  created_at: string;
  updated_at: string;
}

export interface KnowledgeSourceSync {
  id: string;

  knowledge_source_id: string;
  triggered_by: string;

  status: KnowledgeSourceSyncStatus;

  started_at: string | null;
  completed_at: string | null;

  items_discovered: number;
  items_new: number;
  items_changed: number;
  items_unchanged: number;
  items_missing: number;
  items_failed: number;

  error_message: string | null;
  provider_summary: string | null;

  created_at: string;
  updated_at: string;
}

export interface CreateKnowledgeSourceRequest {
  name: string;
  type: KnowledgeSourceType;

  configuration: Record<
    string,
    unknown
  >;
}

export interface UpdateKnowledgeSourceRequest {
  name: string;

  status: KnowledgeSourceStatus;

  configuration: Record<
    string,
    unknown
  >;
}