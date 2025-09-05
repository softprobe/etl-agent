"""
Enhanced File-Based Evaluation Framework for Agentic ETL Systems
Extends the existing evaluation system to handle file-based intermediate outputs.
"""

import json
import asyncio
import shutil
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import re
from dataclasses import dataclass
from datetime import datetime

# Add app directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from app.services.claude_service import ClaudeETLAgent
from app.utils.workspace import setup_workspace, cleanup_workspace


@dataclass
class FileState:
    """Represents the state of files in workspace at a point in time."""
    timestamp: float
    files: Dict[str, Dict[str, Any]]  # filename -> {size, mtime, content_hash}
    
    
@dataclass
class AgentAction:
    """Represents an action taken by the agent."""
    timestamp: float
    response_text: str
    files_before: FileState
    files_after: FileState
    tools_used: List[str]


class FileBasedETLEvaluator:
    """Comprehensive evaluator for file-based agentic ETL systems.
    
    Supports two evaluation modes:
    - 'incremental': Evaluates progress at current step (default for agentic behavior)
    - 'full_pipeline': Expects complete end-to-end pipeline (for automated systems)
    """
    
    def __init__(self, test_data_dir: Path = None, evaluation_mode: str = "incremental"):
        if test_data_dir is None:
            test_data_dir = Path(__file__).parent / "fixtures" / "sample_json_files"
        self.test_data_dir = test_data_dir
        self.workspace_dir = None
        self.instance_id = None
        self.action_history: List[AgentAction] = []
        self.evaluation_mode = evaluation_mode  # "incremental" or "full_pipeline"
        
    def capture_workspace_state(self, workspace_dir: Path) -> FileState:
        """Capture the current state of all files in workspace."""
        files = {}
        
        for file_path in workspace_dir.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(workspace_dir)
                files[str(rel_path)] = {
                    "size": file_path.stat().st_size,
                    "mtime": file_path.stat().st_mtime,
                    "content_hash": self._hash_file_content(file_path)
                }
                
        return FileState(timestamp=time.time(), files=files)
    
    def _detect_permission_seeking(self, response_text: str) -> bool:
        """Detect if the agent is appropriately seeking permission before proceeding."""
        permission_indicators = [
            "would you like me to",
            "shall I proceed",
            "should I continue",
            "would you like to proceed",
            "next, I can",
            "ready to move on",
            "permission to",
            "before proceeding",
            "should I generate",
            "would you like the"
        ]
        
        response_lower = response_text.lower()
        return any(indicator in response_lower for indicator in permission_indicators)
    
    def _evaluate_schema_file_quality(self, schema_file_path: str) -> float:
        """Evaluate the quality of a schema file."""
        try:
            full_path = self.workspace_dir / schema_file_path
            with open(full_path) as f:
                schema = json.load(f)
            
            quality_score = 0.0
            
            # Check for required top-level sections
            if "entities" in schema: quality_score += 0.5
            if "tables" in schema: quality_score += 1.0
            if "transformations" in schema: quality_score += 0.5
            
            # Check table structure quality
            if "tables" in schema:
                for table_name, table_data in schema["tables"].items():
                    if "fields" in table_data:
                        fields = table_data["fields"]
                        if len(fields) >= 3:  # Reasonable number of fields
                            quality_score += 0.5
                        
                        # Check field definition completeness
                        well_defined_fields = 0
                        for field_name, field_data in fields.items():
                            if isinstance(field_data, dict):
                                if "type" in field_data and "bigquery_type" in field_data:
                                    well_defined_fields += 1
                        
                        if well_defined_fields >= len(fields) * 0.8:  # 80% well-defined
                            quality_score += 1.0
            
            # Check for confidence indicators
            if "confidence" in schema:
                conf = schema["confidence"]
                if isinstance(conf, dict) and "overall" in conf:
                    if conf["overall"] >= 0.8:
                        quality_score += 0.5
            
            # Bonus for comprehensive structure (like schema_output.json format)
            if all(key in schema for key in ["entities", "tables", "transformations", "confidence"]):
                quality_score += 1.0
            
            return min(5.0, quality_score)
            
        except Exception as e:
            print(f"Error evaluating schema file {schema_file_path}: {e}")
            return 0.0
    
    def _hash_file_content(self, file_path: Path) -> str:
        """Create a hash of file content for change detection."""
        try:
            import hashlib
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return "error"
    
    async def evaluate_multi_step_etl_process(self, scenario: Dict, mode: str = None) -> Dict:
        """Evaluate a multi-step ETL process with file tracking.
        
        Args:
            scenario: Test scenario configuration
            mode: Override evaluation mode ('incremental' or 'full_pipeline')
        """
        
        # Use mode parameter or instance default
        eval_mode = mode or self.evaluation_mode
        
        # Setup workspace
        self.instance_id, self.workspace_dir = setup_workspace()
        print(f"📁 Created workspace: {self.instance_id}")
        
        # Copy test data
        data_dir = self.workspace_dir / "data"
        data_dir.mkdir(exist_ok=True)
        source_file = self.test_data_dir / scenario["json_file"]
        dest_file = data_dir / scenario["json_file"]
        shutil.copy2(source_file, dest_file)
        
        # Initialize agent
        agent = ClaudeETLAgent(work_dir=str(self.workspace_dir), debug=True)
        
        try:
            # Initial state
            initial_state = self.capture_workspace_state(self.workspace_dir)
            
            # Execute scenario with mode-appropriate instructions
            if eval_mode == "full_pipeline":
                message = f"I have uploaded {scenario['json_file']} to the data folder. {scenario['query']} Please generate the complete ETL pipeline: schemas, ETL code, and CSV output for validation. Do not ask for permission - complete all steps automatically."
            else:
                message = f"I have uploaded {scenario['json_file']} to the data folder. {scenario['query']} Please start by generating the schema."
            
            print(f"\nExecuting: {scenario['name']} (mode: {eval_mode})")
            print(f"Query: {scenario['query']}")
            
            # Track agent actions
            actions = []
            response_parts = []
            
            async for response_chunk in agent.chat_stream(message):
                if isinstance(response_chunk, dict):
                    if response_chunk.get("type") == "assistant":
                        content = response_chunk.get("content", [])
                        for content_block in content:
                            if content_block.get("type") == "text":
                                text = content_block.get("text", "")
                                response_parts.append(text)
                    elif response_chunk.get("type") == "tool_use":
                        tool_name = response_chunk.get("name", "unknown")
                        print(f"[TOOL] {tool_name}")
                        
                        # Capture state after tool use
                        current_state = self.capture_workspace_state(self.workspace_dir)
                        actions.append(AgentAction(
                            timestamp=time.time(),
                            response_text=" ".join(response_parts[-10:]),  # Last few response parts
                            files_before=initial_state if not actions else actions[-1].files_after,
                            files_after=current_state,
                            tools_used=[tool_name]
                        ))
            
            # Final state
            final_state = self.capture_workspace_state(self.workspace_dir)
            
            # Comprehensive evaluation
            evaluation = await self._evaluate_complete_pipeline(
                scenario=scenario,
                initial_state=initial_state,
                final_state=final_state,
                actions=actions,
                full_response=" ".join(response_parts),
                evaluation_mode=eval_mode
            )
            
            return evaluation
            
        finally:
            await agent.cleanup()
    
    async def _evaluate_complete_pipeline(self, 
                                        scenario: Dict,
                                        initial_state: FileState,
                                        final_state: FileState,
                                        actions: List[AgentAction],
                                        full_response: str,
                                        evaluation_mode: str = "incremental") -> Dict:
        """Comprehensive evaluation of the ETL pipeline (mode-aware)."""
        
        # Detect permission-seeking behavior
        permission_seeking = self._detect_permission_seeking(full_response)
        
        evaluation = {
            "scenario": scenario["name"],
            "evaluation_mode": evaluation_mode,
            "permission_seeking_detected": permission_seeking,
            "process_evaluation": self._evaluate_process_quality(actions, evaluation_mode),
            "file_outputs": self._evaluate_file_outputs(final_state, evaluation_mode),
            "pipeline_functionality": await self._evaluate_pipeline_functionality(scenario, evaluation_mode),
            "cross_file_consistency": self._evaluate_cross_file_consistency(evaluation_mode),
            "production_readiness": self._evaluate_production_readiness(evaluation_mode)
        }
        
        # Mode-aware overall scoring
        if evaluation_mode == "incremental":
            # In incremental mode, weight early-stage outputs more heavily
            scores = [
                evaluation["process_evaluation"]["score"] * 0.15,  # Process quality
                evaluation["file_outputs"]["score"] * 0.40,       # Schema/early outputs (most important)
                evaluation["pipeline_functionality"]["score"] * 0.20,  # What functionality exists
                evaluation["cross_file_consistency"]["score"] * 0.15,   # Consistency of current files
                evaluation["production_readiness"]["score"] * 0.10      # Future readiness indicators
            ]
            # Add bonus for appropriate permission-seeking
            if permission_seeking:
                scores.append(1.0)  # Bonus point for good agentic behavior
                evaluation["permission_seeking_bonus"] = 1.0
        else:
            # In full_pipeline mode, use original equal weighting
            scores = [
                evaluation["process_evaluation"]["score"],
                evaluation["file_outputs"]["score"], 
                evaluation["pipeline_functionality"]["score"],
                evaluation["cross_file_consistency"]["score"],
                evaluation["production_readiness"]["score"]
            ]
        
        evaluation["overall_score"] = sum(scores) / len([s for s in scores if s > 0]) if scores else 0.0
        evaluation["overall_pass"] = evaluation["overall_score"] >= (2.5 if evaluation_mode == "incremental" else 3.5)
        
        return evaluation
    
    def _evaluate_process_quality(self, actions: List[AgentAction], evaluation_mode: str = "incremental") -> Dict:
        """Evaluate the quality of the multi-step process (mode-aware)."""
        
        if not actions:
            return {"score": 0.0, "issues": ["No actions recorded"]}
        
        # Analyze action sequence
        file_creation_sequence = []
        for action in actions:
            new_files = set(action.files_after.files.keys()) - set(action.files_before.files.keys())
            if new_files:
                file_creation_sequence.extend(new_files)
        
        if evaluation_mode == "incremental":
            # In incremental mode, focus on current step completion
            # Check for schema_output.json (primary output in incremental mode)
            schema_output_files = [f for f in file_creation_sequence if "schema_output.json" in f]
            if schema_output_files:
                sequence_score = 5.0  # Perfect score for completing schema step
            else:
                # Look for any schema-related files
                schema_files = [f for f in file_creation_sequence if "schema" in f.lower()]
                sequence_score = 3.0 if schema_files else 1.0
        else:
            # Full pipeline mode: Expected sequence: JSON -> Schema -> ETL -> CSV -> DDL
            expected_patterns = [
                r"schema.*\.json",
                r"etl/.*\.py", 
                r"output/.*\.csv",
                r"ddl/.*\.sql"
            ]
            
            sequence_score = 0.0
            for i, pattern in enumerate(expected_patterns):
                pattern_found = False
                for j, file_path in enumerate(file_creation_sequence):
                    if re.match(pattern, file_path):
                        if j >= i:  # File appeared in reasonable order
                            sequence_score += 1.25  # 5.0 total / 4 patterns
                        pattern_found = True
                        break
                
                if not pattern_found:
                    sequence_score -= 0.5  # Penalty for missing expected files
        
        issues = []
        min_score_threshold = 2.5 if evaluation_mode == "incremental" else 3.5
        if sequence_score < min_score_threshold:
            if evaluation_mode == "incremental":
                issues.append("Schema generation incomplete or missing")
            else:
                issues.append("Suboptimal file creation sequence")
        
        return {
            "score": max(0.0, min(5.0, sequence_score)),
            "file_creation_sequence": file_creation_sequence,
            "actions_count": len(actions),
            "evaluation_mode": evaluation_mode,
            "issues": issues
        }
    
    def _evaluate_file_outputs(self, final_state: FileState, evaluation_mode: str = "incremental") -> Dict:
        """Evaluate the quality and completeness of generated files (mode-aware)."""
        
        files = final_state.files
        
        # Check for expected file types - be flexible with paths
        schema_files = [f for f in files.keys() if ("schema" in f.lower() and f.endswith(".json"))]
        etl_files = [f for f in files.keys() if f.endswith(".py") and "etl" in f.lower()]
        csv_files = [f for f in files.keys() if f.endswith(".csv")]
        ddl_files = [f for f in files.keys() if f.endswith(".sql")]
        
        # Mode-aware scoring
        if evaluation_mode == "incremental":
            # In incremental mode, focus heavily on schema quality
            completeness_score = 0.0
            if schema_files:
                # Check if it's the high-quality schema_output.json format
                schema_quality = self._evaluate_schema_file_quality(schema_files[0]) if schema_files else 0.0
                completeness_score = 5.0 * (schema_quality / 5.0)  # Full score possible just from schema
            # Small bonus for any additional files created
            if etl_files: completeness_score += 0.3
            if csv_files: completeness_score += 0.3
            if ddl_files: completeness_score += 0.4
        else:
            # Full pipeline mode: all components expected
            completeness_score = 0.0
            if schema_files: completeness_score += 1.25
            if etl_files: completeness_score += 1.25  
            if csv_files: completeness_score += 1.25
            if ddl_files: completeness_score += 1.25
        
        # Quality checks
        quality_issues = []
        
        # Check file sizes (too small indicates potential issues)
        for file_path in files:
            if files[file_path]["size"] < 10:  # Very small files
                quality_issues.append(f"Potentially empty file: {file_path}")
        
        # Check naming conventions
        if not all(re.match(r".*_schema\.json", f) for f in schema_files):
            quality_issues.append("Schema files don't follow naming convention")
            
        return {
            "score": completeness_score,
            "schema_files": len(schema_files),
            "etl_files": len(etl_files),
            "csv_files": len(csv_files), 
            "ddl_files": len(ddl_files),
            "quality_issues": quality_issues
        }
    
    async def _evaluate_pipeline_functionality(self, scenario: Dict, evaluation_mode: str = "incremental") -> Dict:
        """Test if the generated pipeline actually works (mode-aware)."""
        
        functionality_score = 0.0
        issues = []
        
        try:
            if evaluation_mode == "incremental":
                # In incremental mode, focus on validating what exists
                schema_files = list(self.workspace_dir.glob("**/schema_output.json")) or \
                              list(self.workspace_dir.glob("**/*schema*.json"))
                
                if schema_files:
                    schema_quality = self._evaluate_schema_file_quality(str(schema_files[0].relative_to(self.workspace_dir)))
                    functionality_score = schema_quality  # Schema quality IS functionality in incremental mode
                    print(f"✓ Schema file validated with quality score: {schema_quality}/5")
                else:
                    issues.append("No schema files found")
                    
            else:
                # Full pipeline mode: Test ETL script execution
                etl_files = list((self.workspace_dir / "etl").glob("*.py"))
                if etl_files:
                    etl_script = etl_files[0]  # Test first script
                    
                    result = subprocess.run([
                        "python", str(etl_script)
                    ], cwd=self.workspace_dir, capture_output=True, timeout=30, text=True)
                    
                    if result.returncode == 0:
                        functionality_score += 2.5
                        print("✓ ETL script executed successfully")
                    else:
                        issues.append(f"ETL execution failed: {result.stderr}")
                        print(f"✗ ETL execution failed: {result.stderr}")
                else:
                    issues.append("No ETL scripts found")
            
            if evaluation_mode == "full_pipeline":
                # Test CSV output validation only in full pipeline mode
                csv_files = list((self.workspace_dir / "output").glob("*.csv"))
                if csv_files:
                    csv_file = csv_files[0]
                    try:
                        df = pd.read_csv(csv_file)
                        
                        # Check if expected columns are present
                        expected_cols = scenario.get("expected_columns", [])
                        present_cols = [col for col in expected_cols if col in df.columns]
                        col_coverage = len(present_cols) / len(expected_cols) if expected_cols else 1.0
                        
                        functionality_score += col_coverage * 2.5
                        
                        if col_coverage < 1.0:
                            missing = set(expected_cols) - set(df.columns)
                            issues.append(f"Missing expected columns: {missing}")
                            
                    except Exception as e:
                        issues.append(f"CSV validation failed: {str(e)}")
                else:
                    if evaluation_mode == "full_pipeline":
                        issues.append("No CSV output files found")
                
        except Exception as e:
            issues.append(f"Pipeline functionality test failed: {str(e)}")
        
        return {
            "score": min(5.0, functionality_score),
            "issues": issues
        }
    
    def _evaluate_cross_file_consistency(self, evaluation_mode: str = "incremental") -> Dict:
        """Check consistency between generated files (mode-aware)."""
        
        consistency_score = 5.0  # Start with perfect score, deduct for issues
        issues = []
        
        try:
            if evaluation_mode == "incremental":
                # In incremental mode, focus on internal schema consistency
                schema_files = list(self.workspace_dir.glob("**/schema*.json"))
                if schema_files:
                    # Internal consistency checks for schema structure
                    with open(schema_files[0]) as f:
                        schema = json.load(f)
                    
                    # Check if entities match table names
                    if "entities" in schema and "tables" in schema:
                        entities = set(schema["entities"])
                        table_keys = set(schema["tables"].keys())
                        # Allow for reasonable transformations (plural, etc.)
                        consistency_ratio = len(entities & table_keys) / len(entities) if entities else 0.0
                        if consistency_ratio < 0.5:
                            consistency_score -= 1.0
                            issues.append("Entity-table name alignment could be improved")
                else:
                    consistency_score = 2.0  # Neutral score if no schema
                    issues.append("No schema files to check consistency")
            else:
                # Full pipeline mode: Check schema-ETL consistency
                schema_files = list(self.workspace_dir.glob("**/*schema*.json"))
                etl_files = list(self.workspace_dir.glob("**/*.py"))
            
            if schema_files and etl_files:
                # Load first schema and ETL script
                with open(schema_files[0]) as f:
                    schema = json.load(f)
                
                with open(etl_files[0]) as f:
                    etl_code = f.read()
                
                # Check if schema fields are referenced in ETL code
                schema_fields = self._extract_schema_fields(schema)
                referenced_fields = re.findall(r'[\'""](\w+)[\'\""]', etl_code)
                
                field_coverage = len(set(schema_fields) & set(referenced_fields)) / len(schema_fields) if schema_fields else 1.0
                if field_coverage < 0.7:
                    consistency_score -= 2.0
                    issues.append(f"Low schema-ETL field consistency: {field_coverage:.1%}")
            
            # Check file naming consistency
            all_files = list(self.workspace_dir.rglob("*"))
            base_names = set()
            for file_path in all_files:
                if file_path.is_file():
                    # Extract base name (e.g., "ecommerce_orders" from "ecommerce_orders_schema.json")
                    name_parts = file_path.stem.split("_")
                    if len(name_parts) >= 2:
                        base_name = "_".join(name_parts[:-1])  # Remove last part (type indicator)
                        base_names.add(base_name)
            
            if len(base_names) > 2:  # Should have consistent naming
                consistency_score -= 1.0
                issues.append("Inconsistent file naming patterns")
                
        except Exception as e:
            consistency_score -= 1.0
            issues.append(f"Consistency check failed: {str(e)}")
        
        return {
            "score": max(0.0, consistency_score),
            "issues": issues
        }
    
    def _evaluate_production_readiness(self, evaluation_mode: str = "incremental") -> Dict:
        """Evaluate if the pipeline is ready for production deployment (mode-aware)."""
        
        readiness_score = 0.0
        issues = []
        
        if evaluation_mode == "incremental":
            # In incremental mode, assess potential for production readiness
            schema_files = list(self.workspace_dir.glob("**/schema*.json"))
            if schema_files:
                with open(schema_files[0]) as f:
                    schema = json.load(f)
                
                # Check if schema has BigQuery-specific elements
                has_bq_types = False
                if "tables" in schema:
                    for table_data in schema["tables"].values():
                        if "fields" in table_data:
                            for field_data in table_data["fields"].values():
                                if isinstance(field_data, dict) and "bigquery_type" in field_data:
                                    has_bq_types = True
                                    break
                
                if has_bq_types:
                    readiness_score += 3.0  # Good foundation for production
                else:
                    readiness_score += 1.0
                    issues.append("Schema lacks BigQuery-specific type information")
                    
                # Check confidence levels
                if "confidence" in schema and isinstance(schema["confidence"], dict):
                    overall_conf = schema["confidence"].get("overall", 0.0)
                    if overall_conf >= 0.9:
                        readiness_score += 2.0
                    elif overall_conf >= 0.7:
                        readiness_score += 1.0
                    else:
                        issues.append(f"Low schema confidence: {overall_conf}")
            else:
                issues.append("No schema files found for production readiness assessment")
        else:
            # Full pipeline mode: Check for BigQuery DDL files
            ddl_files = list(self.workspace_dir.glob("**/*.sql"))
            if ddl_files:
                readiness_score += 2.0
            
                # Basic DDL validation
                with open(ddl_files[0]) as f:
                    ddl_content = f.read().upper()
                    
                if "CREATE TABLE" in ddl_content:
                    readiness_score += 1.0
                else:
                    issues.append("DDL doesn't contain CREATE TABLE statement")
                    
                if "BIGQUERY" in ddl_content or "DATASET" in ddl_content:
                    readiness_score += 1.0
                else:
                    issues.append("DDL doesn't seem BigQuery-specific")
            else:
                if evaluation_mode == "full_pipeline":
                    issues.append("No BigQuery DDL files found")
        
            # Check for error handling in ETL scripts (full pipeline mode only)
            if evaluation_mode == "full_pipeline":
                etl_files = list(self.workspace_dir.glob("**/*.py"))
                if etl_files:
                    with open(etl_files[0]) as f:
                        etl_content = f.read()
                        
                    if "try:" in etl_content and "except:" in etl_content:
                        readiness_score += 1.0
                    else:
                        issues.append("ETL script lacks error handling")
                        readiness_score -= 0.5
        
        return {
            "score": min(5.0, max(0.0, readiness_score)),
            "issues": issues
        }
    
    def _extract_schema_fields(self, schema: Dict) -> List[str]:
        """Extract field names from schema structure."""
        fields = []
        
        # Handle schema-generator format
        if "tables" in schema:
            for table_name, table_data in schema["tables"].items():
                if "fields" in table_data:
                    fields.extend(table_data["fields"].keys())
        
        return fields


