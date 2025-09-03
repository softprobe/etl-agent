from fastapi import FastAPI, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import json
import asyncio
import os
import shutil
from pathlib import Path

from .services.claude_service import ClaudeETLAgent
from .models.etl import DDLRequest, UploadResponse

app = FastAPI(title="Agentic ETL Engineer", version="0.1.0")

# Global variables
WORK_DIR = None
claude_agent = None

@app.on_event("startup")
async def startup_tasks():
    """Initialize app components on startup"""
    global WORK_DIR, claude_agent
    
    # Create clean working directory
    WORK_DIR = Path("uploads")
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(exist_ok=True)
    print(f"📁 Created clean working directory: {WORK_DIR.absolute()}")
    
    # Initialize Claude agent with uploads directory
    claude_agent = ClaudeETLAgent(work_dir=str(WORK_DIR.absolute()))
    print(f"🤖 Initialized Claude ETL Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/upload", response_model=UploadResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload and store JSON files"""
    try:
        uploaded_files = []
        
        # Just save files for later analysis
        for file in files:
            if not file.filename.endswith('.json'):
                continue
                
            content = await file.read()
            file_path = WORK_DIR / file.filename
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "path": str(file_path),
                "size": len(content)
            })
        
        return UploadResponse(
            files=uploaded_files,
            schema_preview=[],  # No analysis yet, wait for user query
            status="success"
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"error": f"Failed to upload files: {str(e)}"}
        )

@app.post("/api/generate-ddl")
async def generate_ddl(request: DDLRequest):
    """Generate BigQuery DDL from JSON schema"""
    try:
        ddl = await claude_agent.generate_ddl(
            json_schemas=request.json_files,
            table_name=request.table_name,
            dataset_id=request.dataset_id,
            user_requirements=request.user_requirements
        )
        return {"ddl": ddl}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate DDL: {str(e)}"}
        )

@app.post("/api/generate-etl")
async def generate_etl(request: DDLRequest):
    """Generate ETL code"""
    try:
        etl_code = await claude_agent.generate_etl_code(
            json_schemas=request.json_files,
            table_name=request.table_name,
            dataset_id=request.dataset_id,
            user_requirements=request.user_requirements
        )
        return {"etl_code": etl_code}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to generate ETL: {str(e)}"}
        )

@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    """Real-time chat with Claude for ETL guidance"""
    await websocket.accept()
    
    try:
        while True:
            # Receive user message
            user_input = await websocket.receive_text()
            
            # Process with Claude
            async for response in claude_agent.chat_stream(user_input):
                await websocket.send_text(json.dumps(response))
                
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": f"Chat error: {str(e)}"
        }))
    finally:
        await websocket.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)