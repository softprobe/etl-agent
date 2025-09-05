"""
JSON to CSV Schema Inference Evaluation Tests
Tests agent's ability to produce accurate schemas for analytical queries from JSON data.
Focuses on schema flattening accuracy and query intent support.
"""

import json
import asyncio
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd
import re

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent))
from app.services.claude_service import ClaudeETLAgent
from app.utils.workspace import setup_workspace, cleanup_workspace


class JSONToCSVSchemaEvaluator:
    """Evaluates agent's JSON to CSV schema inference accuracy for analytical queries."""
    
    def __init__(self):
        # Always use the fixtures directory for test data (use absolute path)
        script_dir = Path(__file__).parent
        self.test_data_dir = script_dir / "fixtures" / "sample_json_files"
        
        # Verify the fixtures directory exists
        if not self.test_data_dir.exists():
            raise FileNotFoundError(f"Test data directory not found: {self.test_data_dir}")
        
        # Verify ecommerce_orders.json exists
        ecommerce_file = self.test_data_dir / "ecommerce_orders.json"
        if not ecommerce_file.exists():
            raise FileNotFoundError(f"Test file not found: {ecommerce_file}")
        
        self.instance_id = None
        self.workspace_dir = None
        
        # Define test scenarios with expected schema requirements
        self.test_scenarios = [
            {
                "name": "Ecommerce Top Products Analysis",
                "json_file": "ecommerce_orders.json",
                "query": "find the top 2 most sold products",
                "expected_columns": ["product_id", "quantity", "product_name", "category"],
                "required_flattening": ["items"],
                "analytical_intent": "aggregation_by_product"
            },
            # {
            #     "name": "Customer Order Analysis", 
            #     "json_file": "ecommerce_orders.json",
            #     "query": "show me customer order history with totals",
            #     "expected_columns": ["customer_id", "customer_email", "order_id", "total_amount", "order_date"],
            #     "required_flattening": [],
            #     "analytical_intent": "customer_analysis"
            # },
            # {
            #     "name": "Product Category Performance",
            #     "json_file": "ecommerce_orders.json", 
            #     "query": "analyze sales by product category",
            #     "expected_columns": ["category", "quantity", "total_price"],
            #     "required_flattening": ["items"],
            #     "analytical_intent": "category_analysis"
            # },
            # {
            #     "name": "Geographic Sales Analysis",
            #     "json_file": "ecommerce_orders.json",
            #     "query": "show sales by state and city",
            #     "expected_columns": ["state", "city", "total_amount", "order_id"],
            #     "required_flattening": ["shipping_address"],
            #     "analytical_intent": "geographic_analysis"
            # }
        ]
        
    async def test_json_to_csv_schema_inference(self):
        """
        Test agent's ability to infer accurate CSV schemas for analytical queries from JSON data.
        Focuses on schema flattening accuracy and query intent support.
        """
        print("TESTING JSON TO CSV SCHEMA INFERENCE")
        print("=" * 50)
        
        # Setup workspace with timestamp-based instance ID
        self.instance_id, self.workspace_dir = setup_workspace()
        print(f"📁 Created test workspace: {self.instance_id}")
        print(f"📁 Using test data directory: {self.test_data_dir}")
        
        # Create data folder in workspace
        data_dir = self.workspace_dir / "data"
        data_dir.mkdir(exist_ok=True)
        print(f"📁 Created data directory: {data_dir}")
        
        # Copy test files to workspace data directory
        test_files = ["ecommerce_orders.json", "user_analytics.json"]
        
        for filename in test_files:
            source = self.test_data_dir / filename
            dest = data_dir / filename
            
            if source.exists():
                shutil.copy2(source, dest)
                print(f"✓ Copied {filename} to data folder")
            else:
                print(f"✗ Missing test file: {source}")
        
        # Verify files are in data folder
        print(f"\n📁 Files in data folder {data_dir}:")
        for file_path in data_dir.iterdir():
            if file_path.is_file():
                print(f"  - {file_path.name}")
        
        # Initialize the updated ClaudeETLAgent with debug mode enabled
        agent = ClaudeETLAgent(work_dir=str(self.workspace_dir), debug=True)
        
        try:
            total_score = 0
            total_tests = len(self.test_scenarios)
            
            for i, scenario in enumerate(self.test_scenarios, 1):
                print(f"\n{i}. TESTING: {scenario['name']}")
                print("-" * 50)
                print(f"Query: {scenario['query']}")
                print(f"Expected columns: {scenario['expected_columns']}")
                print(f"Required flattening: {scenario['required_flattening']}")
                
                # Clear conversation history for each new scenario
                if i > 1:
                    agent.clear_conversation_history()
                
                # Create a focused message for schema inference
                message = f"I have uploaded {scenario['json_file']} to the data folder in the workspace. I want to analyze this data with the query: '{scenario['query']}'. Please ask the schema-generator to create a CSV schema that supports this analysis."
                
                print(f"\nUser Message: {message}")
                print("\nAgent Response:")
                
                # Get agent response
                response_parts = []
                async for response_chunk in agent.chat_stream(message):
                    if isinstance(response_chunk, dict):
                        if response_chunk.get("type") == "assistant":
                            content = response_chunk.get("content", [])
                            for content_block in content:
                                if content_block.get("type") == "text":
                                    text = content_block.get("text", "")
                                    print(text)
                                    response_parts.append(text)
                        elif response_chunk.get("type") == "tool_use":
                            tool_name = response_chunk.get("name", "unknown")
                            print(f"[TOOL] Using {tool_name}")
                    else:
                        print(str(response_chunk))
                        response_parts.append(str(response_chunk))
                
                # Evaluate schema inference quality
                full_response = " ".join(response_parts)

                print(f"\nFull response: {full_response}")
                # check if schema-generator was used
                if "schema-generator" in full_response.lower():
                    print("✅ Schema-generator was used")
                else:
                    print("❌ Schema-generator was not used")
                    continue

                evaluation = self.evaluate_schema_inference(
                    full_response, 
                    scenario["expected_columns"],
                    scenario["required_flattening"],
                    scenario["analytical_intent"]
                )
                
                print(f"\n📊 SCHEMA INFERENCE EVALUATION:")
                print(f"- Schema extraction: {'✓ SUCCESS' if evaluation['schema_extraction']['success'] else '✗ FAILED'}")
                if evaluation['schema_extraction']['success']:
                    schema_details = evaluation.get('schema_details', {})
                    print(f"- Extracted columns: {schema_details.get('extracted_columns', [])}")
                    print(f"- Flattening operations: {schema_details.get('flattening_operations', [])}")
                    print(f"- Array handling: {schema_details.get('array_handling', 'N/A')}")
                    print(f"- Confidence: {schema_details.get('confidence', 0.0):.2f}")
                print(f"- Column accuracy: {evaluation['column_accuracy']:.1f}/5")
                print(f"- Flattening correctness: {evaluation['flattening_score']:.1f}/5")
                print(f"- Query intent support: {evaluation['intent_score']:.1f}/5")
                print(f"- Overall: {'✓ PASS' if evaluation['overall_pass'] else '✗ NEEDS IMPROVEMENT'}")
                
                if not evaluation['overall_pass']:
                    print("Issues:", evaluation['issues'])
                
                total_score += evaluation['overall_score']
                
                # Print conversation history for debugging
                print("\n🔍 CONVERSATION HISTORY FOR THIS SCENARIO:")
                agent.print_conversation_history()
            
            # Overall results
            avg_score = total_score / total_tests
            print(f"\n" + "=" * 50)
            print(f"OVERALL SCHEMA INFERENCE RESULTS")
            print(f"Average Score: {avg_score:.1f}/5")
            print(f"Success Rate: {(total_score / total_tests) * 100:.1f}%")
            print(f"Status: {'✓ PASS' if avg_score >= 3.5 else '✗ NEEDS IMPROVEMENT'}")
            print("=" * 50)
                    
        except Exception as e:
            print(f"❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            
            # Print conversation history even on failure
            print("\n🔍 CONVERSATION HISTORY (ERROR STATE):")
            agent.print_conversation_history()
            
        finally:
            await agent.cleanup()
            print("🧹 Agent cleaned up")
            
            # Clean up workspace
            # if self.workspace_dir:
            #     cleanup_workspace(self.workspace_dir)
            #     print(f"🧹 Workspace {self.instance_id} cleaned up")

    def extract_schema_generator_output(self, response: str) -> dict:
        """Extract schema from schema-generator sub-agent output."""
        try:
            import re
            
            # Look for JSON schema blocks in the response
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            if not json_matches:
                # Try to find JSON without code blocks
                json_pattern = r'\{[^{}]*"entities"[^{}]*\}'
                json_matches = re.findall(json_pattern, response, re.DOTALL)
            
            if json_matches:
                # Parse the first JSON match
                schema_json = json_matches[0]
                schema_data = json.loads(schema_json)
                
                # Validate it's a schema-generator response
                if "entities" in schema_data and "tables" in schema_data:
                    return {
                        "success": True,
                        "schema": schema_data,
                        "raw_json": schema_json,
                        "source": "schema-generator"
                    }
            
            # Check if schema-generator was used but no structured output found
            if "schema-generator" in response.lower() or "Use the schema-generator" in response:
                return {
                    "success": False,
                    "error": "Schema-generator was called but no structured schema found",
                    "schema": None,
                    "source": "schema-generator"
                }
            
            return {
                "success": False,
                "error": "No structured schema found in response",
                "schema": None,
                "source": "unknown"
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"JSON parsing error: {str(e)}",
                "schema": None,
                "source": "schema-generator"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Schema extraction error: {str(e)}",
                "schema": None,
                "source": "schema-generator"
            }

    def evaluate_schema_inference(self, response: str, expected_columns: List[str], 
                                required_flattening: List[str], analytical_intent: str) -> dict:
        """Evaluate schema inference quality for analytical queries using schema-generator output."""
        
        evaluation = {
            "column_accuracy": 0.0,
            "flattening_score": 0.0,
            "intent_score": 0.0,
            "overall_score": 0.0,
            "overall_pass": False,
            "issues": [],
            "schema_extraction": {"success": False}
        }
        
        # Extract schema from schema-generator output
        schema_extraction = self.extract_schema_generator_output(response)
        evaluation["schema_extraction"] = schema_extraction
        
        if not schema_extraction["success"]:
            evaluation["issues"].append(f"Schema extraction failed: {schema_extraction['error']}")
            return evaluation
        
        schema = schema_extraction["schema"]
        
        # Extract columns from schema-generator format
        schema_columns = []
        flattening_operations = []
        
        # Get columns from tables
        tables = schema.get("tables", {})
        for table_name, table_data in tables.items():
            fields = table_data.get("fields", {})
            for field_name, field_data in fields.items():
                schema_columns.append(field_name)
        
        # Check for flattening operations in transformations
        transformations = schema.get("transformations", {})
        csv_transformations = transformations.get("csv", {})
        array_handling = csv_transformations.get("array_handling", "")
        flattening_strategy = csv_transformations.get("flattening_strategy", "")
        
        # Determine flattening operations based on schema-generator output
        if array_handling == "multiple_rows":
            if "items" in str(schema).lower():
                flattening_operations.append("items")
            if "shipping_address" in str(schema).lower():
                flattening_operations.append("shipping_address")
        
        # Check column accuracy using extracted columns
        found_columns = [col for col in expected_columns if col in schema_columns]
        column_accuracy = len(found_columns) / len(expected_columns) if expected_columns else 0
        evaluation["column_accuracy"] = min(column_accuracy * 5, 5.0)
        
        # Check flattening correctness
        flattening_score = 0.0
        if required_flattening:
            for required_field in required_flattening:
                if any(required_field in op for op in flattening_operations):
                    flattening_score += 2.5  # Half points for each required field
            
            # Additional points for proper array handling
            if "items" in required_flattening and "items" in flattening_operations:
                product_columns = ["product_id", "quantity", "category", "product_name"]
                if any(col in schema_columns for col in product_columns):
                    flattening_score += 1.0
            
            if "shipping_address" in required_flattening and "shipping_address" in flattening_operations:
                address_columns = ["state", "city", "zip_code", "country"]
                if any(col in schema_columns for col in address_columns):
                    flattening_score += 1.0
            
            evaluation["flattening_score"] = min(flattening_score, 5.0)
        else:
            evaluation["flattening_score"] = 5.0  # No flattening required
        
        # Check query intent support using schema confidence and reasoning
        confidence = schema.get("confidence", {})
        overall_confidence = confidence.get("overall", 0.0)
        
        # Use confidence as a proxy for intent support
        evaluation["intent_score"] = overall_confidence * 5.0
        
        # Calculate overall score
        evaluation["overall_score"] = (
            evaluation["column_accuracy"] * 0.4 +
            evaluation["flattening_score"] * 0.3 +
            evaluation["intent_score"] * 0.3
        )
        
        # Overall pass criteria (3.5/5 or higher)
        evaluation["overall_pass"] = evaluation["overall_score"] >= 3.5
        
        # Identify specific issues
        if evaluation["column_accuracy"] < 3.0:
            missing_cols = set(expected_columns) - set(found_columns)
            evaluation["issues"].append(f"Missing expected columns: {missing_cols}")
        
        if evaluation["flattening_score"] < 3.0:
            evaluation["issues"].append("Insufficient nested structure flattening")
        
        if evaluation["intent_score"] < 3.0:
            evaluation["issues"].append(f"Low confidence for {analytical_intent} analysis")
        
        # Add schema details for debugging
        evaluation["schema_details"] = {
            "extracted_columns": schema_columns,
            "flattening_operations": flattening_operations,
            "confidence": overall_confidence,
            "array_handling": array_handling,
            "flattening_strategy": flattening_strategy
        }
        
        return evaluation

    def validate_csv_schema_structure(self, csv_file_path: str, expected_columns: List[str]) -> dict:
        """Validate that a generated CSV file has the expected structure."""
        try:
            # Read CSV and check structure
            df = pd.read_csv(csv_file_path)
            actual_columns = list(df.columns)
            
            # Check column presence
            missing_columns = set(expected_columns) - set(actual_columns)
            extra_columns = set(actual_columns) - set(expected_columns)
            
            # Calculate accuracy metrics
            column_match_rate = len(set(expected_columns) & set(actual_columns)) / len(expected_columns)
            
            return {
                "has_expected_columns": len(missing_columns) == 0,
                "column_match_rate": column_match_rate,
                "missing_columns": list(missing_columns),
                "extra_columns": list(extra_columns),
                "total_columns": len(actual_columns),
                "expected_columns": len(expected_columns)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "has_expected_columns": False,
                "column_match_rate": 0.0
            }

    def extract_schema_from_response(self, response: str) -> dict:
        """Extract schema information from agent response."""
        schema_info = {
            "columns_mentioned": [],
            "flattening_mentioned": [],
            "csv_mentioned": False,
            "schema_mentioned": False
        }
        
        response_lower = response.lower()
        
        # Look for column mentions
        column_patterns = [
            r'(\w+_id)', r'(\w+_name)', r'(\w+_date)', r'(\w+_amount)',
            r'(\w+_email)', r'(\w+_address)', r'(\w+_price)', r'(\w+_quantity)',
            r'(\w+_category)', r'(\w+_status)', r'(\w+_method)'
        ]
        
        for pattern in column_patterns:
            matches = re.findall(pattern, response_lower)
            schema_info["columns_mentioned"].extend(matches)
        
        # Look for flattening mentions
        flattening_terms = ["items", "shipping_address", "payment", "flatten", "unnest", "explode"]
        for term in flattening_terms:
            if term in response_lower:
                schema_info["flattening_mentioned"].append(term)
        
        # Check for CSV and schema mentions
        schema_info["csv_mentioned"] = "csv" in response_lower
        schema_info["schema_mentioned"] = "schema" in response_lower
        
        return schema_info


async def main():
    """Run the JSON to CSV schema inference evaluation test."""
    print("JSON TO CSV SCHEMA INFERENCE EVALUATION")
    print("Testing agent's ability to infer accurate schemas for analytical queries")
    print("=" * 70)
    
    evaluator = JSONToCSVSchemaEvaluator()
    await evaluator.test_json_to_csv_schema_inference()
    
    print(f"\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("This test evaluates the agent's ability to:")
    print("- Infer accurate CSV schemas from JSON data")
    print("- Flatten nested structures appropriately for queries")
    print("- Support specific analytical intents (top products, customer analysis, etc.)")
    print("- Generate schemas that enable the intended analysis")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())