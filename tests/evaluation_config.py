"""
Configuration and Settings for Agentic ETL Evaluation Framework
Centralized configuration for evaluation criteria, thresholds, and test scenarios.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
from pathlib import Path


@dataclass
class EvaluationThresholds:
    """Evaluation scoring thresholds and criteria."""
    
    # Overall scoring thresholds
    excellent_threshold: float = 4.5
    good_threshold: float = 3.5
    acceptable_threshold: float = 2.5
    
    # Component-specific thresholds
    process_quality_min: float = 3.0
    file_outputs_min: float = 3.0
    functionality_min: float = 3.5  # Higher bar for functionality
    consistency_min: float = 3.0
    production_readiness_min: float = 3.5  # Higher bar for production
    
    # File validation thresholds
    schema_validation_min: float = 3.0
    etl_validation_min: float = 3.5
    csv_validation_min: float = 3.0
    ddl_validation_min: float = 3.0
    
    # Performance thresholds
    max_schema_generation_time: float = 30.0  # seconds
    max_etl_execution_time: float = 60.0  # seconds
    max_csv_size: int = 100_000_000  # bytes (100MB)
    min_csv_rows: int = 1


@dataclass 
class TestScenarioConfig:
    """Configuration for test scenarios."""
    
    name: str
    json_file: str
    query: str
    expected_columns: List[str]
    required_flattening: List[str]
    analytical_intent: str
    complexity_level: str = "medium"  # easy, medium, hard
    expected_file_types: List[str] = None  # ["schema", "etl", "csv", "ddl"]
    timeout_seconds: int = 120
    
    def __post_init__(self):
        if self.expected_file_types is None:
            self.expected_file_types = ["schema", "etl", "csv", "ddl"]


class EvaluationConfig:
    """Main configuration class for the evaluation framework."""
    
    def __init__(self):
        self.thresholds = EvaluationThresholds()
        self.test_scenarios = self._load_test_scenarios()
        self.file_validation_rules = self._load_validation_rules()
        self.monitoring_config = self._load_monitoring_config()
        
    def _load_test_scenarios(self) -> List[TestScenarioConfig]:
        """Load predefined test scenarios."""
        
        return [
            TestScenarioConfig(
                name="Basic Product Analysis",
                json_file="ecommerce_orders.json",
                query="find the top selling products by quantity",
                expected_columns=["product_id", "product_name", "quantity", "category"],
                required_flattening=["items"],
                analytical_intent="aggregation_by_product",
                complexity_level="easy"
            ),
            
            TestScenarioConfig(
                name="Customer Geographic Analysis",
                json_file="ecommerce_orders.json", 
                query="analyze sales by customer location (state and city)",
                expected_columns=["customer_id", "state", "city", "total_amount"],
                required_flattening=["shipping_address"],
                analytical_intent="geographic_analysis",
                complexity_level="medium"
            ),
            
            TestScenarioConfig(
                name="Multi-level Nested Analysis",
                json_file="ecommerce_orders.json",
                query="analyze payment methods and shipping costs by product category",
                expected_columns=["category", "payment_method", "shipping_cost", "quantity"],
                required_flattening=["items", "payment", "shipping"],
                analytical_intent="complex_multi_dimension_analysis",
                complexity_level="hard",
                timeout_seconds=180
            ),
            
            TestScenarioConfig(
                name="Time Series Analysis",
                json_file="ecommerce_orders.json",
                query="show daily sales trends with order counts and revenue",
                expected_columns=["order_date", "daily_orders", "daily_revenue", "avg_order_value"],
                required_flattening=[],
                analytical_intent="time_series_analysis",
                complexity_level="medium"
            ),
            
            TestScenarioConfig(
                name="Customer Behavioral Analysis", 
                json_file="ecommerce_orders.json",
                query="analyze customer purchasing patterns including repeat customers and order frequency",
                expected_columns=["customer_id", "customer_email", "order_count", "total_spent", "avg_order_value"],
                required_flattening=[],
                analytical_intent="customer_behavior_analysis",
                complexity_level="hard"
            )
        ]
        
    def _load_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Load file validation rules and criteria."""
        
        return {
            "schema": {
                "required_sections": ["entities", "tables", "transformations"],
                "required_fields_per_table": ["type", "nullable", "description"],
                "min_fields_per_table": 2,
                "max_confidence_threshold": 0.7,
                "required_metadata": ["confidence", "transformations"]
            },
            
            "etl": {
                "required_imports": ["pandas", "json"],
                "required_functions": ["main", "transform_data"],
                "required_operations": ["file_reading", "data_transformation", "csv_output"],
                "code_quality_checks": ["error_handling", "logging", "documentation"],
                "max_lines": 500,
                "min_lines": 20
            },
            
            "csv": {
                "min_rows": 1,
                "max_null_percentage": 0.5,
                "required_column_types": ["string", "numeric"],
                "encoding": "utf-8",
                "delimiter": ",",
                "header_required": True
            },
            
            "ddl": {
                "required_statements": ["CREATE TABLE"],
                "required_data_types": ["STRING", "INTEGER", "FLOAT64"],
                "bigquery_specific": True,
                "min_columns": 2,
                "required_constraints": ["NOT NULL"]
            }
        }
        
    def _load_monitoring_config(self) -> Dict[str, Any]:
        """Load monitoring and observability configuration."""
        
        return {
            "real_time_monitoring": True,
            "file_watcher_enabled": True,
            "performance_profiling": True,
            "validation_on_file_change": True,
            
            "alert_thresholds": {
                "validation_failure_rate": 0.3,
                "performance_degradation": 2.0,  # 2x slower than baseline
                "file_size_anomaly": 10.0,  # 10x larger than expected
                "execution_timeout": 300  # 5 minutes
            },
            
            "metrics_to_track": [
                "schema_generation_time",
                "etl_execution_time", 
                "csv_generation_time",
                "validation_scores",
                "file_sizes",
                "error_rates"
            ],
            
            "dashboard_refresh_interval": 5,  # seconds
            "log_level": "INFO",
            "max_log_files": 10
        }
        
    def get_scenario_by_complexity(self, complexity: str) -> List[TestScenarioConfig]:
        """Get scenarios filtered by complexity level."""
        return [s for s in self.test_scenarios if s.complexity_level == complexity]
        
    def get_scenario_by_name(self, name: str) -> TestScenarioConfig:
        """Get a specific scenario by name."""
        for scenario in self.test_scenarios:
            if name.lower() in scenario.name.lower():
                return scenario
        return None
        
    def validate_workspace_requirements(self, workspace_dir: Path) -> Dict[str, bool]:
        """Validate that workspace has required structure."""
        
        requirements = {
            "data_dir_exists": (workspace_dir / "data").exists(),
            "schema_dir_created": (workspace_dir / "schema").exists(),
            "etl_dir_created": (workspace_dir / "etl").exists(),  
            "output_dir_created": (workspace_dir / "output").exists(),
            "ddl_dir_created": (workspace_dir / "ddl").exists(),
            "has_input_files": len(list((workspace_dir / "data").glob("*.json"))) > 0 if (workspace_dir / "data").exists() else False
        }
        
        return requirements
        
    def calculate_weighted_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate weighted overall score based on component importance."""
        
        weights = {
            "process_evaluation": 0.15,
            "file_outputs": 0.20,
            "pipeline_functionality": 0.30,  # Most important
            "cross_file_consistency": 0.20,
            "production_readiness": 0.15
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for component, score in component_scores.items():
            if component in weights:
                weighted_score += score * weights[component]
                total_weight += weights[component]
                
        return weighted_score / total_weight if total_weight > 0 else 0.0
        
    def generate_evaluation_report_template(self) -> Dict[str, Any]:
        """Generate a template for evaluation reports."""
        
        return {
            "evaluation_metadata": {
                "timestamp": None,
                "evaluator_version": "1.0.0",
                "config_version": "1.0.0",
                "test_scenarios_count": len(self.test_scenarios)
            },
            
            "test_execution": {
                "scenarios_run": [],
                "total_duration": None,
                "agent_version": None,
                "workspace_path": None
            },
            
            "results_summary": {
                "overall_score": None,
                "overall_pass": None,
                "component_scores": {},
                "scenario_results": []
            },
            
            "detailed_analysis": {
                "strengths": [],
                "weaknesses": [], 
                "recommendations": [],
                "risk_factors": []
            },
            
            "monitoring_data": {
                "performance_metrics": {},
                "validation_results": {},
                "file_operations": {}
            },
            
            "appendix": {
                "configuration_used": self.__dict__,
                "test_data_files": [],
                "generated_artifacts": []
            }
        }