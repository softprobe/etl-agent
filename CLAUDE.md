# Agentic ETL Engineer

Build an agentic data engineer that does ETL from JSON files to BigQuery with Google's Cloud Run.

## Backgroud

Data analytics requires structure tablular data in a data warehouse such as BigQuery. Applications generally generate JSON data. Extracting raw JSON files into more structured tabular format.

## Goal

- Agentic coding tool similar to Claude Code and Loveable.dev, but specialized in JSON to BigQuery ETL
- Speed up ETL process for enterprise with two-step approach: JSON → CSV (local validation) → BigQuery (production)
- Target users: data analysts, product managers who need business insights but without strong coding coding skills
- Only support Google's BigQuery as data warehouse and Cloud Run as ETL job runner
- MVP, as simple as possible with immediate local validation

## Non-goal

- Generic coding tool compete with Claude Code or Cursor
- Other data warehouses (e.g. Snowflake, Redshift, StarRocks) and ETL runners (Spark, Flink)
- Full feature, extensibility

## Requirements

- A web app, no installation is required
- A sandbox develop environment with local CSV validation before BigQuery deployment
- Agents takes a problem statement and a set of JSON files as intputs
- Agents generate CSV schemas and ETL code for local validation first
- Agents generate DDL to create tables with a schema that can answer users questions
- The DDL can be run against Bigquery to create tables after local validation
- Generates ETL code that maps JSON schema to table schema with CSV output for validation
- Can be deployed to Google Cloud as Cloud Run jobs after successful local testing
- Multi-run converational copilot, user is able to chat with agents, and be able to edit the files
- Able to run a shell to allow users to intervention with the work
- A web IDE or code editor that show code editing by agents and allow user to edit generated code
- Be able to set variables such as Google credentials, bigquery dataset id, project id, etc. 
- As simple as possible while meet the above requirements

## Considerations

The following are some initial investigation and thoughts, but not requirement. Feel free to select other solutions if you feel they are better.

- build on top of Claude Code SDK. Please refer to https://docs.anthropic.com/en/docs/claude-code/sdk/sdk-python
- the end product similar to loveable.dve, an agentic frontend engineer that generates web apps.

## Dev Environment

- Python: uv + venv, Python 3.11
- Nodejs: nvm, nodejs 22