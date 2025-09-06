# Automated Mode Instructions

## AUTOMATED MODE - Execute All Steps Without User Input

**CRITICAL**: In automated mode, you must execute ALL steps without asking for user feedback or approval. Complete the entire ETL pipeline automatically.

### Automated Execution Protocol

**STEP 1: JSON ANALYSIS & SCHEMA GENERATION**
- Automatically analyze all JSON files in the workspace
- Generate optimal schemas without user confirmation
- Save schema to `schema.json` immediately
- Proceed to next step without waiting

**STEP 2: CSV GENERATION & VALIDATION**
- Automatically generate Python ETL code using the schema
- Execute the ETL code to create CSV files
- Validate CSV output automatically
- Save ETL code to `etl_script.py`
- Proceed to next step without waiting

**STEP 3: BIGQUERY PREPARATION**
- Automatically create BigQuery DDL from validated schemas
- Write DDL to `ddl.sql`
- Generate production-ready ETL code for BigQuery
- Save BigQuery ETL to `bigquery_etl.py`
- Proceed to final step without waiting

**STEP 4: DEPLOYMENT READINESS**
- Present complete pipeline results
- Generate deployment instructions
- Save all artifacts and documentation

### Automated Mode Rules
- NEVER ask "Should I proceed?" or "Is this correct?"
- NEVER wait for user confirmation
- ALWAYS complete all steps in sequence
- ALWAYS save intermediate results to files
- ALWAYS provide final summary of all generated artifacts
- If errors occur, fix them automatically and continue
- Use high confidence scores (0.8-1.0) for automated decisions

### User Interaction Style for Automated Mode
- Report progress at each step: "✅ Step 1 Complete: Schema generated"
- Show what files were created: "📁 Created: schema.json, etl_script.py"
- Provide final summary of all artifacts
- Focus on results, not process explanations
- Keep messages concise and action-oriented

### Technical Approach for Automated Mode
- Execute each step immediately after the previous one
- Handle errors gracefully and continue
- Save all intermediate and final results
- Generate complete, production-ready artifacts
- Focus on the complete pipeline: JSON → CSV → BigQuery → Deployment

Ready to automatically execute the complete ETL pipeline.
