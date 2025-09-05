# UI Design Guidelines - Four-Phase Implementation

## Design Philosophy (Updated)
**Goal:** Provide immediate value and validation at each phase of the JSON → CSV → Query → Results → BigQuery pipeline.

**Key Questions:**
- Phase 1A: "Do users understand what CSV columns will be created from their JSON?"
- Phase 1B: "Can users validate that the CSV output matches their expectations?"
- Phase 1C: "Can users ask questions and get accurate answers from their CSV data?"
- Phase 1D: "Do users understand their data through tables and charts?"

### Phase-by-Phase UI Components

#### Phase 1A: Schema Preview and Validation (Week 1)
**Implementation Time:** 2-3 days maximum

**Core Component:**
```tsx
const SchemaPreviewPhase1A = ({ schemas, onApprove, onModify }) => {
  return (
    <div className="schema-preview-phase1a">
      <h3>📊 Your JSON will create these CSV files:</h3>
      
      {schemas.map(schema => (
        <div key={schema.name} className="csv-schema-preview">
          <h4>📄 {schema.name}.csv ({schema.estimatedRows} rows)</h4>
          <div className="columns-preview">
            {schema.columns.map(col => (
              <div key={col.name} className="column-item">
                <span className="column-name">{col.name}</span>
                <span className="column-type">({col.type})</span>
                {col.relationship && <span className="relationship">→ links to {col.relationship}</span>}
              </div>
            ))}
          </div>
        </div>
      ))}
      
      <div className="phase1a-actions">
        <button className="approve-btn" onClick={onApprove}>
          ✅ Schema looks good, generate ETL code
        </button>
        <button className="modify-btn" onClick={onModify}>
          ✏️ Modify column names or types
        </button>
      </div>
    </div>
  );
};
```

#### Phase 1B: ETL Code and CSV Validation (Week 2)
```tsx
const ETLCodeAndCSVPhase1B = ({ etlCode, csvFiles, onValidateCSV }) => {
  return (
    <div className="etl-csv-phase1b">
      <div className="etl-code-section">
        <h3>🐍 Generated ETL Code:</h3>
        <MonacoEditor
          language="python"
          value={etlCode}
          options={{ readOnly: true, minimap: { enabled: false } }}
        />
      </div>
      
      <div className="csv-output-section">
        <h3>📊 Generated CSV Files:</h3>
        {csvFiles.map(file => (
          <div key={file.name} className="csv-file-preview">
            <h4>{file.name} ({file.rowCount} rows)</h4>
            <CSVPreviewTable data={file.sampleData} />
            <button onClick={() => downloadCSV(file)}>⬇️ Download {file.name}</button>
          </div>
        ))}
      </div>
      
      <div className="phase1b-actions">
        <button className="validate-btn" onClick={onValidateCSV}>
          ✅ CSV looks good, proceed to queries
        </button>
        <button className="regenerate-btn">
          🔄 Regenerate ETL code
        </button>
      </div>
    </div>
  );
};
```

#### Phase 1C: Query Generation and Results (Week 3)
```tsx
const QueryPhase1C = ({ csvFiles, onExecuteQuery }) => {
  const [question, setQuestion] = useState('');
  const [queryResults, setQueryResults] = useState([]);
  
  return (
    <div className="query-phase1c">
      <div className="question-input">
        <h3>❓ Ask questions about your data:</h3>
        <input
          type="text"
          placeholder="How many users are there? What's the average order value?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button onClick={() => onExecuteQuery(question)}>
          🔍 Generate and Run Query
        </button>
      </div>
      
      <div className="generated-query">
        <h4>🐍 Generated Pandas Code:</h4>
        <MonacoEditor
          language="python"
          value={queryResults.generatedCode}
          options={{ readOnly: true }}
        />
      </div>
      
      <div className="query-results">
        <h4>📊 Query Results:</h4>
        <QueryResultsTable data={queryResults.data} />
      </div>
      
      <div className="phase1c-actions">
        <button onClick={() => proceedToVisualization()}>
          📈 Create visualizations
        </button>
      </div>
    </div>
  );
};
```

#### Phase 1D: Results Visualization (Week 4)
```tsx
const VisualizationPhase1D = ({ queryResults, onExportResults }) => {
  const [chartType, setChartType] = useState('auto');
  
  return (
    <div className="visualization-phase1d">
      <div className="results-table">
        <h3>📋 Query Results:</h3>
        <DataTable data={queryResults.data} />
      </div>
      
      <div className="chart-generation">
        <h3>📈 Data Visualization:</h3>
        <div className="chart-controls">
          <label>Chart Type:</label>
          <select value={chartType} onChange={(e) => setChartType(e.target.value)}>
            <option value="auto">Auto-select</option>
            <option value="bar">Bar Chart</option>
            <option value="line">Line Chart</option>
            <option value="pie">Pie Chart</option>
          </select>
        </div>
        
        <div className="chart-display">
          <ChartComponent 
            data={queryResults.data} 
            type={chartType} 
            autoDetectType={chartType === 'auto'}
          />
        </div>
      </div>
      
      <div className="phase1d-actions">
        <button onClick={() => onExportResults('csv')}>
          📄 Export Results as CSV
        </button>
        <button onClick={() => onExportResults('image')}>
          🖼️ Export Chart as Image
        </button>
        <button onClick={() => proceedToBigQuery()}>
          ☁️ Ready for BigQuery deployment
        </button>
      </div>
    </div>
  );
};
```

