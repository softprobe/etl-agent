# Automated ETL Mode

The ClaudeETLAgent now supports two modes of operation:

## 🎯 Interactive Mode (Default)
- Guides users through each step
- Asks for approval before proceeding
- Explains business impact of decisions
- Provides binary choices (Y/N)
- Shows confidence scores and reasoning

## 🤖 Automated Mode
- Executes ALL steps without user input
- Reports progress: "✅ Step 1 Complete: Schema generated"
- Shows created files: "📁 Created: schema.json, etl_script.py"
- Uses high confidence scores (0.8-1.0)
- Generates complete pipeline automatically
- Saves all intermediate and final artifacts

## Usage

### Python API

```python
from app.services.claude_service import ClaudeETLAgent

# Interactive mode (default)
agent = ClaudeETLAgent(mode="interactive")
# or
agent = ClaudeETLAgent.create_interactive_agent()

# Automated mode
agent = ClaudeETLAgent(mode="automated")
# or
agent = ClaudeETLAgent.create_automated_agent()
```

### Environment Variable

Set the `ETL_MODE` environment variable when starting the server:

```bash
# Interactive mode (default)
python run_server.py

# Automated mode
ETL_MODE=automated python run_server.py
```

### API Endpoint

Switch modes dynamically via API:

```bash
# Switch to automated mode
curl -X POST "http://localhost:8000/api/mode/switch" \
     -H "Content-Type: application/json" \
     -d '"automated"'

# Switch to interactive mode
curl -X POST "http://localhost:8000/api/mode/switch" \
     -H "Content-Type: application/json" \
     -d '"interactive"'
```

## Testing

Run the test scripts to see the difference:

```bash
# Test automated mode
python test_automated_mode.py

# Compare both modes
python test_mode_comparison.py
```

## Automated Mode Behavior

When in automated mode, the agent will:

1. **Step 1**: Automatically analyze all JSON files and generate schemas
2. **Step 2**: Generate and execute ETL code to create CSV files
3. **Step 3**: Create BigQuery DDL and production ETL code
4. **Step 4**: Present complete pipeline results

The agent will NEVER ask for user confirmation and will complete all steps automatically, saving intermediate results to files as it goes.

## Files Generated

In automated mode, the agent creates:

- `schema.json` - Generated schema
- `etl_script.py` - Python ETL transformation code
- `ddl.sql` - BigQuery DDL statements
- `bigquery_etl.py` - Production BigQuery ETL code
- Various CSV files for validation

## When to Use Each Mode

**Use Interactive Mode when:**
- Working with complex or unfamiliar data
- Need to understand business impact of decisions
- Want to review and approve each step
- Working with stakeholders who need explanations

**Use Automated Mode when:**
- Working with well-understood data patterns
- Need to process many similar files
- Want to generate complete pipelines quickly
- Running batch processing jobs
- Testing and validation scenarios
