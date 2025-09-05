import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertCircle, Loader2, RotateCcw, Info } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { ChatMessage } from '../types';
import { extractContent } from '../utils/contentExtraction';
import { apiService } from '../services/api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';

interface ChatInterfaceProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isConnected: boolean;
  isLoading: boolean;
  onCodeGenerated?: (code: string) => void;
  onSchemaGenerated?: (schema: any) => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  isConnected,
  isLoading,
  onCodeGenerated,
  onSchemaGenerated
}) => {
  const [input, setInput] = useState('');
  const [sessionStatus, setSessionStatus] = useState<{isActive: boolean, message: string} | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check session status on mount
  useEffect(() => {
    const checkSessionStatus = async () => {
      try {
        const response = await (apiService as any).getChatStatus();
        setSessionStatus({
          isActive: response.is_active,
          message: response.message
        });
      } catch (error) {
        console.error('Failed to check session status:', error);
      }
    };
    
    if (isConnected) {
      checkSessionStatus();
    }
  }, [isConnected]);

  const handleNewSession = async () => {
    try {
      await (apiService as any).startNewChatSession();
      setSessionStatus({
        isActive: true,
        message: 'New conversation session started'
      });
      // Send a system message to indicate new session
      onSendMessage('/new');
    } catch (error) {
      console.error('Failed to start new session:', error);
    }
  };

  const handleCheckStatus = async () => {
    try {
      const response = await (apiService as any).getChatStatus();
      setSessionStatus({
        isActive: response.is_active,
        message: response.message
      });
      onSendMessage('/status');
    } catch (error) {
      console.error('Failed to check session status:', error);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && isConnected && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const formatMessageContent = (message: ChatMessage) => {
    if (message.code && onCodeGenerated) {
      onCodeGenerated(message.code);
    }
    if (message.schema && onSchemaGenerated) {
      onSchemaGenerated(message.schema);
    }

    return extractContent(message.content);
  };

  const getMessageIcon = (type: ChatMessage['type']) => {
    switch (type) {
      case 'user':
        return <User className="h-5 w-5" />;
      case 'assistant':
        return <Bot className="h-5 w-5" />;
      case 'error':
        return <AlertCircle className="h-5 w-5" />;
      default:
        return <Bot className="h-5 w-5" />;
    }
  };

  const getMessageStyle = (type: ChatMessage['type']) => {
    switch (type) {
      case 'user':
        return 'bg-gradient-to-br from-blue-500 to-blue-600 text-white ml-auto max-w-xs shadow-lg border border-blue-400';
      case 'assistant':
        return 'bg-gradient-to-br from-gray-50 to-white text-gray-900 mr-auto max-w-2xl shadow-md border border-gray-200';
      case 'error':
        return 'bg-gradient-to-br from-red-50 to-red-100 border-2 border-red-200 text-red-800 mr-auto max-w-lg shadow-md';
      case 'system':
        return 'bg-gradient-to-br from-amber-50 to-yellow-100 border-2 border-amber-200 text-amber-800 mx-auto max-w-sm shadow-sm';
      default:
        return 'bg-gradient-to-br from-gray-50 to-white text-gray-900 mr-auto max-w-2xl shadow-md border border-gray-200';
    }
  };

  const getIconContainerStyle = (type: ChatMessage['type']) => {
    switch (type) {
      case 'user':
        return 'bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-lg border border-blue-400';
      case 'assistant':
        return 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md border border-indigo-400';
      case 'error':
        return 'bg-gradient-to-br from-red-500 to-red-600 text-white shadow-md border border-red-400';
      case 'system':
        return 'bg-gradient-to-br from-amber-500 to-orange-500 text-white shadow-sm border border-amber-400';
      default:
        return 'bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md border border-indigo-400';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card>
        <CardHeader className="pb-6">
          <CardTitle className="text-md flex items-center">
            <Bot className="h-4 w-4 mr-2 text-blue-500" />
            Chat with Claude
          </CardTitle>
          <CardDescription className="text-xs">
            Ask questions about your ETL pipeline or request modifications
          </CardDescription>
        
          {/* Connection Status */}
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center">
              <Badge 
                variant={isConnected ? "default" : "destructive"}
                className="text-xs mr-3"
              >
                {isConnected ? 'Connected to Claude' : 'Disconnected'}
              </Badge>
              {sessionStatus && (
                <Badge 
                  variant={sessionStatus.isActive ? "default" : "secondary"}
                  className="text-xs"
                >
                  {sessionStatus.isActive ? 'Active Session' : 'No Session'}
                </Badge>
              )}
            </div>
            
            {/* Session Management Controls */}
            <div className="flex items-center space-x-1.5">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleCheckStatus}
                className="h-8 w-8 p-0"
                title="Check session status"
              >
                <Info className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleNewSession}
                className="h-8 w-8 p-0"
                title="Start new conversation"
              >
                <RotateCcw className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </CardHeader>

        {/* Messages Container */}
        <CardContent className="p-0">
          <ScrollArea className="h-96 p-6">
            <div className="space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="p-3 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg border border-indigo-400 w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                <Bot className="h-6 w-6" />
              </div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">
                Start a conversation
              </h3>
              <p className="text-gray-500 text-xs mb-4 max-w-md mx-auto">
                Ask me to analyze your JSON files, generate schemas, or create ETL code
              </p>
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 max-w-lg mx-auto border border-blue-200">
                <div className="flex items-center justify-center mb-3">
                  <span className="text-lg">💡</span>
                  <span className="ml-2 text-xs font-semibold text-blue-800">Try saying:</span>
                </div>
                <div className="space-y-2 text-xs text-blue-700 text-left">
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>"Create a normalized schema for my JSON data"</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>"Generate ETL code for BigQuery"</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-500 mt-0.5">•</span>
                    <span>"The date fields look wrong, can you fix them?"</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div key={message.id} className={`flex items-start space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}>
                  {/* Avatar */}
                  <div className={`p-2 rounded-full ${getIconContainerStyle(message.type)} flex-shrink-0`}>
                    {getMessageIcon(message.type)}
                  </div>
                  
                  {/* Message Content */}
                  <div className={`p-3 rounded-xl ${getMessageStyle(message.type)} relative`}>
                    {/* Message Type Label */}
                    <div className={`text-xs font-semibold uppercase tracking-wide mb-1.5 ${
                      message.type === 'user' 
                        ? 'text-blue-100' 
                        : message.type === 'error'
                          ? 'text-red-600'
                          : message.type === 'system'
                            ? 'text-amber-600'
                            : 'text-indigo-600'
                    }`}>
                      {message.type === 'user' ? 'You' : 
                       message.type === 'assistant' ? 'Claude' :
                       message.type === 'error' ? 'Error' :
                       message.type === 'system' ? 'System' : 'Assistant'}
                    </div>
                    
                    {/* Message Text */}
                    <div className="text-xs leading-relaxed prose prose-sm max-w-none">
                      {message.type === 'assistant' ? (
                        <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          components={{
                            // Custom styling for markdown elements
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                            li: ({ children }) => <li className="text-sm">{children}</li>,
                            code: ({ children, className }) => {
                              const isInline = !className;
                              return isInline ? (
                                <code className="bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-xs font-mono">
                                  {children}
                                </code>
                              ) : (
                                <code className="block bg-gray-900 text-green-400 p-3 rounded-lg text-xs font-mono overflow-x-auto">
                                  {children}
                                </code>
                              );
                            },
                            pre: ({ children }) => (
                              <pre className="bg-gray-900 text-green-400 p-3 rounded-lg text-xs font-mono overflow-x-auto mb-2">
                                {children}
                              </pre>
                            ),
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-4 border-gray-300 pl-4 italic text-gray-600 mb-2">
                                {children}
                              </blockquote>
                            ),
                            h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
                            h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
                            strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                            em: ({ children }) => <em className="italic">{children}</em>,
                          }}
                        >
                          {formatMessageContent(message)}
                        </ReactMarkdown>
                      ) : (
                        <div className="whitespace-pre-wrap">
                          {formatMessageContent(message)}
                        </div>
                      )}
                    </div>
                    
                    {/* Timestamp */}
                    <div className={`text-xs mt-1.5 ${
                      message.type === 'user' 
                        ? 'text-blue-100' 
                        : 'text-gray-400'
                    }`}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                    
                    {/* Code Preview */}
                    {message.code && (
                      <div className="mt-3 p-3 bg-gray-900 text-green-400 rounded-lg text-xs font-mono overflow-x-auto border border-gray-700">
                        <div className="flex items-center justify-between mb-1.5">
                          <span className="text-gray-400 text-xs font-semibold">CODE PREVIEW</span>
                          <button 
                            className="text-blue-400 hover:text-blue-300 text-xs font-medium transition-colors"
                            onClick={() => onCodeGenerated && onCodeGenerated(message.code!)}
                          >
                            View Full Code →
                          </button>
                        </div>
                        <pre className="text-xs leading-relaxed">{message.code.slice(0, 200)}...</pre>
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {/* Loading Indicator */}
              {isLoading && (
                <div className="flex items-start space-x-3">
                  <div className="p-2 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-md border border-indigo-400 flex-shrink-0">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="p-3 rounded-xl bg-gradient-to-br from-gray-50 to-white text-gray-900 mr-auto max-w-2xl shadow-md border border-gray-100">
                    <div className="text-xs font-semibold uppercase tracking-wide mb-1.5 text-indigo-600">
                      Claude
                    </div>
                    <div className="flex items-center space-x-2">
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-indigo-600" />
                      <span className="text-xs">Thinking...</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
        </CardContent>

        {/* Input Form */}
        <CardContent className="border-t p-4">
          <form onSubmit={handleSubmit} className="flex space-x-3">
            <Input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={
                isConnected 
                  ? "Ask Claude about your ETL pipeline..." 
                  : "Connecting to Claude..."
              }
              disabled={!isConnected || isLoading}
              className="text-xs"
            />
            <Button
              type="submit"
              disabled={!input.trim() || !isConnected || isLoading}
              size="sm"
              className="text-xs font-medium"
            >
              {isLoading ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Send className="h-3.5 w-3.5" />
              )}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};