export interface SearchRequest {
  knowledge_base_id: string;
  query: string;
}

export interface SearchResult {
  knowledge_source_id: string;
  knowledge_source_name: string;

  document_id: string;
  document_name: string;

  chunk_id: string;
  chunk_index: number;

  page: number;

  similarity: number;

  text: string;
}

export interface SearchResponse {
  results: SearchResult[];
}