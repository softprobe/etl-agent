import json
from typing import Dict, List, Any, AsyncIterator
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions
import os
import shutil
from pathlib import Path

class ClaudeETLAgent:
    def __init__(self, work_dir: str = None, debug: bool = True, mode: str = "automated"):
        self.debug = debug  # Debug flag to enable/disable tracing
        self.conversation_history = []  # Store conversation history for debugging
        self.mode = mode  # "interactive" or "automated"
        
        # Use provided work directory or default to current directory
        working_directory = work_dir or os.getcwd()
        
        # Ensure we have an absolute path for the working directory
        if not os.path.isabs(working_directory):
            working_directory = os.path.abspath(working_directory)
        
        print(f"🔧 ClaudeETLAgent initialized with working directory: {working_directory}")
        print(f"🔧 Mode: {self.mode}")
        
        # Generate mode-specific system prompt
        system_prompt = self._generate_system_prompt()
        print(system_prompt)
        
        self.options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            allowed_tools=["Bash", "Glob", "Grep", "LS", "Read", "Edit", "MultiEdit", "Write", "NotebookEdit", "WebFetch", "TodoWrite", "WebSearch", "BashOutput", "KillBash"],
            permission_mode="acceptEdits",
            max_turns=15,
            model="claude-3-5-sonnet-20241022",
            cwd=working_directory,
            add_dirs=[working_directory]  # Also add the directory to context
        )
        
        # Initialize persistent client for multi-turn conversations
        self.client = None
        self.is_client_active = False
    
    def _load_prompt_file(self, filename: str) -> str:
        """Load prompt content from markdown file"""
        try:
            prompt_path = Path(__file__).parent.parent / "prompts" / filename
            with open(prompt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                self._debug_log(f"Loaded prompt file: {filename} ({len(content)} chars)")
                return content
        except Exception as e:
            self._debug_log(f"Error loading prompt file {filename}: {e}")
            return f"Error loading prompt file {filename}: {e}"

    def _generate_system_prompt(self) -> str:
        """Generate system prompt based on the current mode"""
        # Load base prompt
        base_prompt = self._load_prompt_file("base_prompt.md")
        
        # Load mode-specific instructions
        if self.mode == "automated":
            execution_instructions = self._load_prompt_file("automated_mode.md")
        else:  # interactive mode
            execution_instructions = self._load_prompt_file("interactive_mode.md")
        
        # Combine prompts
        full_prompt = f"{base_prompt}\n\n{execution_instructions}"

        print(full_prompt)
        
        # Log the generated prompt for debugging
        self._debug_log(f"Generated system prompt for mode '{self.mode}' ({len(full_prompt)} chars)")
        if self.debug:
            print(f"\n{'='*60}")
            print(f"SYSTEM PROMPT FOR MODE: {self.mode.upper()}")
            print(f"{'='*60}")
            print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
            print(f"{'='*60}\n")
        
        return full_prompt

    @classmethod
    def create_automated_agent(cls, work_dir: str = None, debug: bool = False):
        """Convenience method to create an agent in automated mode"""
        return cls(work_dir=work_dir, debug=debug, mode="automated")
    
    @classmethod
    def create_interactive_agent(cls, work_dir: str = None, debug: bool = False):
        """Convenience method to create an agent in interactive mode"""
        return cls(work_dir=work_dir, debug=debug, mode="interactive")

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
            timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] [DEBUG] {message}")
    
    def _log_message(self, message_type: str, content: Any, show_content: bool = True):
        """Log messages with better formatting for tracing"""
        timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if self.debug:
            print(f"\n[{timestamp}] [{message_type.upper()}]")
            print("-" * 50)
            
            if show_content:
                if isinstance(content, str):
                    # Truncate very long strings for readability
                    display_content = content[:500] + "..." if len(content) > 500 else content
                    print(display_content)
                elif isinstance(content, dict):
                    # Show key information from dict
                    if 'type' in content:
                        print(f"Type: {content['type']}")
                    if 'content' in content and isinstance(content['content'], str):
                        display_content = content['content'][:300] + "..." if len(content['content']) > 300 else content['content']
                        print(f"Content: {display_content}")
                    else:
                        print(f"Data: {str(content)[:300]}...")
                else:
                    print(str(content)[:300] + "..." if len(str(content)) > 300 else str(content))
            else:
                print(f"Content length: {len(str(content))} chars")
            
            print("-" * 50)
    
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
            # Handle different message types based on their class names
            message_type = type(message).__name__
            self._debug_log(f"Serializing {message_type}")
            
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
            error_msg = f"Error serializing {type(message).__name__}: {e}"
            self._debug_log(error_msg)
            return {
                'type': 'error',
                'content': f"Error processing message: {str(e)}"
            }

    async def chat_stream(self, user_message: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream chat responses for real-time interaction with persistent conversation"""
        
        # Log user input
        self._log_message('USER_INPUT', user_message)
        self._add_to_history('user_input', user_message)
        
        # Ensure we have an active client for multi-turn conversations
        await self._ensure_client()
        
        try:
            # Send user message to Claude using the persistent client
            self._debug_log("Sending query to Claude...")
            await self.client.query(user_message)
            
            # Stream responses back
            self._debug_log("Starting response stream...")
            response_count = 0
            async for message in self.client.receive_response():
                response_count += 1
                message_type = type(message).__name__
                self._debug_log(f"Received response #{response_count}: {message_type}")
                
                # Serialize the message before yielding
                serialized_message = self._serialize_message(message)
                
                # Log the response with better formatting
                self._log_message('CLAUDE_RESPONSE', serialized_message, show_content=True)
                
                # Add to history for debugging
                self._add_to_history('claude_response', serialized_message)
                
                yield serialized_message
                
            self._debug_log(f"Stream completed. Total responses: {response_count}")
                
        except Exception as e:
            error_msg = f"Error in chat_stream: {e}"
            self._log_message('ERROR', error_msg)
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