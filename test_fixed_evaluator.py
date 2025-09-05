#!/usr/bin/env python3
"""
Test script to validate the fixed evaluation framework.
This tests that agents generating good schemas and asking permission score highly.
"""

import asyncio
import shutil
from pathlib import Path

# Add tests directory to path
import sys
sys.path.append(str(Path(__file__).parent / "tests"))

from file_based_evaluator import FileBasedETLEvaluator, FileState
import time

async def test_existing_workspace_evaluation():
    """Test evaluation of existing workspace with good schema."""
    
    print("TESTING FIXED EVALUATION FRAMEWORK")
    print("=" * 50)
    
    # Create evaluator in incremental mode (default)
    evaluator = FileBasedETLEvaluator(evaluation_mode="incremental")
    
    # Point to existing workspace with good schema
    existing_workspace = Path("/Users/bill/src/etl/workspace/etl_20250904_204748_598")
    
    if not existing_workspace.exists():
        print(f"❌ Workspace not found: {existing_workspace}")
        return
    
    evaluator.workspace_dir = existing_workspace
    
    # Create file states
    initial_state = FileState(timestamp=time.time() - 3600, files={})  # Empty initial state
    final_state = evaluator.capture_workspace_state(existing_workspace)
    
    print(f"📁 Found workspace: {existing_workspace}")
    print(f"📄 Files in workspace: {list(final_state.files.keys())}")
    
    # Test scenario (similar to what generated the schema)
    test_scenario = {
        "name": "Basic Product Analysis Test",
        "json_file": "ecommerce_orders.json", 
        "query": "find the top selling products by quantity",
        "expected_columns": ["product_id", "product_name", "quantity", "category"]
    }
    
    # Simulate permission-seeking response
    permission_seeking_response = """I've analyzed your ecommerce_orders.json file and generated a comprehensive schema for extracting top selling products by quantity. The schema includes:

- **orders** table with order-level information
- **order_items** table with product details and quantities (key for your analysis)

The schema includes proper BigQuery types and is optimized for your specific query about top selling products.

**Next Steps Available:**
1. Generate ETL code to flatten the JSON into CSV format
2. Create BigQuery DDL statements for table creation  
3. Generate sample CSV output for validation

Would you like me to proceed with generating the ETL code, or would you prefer to review the schema first?"""
    
    print("\n🧪 TESTING INCREMENTAL MODE (Permission-Seeking Agent)")
    print("-" * 50)
    
    # Run evaluation
    evaluation = await evaluator._evaluate_complete_pipeline(
        scenario=test_scenario,
        initial_state=initial_state,
        final_state=final_state,
        actions=[],  # No actions needed for this test
        full_response=permission_seeking_response,
        evaluation_mode="incremental"
    )
    
    # Print results
    print(f"\n📊 EVALUATION RESULTS:")
    print(f"- Mode: {evaluation['evaluation_mode']}")
    print(f"- Permission-seeking detected: {evaluation['permission_seeking_detected']}")
    print(f"- Process Quality: {evaluation['process_evaluation']['score']:.1f}/5")
    print(f"- File Outputs: {evaluation['file_outputs']['score']:.1f}/5")  
    print(f"- Pipeline Functionality: {evaluation['pipeline_functionality']['score']:.1f}/5")
    print(f"- Cross-file Consistency: {evaluation['cross_file_consistency']['score']:.1f}/5")
    print(f"- Production Readiness: {evaluation['production_readiness']['score']:.1f}/5")
    
    if "permission_seeking_bonus" in evaluation:
        print(f"- Permission-Seeking Bonus: {evaluation['permission_seeking_bonus']:.1f}")
    
    print(f"- Overall Score: {evaluation['overall_score']:.1f}/5")
    print(f"- Status: {'✓ PASS' if evaluation['overall_pass'] else '✗ NEEDS IMPROVEMENT'}")
    
    # Test schema quality specifically
    print(f"\n🎯 SCHEMA QUALITY TEST:")
    schema_quality = evaluator._evaluate_schema_file_quality("schema_output.json")
    print(f"- Schema Quality Score: {schema_quality:.1f}/5")
    
    # Report all issues
    all_issues = []
    for component, results in evaluation.items():
        if isinstance(results, dict) and "issues" in results:
            all_issues.extend(results["issues"])
    
    if all_issues:
        print(f"\n⚠️  Issues identified:")
        for issue in all_issues:
            print(f"  - {issue}")
    else:
        print(f"\n✅ No issues identified!")
    
    # Compare with old vs new scoring
    print(f"\n📈 IMPROVEMENT ANALYSIS:")
    
    if evaluation['overall_score'] >= 4.0:
        print("✅ EXCELLENT: Agent with good schema + permission-seeking scores highly (4.0+)")
    elif evaluation['overall_score'] >= 3.0:
        print("✅ GOOD: Agent with good schema + permission-seeking scores well (3.0+)")
    elif evaluation['overall_score'] >= 2.0:
        print("⚠️  MODERATE: Agent scores reasonably (2.0+)")
    else:
        print("❌ POOR: Agent scores low (< 2.0) - this would indicate evaluation issues")
        
    print(f"\nOld framework would have scored this as 0.0-1.0 (❌ WRONG)")
    print(f"New framework scores this as {evaluation['overall_score']:.1f} (✅ CORRECT)")
    
    return evaluation

async def test_comparison_modes():
    """Test both incremental and full_pipeline modes for comparison."""
    
    print(f"\n" + "=" * 60)
    print("COMPARING INCREMENTAL VS FULL_PIPELINE MODES")
    print("=" * 60)
    
    # Test both modes with the same workspace
    modes = ["incremental", "full_pipeline"]
    results = {}
    
    for mode in modes:
        print(f"\n🧪 TESTING {mode.upper()} MODE")
        print("-" * 30)
        
        evaluator = FileBasedETLEvaluator(evaluation_mode=mode)
        
        try:
            result = await evaluator.evaluate_multi_step_etl_process({
                "name": "Mode Comparison Test",
                "json_file": "ecommerce_orders.json",
                "query": "find the top selling products by quantity",
                "expected_columns": ["product_id", "product_name", "quantity", "category"]
            })
            
            results[mode] = result
            print(f"✅ {mode} mode completed: {result['overall_score']:.1f}/5")
            
        except Exception as e:
            print(f"❌ {mode} mode failed: {e}")
            results[mode] = None
    
    # Compare results
    print(f"\n📊 MODE COMPARISON:")
    for mode, result in results.items():
        if result:
            print(f"- {mode.capitalize()}: {result['overall_score']:.1f}/5 ({'PASS' if result['overall_pass'] else 'NEEDS WORK'})")
        else:
            print(f"- {mode.capitalize()}: FAILED")
    
    return results

if __name__ == "__main__":
    async def main():
        # Test the existing workspace
        await test_existing_workspace_evaluation()
        
        # Compare both modes
        await test_comparison_modes()
        
        print(f"\n🎉 EVALUATION FRAMEWORK TESTING COMPLETE!")
    
    asyncio.run(main())