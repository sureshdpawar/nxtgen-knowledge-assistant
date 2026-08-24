export type Visibility =
  | "PRIVATE"
  | "PUBLIC";


export interface KnowledgeBase {
  id: string;

  tenant_id: string;

  owner_user_id: string;

  llm_configuration_id:
    string | null;

  name: string;

  description:
    string | null;

  /*
   * KB-level RAG overrides.
   *
   * null means:
   * inherit the platform default.
   */
  chunk_size:
    number | null;

  chunk_overlap:
    number | null;

  top_k:
    number | null;

  status: string;

  visibility:
    Visibility;

  created_at: string;

  updated_at: string;
}


export interface CreateKnowledgeBaseRequest {
  name: string;

  description?: string;

  visibility:
    Visibility;

  chunk_size?:
    number | null;

  chunk_overlap?:
    number | null;

  top_k?:
    number | null;
}


export interface UpdateKnowledgeBaseRequest {
  name: string;

  description?: string;

  visibility:
    Visibility;

  chunk_size?:
    number | null;

  chunk_overlap?:
    number | null;

  top_k?:
    number | null;
}


export interface UpdateKnowledgeBaseLLMProfileRequest {
  llm_configuration_id:
    string | null;
}


export interface UpdateKnowledgeBaseLLMProfileResponse {
  knowledge_base_id: string;

  llm_configuration_id:
    string | null;
}