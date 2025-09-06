#!/usr/bin/env python3
"""
Script to show the prompt files structure and content.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent / "app"))

from services.claude_service import ClaudeETLAgent

def show_prompts():
    """Show the prompt files structure and content"""
    
    print("📁 Prompt Files Structure")
    print("=" * 60)
    
    prompts_dir = Path(__file__).parent / "prompts"
    
    if not prompts_dir.exists():
        print("❌ Prompts directory not found!")
        return
    
    print(f"Prompts directory: {prompts_dir}")
    print()
    
    # List all prompt files
    prompt_files = list(prompts_dir.glob("*.md"))
    print(f"Found {len(prompt_files)} prompt files:")
    for file in prompt_files:
        print(f"  - {file.name}")
    print()
    
    # Show content of each file
    for file in prompt_files:
        print(f"📄 {file.name}")
        print("-" * 40)
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Length: {len(content)} characters")
                print("Preview:")
                print(content[:200] + "..." if len(content) > 200 else content)
        except Exception as e:
            print(f"Error reading file: {e}")
        print()
    
    print("🔧 Testing Prompt Loading")
    print("-" * 40)
    
    # Test prompt loading
    test_workspace = Path(__file__).parent / "test_workspace"
    test_workspace.mkdir(exist_ok=True)
    
    # Test automated mode
    print("Testing automated mode prompt loading...")
    automated_agent = ClaudeETLAgent.create_automated_agent(
        work_dir=str(test_workspace),
        debug=False
    )
    
    # Test interactive mode
    print("Testing interactive mode prompt loading...")
    interactive_agent = ClaudeETLAgent.create_interactive_agent(
        work_dir=str(test_workspace),
        debug=False
    )
    
    print("✅ Prompt loading test completed!")
    print("\nKey benefits:")
    print("  ✓ Prompts are now in separate markdown files")
    print("  ✓ Easy to edit and version control prompts")
    print("  ✓ Clear separation between base prompt and mode-specific instructions")
    print("  ✓ Better maintainability and readability")

if __name__ == "__main__":
    show_prompts()
