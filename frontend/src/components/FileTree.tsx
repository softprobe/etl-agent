import React, { useEffect, useState } from 'react';
import { Tree } from 'react-arborist';
import { File, Folder, FolderOpen } from 'lucide-react';

interface FileNode {
  id: string;
  name: string;
  path: string;
  isFolder: boolean;
  children?: FileNode[];
}

interface FileTreeProps {
  onFileSelect: (filePath: string) => void;
}

export const FileTree: React.FC<FileTreeProps> = ({ onFileSelect }) => {
  const [files, setFiles] = useState<FileNode[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    try {
      console.log('Fetching files from /api/files...');
      const response = await fetch('/api/files');
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const fileList = await response.json();
      console.log('Received files:', fileList?.length || 0, 'items');
      
      // Convert flat file list to tree structure
      const tree = buildTree(fileList);
      console.log('Built tree with', tree?.length || 0, 'root items');
      setFiles(tree);
    } catch (error) {
      console.error('Failed to fetch files:', error);
    } finally {
      setLoading(false);
    }
  };

  const buildTree = (fileList: FileNode[]): FileNode[] => {
    const tree: FileNode[] = [];
    const pathMap = new Map<string, FileNode>();

    // Sort files by path to process directories first
    fileList.sort((a, b) => a.path.localeCompare(b.path));

    fileList.forEach(file => {
      const parts = file.path.split('/').filter(p => p && p !== '.');
      let currentPath = '';
      
      parts.forEach((part, index) => {
        const parentPath = currentPath;
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        
        if (!pathMap.has(currentPath)) {
          const isLastPart = index === parts.length - 1;
          const node: FileNode = {
            id: currentPath,
            name: part,
            path: currentPath,
            isFolder: !isLastPart || file.isFolder,
            children: !isLastPart || file.isFolder ? [] : undefined
          };
          
          pathMap.set(currentPath, node);
          
          if (parentPath && pathMap.has(parentPath)) {
            pathMap.get(parentPath)!.children!.push(node);
          } else if (!parentPath) {
            tree.push(node);
          }
        }
      });
    });

    return tree;
  };

  const Node = ({ node, style, dragHandle }: any) => {
    return (
      <div 
        style={style} 
        ref={dragHandle}
        className={`flex items-center px-2 py-1 cursor-pointer hover:bg-gray-100 text-sm ${
          !node.data.isFolder ? 'text-gray-700' : 'text-gray-900'
        }`}
        onClick={() => {
          if (!node.data.isFolder) {
            onFileSelect(node.data.path);
          }
        }}
      >
        {node.data.isFolder ? (
          node.isOpen ? <FolderOpen className="h-4 w-4 mr-2 text-blue-500" /> 
                     : <Folder className="h-4 w-4 mr-2 text-blue-500" />
        ) : (
          <File className="h-4 w-4 mr-2 text-gray-500" />
        )}
        <span>{node.data.name}</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="p-4 text-sm text-gray-500">
        Loading files...
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-2 border-b border-gray-200 bg-gray-50">
        <h3 className="text-sm font-medium text-gray-900">Files</h3>
      </div>
      <div className="flex-1 overflow-auto">
        <Tree
          data={files}
          openByDefault={false}
          width={300}
          height={500}
          rowHeight={28}
          overscanCount={50}
        >
          {Node}
        </Tree>
      </div>
    </div>
  );
};