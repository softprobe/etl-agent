import { useState } from 'react';
import type { UploadedFile } from '../types';
import { apiService } from '../services/api';

export const useFileUpload = () => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const uploadFiles = async (files: File[]) => {
    setLoading(true);
    setError(null);
    
    try {
      // Basic validation
      const jsonFiles = files.filter(file => 
        file.type === 'application/json' || file.name.endsWith('.json')
      );
      
      if (jsonFiles.length === 0) {
        throw new Error('Please select JSON files only');
      }

      const maxSize = 100 * 1024 * 1024; // 100MB
      const oversizedFiles = jsonFiles.filter(file => file.size > maxSize);
      if (oversizedFiles.length > 0) {
        throw new Error(`File too large: ${oversizedFiles[0].name}. Max size is 100MB`);
      }

      const response = await apiService.uploadFiles(jsonFiles);
      setUploadedFiles(prev => [...prev, ...response.files]);
      return response;
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to upload files';
      setError(errorMessage);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const clearFiles = () => {
    setUploadedFiles([]);
    setError(null);
  };

  const removeFile = (filename: string) => {
    setUploadedFiles(prev => prev.filter(file => file.filename !== filename));
  };

  return {
    uploadedFiles,
    loading,
    error,
    uploadFiles,
    clearFiles,
    removeFile
  };
};