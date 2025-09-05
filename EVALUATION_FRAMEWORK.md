# Comprehensive Evaluation Framework for Agentic ETL Systems

This document describes the comprehensive evaluation framework designed specifically for agentic ETL systems that generate schemas and write intermediate results to files.

## Framework Overview

The evaluation framework addresses the unique challenges of evaluating file-based agentic systems through:

1. **Multi-dimensional evaluation** across process quality, file outputs, functionality, consistency, and production readiness
2. **Real-time monitoring** of file operations and validation
3. **Cross-file consistency checking** to ensure generated artifacts work together
4. **Performance profiling** and observability
5. **Production readiness assessment** for deployment validation

## Key Components

### 1. File-Based Evaluator (`tests/file_based_evaluator.py`)

**Purpose**: Comprehensive evaluation of multi-step ETL processes with file tracking

**Key Features**:
- Workspace state capture before/after agent actions
- Cross-file consistency validation
- Pipeline functionality testing (actual ETL script execution)
- Production readiness assessment

**Usage**:
```python
from tests.file_based_evaluator import FileBasedETLEvaluator

evaluator = FileBasedETLEvaluator()
evaluation = await evaluator.evaluate_multi_step_etl_process(scenario)
```

### 2. Real-Time Monitoring System (`tests/etl_monitoring.py`)

**Purpose**: Observability and debugging for agent file operations

**Key Features**:
- File system event monitoring with automatic validation
- Real-time validation of schemas, ETL scripts, CSV outputs, and DDL files
- Performance metric collection
- Live monitoring dashboard

**Usage**:
```python
from tests.etl_monitoring import RealTimeETLMonitor

monitor = RealTimeETLMonitor(workspace_dir)
monitor.start_monitoring()
# ... agent operations occur ...
report = monitor.generate_monitoring_report()
monitor.stop_monitoring()
```

### 3. Configuration Management (`tests/evaluation_config.py`)

**Purpose**: Centralized configuration for evaluation criteria and test scenarios

**Key Features**:
- Configurable evaluation thresholds
- Test scenario definitions with complexity levels
- File validation rules
- Weighted scoring algorithms

### 4. Comprehensive Demo (`tests/comprehensive_etl_evaluation_demo.py`)

**Purpose**: Complete demonstration showing all framework components working together

## Evaluation Dimensions

### 1. Process Quality (Weight: 15%)
- File creation sequence correctness
- Multi-step workflow execution
- Tool usage patterns
- Action history analysis

### 2. File Outputs (Weight: 20%)
- Completeness of generated files (schema, ETL, CSV, DDL)
- File naming conventions
- File size reasonableness
- Directory structure compliance

### 3. Pipeline Functionality (Weight: 30%) - **Most Important**
- ETL script execution success
- CSV generation correctness
- Column mapping accuracy
- Data transformation quality

### 4. Cross-File Consistency (Weight: 20%)
- Schema-ETL field alignment
- ETL-CSV output matching
- Schema-DDL consistency
- Naming pattern consistency

### 5. Production Readiness (Weight: 15%)
- BigQuery DDL compliance
- Error handling in ETL scripts
- Deployment artifact completeness
- Configuration management

## Best Practices for File-Based Agent Evaluation

### 1. Workspace State Tracking
```python
# Capture state before and after agent actions
initial_state = evaluator.capture_workspace_state(workspace_dir)
# ... agent performs actions ...
final_state = evaluator.capture_workspace_state(workspace_dir)

# Analyze what changed
file_changes = evaluator.analyze_state_changes(initial_state, final_state)
```

### 2. Real-Time Validation
```python
# Validate files as they're created
monitor = RealTimeETLMonitor(workspace_dir)
monitor.start_monitoring()  # Automatically validates new files

# Custom validation triggers
def on_schema_created(file_path):
    result = monitor._validate_schema_file(file_path)
    if not result.passed:
        alert_user(result.issues)
```

### 3. Cross-File Dependency Validation
```python
# Check that schema fields are used in ETL scripts
schema_fields = extract_schema_fields(schema_file)
etl_references = extract_field_references(etl_file)
consistency_score = calculate_field_overlap(schema_fields, etl_references)
```

### 4. End-to-End Pipeline Testing
```python
# Actually execute the generated ETL pipeline
result = subprocess.run(["python", etl_script], capture_output=True)
if result.returncode == 0:
    csv_validation = validate_csv_output(generated_csv, expected_schema)
```

## Schema Validation Strategies

