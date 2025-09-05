#!/usr/bin/env python3
"""
Test script to verify that test files are properly copied to the workspace.
"""

import asyncio
import sys
from pathlib import Path

# Add tests directory to path
sys.path.append(str(Path(__file__).parent / "tests"))

from eval import JSONToCSVSchemaEvaluator
from app.utils.workspace import setup_workspace, cleanup_workspace

async def test_file_copying():
    """Test that files are properly copied to the workspace."""
    print("🧪 TESTING FILE COPYING TO WORKSPACE")
    print("=" * 50)
    
    evaluator = JSONToCSVSchemaEvaluator()
    
    # Setup workspace
    instance_id, workspace_dir = setup_workspace()
    print(f"📁 Created test workspace: {instance_id}")
    print(f"📁 Workspace directory: {workspace_dir}")
    print(f"📁 Test data directory: {evaluator.test_data_dir}")
    print(f"📁 Test data directory exists: {evaluator.test_data_dir.exists()}")
    
    # Create data folder in workspace
    data_dir = workspace_dir / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"📁 Created data directory: {data_dir}")
    
    # Copy test files to data folder
    test_files = ["ecommerce_orders.json", "user_analytics.json"]
    
    for filename in test_files:
        source = evaluator.test_data_dir / filename
        dest = data_dir / filename
        
        if source.exists():
            import shutil
            shutil.copy2(source, dest)
            print(f"✓ Copied {filename} from {source} to {dest}")
        else:
            print(f"✗ Source file not found: {source}")
    
    # Verify files are in data folder
    print(f"\n📁 Files in data folder {data_dir}:")
    for file_path in data_dir.iterdir():
        if file_path.is_file():
            print(f"  - {file_path.name} ({file_path.stat().st_size} bytes)")
    
    # Check if ecommerce_orders.json exists and has content
    ecommerce_file = data_dir / "ecommerce_orders.json"
    if ecommerce_file.exists():
        with open(ecommerce_file, 'r') as f:
            content = f.read()
            print(f"\n📄 ecommerce_orders.json content preview:")
            print(f"  - File size: {len(content)} characters")
            print(f"  - First 200 chars: {content[:200]}...")
    else:
        print(f"\n❌ ecommerce_orders.json not found in data folder")
    
    # Clean up
    cleanup_workspace(workspace_dir)
    print(f"\n🧹 Cleaned up workspace {instance_id}")

if __name__ == "__main__":
    asyncio.run(test_file_copying())
