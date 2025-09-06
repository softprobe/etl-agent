#!/usr/bin/env python3
"""
Test script for the automated ETL mode.
This demonstrates how to use the ClaudeETLAgent in automated mode
to run the complete ETL pipeline without user interaction.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.claude_service import ClaudeETLAgent

async def test_automated_mode():
    """Test the automated ETL mode with sample data"""
    
    # Create a test workspace directory
    test_workspace = Path(__file__).parent / "test_workspace"
    test_workspace.mkdir(exist_ok=True)
    
    # Copy some sample JSON files to the test workspace
    sample_files = [
        "frontend/public/ecommerce_orders.json",
        "frontend/public/financial_transactions.json", 
        "frontend/public/user_analytics.json"
    ]
    
    for sample_file in sample_files:
        if Path(sample_file).exists():
            import shutil
            shutil.copy2(sample_file, test_workspace)
            print(f"📁 Copied {sample_file} to test workspace")
    
    # Create automated agent
    print("🤖 Creating automated ETL agent...")
    agent = ClaudeETLAgent.create_automated_agent(
        work_dir=str(test_workspace),
        debug=True
    )
    
    try:
        print("🚀 Starting automated ETL pipeline...")
        print("=" * 60)
        
        # Send a message to start the automated process
        user_message = "Please analyze all JSON files in this workspace and run the complete ETL pipeline automatically. Generate schemas, CSV files, BigQuery DDL, and all necessary artifacts."
        
        print(f"📤 Sending message: {user_message}")
        print("=" * 60)
        
        # Stream the response
        async for response in agent.chat_stream(user_message):
            if response.get('type') == 'assistant':
                content = response.get('content', [])
                if isinstance(content, list):
                    for block in content:
                        if block.get('type') == 'text':
                            print(block.get('text', ''), end='')
                elif isinstance(content, str):
                    print(content, end='')
            elif response.get('type') == 'error':
                print(f"❌ Error: {response.get('content', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        print("✅ Automated ETL pipeline completed!")
        
        # Show generated files
        print("\n📁 Generated files:")
        for file_path in test_workspace.glob("*"):
            if file_path.is_file():
                print(f"  - {file_path.name}")
        
        # Print conversation history for debugging
        print("\n🔍 Conversation History:")
        agent.print_conversation_history()
        
    except Exception as e:
        print(f"❌ Error during automated ETL: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await agent.cleanup()
        print("\n🧹 Cleaned up agent resources")

if __name__ == "__main__":
    print("🧪 Testing Automated ETL Mode")
    print("=" * 60)
    asyncio.run(test_automated_mode())
