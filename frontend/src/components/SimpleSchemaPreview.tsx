import React from 'react';
import { CheckCircle, AlertCircle, Table } from 'lucide-react';
import type { TableSchema } from '../types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

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
          <Table className="mx-auto h-12 w-12 text-gray-300 mb-3" />
          <h3 className="text-sm font-medium text-gray-700 mb-1">
            No schema preview available
          </h3>
          <p className="text-xs text-gray-400">
            Upload JSON files to see the proposed BigQuery table structure
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      <Card>
        <CardHeader className="pb-6">
          <CardTitle className="text-md">📋 Schema Preview</CardTitle>
          <CardDescription className="text-xs">
            Your JSON will create these BigQuery tables:
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-6">
            {schemas.map((table) => (
              <Card key={table.name} className="p-6">
                {/* Table Header */}
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-semibold text-gray-800 flex items-center">
                    <Table className="h-4 w-4 mr-2 text-blue-500" />
                    {table.name}
                  </h3>
                  <Badge variant="secondary" className="text-xs">
                    {table.estimatedRows.toLocaleString()} rows
                  </Badge>
                </div>

            {/* Columns */}
            <div className="mb-4">
              <h4 className="text-xs font-medium text-gray-600 mb-3">Columns:</h4>
              <div className="grid gap-2">
                {table.columns.map((col) => (
                  <div
                    key={col.name}
                    className="flex items-center justify-between p-2 bg-gray-50 rounded-lg border border-gray-100"
                  >
                    <div className="flex items-center">
                      <span className="text-xs font-medium text-gray-700">{col.name}</span>
                      <span className="ml-2 text-xs text-gray-400">({col.type})</span>
                      {col.isPrimaryKey && (
                        <Badge variant="default" className="ml-2 text-xs">
                          Primary Key
                        </Badge>
                      )}
                      {col.isForeignKey && col.referencedTable && (
                        <Badge variant="outline" className="ml-2 text-xs">
                          → {col.referencedTable}
                        </Badge>
                      )}
                    </div>
                    <div className="text-xs text-gray-400">
                      {col.nullable ? 'Nullable' : 'Required'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Relationships */}
            {table.relationships && table.relationships.length > 0 && (
              <div className="mb-4">
                <h4 className="text-xs font-medium text-gray-600 mb-3">Relationships:</h4>
                <div className="space-y-2">
                  {table.relationships.map((rel, index) => (
                    <div key={index} className="text-xs text-gray-600 bg-blue-50 p-2 rounded-lg border border-blue-100">
                      <span className="font-medium">{rel.fromTable}.{rel.fromColumn}</span>
                      <span className="mx-2">→</span>
                      <span className="font-medium">{rel.toTable}.{rel.toColumn}</span>
                      <span className="ml-2 text-xs text-gray-400">({rel.type})</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sample Data Preview */}
            {sampleData && sampleData[table.name] && (
              <div className="mt-4">
                <h4 className="text-xs font-medium text-gray-600 mb-3">
                  Sample data (first 5 rows):
                </h4>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-xs">
                    <thead>
                      <tr className="bg-gray-50">
                        {table.columns.slice(0, 6).map((col) => (
                          <th key={col.name} className="px-2 py-1.5 text-left font-medium text-gray-600">
                            {col.name}
                          </th>
                        ))}
                        {table.columns.length > 6 && (
                          <th className="px-2 py-1.5 text-left font-medium text-gray-400">
                            +{table.columns.length - 6} more...
                          </th>
                        )}
                      </tr>
                    </thead>
                    <tbody>
                      {sampleData[table.name].slice(0, 5).map((row, rowIndex) => (
                        <tr key={rowIndex} className="border-t border-gray-100">
                          {table.columns.slice(0, 6).map((col) => (
                            <td key={col.name} className="px-2 py-1.5 text-gray-700">
                              {typeof row[col.name] === 'object' 
                                ? JSON.stringify(row[col.name]).slice(0, 30) + '...'
                                : String(row[col.name] || '').slice(0, 30)
                              }
                            </td>
                          ))}
                          {table.columns.length > 6 && (
                            <td className="px-2 py-1.5 text-gray-400">...</td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
              </Card>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="mt-8 flex gap-4 justify-center">
            <Button
              onClick={onApprove}
              disabled={loading}
              className="text-xs font-medium"
            >
              <CheckCircle className="h-3.5 w-3.5 mr-1.5" />
              ✅ This looks right, continue
            </Button>
            <Button
              onClick={onModify}
              disabled={loading}
              variant="outline"
              className="text-xs font-medium"
            >
              <AlertCircle className="h-3.5 w-3.5 mr-1.5" />
              ❓ Something looks wrong
            </Button>
          </div>

          {/* Confidence Indicator */}
          <div className="mt-6 text-center">
            <Badge variant="outline" className="bg-blue-50 border-blue-200 text-blue-700">
              <div className="h-1.5 w-1.5 bg-green-500 rounded-full mr-2"></div>
              Agent is confident about this schema structure
            </Badge>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};