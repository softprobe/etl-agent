#!/usr/bin/env python3
"""
Comparison script showing the difference between interactive and automated modes.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.claude_service import ClaudeETLAgent

async def test_mode_comparison():
    """Compare interactive vs automated modes"""
    
    test_workspace = Path(__file__).parent / "test_workspace"
    test_workspace.mkdir(exist_ok=True)
    
    print("🔍 Mode Comparison: Interactive vs Automated")
    print("=" * 60)
    
    # Test Interactive Mode
    print("\n1️⃣ INTERACTIVE MODE")
    print("-" * 30)
    interactive_agent = ClaudeETLAgent.create_interactive_agent(
        work_dir=str(test_workspace),
        debug=False
    )
    
    print("Interactive mode characteristics:")
    print("  - Asks for user approval at each step")
    print("  - Explains business impact of decisions")
    print("  - Provides binary choices (Y/N)")
    print("  - Shows confidence scores and reasoning")
    print("  - Waits for user feedback before proceeding")
    
    await interactive_agent.cleanup()
    
    # Test Automated Mode
    print("\n2️⃣ AUTOMATED MODE")
    print("-" * 30)
    automated_agent = ClaudeETLAgent.create_automated_agent(
        work_dir=str(test_workspace),
        debug=False
    )
    
    print("Automated mode characteristics:")
    print("  - Executes ALL steps without user input")
    print("  - Reports progress: '✅ Step 1 Complete'")
    print("  - Shows created files: '📁 Created: schema.json'")
    print("  - Uses high confidence scores (0.8-1.0)")
    print("  - Generates complete pipeline automatically")
    print("  - Saves all intermediate and final artifacts")
    
    await automated_agent.cleanup()
    
    print("\n📊 USAGE EXAMPLES")
    print("-" * 30)
    print("Interactive Mode:")
    print("  agent = ClaudeETLAgent(mode='interactive')")
    print("  # or")
    print("  agent = ClaudeETLAgent.create_interactive_agent()")
    print()
    print("Automated Mode:")
    print("  agent = ClaudeETLAgent(mode='automated')")
    print("  # or")
    print("  agent = ClaudeETLAgent.create_automated_agent()")
    
    print("\n✅ Comparison complete!")

if __name__ == "__main__":
    asyncio.run(test_mode_comparison())
