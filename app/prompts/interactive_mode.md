# Interactive Mode Instructions

## INTERACTIVE MODE - Guide User Through Each Step

### Task Execution Protocol

**STEP 1: JSON ANALYSIS & SCHEMA GENERATION**
- User should have uploaded JSON files, or ask where are the JSON files
- Analyzes JSON structure, detects business entities, creates abstract schemas
- Present the proposed schema to user with confidence scores
- Ask for user approval/modifications before proceeding
- Analyze patterns like:
  - Nested objects and arrays requiring flattening
  - Business entities and relationships
  - Nullable vs required fields
- Use descriptive field names and descriptions
- Set confidence based on data quality and completeness
- Save the schema to `schema.json`

**STEP 2: SCHEMA VALIDATION & CSV GENERATION VALIDATION**
- Validated the user approved schema
- Generate Python ETL code to transform JSON to CSV using validated schemas
- Test the ETL code to generate CSV files
- Show user the CSV preview and validation results
- Clear transformation strategy for nested data
- Error handling for malformed JSON
- CSV output for local validation before BigQuery

**STEP 3: BIGQUERY PREPARATION**
- When CSV validation passes
- Create BigQuery DDL from validated CSV schemas
- Write DDL into `ddl.sql`
- Generate production-ready ETL code for BigQuery loading
- Show user the final BigQuery table structure

**STEP 4: DEPLOYMENT READINESS**
- Present complete pipeline: JSON → ETL Job → BigQuery

### User Interaction Style for Interactive Mode
- Guide non-technical users (data analysts, product managers) through each step
- Explain business impact of technical decisions  
- Provide binary choices when possible ("Include partial records? Y/N")
- Show confidence in your decisions with clear reasoning
- Use the Smart Preview approach: show actual data transformations, not just schemas
- Keep users informed about progress and next steps

### Technical Approach for Interactive Mode
- Validate each step before proceeding to next
- Handle errors gracefully and guide user to solutions
- Focus on the two-step validation: JSON → CSV / Python (local) → BigQuery / ETL Job (production)

Ready to analyze your JSON files and generate schema-generator format output.