### Implementation Priority (Phase-by-Phase)

#### Week 1 Focus: Phase 1A Only
- JSON upload with drag-and-drop
- Simple text-based schema preview
- Basic column type display
- Approve/Modify buttons
- NO complex visualizations or interactions

#### Week 2 Focus: Phase 1B Only  
- ETL code display in Monaco editor (read-only)
- CSV file generation and download
- Simple CSV data preview (first 5 rows)
- Basic validation feedback
- NO advanced code editing features

#### Week 3 Focus: Phase 1C Only
- Natural language question input
- Pandas code generation display
- Query results table
- Basic query validation
- NO complex query builders or advanced analytics

#### Week 4 Focus: Phase 1D Only
- Results table display
- Basic chart generation (bar, line, pie)
- Simple chart type selection
- Export functionality (CSV, images)
- NO interactive chart editing or advanced visualizations

### What NOT to Build Initially

❌ **Avoid Over-Engineering in Each Phase:**
- Phase 1A: Interactive schema editing, complex relationship diagrams
- Phase 1B: Advanced code editing, complex ETL debugging
- Phase 1C: Visual query builders, advanced analytics
- Phase 1D: Interactive chart editing, complex dashboard features

✅ **Focus on Core Value Per Phase:**
- Phase 1A: Clear schema understanding and user confidence
- Phase 1B: Working CSV output with validation
- Phase 1C: Accurate query results from natural language
- Phase 1D: Clear data insights through tables and basic charts

### Data Types and Interfaces (Updated for Phases)

```typescript
// Phase 1A: Schema Preview
interface CSVSchema {
  name: string;
  estimatedRows: number;
  columns: CSVColumn[];
  relationships?: string[]; // Simple text relationships
}

interface CSVColumn {
  name: string;
  type: 'INTEGER' | 'STRING' | 'FLOAT' | 'DATE' | 'BOOLEAN';
  nullable: boolean;
  relationship?: string; // Simple "links to table.column" text
}

// Phase 1B: ETL and CSV
interface ETLResult {
  etlCode: string;
  csvFiles: CSVFile[];
  executionLog: string[];
}

interface CSVFile {
  name: string;
  rowCount: number;
  sampleData: Record<string, any>[];
  downloadUrl: string;
}

// Phase 1C: Query Generation
interface QueryResult {
  question: string;
  generatedCode: string;
  data: Record<string, any>[];
  executionTime: number;
  success: boolean;
  errorMessage?: string;
}

// Phase 1D: Visualization
interface ChartConfig {
  type: 'bar' | 'line' | 'pie' | 'auto';
  data: Record<string, any>[];
  xAxis?: string;
  yAxis?: string;
  title?: string;
}

interface ExportOptions {
  format: 'csv' | 'png' | 'svg';
  filename: string;
  data: Record<string, any>[];
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

### User Feedback Validation Questions (Per Phase)

**Phase 1A Questions:**
- "Does the schema preview help you understand what CSV columns will be created?"
- "Are the column types and relationships clear?"
- "What would help you feel more confident about approving this schema?"

**Phase 1B Questions:**
- "Does the generated CSV data match what you expected?"
- "Is the ETL code display helpful or confusing?"
- "Can you easily validate the CSV output quality?"

**Phase 1C Questions:**
- "Can you easily ask questions about your data in natural language?"
- "Do the pandas query results make sense?"
- "What types of questions do you most want to ask?"

**Phase 1D Questions:**
- "Do the tables and charts help you understand your data?"
- "Are the chart types appropriate for your data?"
- "What insights are you hoping to discover?"

### Success Metrics Per Phase

**Phase 1A Success:**
- 90%+ users understand schema preview without explanation
- Users can successfully modify column names/types
- Schema preview loads within 2 seconds

**Phase 1B Success:**
- Generated CSV files match expected structure 98%+ of the time
- Users can successfully download and inspect CSV files
- ETL code execution completes without errors 95%+ of the time

**Phase 1C Success:**
- 85%+ of basic questions generate working pandas code
- Query execution produces accurate results 90%+ of the time
- Users can iterate on questions successfully

**Phase 1D Success:**
- Charts display correctly for all appropriate query types
- Users can successfully export results in desired formats
- Visualization selection is intuitive and accurate

### Design Principles (Updated for Phased Approach)

1. **Phase-by-Phase Value:** Each phase must provide standalone value and validation
2. **Incremental Complexity:** Only add complexity after validating simpler approach works
3. **User-Driven Enhancement:** Let user feedback from each phase drive next phase requirements
4. **Fast Iteration:** Each phase should be implementable in 1 week maximum
5. **Clear Validation:** Users must understand and approve output before proceeding to next phase
6. **Progressive Disclosure:** Advanced features are separate phases, not default complexity

### Phase Transition Strategy

**Phase 1A → 1B:** Only proceed after users consistently approve schemas
**Phase 1B → 1C:** Only proceed after users validate CSV output quality  
**Phase 1C → 1D:** Only proceed after users get accurate query results
**Phase 1D → 2:** Only proceed after users find value in visualizations

This ensures each phase is validated before building the next phase, reducing wasted development effort and ensuring product-market fit at each step.