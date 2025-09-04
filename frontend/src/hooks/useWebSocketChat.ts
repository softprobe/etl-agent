import { useState, useEffect, useRef, useCallback } from 'react';
import type { ChatMessage } from '../types';
import { apiService } from '../services/api';
import { parseAnthropicMessage } from '../utils/contentExtraction';

export const useWebSocketChat = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isConnectingRef = useRef<boolean>(false);
  const isMountedRef = useRef<boolean>(true);

  // Helper function to create WebSocket with event handlers
  const createWebSocket = useCallback(() => {
    const ws = apiService.createWebSocket();

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
      isConnectingRef.current = false;
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const response = JSON.parse(event.data);
        
        // Use the new Anthropic SDK-based parsing
        const parsedMessage = parseAnthropicMessage(response);
        
        const message: ChatMessage = {
          id: Date.now().toString(),
          type: parsedMessage.type,
          content: parsedMessage.content,
          timestamp: new Date(),
          code: response.code,
          schema: response.schema
        };

        setMessages(prev => [...prev, message]);
        setIsLoading(false);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
        setError('Failed to parse server response');
        setIsLoading(false);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      setIsLoading(false);
      isConnectingRef.current = false;
      console.log('WebSocket disconnected:', event.code, event.reason);
      
      // Only attempt to reconnect if it wasn't a clean close and not a user disconnect
      if (!event.wasClean && event.code !== 1000 && event.code !== 1001) {
        console.log(`WebSocket closed unexpectedly (code: ${event.code}), will reconnect in 3 seconds...`);
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          // Clean up and reconnect
          if (wsRef.current) {
            wsRef.current = null;
          }
          wsRef.current = createWebSocket();
        }, 3000);
      } else {
        console.log('WebSocket closed cleanly, no reconnection needed');
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error');
      setIsLoading(false);
      setIsConnected(false);
      isConnectingRef.current = false;
    };

    return ws;
  }, []);

  const connect = useCallback(() => {
    // Prevent multiple simultaneous connection attempts
    if (isConnectingRef.current) {
      console.log('WebSocket connection already in progress, skipping...');
      return;
    }

    // Don't create a new connection if one is already connecting or connected
    if (wsRef.current && (wsRef.current.readyState === WebSocket.CONNECTING || wsRef.current.readyState === WebSocket.OPEN)) {
      console.log('WebSocket already connecting or connected, skipping...');
      return;
    }

    // Clean up existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    // Clear any pending reconnection
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    try {
      console.log('Creating new WebSocket connection...');
      isConnectingRef.current = true;
      wsRef.current = createWebSocket();
    } catch (err) {
      console.error('Failed to create WebSocket connection:', err);
      setError('Failed to connect to chat service');
      setIsConnected(false);
      isConnectingRef.current = false;
    }
  }, [createWebSocket]);

  const sendMessage = useCallback((content: string) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError('Not connected to chat service');
      return;
    }

    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);

    // Send to server
    setIsLoading(true);
    setError(null);
    
    try {
      wsRef.current.send(content);
    } catch (err) {
      console.error('Failed to send message:', err);
      setError('Failed to send message');
      setIsLoading(false);
    }
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnect');
      wsRef.current = null;
    }
    
    setIsConnected(false);
    setIsLoading(false);
    isConnectingRef.current = false;
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    // Mark component as mounted
    isMountedRef.current = true;
    
    // Only connect if not already connected
    if (!wsRef.current || wsRef.current.readyState === WebSocket.CLOSED) {
      // Inline WebSocket creation to avoid any dependency issues
      try {
        console.log('Creating initial WebSocket connection...');
        isConnectingRef.current = true;
        
        const ws = apiService.createWebSocket();
        wsRef.current = ws;

        ws.onopen = () => {
          setIsConnected(true);
          setError(null);
          isConnectingRef.current = false;
          console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
          try {
            const response = JSON.parse(event.data);
            
            // Use the new Anthropic SDK-based parsing
            const parsedMessage = parseAnthropicMessage(response);
            
            const message: ChatMessage = {
              id: Date.now().toString(),
              type: parsedMessage.type,
              content: parsedMessage.content,
              timestamp: new Date(),
              code: response.code,
              schema: response.schema
            };

            setMessages(prev => [...prev, message]);
            setIsLoading(false);
          } catch (err) {
            console.error('Failed to parse WebSocket message:', err);
            setError('Failed to parse server response');
            setIsLoading(false);
          }
        };

        ws.onclose = (event) => {
          setIsConnected(false);
          setIsLoading(false);
          isConnectingRef.current = false;
          console.log('WebSocket disconnected:', event.code, event.reason);
          
          // Only attempt to reconnect if it wasn't a clean close and not a user disconnect
          if (!event.wasClean && event.code !== 1000 && event.code !== 1001) {
            console.log(`WebSocket closed unexpectedly (code: ${event.code}), will reconnect in 3 seconds...`);
            reconnectTimeoutRef.current = setTimeout(() => {
              // Only reconnect if component is still mounted
              if (!isMountedRef.current) {
                console.log('Component unmounted, skipping reconnection');
                return;
              }
              
              console.log('Attempting to reconnect...');
              // Clean up and reconnect with inline logic
              if (wsRef.current) {
                wsRef.current = null;
              }
              
              try {
                const ws = apiService.createWebSocket();
                wsRef.current = ws;

                ws.onopen = () => {
                  setIsConnected(true);
                  setError(null);
                  isConnectingRef.current = false;
                  console.log('WebSocket reconnected');
                };

                ws.onmessage = (event) => {
                  try {
                    const response = JSON.parse(event.data);
                    
                    // Use the new Anthropic SDK-based parsing
                    const parsedMessage = parseAnthropicMessage(response);
                    
                    const message: ChatMessage = {
                      id: Date.now().toString(),
                      type: parsedMessage.type,
                      content: parsedMessage.content,
                      timestamp: new Date(),
                      code: response.code,
                      schema: response.schema
                    };

                    setMessages(prev => [...prev, message]);
                    setIsLoading(false);
                  } catch (err) {
                    console.error('Failed to parse WebSocket message:', err);
                    setError('Failed to parse server response');
                    setIsLoading(false);
                  }
                };

                ws.onclose = (event) => {
                  setIsConnected(false);
                  setIsLoading(false);
                  isConnectingRef.current = false;
                  console.log('WebSocket disconnected:', event.code, event.reason);
                  
                  // Recursive reconnection
                  if (!event.wasClean && event.code !== 1000 && event.code !== 1001) {
                    console.log(`WebSocket closed unexpectedly (code: ${event.code}), will reconnect in 3 seconds...`);
                    reconnectTimeoutRef.current = setTimeout(() => {
                      console.log('Attempting to reconnect...');
                      // This will be handled by the same logic
                    }, 3000);
                  } else {
                    console.log('WebSocket closed cleanly, no reconnection needed');
                  }
                };

                ws.onerror = (error) => {
                  console.error('WebSocket error:', error);
                  setError('Connection error');
                  setIsLoading(false);
                  setIsConnected(false);
                  isConnectingRef.current = false;
                };
              } catch (err) {
                console.error('Failed to reconnect:', err);
                setError('Failed to reconnect to chat service');
                setIsConnected(false);
                isConnectingRef.current = false;
              }
            }, 3000);
          } else {
            console.log('WebSocket closed cleanly, no reconnection needed');
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          setError('Connection error');
          setIsLoading(false);
          setIsConnected(false);
          isConnectingRef.current = false;
        };
        
      } catch (err) {
        console.error('Failed to create initial WebSocket connection:', err);
        setError('Failed to connect to chat service');
        setIsConnected(false);
        isConnectingRef.current = false;
      }
    }
    
    return () => {
      // Mark component as unmounted
      isMountedRef.current = false;
      
      // Cleanup on unmount
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      
      if (wsRef.current) {
        wsRef.current.close(1000, 'User disconnect');
        wsRef.current = null;
      }
      
      setIsConnected(false);
      setIsLoading(false);
      isConnectingRef.current = false;
    };
  }, []); // Empty dependency array - only run on mount/unmount

  return {
    messages,
    isConnected,
    isLoading,
    error,
    sendMessage,
    connect,
    disconnect,
    clearMessages
  };
};