# Agentic ETL Engineer - System Design

## Overview

This document outlines the system design for the Agentic ETL Engineer - a specialized tool for converting JSON data to BigQuery tables with automated ETL pipeline generation using Google Cloud Run.

## Product Design Evolution & Roadmap

### Design Change Summary (Sept 2024)
Based on product design reviews, competitive research, and user research insights, the approach has evolved significantly to better serve target users while reducing development complexity.

**Key Insights:**
- Templates for complex JSON handling would require MORE development work than code generation
- Target users (data analysts vs product managers) have different needs requiring validation
- Non-technical users need results-first approach, not ETL-first approach
- Visual previews are more valuable than code editing for product managers
- Code generation with visual preview is more scalable than template systems

**Competitive Research Findings:**
- Lovable.dev: Natural language → visual preview → deployment (code editing rarely used)
- Matillion Maia: Visual ETL builder with AI enhancement, 80% users never see underlying code
- Pattern: Start conversational, show visual results, hide code complexity by default

### Product Roadmap

#### Phase 1: Local Data Processing with Visual Validation (4-6 weeks)
**Target Users:** Data analysts and product managers who need to understand their JSON data structure

**Core Features:**
- JSON file upload and analysis
- Visual schema preview ("Your JSON will become these BigQuery tables")
- Sample data transformation preview with pandas
- Interactive data visualization and validation
- Claude Code SDK powered Python ETL code generation (viewable but not emphasized)
- Local execution with immediate visual results

**Technical Stack:**
- Frontend: React + file upload + data visualization components (D3.js/Chart.js)
- Backend: FastAPI + Claude API + pandas + matplotlib/plotly for data preview
- Data Processing: pandas DataFrames (local processing only)
- Output: Python ETL scripts + visual data previews

**Success Metrics:**
- Can users successfully upload JSON and understand the proposed table structure?
- Do visual previews reduce user anxiety about data transformation?
- What percentage of users request code editing vs natural language iteration?

#### Phase 2: BigQuery Integration (2-3 weeks)
**Core Features:**
- Deploy pandas-generated ETL code to process data in BigQuery
- Schema creation in BigQuery datasets
- Basic data upload and transformation execution
- Simple monitoring and status reporting

**Technical Additions:**
- Google Cloud BigQuery integration
- Authentication and project management
- ETL job execution tracking

#### Phase 3: Cloud Run Deployment (3-4 weeks)
**Core Features:**
- Package ETL jobs as containerized Cloud Run services
- Automated deployment pipeline
- Scheduled ETL job execution
- Enhanced monitoring and alerting

**Out of Future Scope (Validating Demand First):**
- Multi-tenancy and user management
- Advanced cost optimization
- Complex visual ETL pipeline builders
- Enterprise features and integrations

## Technology Stack

### Backend
- **Runtime**: Python 3.11+
- **Framework**: FastAPI
- **Key Libraries**:
  - `google-cloud-bigquery` - BigQuery client library
  - `google-cloud-run` - Cloud Run deployment
  - `pydantic` - Data validation and serialization
  - `uvicorn` - ASGI server
  - `anthropic` - Claude API integration
  - `python-multipart` - File upload handling

### Frontend
- **Build Tool**: Vite
- **Framework**: React 18
- **Language**: TypeScript
- **Key Libraries**:
  - `@tanstack/react-query` - Server state management
  - `react-router-dom` - Client-side routing
  - `@monaco-editor/react` - Code editor component
  - `tailwindcss` - Styling framework
  - `lucide-react` - Icons

### Infrastructure
- **Container Platform**: Docker
- **Cloud Provider**: Google Cloud Platform
- **Compute**: Cloud Run (for both web app and ETL jobs)
- **Data Warehouse**: BigQuery
- **Authentication**: Google Cloud IAM

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │    │  Python Backend │    │  Google Cloud   │
│   (Vite/React)  │    │    (FastAPI)    │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • React UI      │◄──►│ • REST API      │◄──►│ • BigQuery      │
│ • Code Editor   │    │ • Claude Agent  │    │ • Cloud Run     │
│ • File Upload   │    │ • JSON Parser   │    │ • IAM           │
│ • Chat Interface│    │ • DDL Generator │    │ • Artifact Reg  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Core Components

### 1. Frontend Application (Vite + React + TypeScript)

#### Key Features (Refined):
- **File Upload Interface**: Drag-and-drop JSON file uploads with immediate analysis
- **Visual Schema Preview**: Interactive table structure preview with relationships  
- **Progressive Disclosure UI**: Beginner/intermediate/advanced modes
- **Decision Guidance**: High-level choices ("3 tables vs 1 table?") with context
- **Optional Code Editor**: Monaco-based editor for advanced users only
- **Results Dashboard**: Quick insights from JSON data (alternative entry point)
- **Confidence Indicators**: Show agent confidence in decisions
- **Configuration Panel**: Simplified Google Cloud authentication

