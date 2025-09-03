import json
from typing import Dict, List, Any, AsyncIterator
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
import os

class ClaudeETLAgent:
    def __init__(self, work_dir: str = None):
        # Use provided work directory or default to current directory
        working_directory = work_dir or os.getcwd()
        
        self.options = ClaudeCodeOptions(
            system_prompt="""You are an expert ETL engineer specializing in JSON to BigQuery transformations.

UPLOADED FILES CONTEXT:
- Sample JSON files may be uploaded to the current working directory
- When users ask about analyzing data, check for .json files in the current directory
- Use file analysis tools to understand JSON structure before making recommendations

Your responsibilities:
1. Analyze JSON data structures and infer optimal BigQuery table schemas
2. Generate production-ready BigQuery DDL statements  
3. Create Python ETL code using pandas and google-cloud-bigquery
4. Suggest best practices for data normalization and schema design
5. Generate Cloud Run deployment configurations

When analyzing JSON files:
- Sample a few records to understand structure
- Identify nested objects and arrays
- Consider data types and nullability
- Recommend schema normalization strategies

Always consider:
- Data types and nullability
- Nested JSON handling (flatten vs JSON columns)  
- Performance implications of schema choices
- BigQuery pricing considerations
- Error handling and data validation

Available tools: Read files, analyze JSON structure, generate code, create schemas.
""",
            allowed_tools=["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "NotebookEdit", "WebFetch", "TodoWrite", "WebSearch", "BashOutput", "KillBash"],
            permission_mode="acceptEdits",
            max_turns=10,
            cwd=working_directory  # Use uploads directory for file operations
        )
    
    async def generate_ddl(self, json_schemas: List[str], table_name: str, 
                          dataset_id: str, user_requirements: str) -> str:
        """Generate BigQuery DDL from JSON schema analysis"""
        
        prompt = f"""
        Analyze these JSON data structures and generate BigQuery DDL:
        
        JSON Schemas: {json_schemas}
        Target table name: {table_name}
        Dataset ID: {dataset_id}
        User requirements: {user_requirements}
        
        Generate a CREATE TABLE statement that:
        1. Handles all data types properly
        2. Considers nested structures (flatten vs JSON type)
        3. Includes appropriate constraints
        4. Optimizes for query performance
        
        Return only the DDL statement.
        """
        
        result = []
        async with ClaudeSDKClient(options=self.options) as client:
            await client.query(prompt)
            
            async for message in client.receive_response():
                if isinstance(message, dict) and message.get('type') == 'code':
                    result.append(message.get('content', ''))
                elif isinstance(message, str):
                    result.append(message)
        
        return '\n'.join(result)
    
    async def generate_etl_code(self, json_schemas: List[str], table_name: str,
                               dataset_id: str, user_requirements: str) -> str:
        """Generate Python ETL code for JSON to BigQuery transformation"""
        
        prompt = f"""
        Generate Python ETL code for transforming JSON data to BigQuery:
        
        JSON Schemas: {json_schemas}
        Target table: {dataset_id}.{table_name}
        Requirements: {user_requirements}
        
        Generate complete Python code that:
        1. Reads JSON files from Cloud Storage or local filesystem
        2. Transforms and validates data using pandas
        3. Loads data to BigQuery using google-cloud-bigquery
        4. Includes proper error handling and logging
        5. Can be deployed as a Cloud Run job
        
        Use these imports:
        - pandas as pd
        - google.cloud.bigquery as bigquery
        - json, logging, os
        """
        
        result = []
        async with ClaudeSDKClient(options=self.options) as client:
            await client.query(prompt)
            
            async for message in client.receive_response():
                if isinstance(message, dict) and message.get('type') == 'code':
                    result.append(message.get('content', ''))
                elif isinstance(message, str):
                    result.append(message)
        
        return '\n'.join(result)
    
    async def chat_stream(self, user_message: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat responses for real-time interaction"""
        
        async with ClaudeSDKClient(options=self.options) as client:
            # Send user message to Claude
            await client.query(user_message)
            
            # Stream responses back
            async for message in client.receive_response():
                if isinstance(message, dict):
                    yield message
                else:
                    yield {
                        "type": "text", 
                        "content": str(message)
                    }
    
    async def analyze_json_for_schema(self, json_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze JSON data and suggest table schema"""
        
        sample_data = json.dumps(json_data[:5] if len(json_data) > 5 else json_data, 
                                indent=2, default=str)
        
        prompt = f"""
        Analyze this JSON data and suggest a BigQuery table schema:
        
        Sample data ({len(json_data)} total records):
        {sample_data}
        
        Provide:
        1. Suggested table structure with column names and types
        2. Recommendation for handling nested objects
        3. Estimated storage and query performance considerations
        4. Alternative schema options if applicable
        
        Return as JSON with this structure:
        {{
            "recommended_schema": [
                {{"name": "column_name", "type": "STRING", "mode": "NULLABLE", "description": "..."}}
            ],
            "nested_handling": "FLATTEN|JSON_TYPE|SEPARATE_TABLE",
            "considerations": ["performance note 1", "storage note 2"],
            "alternatives": [{{...}}]
        }}
        """
        
        result = []
        async with ClaudeSDKClient(options=self.options) as client:
            await client.query(prompt)
            
            async for message in client.receive_response():
                if isinstance(message, dict) and message.get('type') == 'code':
                    content = message.get('content', '')
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        result.append(content)
                elif isinstance(message, str):
                    result.append(message)
        
        # Fallback if no structured response
        return {
            "recommended_schema": [],
            "nested_handling": "FLATTEN",
            "considerations": ["Analysis incomplete"],
            "alternatives": []
        }