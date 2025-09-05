import React, { useState } from 'react';
import { Editor } from '@monaco-editor/react';
import { Code, Copy, Download, Eye, Save } from 'lucide-react';
import { FileTree } from './FileTree';

interface CodeEditorProps {
  ddl?: string;
  etlCode?: string;
  onCodeChange?: (type: 'ddl' | 'etl', code: string) => void;
  readonly?: boolean;
  collapsed?: boolean;
}

export const CodeEditor: React.FC<CodeEditorProps> = ({
  ddl = '',
  etlCode = '',
  onCodeChange,
  readonly = false,
  collapsed = true
}) => {
  const [activeTab, setActiveTab] = useState<'ddl' | 'etl' | 'file'>('ddl');
  const [isCollapsed, setIsCollapsed] = useState(collapsed);
  const [currentFile, setCurrentFile] = useState<string>('');
  const [fileContent, setFileContent] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');
  const [hasChanges, setHasChanges] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(160);

  const getFileLanguage = (filename: string): string => {
    const ext = filename.split('.').pop()?.toLowerCase();
    const langMap: Record<string, string> = {
      'py': 'python',
      'js': 'javascript',
      'ts': 'typescript',
      'json': 'json',
      'sql': 'sql',
      'md': 'markdown',
      'html': 'html',
      'css': 'css',
      'yaml': 'yaml',
      'yml': 'yaml'
    };
    return langMap[ext || ''] || 'plaintext';
  };

  const currentCode = activeTab === 'ddl' ? ddl : activeTab === 'etl' ? etlCode : fileContent;
  const language = activeTab === 'ddl' ? 'sql' : activeTab === 'etl' ? 'python' : getFileLanguage(fileName);

  const handleFileSelect = async (filePath: string) => {
    try {
      const response = await fetch(`/api/file/${filePath}`);
      const data = await response.json();
      setCurrentFile(filePath);
      setFileContent(data.content);
      setFileName(filePath.split('/').pop() || filePath);
      setActiveTab('file');
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to load file:', error);
    }
  };

  const handleSaveFile = async () => {
    if (!currentFile) return;

    try {
      await fetch(`/api/file/${currentFile}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: fileContent })
      });
      setHasChanges(false);
    } catch (error) {
      console.error('Failed to save file:', error);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(currentCode);
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy code:', err);
    }
  };

  const handleDownload = () => {
    const filename = activeTab === 'ddl' ? 'schema.sql' : 'etl_job.py';
    const blob = new Blob([currentCode], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined) {
      if (activeTab === 'file') {
        setFileContent(value);
        setHasChanges(true);
      } else if (onCodeChange && !readonly) {
        onCodeChange(activeTab as 'ddl' | 'etl', value);
      }
    }
  };

  if (isCollapsed) {
    return (
      <div className="w-full h-full flex items-center justify-center p-6">
        <div className="border border-gray-200 rounded-lg bg-gray-50 max-w-md w-full">
          <button
            onClick={() => setIsCollapsed(false)}
            className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center">
              <Code className="h-5 w-5 text-gray-600 mr-2" />
              <span className="font-medium text-gray-900">View Generated Code</span>
              <span className="ml-2 text-sm text-gray-500">
                (Optional - for advanced users)
              </span>
            </div>
            <Eye className="h-5 w-5 text-gray-400" />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      <div className="bg-white border border-gray-200 shadow-sm flex-1 flex flex-col">
        <div className="flex h-full">
          {/* File Tree Sidebar */}
          <div
            className="flex-shrink-0 border-r border-gray-200 bg-white relative"
            style={{ width: sidebarWidth }}
          >
            <FileTree onFileSelect={handleFileSelect} />
            {/* Resize Handle */}
            <div
              className="absolute top-0 right-0 w-1 h-full cursor-col-resize bg-gray-200 hover:bg-blue-400 transition-colors"
              onMouseDown={(e) => {
                const startX = e.clientX;
                const startWidth = sidebarWidth;

                const handleMouseMove = (e: MouseEvent) => {
                  const newWidth = startWidth + e.clientX - startX;
                  if (newWidth >= 200 && newWidth <= 600) {
                    setSidebarWidth(newWidth);
                  }
                };

                const handleMouseUp = () => {
                  document.removeEventListener('mousemove', handleMouseMove);
                  document.removeEventListener('mouseup', handleMouseUp);
                };

                document.addEventListener('mousemove', handleMouseMove);
                document.addEventListener('mouseup', handleMouseUp);
              }}
            />
          </div>

          {/* Main Editor Area */}
          <div className="flex-1 flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                {/* <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Code className="h-5 w-5 mr-2 text-blue-600" />
                  Code Editor
                </h3> */}
                {activeTab === 'file' && hasChanges && (
                  <span className="text-xs bg-orange-100 text-orange-600 px-2 py-1 rounded">
                    Unsaved changes
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                {activeTab === 'file' && hasChanges && (
                  <button
                    onClick={handleSaveFile}
                    className="flex items-center px-3 py-1 text-sm bg-blue-600 text-white hover:bg-blue-700 rounded transition-colors"
                  >
                    <Save className="h-4 w-4 mr-1" />
                    Save
                  </button>
                )}
                {/* <button
                  onClick={() => setIsCollapsed(true)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <EyeOff className="h-5 w-5" />
                </button> */}
              </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setActiveTab('ddl')}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'ddl'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
              >
                DDL Schema (SQL)
              </button>
              <button
                onClick={() => setActiveTab('etl')}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'etl'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
              >
                ETL Code (Python)
              </button>
              {currentFile && (
                <button
                  onClick={() => setActiveTab('file')}
                  className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${activeTab === 'file'
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                    }`}
                >
                  {fileName} {hasChanges && '*'}
                </button>
              )}
            </div>

            {/* Code Actions */}
            <div className="flex items-center justify-between p-3 bg-gray-50 border-b border-gray-200">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <span>Language: {language.toUpperCase()}</span>
                <span>•</span>
                <span>{currentCode.split('\n').length} lines</span>
                {activeTab === 'file' && currentFile && (
                  <>
                    <span>•</span>
                    <span>{currentFile}</span>
                  </>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleCopy}
                  className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                >
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </button>
                <button
                  onClick={handleDownload}
                  className="flex items-center px-3 py-1 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded transition-colors"
                >
                  <Download className="h-4 w-4 mr-1" />
                  Download
                </button>
              </div>
            </div>

            {/* Editor */}
            <div className="flex-1">
              {currentCode ? (
                <Editor
                  value={currentCode}
                  language={language}
                  onChange={handleEditorChange}
                  options={{
                    readOnly: activeTab !== 'file' && readonly,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    wordWrap: 'on',
                    lineNumbers: 'on',
                    folding: true,
                    theme: 'vs-light'
                  }}
                />
              ) : (
                <div className="flex items-center justify-center h-full bg-gray-50">
                  <div className="text-center">
                    <Code className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">
                      {activeTab === 'file' ? 'Select a file from the tree' :
                        activeTab === 'ddl' ? 'No DDL code generated yet' :
                          'No ETL code generated yet'}
                    </h3>
                    <p className="text-gray-500 text-sm">
                      {activeTab === 'file' ? 'Choose a file from the left sidebar to edit' :
                        activeTab === 'ddl' ? 'Upload JSON files and approve schema to generate DDL' :
                          'Complete the schema step to generate ETL code'}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Footer Info */}
            <div className="p-3 bg-blue-50 border-t border-blue-200">
              <p className="text-sm text-blue-800">
                💡 {activeTab === 'file' ? 'Edit project files directly in the browser' :
                  'This code will be deployed to Google Cloud Run to process your JSON files into BigQuery'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};