# Test scenarios for comprehensive evaluation
TEST_SCENARIOS = [
    {
        "name": "Basic Product Analysis",
        "json_file": "ecommerce_orders.json",
        "query": "find the top selling products by quantity",
        "expected_columns": ["product_id", "product_name", "quantity", "category"],
        "required_flattening": ["items"]
    },
    {
        "name": "Customer Geographic Analysis", 
        "json_file": "ecommerce_orders.json",
        "query": "analyze sales by customer location (state and city)",
        "expected_columns": ["customer_id", "state", "city", "total_amount"],
        "required_flattening": ["shipping_address"]
    }
]


async def main(evaluation_mode: str = "incremental"):
    """Run comprehensive file-based ETL evaluation.
    
    Args:
        evaluation_mode: "incremental" for step-by-step or "full_pipeline" for end-to-end
    """
    print(f"COMPREHENSIVE FILE-BASED ETL EVALUATION ({evaluation_mode.upper()} MODE)")
    print("=" * 60)
    
    evaluator = FileBasedETLEvaluator(evaluation_mode=evaluation_mode)
    
    total_score = 0.0
    total_tests = len(TEST_SCENARIOS)
    
    for i, scenario in enumerate(TEST_SCENARIOS, 1):
        print(f"\n{i}. EVALUATING: {scenario['name']}")
        print("-" * 50)
        
        try:
            evaluation = await evaluator.evaluate_multi_step_etl_process(scenario)
            
            print(f"📊 EVALUATION RESULTS:")
            print(f"- Process Quality: {evaluation['process_evaluation']['score']:.1f}/5")
            print(f"- File Outputs: {evaluation['file_outputs']['score']:.1f}/5")
            print(f"- Pipeline Functionality: {evaluation['pipeline_functionality']['score']:.1f}/5")
            print(f"- Cross-file Consistency: {evaluation['cross_file_consistency']['score']:.1f}/5")
            print(f"- Production Readiness: {evaluation['production_readiness']['score']:.1f}/5")
            print(f"- Overall Score: {evaluation['overall_score']:.1f}/5")
            print(f"- Status: {'✓ PASS' if evaluation['overall_pass'] else '✗ NEEDS IMPROVEMENT'}")
            
            # Report issues
            all_issues = []
            for component, results in evaluation.items():
                if isinstance(results, dict) and "issues" in results:
                    all_issues.extend(results["issues"])
            
            if all_issues:
                print(f"Issues identified: {all_issues}")
            
            total_score += evaluation["overall_score"]
            
        except Exception as e:
            print(f"❌ Evaluation failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Overall results
    if total_tests > 0:
        avg_score = total_score / total_tests
        print(f"\n" + "=" * 60)
        print(f"OVERALL EVALUATION RESULTS")
        print(f"Average Score: {avg_score:.1f}/5")
        print(f"Pass Rate: {(avg_score / 5) * 100:.1f}%")
        print(f"Status: {'✓ SYSTEM READY' if avg_score >= 4.0 else '✗ NEEDS IMPROVEMENT'}")
        print("=" * 60)


if __name__ == "__main__":
    import sys
    
    # Allow command line argument for evaluation mode
    mode = "incremental"  # Default to incremental
    if len(sys.argv) > 1:
        mode = sys.argv[1] if sys.argv[1] in ["incremental", "full_pipeline"] else "incremental"
    
    print(f"Running evaluation in {mode} mode...")
    asyncio.run(main(mode))