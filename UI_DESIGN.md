# UI Design Guidelines

## Visual Schema Preview Implementation Strategy

### Design Philosophy
**Goal:** Validate user understanding of JSON → BigQuery transformation, NOT build a complex schema editor.

**Key Question:** "Do users understand what will happen to their JSON data?"

### Progressive Enhancement Approach

#### MVP (Week 1) - Simple Text Preview
**Implementation Time:** 2-3 days maximum

**Core Component:**
```tsx
const SimpleSchemaPreview = ({ schemas }) => {
  return (
    <div className="simple-schema">
      <h3>Your JSON will create these BigQuery tables:</h3>
      
      {schemas.map(table => (
        <div key={table.name} className="table-summary">
          <h4>📋 {table.name} ({table.estimatedRows} rows)</h4>
          <ul>
            {table.columns.map(col => (
              <li key={col.name}>
                {col.name} ({col.type})
                {col.isForeignKey && <span> → links to {col.referencedTable}</span>}
              </li>
            ))}
          </ul>
        </div>
      ))}
      
      <div className="preview-actions">
        <button className="primary">✅ This looks right, continue</button>
        <button className="secondary">❓ Something looks wrong</button>
      </div>
    </div>
  );
};
```

**Visual Output Example:**
```
Table: users (1,234 rows)  
- user_id (INTEGER)
- email (STRING)
- signup_date (DATE)

Table: orders (5,678 rows)
- user_id (INTEGER) → users.user_id  
- order_total (FLOAT)
```

#### Enhancement Phase (Week 4) - Basic Visualizations
**If users love MVP and request more visual detail:**

```
📋 users     📋 orders
├─ user_id   ├─ user_id ──┐
├─ email     ├─ total     │
└─ date      └─ items     │
              ↑___________┘
```

#### Advanced Phase (Month 2) - Interactive Diagrams
**Only if there's proven demand:**
- Interactive relationship editing
- Drag-and-drop schema modifications
- Database diagram libraries (React Flow)

### What NOT to Build Initially

❌ **Avoid Over-Engineering:**
- Interactive relationship editing
- Schema modification UI  
- Drag-and-drop table design
- Visual query builders
- Complex animations and transitions
- Database diagram libraries like React Flow

✅ **Focus on Core Value:**
- Simple HTML table showing proposed schema
- Basic sample data preview (5 rows max)
- "Approve" or "Modify" buttons
- Natural language iteration: "The dates look wrong" → regenerate

### Data Types and Interfaces

```typescript
interface TableSchema {
  name: string;
  estimatedRows: number;
  columns: Column[];
  relationships: Relationship[];
}

interface Column {
  name: string;
  type: 'INTEGER' | 'STRING' | 'FLOAT' | 'DATE' | 'JSON' | 'BOOLEAN';
  nullable: boolean;
  isPrimaryKey?: boolean;
  isForeignKey?: boolean;
  referencedTable?: string;
}

interface Relationship {
  fromTable: string;
  fromColumn: string;
  toTable: string;
  toColumn: string;
  type: 'one-to-many' | 'many-to-one' | 'one-to-one';
}
```

### Sample Data Preview Integration

```tsx
const SchemaWithDataPreview = ({ schema, sampleData }) => {
  return (
    <div className="schema-data-preview">
      <SimpleSchemaPreview schemas={[schema]} />
      
      <div className="sample-data">
        <h4>Sample transformed data (first 5 rows):</h4>
        <table className="data-preview-table">
          <thead>
            <tr>
              {schema.columns.map(col => (
                <th key={col.name}>{col.name}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sampleData.slice(0, 5).map((row, idx) => (
              <tr key={idx}>
                {schema.columns.map(col => (
                  <td key={col.name}>{row[col.name]}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      <div className="validation-controls">
        <button className="approve-btn">✅ Looks good, generate ETL code</button>
        <button className="modify-btn">🔄 Modify schema structure</button>
      </div>
    </div>
  );
};
```

### User Feedback Validation Questions

After implementing MVP preview, ask users:
- "Is this preview helpful for understanding your data transformation?"
- "What's confusing about this preview?"
- "Would you want more visual detail, or is this sufficient?"
- "What would help you feel more confident about the proposed structure?"

### Implementation Priority

**Phase 1A (Week 1-2):**
- Simple text-based table preview with icons
- Basic relationship indicators (→ arrows)
- Row count estimates
- Sample data preview (first 5 rows)

**Phase 1B (Week 3-4):**
- Only if user feedback demands more visual detail
- Simple relationship visualization
- Interactive approval/modification workflow

**Future Enhancement:**
- Only build complex features if there's validated user demand
- Let user feedback drive complexity, not engineering assumptions

### Design Principles

1. **Simplicity First:** Start with the minimum viable preview
2. **User-Driven Enhancement:** Add complexity only based on user feedback
3. **Fast Implementation:** Visual preview should not delay core ETL functionality
4. **Clear Communication:** Focus on helping users understand what will happen to their data
5. **Progressive Disclosure:** Advanced features should be opt-in, not default