#### Component Structure (Refined):
```
src/
├── components/
│   ├── FileUpload.tsx
│   ├── VisualSchemaPreview.tsx    # NEW: Table structure visualization
│   ├── DecisionGuidance.tsx       # NEW: High-level choice prompts
│   ├── ConfidenceIndicator.tsx    # NEW: Agent confidence display
│   ├── CodeEditor.tsx             # OPTIONAL: For advanced users
│   ├── ResultsDashboard.tsx       # NEW: Quick insights view
│   └── ConfigPanel.tsx
├── hooks/
│   ├── useFileUpload.ts
│   ├── useSchemaPreview.ts        # NEW: Schema visualization logic
│   ├── useClaudeAgent.ts          # RENAMED: More focused than chat
│   └── useBigQuery.ts
├── services/
│   ├── api.ts
│   ├── claude.ts
│   ├── schemaAnalyzer.ts          # NEW: JSON schema analysis
│   └── bigquery.ts
└── types/
    ├── etl.ts
    ├── schema.ts                  # NEW: Schema preview types
    ├── bigquery.ts
    └── claude.ts
```

### 2. Backend API (Python + FastAPI)

#### Core Modules:

##### API Layer (`app/api/`)
- **Endpoints**:
  - `POST /api/upload` - JSON file upload and analysis
  - `POST /api/generate-ddl` - Generate BigQuery DDL
  - `POST /api/generate-etl` - Generate ETL code
  - `POST /api/chat` - Claude conversation endpoint
  - `GET /api/projects` - List user projects
  - `POST /api/deploy` - Deploy ETL job to Cloud Run

##### Core Services (`app/services/`)
- **`claude_service.py`** - Claude API integration and prompt management
- **`json_analyzer.py`** - JSON schema analysis and type inference
- **`ddl_generator.py`** - BigQuery DDL generation from JSON schemas
- **`etl_generator.py`** - ETL code generation (Python/SQL)
- **`bigquery_service.py`** - BigQuery client operations
- **`cloud_run_service.py`** - Cloud Run deployment automation

##### Data Models (`app/models/`)
```python
from pydantic import BaseModel
from typing import Dict, List, Any

class JSONSchema(BaseModel):
    fields: Dict[str, str]
    nested_objects: List[str]
    arrays: List[str]

class DDLRequest(BaseModel):
    json_files: List[str]
    table_name: str
    dataset_id: str
    user_requirements: str

class ETLJob(BaseModel):
    ddl: str
    etl_code: str
    deployment_config: Dict[str, Any]
```

### 3. ETL Job Runner (Python + Cloud Run)

#### Generated ETL Jobs Structure:
```
etl_job/
├── main.py              # ETL job entry point
├── requirements.txt     # Python dependencies
├── Dockerfile          # Container configuration
├── schemas/
│   └── table_schema.json
├── sql/
│   └── transform.sql
└── config/
    └── bigquery_config.json
```

#### ETL Job Template:
```python
# Generated ETL job template (main.py)
import json
from google.cloud import bigquery
from typing import Dict, Any

class ETLProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.client = bigquery.Client(project=config['project_id'])
        self.dataset_id = config['dataset_id']
        self.table_id = config['table_id']
    
    def process_json_files(self, json_data: List[Dict[str, Any]]):
        # Generated transformation logic
        transformed_data = self.transform_data(json_data)
        self.load_to_bigquery(transformed_data)
    
    def transform_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        # AI-generated transformation logic based on user requirements
        pass
    
    def load_to_bigquery(self, data: List[Dict[str, Any]]):
        # BigQuery loading logic
        pass
```

## Refined User Flow

### Target User Segments (Requires Validation)
1. **Data Analysts**: Some technical comfort, understand SQL and normalization
2. **Product Managers**: Want insights from JSON data, not ETL engineering

### Core User Flow (Hybrid Approach)
```
JSON Upload → Agent Analysis → Generated Code → Visual Preview → User Decision → Deploy
```

**Progressive Disclosure Flow:**
1. **Beginner Mode**: "Create 3 normalized tables vs 1 denormalized table?"
2. **Intermediate**: Show table structure preview with row counts and relationships
3. **Advanced**: Allow code editing and custom transformations
4. **Results-First Alternative**: Auto-generate insights dashboard → optional ETL customization

