import React from 'react';
import { CheckCircle, AlertCircle, Table } from 'lucide-react';
import type { TableSchema } from '../types';

interface SimpleSchemaPreviewProps {
  schemas: TableSchema[];
  sampleData?: Record<string, any[]>;
  onApprove: () => void;
  onModify: () => void;
  loading?: boolean;
}

export const SimpleSchemaPreview: React.FC<SimpleSchemaPreviewProps> = ({
  schemas,
  sampleData,
  onApprove,
  onModify,
  loading = false
}) => {
  if (schemas.length === 0) {
    return (
      <div className="w-full max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <Table className="mx-auto h-16 w-16 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No schema preview available
          </h3>
          <p className="text-gray-500">
            Upload JSON files to see the proposed BigQuery table structure
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          📋 Schema Preview
        </h2>
        <p className="text-gray-600">
          Your JSON will create these BigQuery tables:
        </p>
      </div>

      <div className="space-y-6">
        {schemas.map((table) => (
          <div key={table.name} className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            {/* Table Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                <Table className="h-5 w-5 mr-2 text-blue-600" />
                {table.name}
              </h3>
              <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
                {table.estimatedRows.toLocaleString()} rows
              </span>
            </div>

            {/* Columns */}
            <div className="mb-4">
              <h4 className="text-sm font-medium text-gray-700 mb-3">Columns:</h4>
              <div className="grid gap-2">
                {table.columns.map((col) => (
                  <div
                    key={col.name}
                    className="flex items-center justify-between p-3 bg-gray-50 rounded-md"
                  >
                    <div className="flex items-center">
                      <span className="font-medium text-gray-900">{col.name}</span>
                      <span className="ml-2 text-sm text-gray-500">({col.type})</span>
                      {col.isPrimaryKey && (
                        <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                          Primary Key
                        </span>
                      )}
                      {col.isForeignKey && col.referencedTable && (
                        <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          → {col.referencedTable}
                        </span>
                      )}
                    </div>
                    <div className="text-sm text-gray-500">
                      {col.nullable ? 'Nullable' : 'Required'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Relationships */}
            {table.relationships && table.relationships.length > 0 && (
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Relationships:</h4>
                <div className="space-y-2">
                  {table.relationships.map((rel, index) => (
                    <div key={index} className="text-sm text-gray-600 bg-blue-50 p-2 rounded">
                      <span className="font-medium">{rel.fromTable}.{rel.fromColumn}</span>
                      <span className="mx-2">→</span>
                      <span className="font-medium">{rel.toTable}.{rel.toColumn}</span>
                      <span className="ml-2 text-xs text-gray-500">({rel.type})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sample Data Preview */}
            {sampleData && sampleData[table.name] && (
              <div className="mt-4">
                <h4 className="text-sm font-medium text-gray-700 mb-3">
                  Sample data (first 5 rows):
                </h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="bg-gray-100">
                        {table.columns.slice(0, 6).map((col) => (
                          <th key={col.name} className="px-3 py-2 text-left font-medium text-gray-700">
                            {col.name}
                          </th>
                        ))}
                        {table.columns.length > 6 && (
                          <th className="px-3 py-2 text-left font-medium text-gray-500">
                            +{table.columns.length - 6} more...
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {sampleData[table.name].slice(0, 5).map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-t border-gray-200">
                          {table.columns.slice(0, 6).map((col) => (
                            <td key={col.name} className="px-3 py-2 text-gray-900">
                              {typeof row[col.name] === 'object' 
                                ? JSON.stringify(row[col.name]).slice(0, 50) + '...'
                                : String(row[col.name] || '').slice(0, 50)
                              }
                            </td>
                          ))}
                          {table.columns.length > 6 && (
                            <td className="px-3 py-2 text-gray-500">...</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Action Buttons */}
      <div className="mt-8 flex gap-4 justify-center">
        <button
          onClick={onApprove}
          disabled={loading}
          className="flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <CheckCircle className="h-5 w-5 mr-2" />
          ✅ This looks right, continue
        </button>
        <button
          onClick={onModify}
          disabled={loading}
          className="flex items-center px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <AlertCircle className="h-5 w-5 mr-2" />
          ❓ Something looks wrong
        </button>
      </div>

      {/* Confidence Indicator */}
      <div className="mt-4 text-center">
        <div className="inline-flex items-center px-4 py-2 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
          <span className="text-sm text-blue-800">
            Agent is confident about this schema structure
          </span>
        </div>
      </div>
    </div>
  );
};