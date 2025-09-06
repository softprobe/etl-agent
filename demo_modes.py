#!/usr/bin/env python3
"""
Simple demonstration of the two modes without requiring actual Claude API calls.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.claude_service import ClaudeETLAgent

def demo_modes():
    """Demonstrate the difference between modes"""
    
    print("🔍 ClaudeETLAgent Mode Demonstration")
    print("=" * 50)
    
    # Create test workspace
    test_workspace = Path(__file__).parent / "demo_workspace"
    test_workspace.mkdir(exist_ok=True)
    
    print("\n1️⃣ INTERACTIVE MODE")
    print("-" * 30)
    interactive_agent = ClaudeETLAgent.create_interactive_agent(
        work_dir=str(test_workspace),
        debug=False
    )
    
    print(f"Mode: {interactive_agent.mode}")
    print("System prompt includes:")
    print("  ✓ 'Ask for user approval/modifications before proceeding'")
    print("  ✓ 'Present the proposed schema to user with confidence scores'")
    print("  ✓ 'Guide non-technical users through each step'")
    print("  ✓ 'Provide binary choices when possible'")
    
    print("\n2️⃣ AUTOMATED MODE")
    print("-" * 30)
    automated_agent = ClaudeETLAgent.create_automated_agent(
        work_dir=str(test_workspace),
        debug=False
    )
    
    print(f"Mode: {automated_agent.mode}")
    print("System prompt includes:")
    print("  ✓ 'Execute ALL steps without asking for user feedback'")
    print("  ✓ 'NEVER ask Should I proceed? or Is this correct?'")
    print("  ✓ 'ALWAYS complete all steps in sequence'")
    print("  ✓ 'Report progress: ✅ Step 1 Complete: Schema generated'")
    
    print("\n📊 KEY DIFFERENCES")
    print("-" * 30)
    print("Interactive Mode:")
    print("  • Waits for user confirmation at each step")
    print("  • Explains business impact of decisions")
    print("  • Shows confidence scores and reasoning")
    print("  • Provides detailed explanations")
    
    print("\nAutomated Mode:")
    print("  • Executes all steps automatically")
    print("  • Reports progress concisely")
    print("  • Uses high confidence scores (0.8-1.0)")
    print("  • Focuses on results, not explanations")
    
    print("\n✅ Mode demonstration complete!")
    print(f"Both agents created in: {test_workspace}")

if __name__ == "__main__":
    demo_modes()
