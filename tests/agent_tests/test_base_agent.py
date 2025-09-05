"""
Base test framework for ETL agent capabilities.
Provides common testing utilities and fixtures for agent testing.
"""

import json
import pytest
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentTestCase:
    """Represents a single agent test case with input and expected output."""
    name: str
    input_file: str
    expected_file: str
    description: str
    domain: str  # ecommerce, analytics, finance, etc.


@dataclass
class SchemaAnalysisResult:
    """Expected structure for schema analysis results."""
    business_entities: List[Dict[str, Any]]
    suggested_schema: Dict[str, Any]
    confidence_scores: Dict[str, float]
    potential_issues: List[Dict[str, Any]]


class AgentTestFramework:
    """Base framework for testing ETL agent capabilities."""
    
    def __init__(self):
        self.fixtures_dir = Path(__file__).parent.parent / "fixtures"
        self.sample_json_dir = self.fixtures_dir / "sample_json_files"
        self.expected_outputs_dir = self.fixtures_dir / "expected_outputs"
    
    def load_sample_json(self, filename: str) -> List[Dict[str, Any]]:
        """Load a sample JSON file for testing."""
        file_path = self.sample_json_dir / filename
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def load_expected_output(self, filename: str) -> Dict[str, Any]:
        """Load expected output for comparison."""
        file_path = self.expected_outputs_dir / filename
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def get_test_cases(self) -> List[AgentTestCase]:
        """Get all available test cases."""
        return [
            AgentTestCase(
                name="ecommerce_orders",
                input_file="ecommerce_orders.json",
                expected_file="ecommerce_orders_expected.json",
                description="E-commerce order data with nested items and addresses",
                domain="ecommerce"
            ),
            AgentTestCase(
                name="user_analytics",
                input_file="user_analytics.json", 
                expected_file="user_analytics_expected.json",
                description="User behavior analytics with events and properties",
                domain="analytics"
            ),
            AgentTestCase(
                name="financial_transactions",
                input_file="financial_transactions.json",
                expected_file="financial_transactions_expected.json", 
                description="Financial transaction data with account and merchant info",
                domain="finance"
            )
        ]
    
    def validate_schema_analysis(self, result: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
        """Validate schema analysis results against expected output."""
        validation_results = {
            "overall_success": True,
            "details": {}
        }
        
        # Check business entities detection
        result_entities = {e["name"]: e for e in result.get("business_entities", [])}
        expected_entities = {e["name"]: e for e in expected.get("business_entities", [])}
        
        entity_matches = 0
        for entity_name, expected_entity in expected_entities.items():
            if entity_name in result_entities:
                result_entity = result_entities[entity_name]
                if result_entity.get("type") == expected_entity.get("type"):
                    entity_matches += 1
        
        entity_accuracy = entity_matches / len(expected_entities) if expected_entities else 0
        validation_results["details"]["entity_detection_accuracy"] = entity_accuracy
        
        # Check schema structure
        result_schema = result.get("suggested_schema", {})
        expected_schema = expected.get("suggested_schema", {})
        
        schema_matches = 0
        total_expected_fields = 0
        
        for table_name, expected_fields in expected_schema.items():
            if table_name in result_schema:
                result_fields = result_schema[table_name]
                for field_name, expected_field in expected_fields.items():
                    total_expected_fields += 1
                    if field_name in result_fields:
                        result_field = result_fields[field_name]
                        if result_field.get("type") == expected_field.get("type"):
                            schema_matches += 1
        
        schema_accuracy = schema_matches / total_expected_fields if total_expected_fields else 0
        validation_results["details"]["schema_accuracy"] = schema_accuracy
        
        # Check confidence scores
        result_confidence = result.get("confidence_scores", {})
        expected_confidence = expected.get("confidence_scores", {})
        
        confidence_check = all(
            result_confidence.get(key, 0) >= (expected_val * 0.8)  # Allow 20% variance
            for key, expected_val in expected_confidence.items()
        )
        validation_results["details"]["confidence_acceptable"] = confidence_check
        
        # Overall success criteria
        validation_results["overall_success"] = (
            entity_accuracy >= 0.8 and 
            schema_accuracy >= 0.7 and 
            confidence_check
        )
        
        return validation_results
    
    def create_test_report(self, test_case: AgentTestCase, validation_results: Dict[str, Any]) -> str:
        """Create a detailed test report."""
        report = f"""
Test Case: {test_case.name}
Domain: {test_case.domain}
Description: {test_case.description}

Results:
- Overall Success: {validation_results['overall_success']}
- Entity Detection Accuracy: {validation_results['details']['entity_detection_accuracy']:.2%}
- Schema Accuracy: {validation_results['details']['schema_accuracy']:.2%}
- Confidence Acceptable: {validation_results['details']['confidence_acceptable']}

Status: {'PASS' if validation_results['overall_success'] else 'FAIL'}
        """
        return report.strip()


# Test fixtures
@pytest.fixture
def agent_test_framework():
    """Pytest fixture for agent test framework."""
    return AgentTestFramework()


@pytest.fixture
def sample_ecommerce_data(agent_test_framework):
    """Pytest fixture for ecommerce test data."""
    return agent_test_framework.load_sample_json("ecommerce_orders.json")


@pytest.fixture
def expected_ecommerce_output(agent_test_framework):
    """Pytest fixture for expected ecommerce output."""
    return agent_test_framework.load_expected_output("ecommerce_orders_expected.json")


if __name__ == "__main__":
    # Quick test to validate framework setup
    framework = AgentTestFramework()
    test_cases = framework.get_test_cases()
    
    print("Agent Test Framework initialized successfully!")
    print(f"Found {len(test_cases)} test cases:")
    
    for case in test_cases:
        print(f"- {case.name}: {case.description}")
        
        # Try to load sample data
        try:
            sample_data = framework.load_sample_json(case.input_file)
            print(f"  ✓ Sample data loaded: {len(sample_data)} records")
        except FileNotFoundError:
            print(f"  ✗ Sample data file not found: {case.input_file}")
        
        # Try to load expected output (if exists)
        try:
            expected = framework.load_expected_output(case.expected_file)
            print(f"  ✓ Expected output loaded")
        except FileNotFoundError:
            print(f"  ⚠ Expected output file not found: {case.expected_file}")