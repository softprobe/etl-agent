import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle, Clock, AlertCircle, Code, Table } from 'lucide-react';
import { FileUpload } from './FileUpload';
import { SimpleSchemaPreview } from './SimpleSchemaPreview';
import { ChatInterface } from './ChatInterface';
import { CodeEditor } from './CodeEditor';
import { useFileUpload } from '../hooks/useFileUpload';
import { useWebSocketChat } from '../hooks/useWebSocketChat';
import type { WorkflowState, TableSchema } from '../types';
import { apiService } from '../services/api';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';

const WORKFLOW_STEPS = [
  { id: 'upload', label: 'Upload Files', description: 'Upload your data files' },
  { id: 'schema', label: 'Review Schema', description: 'Approve the proposed table structure' },
  { id: 'chat', label: 'Claude Refine', description: 'Chat to customize your ETL' },
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
  const [rightPanelView, setRightPanelView] = useState<'code' | 'schema'>('code');

  const fileUpload = useFileUpload();
  const chat = useWebSocketChat();

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
        return <CheckCircle className="h-4 w-4 text-white" />;
      case 'current':
        return <Circle className="h-4 w-4 text-white" />;
      case 'loading':
        return <Clock className="h-4 w-4 text-white animate-pulse" />;
      default:
        return <Circle className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="h-screen overflow-hidden" style={{ backgroundColor: '#FCFBF8' }}>
      <ResizablePanelGroup direction="horizontal" className="h-full">
        {/* Left Side - Chat Interface */}
        <ResizablePanel defaultSize={50} minSize={30} maxSize={70}>
          <Card className="h-full border-0 !bg-[#FCFBF8] shadow-none flex flex-col overflow-hidden">
            {/* Header */}
            <div className="px-6 py-4 border-b border-gray-200">
              <h1 className="text-xl font-bold">Softprobe Agentic ETL Engineer</h1>
              <div className="text-xs text-gray-600">
                Transform your JSON data into BigQuery tables with AI assistance
              </div>
            </div>

            {/* Progress Steps */}
            <div className="px-6 py-4">
              <div className="bg-gray-100 rounded-2xl p-4">
                <div className="relative flex items-center justify-between">
                  {WORKFLOW_STEPS.map((step) => (
                    <div key={step.id} className="flex flex-col items-center space-y-2 relative z-10">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center border-2 ${getStepStatus(step.id) === 'completed'
                        ? 'border-green-500 bg-green-500'
                        : getStepStatus(step.id) === 'current'
                          ? 'border-blue-500 bg-blue-500'
                          : 'border-gray-300 bg-gray-200'
                        }`}>
                        {getStepIcon(step.id)}
                      </div>
                      <div className="text-center">
                        <p className={`text-xs font-medium ${getStepStatus(step.id) === 'current'
                          ? 'text-blue-600'
                          : getStepStatus(step.id) === 'completed'
                            ? 'text-green-600'
                            : 'text-gray-500'
                          }`}>
                          {step.label}
                        </p>
                        <p className="text-xs text-gray-400 mt-1">{step.description}</p>
                      </div>
                    </div>
                  ))}
                  {/* 连接线 */}
                  <div className="absolute top-4 left-8 right-8 h-0.5 bg-gray-300 -z-10"></div>
                </div>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="px-6 pb-4 flex-shrink-0">
                <Alert variant="destructive">
                  <AlertCircle className="h-3.5 w-3.5" />
                  <AlertDescription className="text-xs">
                    {error}
                  </AlertDescription>
                </Alert>
              </div>
            )}

            {/* Step Content */}
            <div className="flex-1 flex flex-col px-6 min-h-0">
              {/* Step 1: File Upload */}
              {workflowState.step === 'upload' && (
                <div className="py-4 flex-shrink-0">
                  <FileUpload
                    onFilesUpload={handleFilesUpload}
                    uploadedFiles={fileUpload.uploadedFiles}
                    loading={fileUpload.loading}
                    error={fileUpload.error}
                  />
                </div>
              )}

              {/* Step 2: Schema Analysis - Manual Control */}
              {workflowState.step === 'schema' && schemas.length === 0 && (
                <div className="py-4 flex-shrink-0">
                  <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2">
                      Files Uploaded Successfully
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Ready to analyze your JSON files and generate BigQuery schema. 
                      Click the button below to start the analysis.
                    </p>
                    <Button
                      onClick={() => {
                        const fileNames = workflowState.files.map(f => f.filename).join(', ');
                        chat.sendMessage(`Please analyze the uploaded JSON files and show me the proposed BigQuery schema structure. Files: ${fileNames}`);
                      }}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Table className="h-4 w-4 mr-2" />
                      Analyze Files & Generate Schema
                    </Button>
                  </div>
                </div>
              )}

              {/* Step 3: Chat for Schema Modification - Manual Control */}
              {workflowState.step === 'chat' && schemas.length > 0 && (
                <div className="py-4 flex-shrink-0">
                  <div className="bg-blue-50 rounded-lg border border-blue-200 p-4 text-center">
                    <h3 className="text-sm font-semibold text-blue-800 mb-1">
                      Schema Modification Mode
                    </h3>
                    <p className="text-xs text-blue-600">
                      You can now chat with Claude to modify the schema or ask questions about your data structure.
                    </p>
                  </div>
                </div>
              )}

              {/* Chat Interface - Always visible, takes remaining space */}
              <div className="flex-1 min-h-0">
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
          </Card>
        </ResizablePanel>

        {/* Resize Handle */}
        <ResizableHandle 
          withHandle={false} 
          className="w-1 bg-transparent hover:w-1 my-12 hover:bg-gradient-to-b hover:from-transparent hover:via-blue-500 hover:to-transparent transition-all duration-200 group"
        />

        {/* Right Side - Code Editor / Schema Preview */}
        <ResizablePanel defaultSize={50} minSize={30} maxSize={70}>
          <Card className="h-full border-0 !bg-[#FCFBF8] shadow-none">
            <CardHeader
              className="flex-row items-center justify-between space-y-0"
              style={{ height: '60px', padding: '16px' }}
            >
              <CardTitle
                className="!text-xl !font-bold"
                style={{ fontSize: '1.25rem', fontWeight: '700' }}
              >
                {rightPanelView === 'code' ? 'Code Editor' : 'Schema Preview'}
              </CardTitle>
              <div className="flex items-center space-x-2">
                <Button
                  onClick={() => setRightPanelView('code')}
                  variant={rightPanelView === 'code' ? "default" : "outline"}
                  size="sm"
                  className="relative"
                  style={{
                    padding: '2px 8px',
                    backgroundColor: rightPanelView === 'code' ? '#1f2937' : 'transparent',
                    color: rightPanelView === 'code' ? 'white' : 'inherit',
                    borderColor: rightPanelView === 'code' ? '#1f2937' : '#d1d5db'
                  }}
                >
                  <Code
                    className="mr-1.5"
                    style={{ width: '16px', height: '16px' }}
                  />
                  Code
                  {(ddl || etlCode) && rightPanelView !== 'code' && (
                    <Badge className="absolute -top-1 -right-1 h-2.5 w-2.5 p-0 bg-green-500 border-2 border-white rounded-full" />
                  )}
                </Button>
                <Button
                  onClick={() => setRightPanelView('schema')}
                  variant={rightPanelView === 'schema' ? "default" : "outline"}
                  size="sm"
                  className="relative"
                  style={{
                    padding: '2px 8px',
                    backgroundColor: rightPanelView === 'schema' ? '#1f2937' : 'transparent',
                    color: rightPanelView === 'schema' ? 'white' : 'inherit',
                    borderColor: rightPanelView === 'schema' ? '#1f2937' : '#d1d5db'
                  }}
                >
                  <Table
                    className="mr-1.5"
                    style={{ width: '16px', height: '16px' }}
                  />
                  Schema
                  {schemas.length > 0 && rightPanelView !== 'schema' && (
                    <Badge className="absolute -top-1 -right-1 h-2.5 w-2.5 p-0 bg-blue-500 border-2 border-white rounded-full" />
                  )}
                </Button>
              </div>
            </CardHeader>

            {/* Right Panel Content */}
            <div className="flex-1 h-full">
              {rightPanelView === 'code' ? (
                <div className="h-full">
                  <CodeEditor
                    ddl={ddl}
                    etlCode={etlCode}
                    readonly={false}
                    collapsed={false}
                  />
                </div>
              ) : (
                <div className="h-full overflow-y-auto">
                  <SimpleSchemaPreview
                    schemas={schemas}
                    onApprove={handleSchemaApprove}
                    onModify={handleSchemaModify}
                    loading={loading}
                  />
                </div>
              )}
            </div>
          </Card>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};