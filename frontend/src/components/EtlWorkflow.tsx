import React, { useState, useEffect, useRef, useCallback } from 'react';
import { CheckCircle, Circle, Clock, AlertCircle, Code, GripVertical } from 'lucide-react';
import { FileUpload } from './FileUpload';
import { SimpleSchemaPreview } from './SimpleSchemaPreview';
import { ChatInterface } from './ChatInterface';
import { CodeEditor } from './CodeEditor';
import { useFileUpload } from '../hooks/useFileUpload';
import { useWebSocketChat } from '../hooks/useWebSocketChat';
import type { WorkflowState, TableSchema } from '../types';
import { apiService } from '../services/api';

const WORKFLOW_STEPS = [
  { id: 'upload', label: 'Upload JSON Files', description: 'Upload your data files' },
  { id: 'schema', label: 'Review Schema', description: 'Approve the proposed table structure' },
  { id: 'chat', label: 'Refine with Claude', description: 'Chat to customize your ETL' },
  { id: 'deploy', label: 'Deploy ETL', description: 'Deploy to Google Cloud Run' }
];

export const EtlWorkflow: React.FC = () => {
  const [workflowState, setWorkflowState] = useState<WorkflowState>({
    step: 'upload',
    files: []
  });
  const [schemas, setSchemas] = useState<TableSchema[]>([]);
  const [ddl, setDdl] = useState('');
  const [etlCode, setEtlCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCodeEditor, setShowCodeEditor] = useState(true);
  const [leftColumnWidth, setLeftColumnWidth] = useState(60); // percentage
  const [isResizing, setIsResizing] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const fileUpload = useFileUpload();
  const chat = useWebSocketChat();

  // Resize handlers
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing || !containerRef.current) return;
    
    const containerRect = containerRef.current.getBoundingClientRect();
    const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100;
    
    // Constrain between 30% and 80%
    const constrainedWidth = Math.min(Math.max(newLeftWidth, 30), 80);
    setLeftColumnWidth(constrainedWidth);
  }, [isResizing]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  // Add event listeners for mouse move and up
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  // Update workflow files when upload succeeds
  useEffect(() => {
    setWorkflowState(prev => ({
      ...prev,
      files: fileUpload.uploadedFiles
    }));
  }, [fileUpload.uploadedFiles]);

  const handleFilesUpload = async (files: File[]) => {
    try {
      const response = await fileUpload.uploadFiles(files);
      
      // Auto-advance to schema step if files uploaded successfully
      if (response.status === 'success' && response.files.length > 0) {
        // Generate initial schema analysis via chat
        chat.sendMessage(`Please analyze the uploaded JSON files and show me the proposed BigQuery schema structure. Files: ${response.files.map(f => f.filename).join(', ')}`);
        setWorkflowState(prev => ({
          ...prev,
          step: 'schema'
        }));
      }
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const handleSchemaApprove = async () => {
    if (workflowState.files.length === 0) {
      setError('No files uploaded');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Generate DDL
      const ddlResponse = await apiService.generateDDL({
        json_files: workflowState.files.map(f => f.path),
        table_name: 'generated_table',
        dataset_id: 'etl_dataset',
        user_requirements: 'Generate optimized BigQuery schema from uploaded JSON files'
      });

      // Generate ETL code
      const etlResponse = await apiService.generateETL({
        json_files: workflowState.files.map(f => f.path),
        table_name: 'generated_table',
        dataset_id: 'etl_dataset',
        user_requirements: 'Generate Python ETL code for BigQuery deployment'
      });

      setDdl(ddlResponse.ddl);
      setEtlCode(etlResponse.etl_code);
      
      setWorkflowState(prev => ({
        ...prev,
        step: 'chat',
        ddl: ddlResponse.ddl,
        etl_code: etlResponse.etl_code
      }));
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate code';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleSchemaModify = () => {
    // Switch to chat to discuss modifications
    setWorkflowState(prev => ({
      ...prev,
      step: 'chat'
    }));
    chat.sendMessage('I see some issues with the proposed schema. Can you help me modify it?');
  };

  const handleChatCodeGenerated = (code: string) => {
    if (code.includes('CREATE TABLE') || code.includes('CREATE OR REPLACE TABLE')) {
      setDdl(code);
    } else if (code.includes('def') && code.includes('bigquery')) {
      setEtlCode(code);
    }
  };

  const handleChatSchemaGenerated = (schema: any) => {
    if (schema && Array.isArray(schema)) {
      setSchemas(schema);
    }
  };

  const getStepStatus = (stepId: string) => {
    const currentIndex = WORKFLOW_STEPS.findIndex(s => s.id === workflowState.step);
    const stepIndex = WORKFLOW_STEPS.findIndex(s => s.id === stepId);
    
    if (stepIndex < currentIndex) return 'completed';
    if (stepIndex === currentIndex) return loading ? 'loading' : 'current';
    return 'pending';
  };

  const getStepIcon = (stepId: string) => {
    const status = getStepStatus(stepId);
    
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'current':
        return <Circle className="h-5 w-5 text-blue-600" />;
      case 'loading':
        return <Clock className="h-5 w-5 text-blue-600 animate-pulse" />;
      default:
        return <Circle className="h-5 w-5 text-gray-400" />;
    }
  };

  return (
    <div ref={containerRef} className="h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex overflow-hidden">
      {/* Left Side - Code Editor (adjustable width) */}
      <div 
        className="flex flex-col"
        style={{ width: `${leftColumnWidth}%` }}
      >
        {/* Code Editor Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Code Editor
            </h1>
            <p className="text-sm text-gray-600">
              DDL and ETL Code
            </p>
          </div>
          <button
            onClick={() => setShowCodeEditor(!showCodeEditor)}
            className={`relative flex items-center px-4 py-2 rounded-lg border transition-all duration-200 ${
              showCodeEditor
                ? 'bg-blue-600 text-white border-blue-600 shadow-lg'
                : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:shadow-md'
            }`}
          >
            <Code className="h-4 w-4 mr-2" />
            {showCodeEditor ? 'Hide Code' : 'View Code'}
            {(ddl || etlCode) && !showCodeEditor && (
              <div className="absolute -top-1 -right-1 h-3 w-3 bg-green-500 border-2 border-white rounded-full"></div>
            )}
          </button>
        </div>

        {/* Code Editor Content */}
        <div className="flex-1 min-h-0">
          {showCodeEditor ? (
            <div className="h-full">
              <CodeEditor
                ddl={ddl}
                etlCode={etlCode}
                readonly={false}
                collapsed={false}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full bg-gray-50">
              <div className="text-center">
                <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Click "View Code" to see the generated DDL and ETL code</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Resize Handle */}
      <div
        className={`w-1 bg-gray-300 hover:bg-blue-400 cursor-col-resize flex items-center justify-center transition-colors ${
          isResizing ? 'bg-blue-500' : ''
        }`}
        onMouseDown={handleMouseDown}
      >
        <GripVertical className="h-4 w-4 text-gray-500" />
      </div>

      {/* Right Side - Adjustable Width Column */}
      <div 
        className="bg-white border-l border-gray-200 flex flex-col"
        style={{ width: `${100 - leftColumnWidth}%` }}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Agentic ETL Engineer
          </h1>
          <p className="text-sm text-gray-600">
            Transform your JSON data into BigQuery tables with AI assistance
          </p>
        </div>

        {/* Progress Steps */}
        <div className="p-6 border-b border-gray-200">
          <div className="space-y-4">
            {WORKFLOW_STEPS.map((step) => (
              <div key={step.id} className="flex items-start space-x-3">
                <div className={`p-2 rounded-full border-2 ${
                  getStepStatus(step.id) === 'completed' 
                    ? 'border-green-600 bg-green-50'
                    : getStepStatus(step.id) === 'current'
                      ? 'border-blue-600 bg-blue-50'
                      : 'border-gray-300 bg-white'
                }`}>
                  {getStepIcon(step.id)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className={`text-sm font-medium ${
                    getStepStatus(step.id) === 'current' 
                      ? 'text-blue-600' 
                      : 'text-gray-900'
                  }`}>
                    {step.label}
                  </p>
                  <p className="text-xs text-gray-500">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="p-6 border-b border-gray-200">
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-start">
                <AlertCircle className="h-4 w-4 text-red-400 mr-2 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Step Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6 space-y-6">
            {/* Step 1: File Upload */}
            {workflowState.step === 'upload' && (
              <FileUpload
                onFilesUpload={handleFilesUpload}
                uploadedFiles={fileUpload.uploadedFiles}
                loading={fileUpload.loading}
                error={fileUpload.error}
              />
            )}

            {/* Step 2: Schema Preview */}
            {workflowState.step === 'schema' && (
              <SimpleSchemaPreview
                schemas={schemas}
                onApprove={handleSchemaApprove}
                onModify={handleSchemaModify}
                loading={loading}
              />
            )}

            {/* Chat Interface */}
            <ChatInterface
              messages={chat.messages}
              onSendMessage={chat.sendMessage}
              isConnected={chat.isConnected}
              isLoading={chat.isLoading}
              onCodeGenerated={handleChatCodeGenerated}
              onSchemaGenerated={handleChatSchemaGenerated}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <div className="text-xs text-gray-500 space-y-1">
            <p className="flex items-center space-x-2">
              <span>🤖 Powered by Claude AI</span>
            </p>
            <p className="flex items-center space-x-2">
              <span>☁️ Built for Google BigQuery and Cloud Run</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};