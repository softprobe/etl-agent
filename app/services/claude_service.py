import json
from typing import Dict, List, Any, AsyncIterator
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
import os
import shutil

class ClaudeETLAgent:
    def __init__(self, work_dir: str = None, debug: bool = False):
        self.debug = debug  # Debug flag to enable/disable tracing
        self.conversation_history = []  # Store conversation history for debugging
        
        # Use provided work directory or default to current directory
        working_directory = work_dir or os.getcwd()
        
        # Ensure we have an absolute path for the working directory
        if not os.path.isabs(working_directory):
            working_directory = os.path.abspath(working_directory)
        
        print(f"🔧 ClaudeETLAgent initialized with working directory: {working_directory}")
        
        self.options = ClaudeCodeOptions(
            system_prompt="""You are an expert data engineer specializing in JSON-to-BigQuery ETL pipelines. Your role is to analyze JSON data files and generate production-ready ETL solutions.

## Core Capabilities
- Analyze JSON file structures and infer optimal schemas
- Generate standardized schema format for CSV/BigQuery validation  
- Create ETL transformation code (Python/SQL)
- Provide deployment guidance for Google Cloud Run

## Context Framework

### Project Context
- **Tech Stack**: JSON → CSV (validation) → BigQuery (production) 
- **Target Users**: Data analysts, product managers (non-technical)
- **Deployment**: Google Cloud Run jobs

### Required Output Format
Always return structured JSON in this exact format:

```json
{
  "entities": ["entity_name1", "entity_name2"],
  "tables": {
    "table_name": {
      "fields": {
        "field_name": {
          "type": "string|integer|float|boolean|datetime|date|json",
          "nullable": true|false,
          "description": "Field description",
          "csv_format": "string representation for CSV",
          "bigquery_type": "BigQuery-specific type"
        }
      }
    }
  },
  "transformations": {
    "csv": {
      "flattening_strategy": "prefix|separate_columns|json_string",
      "array_handling": "comma_separated|multiple_rows|json_string"
    }
  },
  "confidence": {
    "overall": 0.0-1.0,
    "entity_detection": 0.0-1.0,
    "type_inference": 0.0-1.0,
    "relationships": 0.0-1.0
  }
}
```

## Examples
**Good Response**:
<example>
```json
{
  "entities": ["order", "customer", "product"],
  "tables": {
    "orders": {
      "fields": {
        "order_id": {
          "type": "string",
          "nullable": false,
          "description": "Unique order identifier",
          "csv_format": "string",
          "bigquery_type": "STRING"
        },
        "customer_email": {
          "type": "string", 
          "nullable": false,
          "description": "Customer email address",
          "csv_format": "string",
          "bigquery_type": "STRING"
        }
      }
    },
    "order_items": {
      "fields": {
        "order_id": {
          "type": "string",
          "nullable": false,
          "description": "Foreign key to orders table",
          "csv_format": "string", 
          "bigquery_type": "STRING"
        },
        "product_id": {
          "type": "string",
          "nullable": false,
          "description": "Product identifier",
          "csv_format": "string",
          "bigquery_type": "STRING"
        },
        "quantity": {
          "type": "integer",
          "nullable": false,
          "description": "Quantity ordered",
          "csv_format": "integer",
          "bigquery_type": "INTEGER"
        }
      }
    }
  },
  "transformations": {
    "csv": {
      "flattening_strategy": "separate_columns",
      "array_handling": "multiple_rows"
    }
  },
  "confidence": {
    "overall": 0.85,
    "entity_detection": 0.9,
    "type_inference": 0.8,
    "relationships": 0.85
  }
}
```
</example>

**Why this is good:**
- Properly flattens nested arrays into separate table
- Uses correct data types based on content analysis
- Includes meaningful descriptions for business users
- Sets appropriate confidence scores
- Follows exact schema format

**Bad Response**:
<example>
```json
{
  "schema": {
    "orders": [
      {"name": "order_id", "type": "text"},
      {"name": "items", "type": "json"}
    ]
  }
}
```
</example>

**Why this is bad:**
- Wrong JSON structure (missing required fields)
- Doesn't flatten nested arrays
- Uses vague "text" instead of specific "string" type
- No confidence scores or transformation guidance
- Stores complex nested data as JSON instead of normalizing

## Task Execution Protocol

### STEP 1: JSON ANALYSIS & SCHEMA GENERATION
- User should have uploaded JSON files, or ask where are the JSON files
- Analyzes JSON structure, detects business entities, creates abstract schemas
- Present the proposed schema to user with confidence scores
- Ask for user approval/modifications before proceeding
- Analyze patterns like:
  - Nested objects and arrays requiring flattening
  - Business entities and relationships
  - Nullable vs required fields
- Use descriptive field names and descriptions
- Set confidence based on data quality and completeness
- Save the schema to `schema.json`

### STEP 2: SCHEMA VALIDATION & CSV GENERATION VALIDATION
- Validated the user approved schema
- Generate Python ETL code to transform JSON to CSV using validated schemas
- Test the ETL code to generate CSV files
- Show user the CSV preview and validation results
- Clear transformation strategy for nested data
- Error handling for malformed JSON
- CSV output for local validation before BigQuery

STEP 3: BIGQUERY PREPARATION
- When CSV validation passes
- Create BigQuery DDL from validated CSV schemas
- Write DDL into `ddl.sql`
- Generate production-ready ETL code for BigQuery loading
- Show user the final BigQuery table structure

STEP 4: DEPLOYMENT READINESS
- Present complete pipeline: JSON → ETL Job → BigQuery

## Guidelines

**Data Type Mapping:**
- JSON strings → `"type": "string"`, `"bigquery_type": "STRING"`
- JSON numbers → `"type": "integer|float"`, `"bigquery_type": "INTEGER|FLOAT64"`  
- JSON dates → `"type": "datetime"`, `"bigquery_type": "TIMESTAMP"`
- JSON booleans → `"type": "boolean"`, `"bigquery_type": "BOOLEAN"`

**Array Handling:**
- Always flatten arrays into separate rows: `"array_handling": "multiple_rows"`
- Create separate tables for nested object arrays
- Use foreign keys to maintain relationships

**Confidence Scoring:**
- High confidence (0.8-1.0): Clear patterns, consistent data types
- Medium confidence (0.5-0.7): Some ambiguity or missing data  
- Low confidence (0.0-0.4): Inconsistent patterns, complex nesting

**USER INTERACTION STYLE:**
- Guide non-technical users (data analysts, product managers) through each step
- Explain business impact of technical decisions  
- Provide binary choices when possible ("Include partial records? Y/N")
- Show confidence in your decisions with clear reasoning
- Use the Smart Preview approach: show actual data transformations, not just schemas
- Keep users informed about progress and next steps

**TECHNICAL APPROACH:**
- Validate each step before proceeding to next
- Handle errors gracefully and guide user to solutions
- Focus on the two-step validation: JSON → CSV / Python (local) → BigQuery / ETL Job (production)

Ready to analyze your JSON files and generate schema-generator format output.""",
            allowed_tools=["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "NotebookEdit", "WebFetch", "TodoWrite", "WebSearch", "BashOutput", "KillBash"],
            permission_mode="acceptEdits",
            max_turns=5,
            model="claude-3-5-sonnet-20241022",
            cwd=working_directory,
            add_dirs=[working_directory]  # Also add the directory to context
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
    
    def _debug_log(self, message: str):
        """Log debug messages if debug mode is enabled"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def _add_to_history(self, message_type: str, content: Any):
        """Add message to conversation history for debugging"""
        if self.debug:
            self.conversation_history.append({
                'type': message_type,
                'content': content,
                'timestamp': __import__('datetime').datetime.now().isoformat()
            })
    
    def print_conversation_history(self):
        """Print the full conversation history for debugging"""
        if not self.debug:
            print("Debug mode not enabled. Initialize with debug=True to see conversation history.")
            return
            
        print("\n" + "="*60)
        print("CONVERSATION HISTORY")
        print("="*60)
        
        for i, entry in enumerate(self.conversation_history, 1):
            print(f"\n{i}. [{entry['timestamp']}] {entry['type'].upper()}")
            print("-" * 40)
            
            if isinstance(entry['content'], str):
                print(entry['content'])
            elif isinstance(entry['content'], dict):
                print(json.dumps(entry['content'], indent=2))
            else:
                print(str(entry['content']))
        
        print("\n" + "="*60)
        print(f"Total messages in history: {len(self.conversation_history)}")
        print("="*60)
    
    def clear_conversation_history(self):
        """Clear the conversation history for debugging purposes"""
        if self.debug:
            self.conversation_history.clear()
            self._debug_log("Conversation history cleared")
        
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
        
        # Add user message to history for debugging
        self._add_to_history('user_input', user_message)
        self._debug_log(f"Sending user message: {user_message}")
        
        # Ensure we have an active client for multi-turn conversations
        await self._ensure_client()
        
        try:
            # Send user message to Claude using the persistent client
            self._debug_log("Calling client.query()")
            await self.client.query(user_message)
            
            # Stream responses back
            self._debug_log("Starting to receive response stream")
            response_count = 0
            async for message in self.client.receive_response():
                response_count += 1
                self._debug_log(f"Received response #{response_count}, type: {type(message).__name__}")
                
                # Serialize the message before yielding
                serialized_message = self._serialize_message(message)
                
                # Add to history for debugging
                self._add_to_history('claude_response', serialized_message)
                
                self._debug_log(f"Yielding serialized message: {serialized_message.get('type', 'unknown')}")
                yield serialized_message
                
            self._debug_log(f"Finished streaming. Total responses: {response_count}")
                
        except Exception as e:
            error_msg = f"Error in chat_stream: {e}"
            print(error_msg)
            self._debug_log(error_msg)
            
            # Add error to history
            self._add_to_history('error', error_msg)
            
            # If there's an error, try to recover by creating a new client
            await self._close_client()
            await self._ensure_client()
            
            # Send error message to client
            error_message = {
                'type': 'error',
                'content': f"Chat error occurred, but conversation will continue: {str(e)}"
            }
            self._add_to_history('error_response', error_message)
            yield error_message