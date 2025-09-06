"""
Workspace management utilities for ETL application.
Creates timestamp-based workspace instances to avoid conflicts.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional


def create_workspace_instance(base_dir: str = "workspace") -> tuple[str, Path]:
    """
    Create a new workspace instance with timestamp-based ID.
    
    Args:
        base_dir: Base directory for workspaces (default: "workspace")
        
    Returns:
        Tuple of (instance_id, workspace_path)
    """
    # Generate timestamp-based instance ID
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
    instance_id = f"etl_{timestamp}"
    
    # Create workspace path
    workspace_path = Path(base_dir) / instance_id
    workspace_path = workspace_path.absolute()
    
    # Clean up existing workspace if it exists
    if workspace_path.exists():
        shutil.rmtree(workspace_path)
    
    # Create the workspace directory
    workspace_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Created workspace instance: {instance_id}")
    print(f"📁 Workspace path: {workspace_path}")
    
    return instance_id, workspace_path


def setup_workspace(base_dir: str = "workspace") -> tuple[str, Path]:
    """
    Setup a new workspace instance and change to that directory.
    
    Args:
        base_dir: Base directory for workspaces (default: "workspace")
        
    Returns:
        Tuple of (instance_id, workspace_path)
    """
    instance_id, workspace_path = create_workspace_instance(base_dir)
    
    # Change to the workspace directory
    # os.chdir(workspace_path)
    # print(f"📁 Changed working directory to: {workspace_path}")
    
    return instance_id, workspace_path


def cleanup_workspace(workspace_path: Path) -> None:
    """
    Clean up a workspace instance.
    
    Args:
        workspace_path: Path to the workspace to clean up
    """
    try:
        if workspace_path.exists():
            shutil.rmtree(workspace_path)
            print(f"🧹 Cleaned up workspace: {workspace_path}")
    except Exception as e:
        print(f"⚠️  Warning: Could not clean up workspace {workspace_path}: {e}")


def get_workspace_info(workspace_path: Path) -> dict:
    """
    Get information about a workspace instance.
    
    Args:
        workspace_path: Path to the workspace
        
    Returns:
        Dictionary with workspace information
    """
    return {
        "path": str(workspace_path),
        "exists": workspace_path.exists(),
        "size": sum(f.stat().st_size for f in workspace_path.rglob('*') if f.is_file()) if workspace_path.exists() else 0,
        "file_count": len(list(workspace_path.rglob('*'))) if workspace_path.exists() else 0
    }
