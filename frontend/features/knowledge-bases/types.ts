export type Visibility =
  | "PRIVATE"
  | "PUBLIC";

export interface KnowledgeBase {
  id: string;

  tenant_id: string;

  owner_user_id: string;

  name: string;

  description: string | null;

  status: string;

  visibility: Visibility;

  created_at: string;

  updated_at: string;
}

export interface CreateKnowledgeBaseRequest {
  name: string;

  description?: string;

  visibility: Visibility;
}

export interface UpdateKnowledgeBaseRequest {
  name: string;

  description?: string;

  visibility: Visibility;
}