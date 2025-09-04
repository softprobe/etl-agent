export interface Column {
  name: string;
  type: 'INTEGER' | 'STRING' | 'FLOAT' | 'DATE' | 'JSON' | 'BOOLEAN';
  nullable: boolean;
  isPrimaryKey?: boolean;
  isForeignKey?: boolean;
  referencedTable?: string;
}

export interface Relationship {
  fromTable: string;
  fromColumn: string;
  toTable: string;
  toColumn: string;
  type: 'one-to-many' | 'many-to-one' | 'one-to-one';
}

export interface TableSchema {
  name: string;
  estimatedRows: number;
  columns: Column[];
  relationships: Relationship[];
}

export interface SchemaPreview {
  tables: TableSchema[];
  sampleData?: Record<string, any[]>;
}