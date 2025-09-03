from pydantic import BaseModel
from typing import Dict, List, Any, Optional

class JSONSchema(BaseModel):
    fields: Dict[str, str]
    nested_objects: List[str]
    arrays: List[str]
    record_count: int

class TableSchema(BaseModel):
    name: str
    estimated_rows: int
    columns: List[Dict[str, Any]]
    relationships: List[Dict[str, str]] = []

class DDLRequest(BaseModel):
    json_files: List[str]
    table_name: str
    dataset_id: str
    user_requirements: str

class ETLJob(BaseModel):
    ddl: str
    etl_code: str
    deployment_config: Dict[str, Any]

class UploadResponse(BaseModel):
    files: List[Dict[str, Any]]
    schema_preview: List[TableSchema]
    status: str

class ChatMessage(BaseModel):
    type: str  # 'user', 'assistant', 'code', 'schema'
    content: str
    data: Optional[Dict[str, Any]] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None