### 1. Structure Validation
```python
def validate_schema_structure(schema):
    required_sections = ["entities", "tables", "transformations"]
    return all(section in schema for section in required_sections)
```

### 2. Semantic Validation
```python
def validate_analytical_intent(schema, query_intent):
    schema_fields = extract_all_fields(schema)
    return check_intent_supportability(schema_fields, query_intent)
```

### 3. Evolution Tracking
```python
def track_schema_changes(workspace_dir):
    schema_versions = get_schema_files_by_timestamp(workspace_dir)
    return analyze_schema_evolution(schema_versions)
```

## Observable Patterns and Metrics

### 1. File Operation Patterns
- **Expected sequence**: JSON → Schema → ETL → CSV → DDL
- **Timing patterns**: Schema generation should complete within 30s
- **Size patterns**: Schema files 1-10KB, ETL scripts 1-50KB, CSV outputs variable

### 2. Quality Metrics
- **Schema coverage**: % of JSON fields represented in schema
- **Type accuracy**: Correctness of inferred data types
- **Flattening completeness**: Proper handling of nested structures
- **Column mapping accuracy**: CSV columns match schema definitions

### 3. Performance Metrics
- **Time to first schema**: How quickly agent generates initial schema
- **ETL execution time**: Duration of generated script execution
- **Memory usage**: Resource consumption during processing
- **File I/O efficiency**: Read/write operation patterns

## Real-World Testing Approaches

### 1. Production-Like Data Testing
```python
# Test with realistic data volumes and complexity
large_dataset_scenario = {
    "name": "Large Dataset Processing",
    "json_file": generate_large_json(10000),  # 10K records
    "complexity_indicators": ["deeply_nested", "mixed_types", "large_arrays"]
}
```

### 2. Edge Case Testing
```python
edge_cases = [
    "missing_fields_json",
    "null_heavy_dataset", 
    "unicode_special_characters",
    "extremely_nested_structures",
    "mixed_schema_evolution"
]
```

### 3. Adversarial Testing
```python
adversarial_scenarios = [
    {"malformed_json": "test_error_handling"},
    {"resource_constraints": "test_memory_limits"},
    {"concurrent_access": "test_file_locking"}
]
```

### 4. Regression Testing
```python
# Compare against golden reference outputs
def compare_against_baseline(current_output, baseline_output):
    return calculate_similarity_scores(current_output, baseline_output)
```

## Usage Examples

### Basic Evaluation
```bash
cd /Users/bill/src/etl/tests
python comprehensive_etl_evaluation_demo.py
```

### Specific Scenario Testing
```python
# Test only product analysis scenarios
framework = ComprehensiveETLEvaluationFramework()
await framework.run_comprehensive_evaluation("product")
```

### Real-Time Monitoring Only
```python
monitor = RealTimeETLMonitor(workspace_dir)
monitor.start_monitoring()
# ... run your agent ...
monitor.print_live_dashboard()
report = monitor.generate_monitoring_report()
monitor.stop_monitoring()
```

### Custom Validation Rules
```python
config = EvaluationConfig()
config.thresholds.functionality_min = 4.0  # Raise the bar
config.file_validation_rules["schema"]["min_fields_per_table"] = 5
```

## Integration with Existing System

The framework integrates with your existing evaluation system (`tests/eval.py`) by:

1. **Extending** the `JSONToCSVSchemaEvaluator` with file-based capabilities
2. **Enhancing** the `extract_schema_generator_output` method with cross-file validation
3. **Adding** real-time monitoring to your current test scenarios
4. **Providing** comprehensive reporting alongside existing metrics

## Key File Paths

- **Framework Core**: `/Users/bill/src/etl/tests/file_based_evaluator.py`
- **Monitoring System**: `/Users/bill/src/etl/tests/etl_monitoring.py`
- **Configuration**: `/Users/bill/src/etl/tests/evaluation_config.py`
- **Demo Script**: `/Users/bill/src/etl/tests/comprehensive_etl_evaluation_demo.py`
- **Existing Integration**: `/Users/bill/src/etl/tests/eval.py`

## Next Steps

1. **Run the demo** to see the framework in action
2. **Customize scenarios** in `evaluation_config.py` for your specific use cases
3. **Integrate monitoring** into your development workflow
4. **Extend validators** for domain-specific requirements
5. **Set up CI/CD** integration for continuous evaluation

This framework provides a robust foundation for evaluating agentic ETL systems that handle complex file-based workflows, ensuring both functional correctness and production readiness.