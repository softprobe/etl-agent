from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import json
import asyncio
import os
import shutil
from pathlib import Path
import mimetypes

from .services.claude_service import ClaudeETLAgent
from .models.etl import DDLRequest, UploadResponse
from .utils.workspace import setup_workspace, cleanup_workspace

app = FastAPI(title="Agentic ETL Engineer", version="0.1.0")

# Global variables
WORK_DIR = None
INSTANCE_ID = None
claude_agent = None

@app.on_event("startup")
async def startup_tasks():
    """Initialize app components on startup"""
    global WORK_DIR, INSTANCE_ID, claude_agent
    
    # Setup workspace with timestamp-based instance ID
    INSTANCE_ID, WORK_DIR = setup_workspace()
    
    # Get mode from environment variable (default to automated)
    mode = os.getenv("ETL_MODE", "automated")
    
    # Initialize Claude agent with workspace directory and mode
    claude_agent = ClaudeETLAgent(work_dir=str(WORK_DIR), mode=mode, debug=True)
    print(f"🤖 Initialized Claude ETL Agent with workspace: {WORK_DIR}")
    print(f"🤖 Mode: {mode}")
    print(f"🤖 Debug logging: enabled")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
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
            file_path = file.filename
            
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

@app.websocket("/ws/chat")
async def chat_endpoint(websocket: WebSocket):
    """Real-time chat with Claude for ETL guidance with persistent conversations"""
    await websocket.accept()
    
    try:
        while True:
            # Receive user message
            user_input = await websocket.receive_text()
            
            # Check for special commands
            if user_input.startswith("/"):
                if user_input == "/new":
                    # Start a new conversation
                    await claude_agent.start_new_conversation()
                    await websocket.send_text(json.dumps({
                        "type": "system",
                        "content": "Started new conversation session"
                    }))
                    continue
                elif user_input == "/status":
                    # Send conversation status
                    status = {
                        "type": "system",
                        "content": f"Conversation active: {claude_agent.is_client_active}"
                    }
                    await websocket.send_text(json.dumps(status))
                    continue
            
            # Process with Claude and send responses
            async for response in claude_agent.chat_stream(user_input):
                try:
                    # Ensure response is JSON serializable
                    serialized_response = json.dumps(response, default=str)
                    await websocket.send_text(serialized_response)
                except Exception as serialize_error:
                    print(f"Serialization error: {serialize_error}")
                    # Send error message to client
                    error_response = {
                        "type": "error",
                        "content": f"Error processing response: {str(serialize_error)}"
                    }
                    await websocket.send_text(json.dumps(error_response))
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        # Try to send error message to client, but don't worry if it fails
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": f"Chat error: {str(e)}"
            }))
        except Exception:
            pass  # Client disconnected, ignore
    finally:
        # Clean up when WebSocket closes
        try:
            await claude_agent.cleanup()
        except Exception as cleanup_error:
            print(f"Cleanup error: {cleanup_error}")

@app.get("/api/files")
async def list_files():
    """Directory listing with both files and folders"""
    import os
    items = []
    
    for root, dirs, filenames in os.walk("."):
        # Skip hidden and common ignore patterns
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
        
        # Add directories
        for dirname in dirs:
            dirpath = os.path.join(root, dirname)
            items.append({
                "id": dirpath,
                "name": dirname,
                "path": dirpath,
                "isFolder": True
            })
        
        # Add files
        for filename in filenames:
            if not filename.startswith('.'):
                filepath = os.path.join(root, filename)
                items.append({
                    "id": filepath,
                    "name": filename, 
                    "path": filepath,
                    "isFolder": False
                })
    
    return items

@app.get("/api/file/{file_path:path}")
async def get_file(file_path: str):
    """Read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return {"content": f.read(), "path": file_path}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/api/file/{file_path:path}")
async def save_file(file_path: str, content: dict):
    """Save file content"""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.get("content", ""))
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/new-session")
async def start_new_chat_session():
    """Start a new chat conversation session"""
    try:
        await claude_agent.start_new_conversation()
        return {"status": "success", "message": "New conversation session started"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to start new session: {str(e)}"}
        )

@app.get("/api/chat/status")
async def get_chat_status():
    """Get the current chat session status"""
    try:
        return {
            "status": "success",
            "is_active": claude_agent.is_client_active,
            "message": "Chat session is active" if claude_agent.is_client_active else "No active chat session"
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get chat status: {str(e)}"}
        )

@app.post("/api/chat/cleanup")
async def cleanup_chat_session():
    """Clean up the current chat session"""
    try:
        await claude_agent.cleanup()
        return {"status": "success", "message": "Chat session cleaned up"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to cleanup session: {str(e)}"}
        )

@app.post("/api/workspace/cleanup")
async def cleanup_workspace_endpoint():
    """Clean up the current workspace instance"""
    try:
        global WORK_DIR
        if WORK_DIR:
            cleanup_workspace(WORK_DIR)
        return {"status": "success", "message": f"Workspace {INSTANCE_ID} cleaned up"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to cleanup workspace: {str(e)}"}
        )

@app.get("/api/workspace/info")
async def get_workspace_info():
    """Get information about the current workspace"""
    try:
        from .utils.workspace import get_workspace_info
        info = get_workspace_info(WORK_DIR) if WORK_DIR else {}
        info["instance_id"] = INSTANCE_ID
        info["mode"] = claude_agent.mode if claude_agent else "unknown"
        return {"status": "success", "workspace": info}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to get workspace info: {str(e)}"}
        )

@app.post("/api/mode/switch")
async def switch_mode(mode: str):
    """Switch between interactive and automated modes"""
    try:
        global claude_agent
        
        if mode not in ["interactive", "automated"]:
            return JSONResponse(
                status_code=400,
                content={"error": "Mode must be 'interactive' or 'automated'"}
            )
        
        # Clean up current agent
        if claude_agent:
            await claude_agent.cleanup()
        
        # Create new agent with specified mode
        claude_agent = ClaudeETLAgent(work_dir=str(WORK_DIR), mode=mode)
        
        return {
            "status": "success", 
            "message": f"Switched to {mode} mode",
            "mode": mode
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to switch mode: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)