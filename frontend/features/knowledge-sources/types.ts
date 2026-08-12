export type KnowledgeSourceType =
  | "UPLOAD";

export type KnowledgeSourceStatus =
  | "ACTIVE";

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