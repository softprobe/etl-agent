import React, { useCallback, useState } from 'react';
import { Upload, File, X, AlertCircle, Plus } from 'lucide-react';
import type { UploadedFile } from '../types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FileUploadProps {
  onFilesUpload: (files: File[]) => void;
  uploadedFiles: UploadedFile[];
  loading: boolean;
  error?: string | null;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onFilesUpload,
  uploadedFiles,
  loading,
  error
}) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const files = Array.from(e.dataTransfer.files).filter(
        file => file.type === 'application/json' || file.name.endsWith('.json')
      );
      setSelectedFiles(prev => [...prev, ...files]);
    }
  }, []);

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      const files = Array.from(e.target.files);
      setSelectedFiles(prev => [...prev, ...files]);
    }
    // Reset the input value so the same file can be selected again
    e.target.value = '';
  }, []);

  const handleUpload = () => {
    if (selectedFiles.length > 0) {
      onFilesUpload(selectedFiles);
      setSelectedFiles([]);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card>
        <CardHeader className="pb-6">
          <CardTitle className="text-md">Upload JSON Files</CardTitle>
          <CardDescription className="text-xs">
            Upload your JSON data files to generate BigQuery schema and ETL code
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">

          {/* Drag and Drop Area - Only show when no files selected */}
          {selectedFiles.length === 0 && (
            <div
              className={`relative border border-dashed rounded-xl p-8 text-center transition-colors ${
                dragActive
                  ? 'border-blue-300 bg-blue-50/50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                type="file"
                multiple
                accept=".json"
                onChange={handleChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={loading}
              />
              
              <Upload className="mx-auto h-10 w-10 text-gray-300 mb-3" />
              <h3 className="text-sm font-medium text-gray-700 mb-1">
                Drop JSON files here, or click to browse
              </h3>
              <p className="text-xs text-gray-400">
                Supports .json files up to 100MB each
              </p>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <Alert variant="destructive" className="mt-4">
              <AlertCircle className="h-3.5 w-3.5" />
              <AlertDescription className="text-xs">
                {error}
              </AlertDescription>
            </Alert>
          )}

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-4">
                Selected Files ({selectedFiles.length})
              </h3>
              <div className="space-y-3">
                {selectedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2.5 bg-gray-50 rounded-xl border border-gray-100"
                  >
                    <div className="flex items-center">
                      <File className="h-4 w-4 text-gray-400 mr-2" />
                      <div>
                        <p className="text-xs font-medium text-gray-700">
                          {file.name}
                        </p>
                        <p className="text-xs text-gray-400">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(index)}
                      className="text-gray-400 hover:text-red-500 h-8 w-8 p-0"
                      disabled={loading}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
              
              {/* Add More Files Button - Show below file list */}
              <div className="flex justify-center mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={loading}
                  className="flex items-center gap-2 text-xs"
                >
                  <Plus className="h-4 w-4" />
                  Add More Files
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".json"
                  onChange={handleChange}
                  className="hidden"
                  disabled={loading}
                />
              </div>
              
              <Button
                onClick={handleUpload}
                disabled={loading || selectedFiles.length === 0}
                className="mt-6 w-full text-xs font-medium"
              >
                {loading ? 'Uploading...' : `Upload ${selectedFiles.length} Files`}
              </Button>
            </div>
          )}

          {/* Uploaded Files */}
          {uploadedFiles.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-gray-700 mb-4">
                Uploaded Files ({uploadedFiles.length})
              </h3>
              <div className="space-y-3">
                {uploadedFiles.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center p-2.5 bg-green-50 border border-green-200 rounded-xl"
                  >
                    <File className="h-4 w-4 text-green-500 mr-2" />
                    <div>
                      <p className="text-xs font-medium text-gray-700">
                        {file.filename}
                      </p>
                      <p className="text-xs text-gray-400">
                        {(file.size / 1024 / 1024).toFixed(2)} MB • Uploaded
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};