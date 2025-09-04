import type { UploadResponse, DDLRequest } from '../types';

const API_BASE = 'http://localhost:8000';

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  async uploadFiles(files: File[]): Promise<UploadResponse> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const response = await fetch(`${this.baseUrl}/api/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Failed to upload files');
    }

    return response.json();
  }

  async generateDDL(request: DDLRequest): Promise<{ ddl: string }> {
    const response = await fetch(`${this.baseUrl}/api/generate-ddl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Failed to generate DDL');
    }

    return response.json();
  }

  async generateETL(request: DDLRequest): Promise<{ etl_code: string }> {
    const response = await fetch(`${this.baseUrl}/api/generate-etl`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Failed to generate ETL code');
    }

    return response.json();
  }

  createWebSocket(): WebSocket {
    const wsUrl = this.baseUrl.replace('http', 'ws');
    return new WebSocket(`${wsUrl}/ws/chat`);
  }

  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    return response.json();
  }

  async startNewChatSession(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/chat/new-session`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Failed to start new session');
    }

    return response.json();
  }

  async getChatStatus(): Promise<{ status: string; is_active: boolean; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/chat/status`);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Failed to get chat status');
    }

    return response.json();
  }

  async cleanupChatSession(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${this.baseUrl}/api/chat/cleanup`, {
      method: 'POST',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.error || 'Failed to cleanup session');
    }

    return response.json();
  }
}

export const apiService = new ApiService();