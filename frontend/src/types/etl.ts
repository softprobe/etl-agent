export interface UploadedFile {
  filename: string;
  path: string;
  size: number;
}

export interface UploadResponse {
  files: UploadedFile[];
  schema_preview: any[];
  status: 'success' | 'error';
}

export interface DDLRequest {
  json_files: string[];
  table_name: string;
  dataset_id: string;
  user_requirements: string;
}

export interface ChatMessage {
  id: string;
  type: 'user' | 'assistant' | 'system' | 'error';
  content: string;
  timestamp: Date;
  code?: string;
  schema?: any;
}

export interface WorkflowState {
  step: 'upload' | 'schema' | 'chat' | 'deploy';
  files: UploadedFile[];
  schema?: any;
  ddl?: string;
  etl_code?: string;
}