### Visual Preview Example
```
Table: users (1,234 rows)
├── user_id (INTEGER)
├── name (STRING) 
└── email (STRING)

Table: orders (5,678 rows)  
├── user_id (INTEGER) → users.user_id
├── order_id (INTEGER)
└── items (JSON)
```

### Legacy Data Flow (Technical Reference)

#### 1. JSON Analysis Flow
```
JSON Files → JSON Analyzer → Schema Extraction → Claude Analysis → DDL Generation
```

#### 2. ETL Generation Flow
```
User Requirements → Claude Agent → ETL Code Generation → Cloud Run Deployment Config
```

#### 3. Deployment Flow
```
Generated Code → Docker Build → Container Registry → Cloud Run Deployment → BigQuery Table Creation
```

## Security & Configuration

### Authentication
- Google Cloud Service Account for backend services
- IAM roles for BigQuery and Cloud Run access
- Frontend uses secure session management

### Configuration Management
```python
# config/settings.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    google_cloud_project_id: str
    bigquery_dataset_location: str = "US"
    claude_api_key: str
    max_file_size_mb: int = 100
    max_files_per_upload: int = 10
    
    class Config:
        env_file = ".env"
```

## Deployment Architecture

### Development Environment
- Docker Compose setup with Python backend and Vite dev server
- Local BigQuery emulator for testing
- Shared volume for file uploads

### Production Environment
- Frontend: Static build deployed to Cloud Run (or Cloud Storage + CDN)
- Backend: FastAPI app on Cloud Run with autoscaling
- Database: BigQuery for data warehouse
- File Storage: Cloud Storage for uploaded JSON files

## API Design

### REST Endpoints (FastAPI)

```python
# API endpoint examples
@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and analyze JSON files"""
    pass

@app.post("/api/generate-ddl", response_model=DDLResponse)
async def generate_ddl(request: DDLRequest):
    """Generate BigQuery DDL from JSON schema"""
    pass

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_claude(request: ChatRequest):
    """Interactive chat with Claude for ETL guidance"""
    pass

@app.post("/api/deploy", response_model=DeploymentResponse)
async def deploy_etl_job(request: DeploymentRequest):
    """Deploy ETL job to Cloud Run"""
    pass
```

## Error Handling & Monitoring

### Error Handling Strategy
- FastAPI exception handlers for API errors
- BigQuery client error handling with retries
- Claude API rate limiting and fallback responses
- Frontend error boundaries for React components

### Monitoring & Logging
- Cloud Logging for backend services
- Error tracking with structured logging
- Performance monitoring for BigQuery queries
- Cloud Run metrics and alerting

## Scalability Considerations

### Backend Scaling
- Stateless FastAPI design for horizontal scaling
- Cloud Run automatic scaling based on request volume
- Connection pooling for BigQuery client
- Async operations for file processing

### Frontend Performance
- Vite build optimization with code splitting
- React Query for efficient API caching
- Lazy loading for large file previews
- Optimized bundle size with tree shaking

## Critical Next Steps for Validation

### Immediate Actions Required (Week 1-2)

**1. User Research Sprint**
- Interview 5-10 data analysts about current JSON-to-BigQuery workflows
- Interview 5-10 product managers about JSON data analysis needs
- **Key Questions:**
  - How do you currently convert JSON data to insights?
  - Do you want to learn ETL concepts or just get results?
  - What's your tolerance for troubleshooting data pipelines?
  - Would you use a tool that shows generated code vs hides it completely?

**2. Competitive Analysis**
- Evaluate: Fivetran, Stitch, ChatGPT Code Interpreter, BigQuery Transfer Service
- **Focus:** How do they handle the "non-technical user + complex data transformation" challenge?

### MVP Validation Strategy (Week 3-6)

**Build Minimal Viable Version:**
1. JSON upload and analysis
2. Visual schema preview only (no code editing)
3. Single deployment option
4. Basic error handling

**Success Metrics:**
- Can users successfully deploy working ETL without engineering help?
- Do users prefer results-first vs ETL-first approach?
- What percentage complete the full workflow on first try?

### Risk Mitigation

**Critical Failure Modes to Address:**
- ETL jobs failing on production data after working on samples
- Users unable to debug BigQuery cost spikes
- Schema changes breaking existing pipelines
- Non-technical users blocked by technical errors

**Proposed Solutions:**
- Confidence indicators for agent decisions
- Cost estimation before deployment
- Schema evolution handling
- "Escape hatches" for common problems

### Alternative Pivot Option

**Results-First Alternative:**
If user research shows preference for insights over ETL:
```
JSON Upload → Auto-generate insights dashboard → "Want to customize? Here's the underlying ETL"
```


This design provides a foundation for building the Agentic ETL Engineer while maintaining focus on user validation and iterative refinement based on real user feedback.