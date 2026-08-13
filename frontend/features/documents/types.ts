export type DocumentStatus =
  | "UPLOADED"
  | "PROCESSING"
  | "READY"
  | "FAILED";

export interface Document {
  id: string;
  knowledge_source_id: string;
  uploaded_by: string;

  original_filename: string;
  stored_filename: string;

  mime_type: string;
  file_size: number;

  checksum: string;
  storage_path: string;

  external_id: string | null;

  status: DocumentStatus;

  created_at: string;
  updated_at: string;
}