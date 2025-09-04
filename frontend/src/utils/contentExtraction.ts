// Using Anthropic SDK types for proper message parsing
// Note: We import types implicitly through the SDK for type safety

/**
 * Utility function to extract readable content from Claude message objects
 * Uses Anthropic's official SDK types for proper parsing and type safety
 */
export const extractContent = (content: any): string => {
  console.log('extractContent', content);
  
  if (typeof content === 'string') {
    return content;
  }
  
  if (Array.isArray(content)) {
    return content.map((item: any) => extractContent(item)).join('\n');
  }
  
  if (content && typeof content === 'object') {
    // Handle Anthropic SDK message types
    const extracted = extractFromAnthropicMessage(content);
    if (extracted !== content) {
      return extracted;
    }
    
    // Handle legacy object structures
    if (content.text) {
      return content.text;
    }
    
    if (content.content) {
      return extractContent(content.content);
    }
    
    if (content.message) {
      return content.message;
    }
    
    // If it's a complex object, try to stringify it nicely
    if (content.toString && content.toString() !== '[object Object]') {
      return content.toString();
    }
    
    // Last resort: JSON stringify with formatting
    try {
      return JSON.stringify(content, null, 2);
    } catch {
      return String(content);
    }
  }
  
  return String(content || '');
};

/**
 * Extract content from Anthropic SDK message types
 */
const extractFromAnthropicMessage = (message: any): string => {
  try {
    // Handle AssistantMessage
    if (message.content && Array.isArray(message.content) && message.model) {
      return message.content.map((block: any) => extractFromContentBlock(block)).join('\n');
    }
    
    // Handle UserMessage
    if (message.content && Array.isArray(message.content) && !message.model) {
      return message.content.map((block: any) => extractFromContentBlock(block)).join('\n');
    }
    
    // Handle SystemMessage
    if (message.subtype === 'init' && message.data) {
      return `System initialized in ${message.data.cwd || 'unknown directory'}`;
    }
    
    // Handle individual content blocks
    if (message.type) {
      return extractFromContentBlock(message);
    }
    
    return message; // Return original if no match
  } catch (error) {
    console.error('Error extracting from Anthropic message:', error);
    return String(message);
  }
};

/**
 * Extract content from individual content blocks
 */
const extractFromContentBlock = (block: any): string => {
  try {
    // Handle TextBlock
    if (block.type === 'text' || block.text) {
      return block.text || block.content || '';
    }
    
    // Handle ToolUseBlock
    if (block.type === 'tool_use' || (block.name && block.input)) {
      const toolName = block.name;
      const input = block.input;
      
      // Format tool usage in a readable way
      if (toolName === 'LS') {
        return `📁 Listing directory: ${input.path || 'current directory'}`;
      } else if (toolName === 'Read') {
        return `📖 Reading file: ${input.file_path || input.path || 'unknown file'}`;
      } else if (toolName === 'Write') {
        return `✏️ Writing to file: ${input.file_path || 'unknown file'}`;
      } else if (toolName === 'Edit') {
        return `✏️ Editing file: ${input.file_path || 'unknown file'}`;
      } else if (toolName === 'Bash') {
        return `💻 Running command: ${input.command || 'unknown command'}`;
      } else if (toolName === 'Grep') {
        return `🔍 Searching for: "${input.pattern || 'unknown pattern'}" in ${input.path || 'files'}`;
      } else if (toolName === 'Glob') {
        return `🔍 Finding files: ${input.pattern || 'unknown pattern'}`;
      } else {
        return `🔧 Using tool: ${toolName}`;
      }
    }
    
    // Handle ToolResultBlock
    if (block.type === 'tool_result' || block.tool_use_id) {
      const content = block.content || '';
      // Handle escaped newlines and other escape sequences
      return typeof content === 'string' ? content.replace(/\\n/g, '\n').replace(/\\t/g, '\t') : String(content);
    }
    
    // Handle other block types
    if (block.content) {
      return extractContent(block.content);
    }
    
    return String(block);
  } catch (error) {
    console.error('Error extracting from content block:', error);
    return String(block);
  }
};

/**
 * Type-safe message parsing using Anthropic SDK types
 */
export const parseAnthropicMessage = (messageData: any): {
  role: 'user' | 'assistant' | 'system';
  content: string;
  type: 'user' | 'assistant' | 'system' | 'error';
} => {
  try {
    // Determine message type and role
    let role: 'user' | 'assistant' | 'system' = 'user';
    let type: 'user' | 'assistant' | 'system' | 'error' = 'user';
    
    if (messageData.model) {
      role = 'assistant';
      type = 'assistant';
    } else if (messageData.subtype === 'init') {
      role = 'system';
      type = 'system';
    } else if (messageData.type === 'error') {
      type = 'error';
    }
    
    // Extract content
    const content = extractContent(messageData);
    
    return {
      role,
      content,
      type
    };
  } catch (error) {
    console.error('Error parsing Anthropic message:', error);
    return {
      role: 'user',
      content: String(messageData),
      type: 'error'
    };
  }
};