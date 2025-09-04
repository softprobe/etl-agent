import json
from typing import Dict, List, Any, AsyncIterator
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
import os

class ClaudeETLAgent:
    def __init__(self, work_dir: str = None):
        # Use provided work directory or default to current directory
        working_directory = work_dir or os.getcwd()
        
        # Ensure we have an absolute path for the working directory
        if not os.path.isabs(working_directory):
            working_directory = os.path.abspath(working_directory)
        
        print(f"🔧 ClaudeETLAgent initialized with working directory: {working_directory}")
        
        self.options = ClaudeCodeOptions(
            system_prompt=f"""You are an expert ETL engineer specializing in JSON to BigQuery transformations.

UPLOADED FILES CONTEXT:
- JSON files are located in the uploads directory: {working_directory}
- When users ask about analyzing data, check for .json files in the uploads directory
- Use file analysis tools to understand JSON structure before making recommendations
- IMPORTANT: The working directory is set to: {working_directory}

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
            max_turns=5,
            model="claude-3-5-sonnet-20241022",
            cwd=working_directory,  # Use uploads directory for file operations
            add_dirs=[working_directory]  # Also add the uploads directory to context
        )
        
        # Initialize persistent client for multi-turn conversations
        self.client = None
        self.is_client_active = False
    
    async def _ensure_client(self):
        """Ensure we have an active Claude client for persistent conversations"""
        if not self.is_client_active or self.client is None:
            self.client = ClaudeSDKClient(options=self.options)
            await self.client.__aenter__()
            self.is_client_active = True
            print("🔄 Created new persistent Claude client for multi-turn conversation")
    
    async def _close_client(self):
        """Close the persistent Claude client"""
        if self.is_client_active and self.client is not None:
            try:
                await self.client.__aexit__(None, None, None)
            except Exception as e:
                print(f"Warning: Error closing Claude client: {e}")
            finally:
                self.client = None
                self.is_client_active = False
                print("🔒 Closed persistent Claude client")
    
    async def start_new_conversation(self):
        """Start a fresh conversation by closing the current client"""
        await self._close_client()
        await self._ensure_client()
        print("🆕 Started new conversation session")
    
    async def cleanup(self):
        """Clean up resources when the agent is no longer needed"""
        await self._close_client()
    
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
    
    def _serialize_content_block(self, block) -> Dict[str, Any]:
        """Serialize individual content blocks based on their type"""
        block_type = type(block).__name__
        
        if block_type == 'TextBlock':
            return {
                'type': 'text',
                'text': block.text
            }
        elif block_type == 'ToolUseBlock':
            return {
                'type': 'tool_use',
                'id': block.id,
                'name': block.name,
                'input': block.input
            }
        elif block_type == 'ToolResultBlock':
            return {
                'type': 'tool_result',
                'tool_use_id': block.tool_use_id,
                'content': block.content,
                'is_error': block.is_error
            }
        elif block_type == 'ThinkingBlock':
            return {
                'type': 'thinking',
                'thinking': block.thinking,
                'signature': block.signature
            }
        else:
            # Fallback for unknown block types
            return {
                'type': 'unknown',
                'content': str(block)
            }

    def _serialize_message(self, message) -> Dict[str, Any]:
        """Convert Claude message objects to JSON-serializable dictionaries"""
        try:
            # Debug: Print the message type and attributes
            print(f"Serializing message type: {type(message)}")
            
            # Handle different message types based on their class names
            message_type = type(message).__name__
            
            if message_type == 'SystemMessage':
                # Handle SystemMessage - has subtype and data fields
                result = {
                    'type': 'system',
                    'subtype': message.subtype,
                    'data': message.data
                }
                return result
                
            elif message_type == 'AssistantMessage':
                # Handle AssistantMessage - has content (list of ContentBlocks) and model
                result = {
                    'type': 'assistant',
                    'content': [],
                    'model': message.model
                }
                
                # Process content blocks
                if message.content:
                    for block in message.content:
                        serialized_block = self._serialize_content_block(block)
                        result['content'].append(serialized_block)
                
                return result
                
            elif message_type == 'UserMessage':
                # Handle UserMessage - has content (string or list of ContentBlocks)
                result = {
                    'type': 'user',
                    'content': []
                }
                
                if isinstance(message.content, str):
                    # Simple string content
                    result['content'] = message.content
                elif isinstance(message.content, list):
                    # List of content blocks
                    for block in message.content:
                        serialized_block = self._serialize_content_block(block)
                        result['content'].append(serialized_block)
                else:
                    result['content'] = str(message.content)
                
                return result
                
            elif message_type == 'ResultMessage':
                # Handle ResultMessage - has cost and usage information
                result = {
                    'type': 'result',
                    'subtype': message.subtype,
                    'duration_ms': message.duration_ms,
                    'duration_api_ms': message.duration_api_ms,
                    'is_error': message.is_error,
                    'num_turns': message.num_turns,
                    'session_id': message.session_id,
                    'total_cost_usd': message.total_cost_usd,
                    'usage': message.usage,
                    'result': message.result
                }
                return result
                
            else:
                # Fallback: try to convert to dict and handle any non-serializable values
                if hasattr(message, '__dict__'):
                    message_dict = {}
                    for key, value in message.__dict__.items():
                        if isinstance(value, (str, int, float, bool, type(None))):
                            message_dict[key] = value
                        elif isinstance(value, (list, dict)):
                            message_dict[key] = value
                        else:
                            message_dict[key] = str(value)
                    
                    # Add message type
                    message_dict['type'] = 'unknown'
                    return message_dict
                else:
                    return {
                        'type': 'unknown',
                        'content': str(message)
                    }
                    
        except Exception as e:
            print(f"Error serializing message: {e}")
            print(f"Message type: {type(message)}")
            return {
                'type': 'error',
                'content': f"Error processing message: {str(e)}"
            }

    async def chat_stream(self, user_message: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat responses for real-time interaction with persistent conversation"""
        
        # Ensure we have an active client for multi-turn conversations
        await self._ensure_client()
        
        try:
            # Send user message to Claude using the persistent client
            await self.client.query(user_message)
            
            # Stream responses back
            async for message in self.client.receive_response():
                # Serialize the message before yielding
                serialized_message = self._serialize_message(message)
                yield serialized_message
                
        except Exception as e:
            print(f"Error in chat_stream: {e}")
            # If there's an error, try to recover by creating a new client
            await self._close_client()
            await self._ensure_client()
            
            # Send error message to client
            error_message = {
                'type': 'error',
                'content': f"Chat error occurred, but conversation will continue: {str(e)}"
            }
            yield error_message
    
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