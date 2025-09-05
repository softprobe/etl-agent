#!/usr/bin/env python3
"""
Comprehensive ETL Evaluation Demonstration
Shows how to use the file-based evaluation framework with real-time monitoring
for evaluating agentic ETL systems that generate schemas and write to files.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add tests directory to path
sys.path.append(str(Path(__file__).parent))

from file_based_evaluator import FileBasedETLEvaluator, TEST_SCENARIOS
from etl_monitoring import RealTimeETLMonitor, ETLPerformanceProfiler


class ComprehensiveETLEvaluationFramework:
    """Complete evaluation framework combining file-based evaluation with real-time monitoring."""
    
    def __init__(self):
        self.evaluator = None
        self.monitor = None
        self.profiler = None
        
    async def run_comprehensive_evaluation(self, scenario_name: str = None):
        """Run a comprehensive evaluation with real-time monitoring."""
        
        print("🚀 COMPREHENSIVE AGENTIC ETL EVALUATION FRAMEWORK")
        print("=" * 70)
        print("This framework evaluates:")
        print("- Agent conversation quality and file output consistency")  
        print("- Multi-step ETL process execution and file dependencies")
        print("- Real-time validation of generated schemas, scripts, and outputs")
        print("- Production readiness and cross-file consistency")
        print("- Performance metrics and monitoring dashboards")
        print("=" * 70)
        
        # Select scenarios to test
        scenarios = TEST_SCENARIOS
        if scenario_name:
            scenarios = [s for s in TEST_SCENARIOS if scenario_name.lower() in s["name"].lower()]
            
        if not scenarios:
            print(f"❌ No scenarios found matching '{scenario_name}'")
            return
            
        total_score = 0.0
        evaluation_results = []
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n📋 SCENARIO {i}/{len(scenarios)}: {scenario['name']}")
            print("-" * 50)
            
            try:
                # Initialize evaluator for this scenario
                self.evaluator = FileBasedETLEvaluator()
                
                # Setup monitoring before starting the agent
                print("🔍 Setting up real-time monitoring...")
                
                # Setup workspace (the evaluator will create it)
                # We need to get the workspace after the evaluator creates it
                evaluation_result = await self._evaluate_with_monitoring(scenario)
                
                evaluation_results.append(evaluation_result)
                total_score += evaluation_result["overall_score"]
                
                # Print detailed results
                self._print_detailed_results(evaluation_result)
                
                # Optional: pause between scenarios for demonstration
                if len(scenarios) > 1 and i < len(scenarios):
                    print("\n⏸️  Press Enter to continue to next scenario...")
                    # input()  # Uncomment for interactive mode
                    time.sleep(2)  # Auto-continue after 2 seconds
                    
            except Exception as e:
                print(f"❌ Evaluation failed for scenario '{scenario['name']}': {str(e)}")
                import traceback
                traceback.print_exc()
                
        # Overall summary
        self._print_overall_summary(evaluation_results, total_score)
        
    async def _evaluate_with_monitoring(self, scenario):
        """Run evaluation with real-time monitoring."""
        
        # Start the file-based evaluation (this creates the workspace)
        print("📁 Creating workspace and initializing agent...")
        
        # We need to modify the evaluator to expose workspace creation
        # For demo purposes, let's run the evaluation and then add monitoring
        evaluation_result = await self.evaluator.evaluate_multi_step_etl_process(scenario)
        
        # Add monitoring data if available
        if hasattr(self.evaluator, 'workspace_dir') and self.evaluator.workspace_dir:
            # Create a monitor for post-evaluation analysis
            self.monitor = RealTimeETLMonitor(self.evaluator.workspace_dir)
            
            # Generate a monitoring report based on final state
            monitoring_report = self._generate_post_evaluation_monitoring_report()
            evaluation_result["monitoring"] = monitoring_report
            
        return evaluation_result
        
    def _generate_post_evaluation_monitoring_report(self):
        """Generate a monitoring report from the final workspace state."""
        
        if not self.monitor:
            return {"error": "No monitor available"}
            
        workspace_dir = self.monitor.workspace_dir
        
        # Scan workspace and create pseudo file events
        file_types = {
            "schema": list((workspace_dir / "schema").glob("*.json")) if (workspace_dir / "schema").exists() else [],
            "etl": list((workspace_dir / "etl").glob("*.py")) if (workspace_dir / "etl").exists() else [],
            "csv": list((workspace_dir / "output").glob("*.csv")) if (workspace_dir / "output").exists() else [],
            "ddl": list((workspace_dir / "ddl").glob("*.sql")) if (workspace_dir / "ddl").exists() else []
        }
        
        # Run post-hoc validations
        validation_results = []
        
        for file_type, files in file_types.items():
            for file_path in files:
                # Run validation
                self.monitor._auto_validate_file(str(file_path))
                
        # Return monitoring summary
        return {
            "files_found": {k: len(v) for k, v in file_types.items()},
            "validation_results": len(self.monitor.validation_results),
            "avg_validation_score": sum(r.score for r in self.monitor.validation_results) / len(self.monitor.validation_results) if self.monitor.validation_results else 0.0,
            "validation_pass_rate": sum(1 for r in self.monitor.validation_results if r.passed) / len(self.monitor.validation_results) if self.monitor.validation_results else 0.0
        }
        
    def _print_detailed_results(self, evaluation_result):
        """Print detailed evaluation results."""
        
        print(f"\n📊 DETAILED EVALUATION RESULTS")
        print("-" * 40)
        
        # Core evaluation metrics
        print(f"🔄 Process Quality: {evaluation_result['process_evaluation']['score']:.1f}/5")
        if evaluation_result['process_evaluation'].get('issues'):
            for issue in evaluation_result['process_evaluation']['issues']:
                print(f"   ⚠️ {issue}")
                
        print(f"📄 File Outputs: {evaluation_result['file_outputs']['score']:.1f}/5")
        print(f"   - Schema files: {evaluation_result['file_outputs']['schema_files']}")
        print(f"   - ETL files: {evaluation_result['file_outputs']['etl_files']}")
        print(f"   - CSV files: {evaluation_result['file_outputs']['csv_files']}")
        print(f"   - DDL files: {evaluation_result['file_outputs']['ddl_files']}")
        
        print(f"⚙️ Pipeline Functionality: {evaluation_result['pipeline_functionality']['score']:.1f}/5")
        if evaluation_result['pipeline_functionality'].get('issues'):
            for issue in evaluation_result['pipeline_functionality']['issues']:
                print(f"   ⚠️ {issue}")
                
        print(f"🔗 Cross-file Consistency: {evaluation_result['cross_file_consistency']['score']:.1f}/5")
        if evaluation_result['cross_file_consistency'].get('issues'):
            for issue in evaluation_result['cross_file_consistency']['issues']:
                print(f"   ⚠️ {issue}")
                
        print(f"🚀 Production Readiness: {evaluation_result['production_readiness']['score']:.1f}/5")
        if evaluation_result['production_readiness'].get('issues'):
            for issue in evaluation_result['production_readiness']['issues']:
                print(f"   ⚠️ {issue}")
                
        # Monitoring results if available
        if "monitoring" in evaluation_result:
            monitoring = evaluation_result["monitoring"]
            print(f"\n🔍 MONITORING RESULTS")
            print(f"   - Files generated: {monitoring.get('files_found', {})}")
            print(f"   - Validation checks: {monitoring.get('validation_results', 0)}")
            print(f"   - Avg validation score: {monitoring.get('avg_validation_score', 0):.1f}/5")
            print(f"   - Validation pass rate: {monitoring.get('validation_pass_rate', 0):.1%}")
            
        # Overall assessment
        overall_score = evaluation_result["overall_score"]
        status = "✅ EXCELLENT" if overall_score >= 4.5 else "✓ GOOD" if overall_score >= 3.5 else "⚠️ NEEDS IMPROVEMENT" if overall_score >= 2.5 else "❌ POOR"
        
        print(f"\n🎯 OVERALL SCORE: {overall_score:.1f}/5 - {status}")
        
        # Recommendations
        if overall_score < 4.0:
            print(f"\n💡 RECOMMENDATIONS:")
            if evaluation_result['process_evaluation']['score'] < 3.5:
                print("   - Improve agent's multi-step process execution")
            if evaluation_result['file_outputs']['score'] < 3.5:
                print("   - Ensure all required file types are generated")
            if evaluation_result['pipeline_functionality']['score'] < 3.5:
                print("   - Fix ETL script execution and CSV generation issues")
            if evaluation_result['cross_file_consistency']['score'] < 3.5:
                print("   - Improve consistency between schemas and generated code")
            if evaluation_result['production_readiness']['score'] < 3.5:
                print("   - Add error handling and BigQuery-specific DDL")
                
    def _print_overall_summary(self, evaluation_results, total_score):
        """Print overall evaluation summary."""
        
        if not evaluation_results:
            print("\n❌ No evaluation results to summarize")
            return
            
        avg_score = total_score / len(evaluation_results)
        
        print(f"\n" + "=" * 70)
        print(f"🎯 COMPREHENSIVE EVALUATION SUMMARY")
        print("=" * 70)
        print(f"Scenarios tested: {len(evaluation_results)}")
        print(f"Average overall score: {avg_score:.1f}/5")
        print(f"Success rate: {sum(1 for r in evaluation_results if r['overall_pass']) / len(evaluation_results):.1%}")
        
        # Component breakdown
        component_scores = {
            "Process Quality": sum(r['process_evaluation']['score'] for r in evaluation_results) / len(evaluation_results),
            "File Outputs": sum(r['file_outputs']['score'] for r in evaluation_results) / len(evaluation_results),
            "Pipeline Functionality": sum(r['pipeline_functionality']['score'] for r in evaluation_results) / len(evaluation_results),
            "Cross-file Consistency": sum(r['cross_file_consistency']['score'] for r in evaluation_results) / len(evaluation_results),
            "Production Readiness": sum(r['production_readiness']['score'] for r in evaluation_results) / len(evaluation_results)
        }
        
        print(f"\nComponent Average Scores:")
        for component, score in component_scores.items():
            print(f"  {component}: {score:.1f}/5")
            
        # Overall recommendation
        if avg_score >= 4.0:
            print(f"\n✅ SYSTEM STATUS: PRODUCTION READY")
            print("The agentic ETL system demonstrates strong performance across all evaluation dimensions.")
        elif avg_score >= 3.0:
            print(f"\n⚠️ SYSTEM STATUS: NEEDS IMPROVEMENT")  
            print("The system shows promise but requires refinement in several areas.")
        else:
            print(f"\n❌ SYSTEM STATUS: NOT READY")
            print("Significant improvements needed before production deployment.")
            
        print("=" * 70)


async def main():
    """Run the comprehensive evaluation demonstration."""
    
    framework = ComprehensiveETLEvaluationFramework()
    
    # Run with all scenarios or specific scenario
    scenario_filter = None  # Change to "product" to test only product analysis
    
    await framework.run_comprehensive_evaluation(scenario_filter)
    
    print(f"\n🎉 EVALUATION COMPLETE")
    print("This framework provides:")
    print("- Multi-dimensional evaluation of agentic ETL systems")
    print("- File-based validation of intermediate outputs") 
    print("- Real-time monitoring and performance metrics")
    print("- Production readiness assessment")
    print("- Actionable recommendations for improvement")


if __name__ == "__main__":
    asyncio.run(main())