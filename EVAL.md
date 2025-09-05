# Agentic ETL System - Comprehensive Evaluation Framework

## Overview

This evaluation framework focuses on the core accuracy and functionality of the two-step Agentic ETL system: JSON → CSV (local validation) → BigQuery (production deployment). The framework evaluates both basic functionality and **agentic decision-making capabilities** with accuracy as the highest priority.

The system operates through a workflow: "Upload JSON → Show schema → Generate CSV → Show BigQuery DDL" where the agent helps non-technical users through iterative refinement without requiring a traditional chat interface.

## 1. Core Component Evaluation (HIGH PRIORITY)

### 1.1 JSON to CSV Schema Inference Engine

**Purpose**: Evaluates the system's ability to analyze JSON files and infer appropriate CSV schemas for local validation.

**Core Test Categories**:
- **Flat JSON structures**: Simple key-value pairs with primitive types
- **Basic nested objects**: 1-2 levels of nesting (common use cases)  
- **Simple arrays**: Arrays of primitives and basic objects
- **Data type inference**: Correct identification of strings, numbers, booleans, nulls

**Primary Evaluation Metrics** (Accuracy focus):
- **Schema accuracy**: Percentage of correctly inferred field types (TARGET: >95%)
- **CSV validity**: Percentage of generated CSV files that are syntactically correct (TARGET: 100%)
- **Transformation accuracy**: Correct JSON to CSV data mapping (TARGET: >98%)

**Basic Test Datasets**:
```
/test_data/
├── flat_basic/            # 50 files with simple flat JSON structures
├── nested_basic/          # 30 files with 1-2 level nesting
├── arrays_simple/         # 25 files with basic arrays
└── mixed_types/           # 20 files with various data types
```

**Success Criteria**:
- 95%+ accuracy for flat structures
- 90%+ accuracy for basic nested structures (1-2 levels)
- 100% valid CSV output

### 1.2 CSV to BigQuery DDL Generation Module

**Purpose**: Assesses the quality and correctness of BigQuery DDL statements generated from validated CSV schemas.

**Core Test Categories**:
- **Data type mapping**: Basic types to BigQuery (STRING, INTEGER, FLOAT, BOOLEAN)
- **Simple nested structure handling**: Basic STRUCT types for 1-2 level nesting
- **Basic array handling**: Simple REPEATED fields
- **Naming conventions**: Valid BigQuery column names from JSON keys

**Primary Evaluation Metrics**:
- **DDL syntax correctness**: 100% of DDL statements execute without errors
- **Type mapping accuracy**: >95% correct JSON to BigQuery type conversion
- **Schema structure accuracy**: >90% correct representation of JSON structure

**Basic Validation Tests**:
```sql
-- Test basic type mappings
CREATE OR REPLACE TABLE test_dataset.basic_types (
    string_field STRING,
    integer_field INTEGER,
    float_field FLOAT64,
    boolean_field BOOLEAN
);
```

**Success Criteria**:
- 100% syntactically correct DDL statements
- 95%+ type mapping accuracy for basic types
- 90%+ structure accuracy for simple nested objects

### 1.3 ETL Code Generation Engine

**Purpose**: Evaluates the quality and correctness of generated ETL code for the two-step process (JSON→CSV→BigQuery).

**Core Test Categories**:
- **JSON to CSV transformation**: Correct mapping from JSON to CSV structure
- **CSV to BigQuery loading**: Basic BigQuery data loading functionality
- **Data type consistency**: Maintaining types through the pipeline
- **Basic error handling**: Handling malformed JSON and type mismatches

**Primary Evaluation Metrics**:
- **Transformation accuracy**: >98% of records correctly transformed JSON→CSV
- **Loading accuracy**: >95% of CSV records correctly loaded to BigQuery
- **Type preservation**: >95% correct type handling through pipeline

**Basic Test Framework**:
```python
def test_json_to_csv_accuracy(json_input, expected_csv):
    """Test JSON to CSV transformation accuracy"""
    result = etl_engine.json_to_csv(json_input)
    accuracy = compare_csv_files(result, expected_csv)
    assert accuracy > 0.98, f"Accuracy only {accuracy:.2%}"

def test_csv_to_bigquery_loading(csv_input, table_schema):
    """Test CSV to BigQuery loading"""
    result = etl_engine.csv_to_bigquery(csv_input, table_schema)
    assert result.success_rate > 0.95
    assert result.type_errors == 0
```

**Success Criteria**:
- 98%+ JSON to CSV transformation accuracy
- 95%+ CSV to BigQuery loading accuracy
- Zero type conversion errors for basic types

## 2. Agent Decision Quality Metrics

### 2.1 Schema Inference Accuracy Assessment

**Purpose**: Evaluate the agent's decision-making quality in inferring optimal schemas from JSON data for non-technical users.

**Key Decision Points**:
- **Data type inference confidence**: How well the agent chooses between STRING, INTEGER, FLOAT64, BOOLEAN based on data patterns
- **Nested structure handling**: Decisions on when to flatten vs. preserve nested structures
- **Array field interpretation**: Choosing between REPEATED fields vs. JSON STRING storage
- **Null handling strategy**: Decisions on nullable vs. required fields based on data completeness

**Evaluation Metrics**:
```python
def evaluate_schema_inference_decisions():
    """Evaluate quality of agent's schema inference decisions"""
    test_scenarios = [
        {
            "json_data": mixed_type_json_files,
            "expected_decisions": {
                "confidence_threshold": 0.85,
                "type_inference_accuracy": 0.95,
                "structure_preservation": 0.90
            }
        }
    ]
    
    for scenario in test_scenarios:
        inference_result = agent.infer_schema(scenario["json_data"])
        
        # Measure decision confidence
        assert inference_result.confidence > scenario["expected_decisions"]["confidence_threshold"]
        
        # Validate type choices with ground truth
        type_accuracy = compare_inferred_types(inference_result, scenario["ground_truth"])
        assert type_accuracy > scenario["expected_decisions"]["type_inference_accuracy"]
```

**Decision Quality Indicators**:
- **Confidence scoring**: Agent provides confidence scores (0-1) for each schema decision
- **Alternative suggestions**: For ambiguous cases, agent provides 2-3 alternative schema options
- **Reasoning transparency**: Clear explanations for why specific types/structures were chosen
- **Error anticipation**: Proactive identification of potential data quality issues

**Success Criteria**:
- Schema inference confidence > 85% for straightforward JSON structures
- Type accuracy > 95% for primitive types with clear patterns
- Structure decisions align with user intent > 90% of the time
- Alternative options provided for ambiguous cases (confidence < 70%)

### 2.2 ETL Code Generation Quality Assessment

**Purpose**: Evaluate the quality and appropriateness of generated ETL code for the target use case.

**Code Quality Dimensions**:
- **Functional correctness**: Code executes without errors and produces expected output
- **Readability for non-technical users**: Clear variable names, comments, logical structure
- **Error handling robustness**: Graceful handling of data anomalies and edge cases
- **Performance considerations**: Efficient processing for typical dataset sizes

**Evaluation Framework**:
```python
def evaluate_etl_code_quality():
    """Comprehensive evaluation of generated ETL code quality"""
    
    # Functional correctness
    code_correctness = test_code_execution_success_rate()
    assert code_correctness > 0.98
    
    # Readability assessment
    readability_score = assess_code_readability(generated_code)
    assert readability_score > 0.8  # Using standardized readability metrics
    
    # Error handling coverage
    error_handling_coverage = test_error_scenarios(generated_code)
    assert error_handling_coverage > 0.85
    
    # Performance benchmarks
    performance_score = benchmark_processing_speed(generated_code, test_datasets)
    assert performance_score.meets_sla == True
```

**Code Generation Decision Metrics**:
- **Library choice justification**: Appropriate use of pandas vs. other libraries
- **Memory optimization**: Efficient handling of large JSON files
- **Data validation logic**: Comprehensive checks for data quality issues
- **Documentation quality**: Clear comments explaining transformation logic

**Success Criteria**:
- Generated code passes all functional tests (>98% accuracy)
- Code readability score > 0.8 for non-technical reviewers
- Handles 85%+ of common error scenarios gracefully
- Processing performance meets SLA (< 30 seconds per 10MB JSON file)

### 2.3 BigQuery DDL Correctness Validation

**Purpose**: Assess the agent's ability to generate production-ready BigQuery DDL that correctly represents the data structure.

**DDL Quality Assessments**:
- **Syntax correctness**: 100% valid BigQuery SQL syntax
- **Type mapping appropriateness**: Optimal BigQuery types for given data patterns
- **Schema evolution support**: DDL supports future schema changes
- **Performance optimization**: Appropriate clustering, partitioning suggestions

**Validation Framework**:
```python
def validate_bigquery_ddl_decisions():
    """Validate BigQuery DDL generation quality and decisions"""
    
    test_cases = load_ddl_test_scenarios()
    
    for test_case in test_cases:
        ddl_result = agent.generate_bigquery_ddl(test_case.csv_schema)
        
        # Syntax validation
        syntax_valid = validate_bigquery_syntax(ddl_result.ddl)
        assert syntax_valid == True
        
        # Type mapping validation
        type_mapping_score = evaluate_type_mapping_quality(
            test_case.source_types, ddl_result.bigquery_types
        )
        assert type_mapping_score > 0.95
        
        # Performance considerations
        perf_optimizations = analyze_performance_features(ddl_result)
        assert perf_optimizations.has_appropriate_optimizations == True
```

**Decision Transparency Requirements**:
- **Type mapping rationale**: Clear explanations for JSON → BigQuery type conversions
- **Optimization recommendations**: Suggestions for partitioning/clustering when beneficial
- **Schema modification guidance**: Instructions for handling future schema changes
- **Cost implications**: Warnings about potential storage/query costs

**Success Criteria**:
- 100% syntactically correct DDL statements
- 95%+ optimal type mapping decisions
- Performance optimization suggestions for tables > 1GB
- Clear documentation for schema evolution path

### 2.4 Decision Transparency and Explainability Metrics

**Purpose**: Ensure the agent's decisions are transparent and understandable to non-technical users.

**Explainability Components**:
- **Decision reasoning**: Clear explanations for each major choice
- **Alternative options**: When applicable, explanation of other possible approaches
- **Confidence indicators**: Visual/textual indicators of decision certainty
- **Impact warnings**: Alerts about consequences of specific decisions

**Measurement Framework**:
```python
def evaluate_decision_transparency():
    """Evaluate the transparency and explainability of agent decisions"""
    
    # Reasoning quality assessment
    explanation_quality = assess_explanation_clarity(agent_decisions)
    assert explanation_quality.user_comprehension_score > 0.8
    
    # Confidence communication
    confidence_communication = evaluate_confidence_presentation(agent_decisions)
    assert confidence_communication.clarity_score > 0.85
    
    # Warning effectiveness
    warning_effectiveness = test_warning_comprehension(agent_warnings)
    assert warning_effectiveness.user_action_rate > 0.7
```

**Transparency Success Criteria**:
- Decision explanations understandable to non-technical users (>80% comprehension)
- Confidence levels clearly communicated with visual indicators
- Warnings lead to appropriate user actions >70% of the time
- Alternative options provided when confidence < 70%

## 3. Conversation Context Tracking (Workflow State Management)

### 3.1 Workflow State Context Maintenance

**Purpose**: Evaluate how well the agent maintains context across the multi-step workflow without traditional chat interface.

**Context Tracking Dimensions**:
- **Schema modification history**: Tracking user changes to inferred schemas
- **Data quality issue resolution**: Remembering identified issues and applied fixes
- **User preference learning**: Adapting to user's schema and naming preferences
- **Error context preservation**: Maintaining context of errors across workflow steps

**Evaluation Framework**:
```python
def evaluate_workflow_context_tracking():
    """Test agent's ability to maintain context across workflow steps"""
    
    workflow_session = start_workflow_session()
    
    # Step 1: Upload JSON and infer schema
    initial_schema = workflow_session.infer_schema(json_files)
    
    # Step 2: User modifies schema
    user_modifications = {
        "rename_field": {"old": "user_id", "new": "customer_id"},
        "change_type": {"field": "age", "from": "STRING", "to": "INTEGER"}
    }
    modified_schema = workflow_session.apply_user_modifications(user_modifications)
    
    # Step 3: Generate CSV with modified schema
    csv_result = workflow_session.generate_csv(modified_schema)
    
    # Validate context preservation
    assert csv_result.reflects_user_modifications == True
    assert workflow_session.remembers_user_preferences == True
    
    # Step 4: Generate DDL
    ddl_result = workflow_session.generate_bigquery_ddl(csv_result)
    
    # Ensure DDL reflects all previous decisions
    assert ddl_result.consistent_with_workflow_decisions == True
```

**Context Preservation Metrics**:
- **Modification tracking**: 100% accuracy in applying user schema modifications
- **Preference consistency**: Schema naming and type preferences maintained across steps
- **Error resolution continuity**: Previous error fixes not forgotten in subsequent steps
- **Decision coherence**: Final BigQuery DDL consistent with all workflow decisions

### 3.2 User Intent Understanding Across Iterations

**Purpose**: Assess the agent's ability to understand and adapt to user intent throughout the iterative refinement process.

**Intent Understanding Categories**:
- **Schema refinement intent**: Understanding why users change field names/types
- **Data quality priorities**: Recognizing user's tolerance for data loss vs. accuracy
- **Business context awareness**: Adapting to industry-specific naming/structuring preferences
- **Performance vs. accuracy trade-offs**: Understanding user priorities

**Assessment Framework**:
```python
def evaluate_user_intent_understanding():
    """Evaluate agent's understanding of user intent across workflow iterations"""
    
    intent_scenarios = [
        {
            "user_action": "rename 'id' to 'customer_id'",
            "expected_inference": "user prefers business-meaningful names",
            "adaptation_test": "suggest similar names for other id fields"
        },
        {
            "user_action": "change STRING to INTEGER for 'quantity'",
            "expected_inference": "user prioritizes type accuracy for numeric fields",
            "adaptation_test": "suggest INTEGER for other numeric string fields"
        }
    ]
    
    for scenario in intent_scenarios:
        agent_response = agent.process_user_modification(scenario["user_action"])
        
        # Test intent inference
        intent_accuracy = evaluate_intent_inference(
            agent_response, scenario["expected_inference"]
        )
        assert intent_accuracy > 0.8
        
        # Test adaptation
        adaptation_quality = test_adaptation_suggestions(
            agent_response, scenario["adaptation_test"]
        )
        assert adaptation_quality > 0.75
```

**Intent Understanding Success Criteria**:
- Intent inference accuracy > 80% for common user modifications
- Proactive suggestions based on inferred intent > 75% relevance
- Consistent application of inferred preferences across workflow
- Adaptation to user corrections within same session > 90%

### 3.3 Schema Modification Decision Tracking

**Purpose**: Track and evaluate the agent's handling of schema modifications throughout the workflow.

**Modification Tracking Components**:
- **Change impact analysis**: Understanding downstream effects of schema changes
- **Consistency enforcement**: Ensuring modifications don't create conflicts
- **Rollback capability**: Ability to revert problematic changes
- **Cumulative change validation**: Ensuring final schema is coherent

**Tracking Framework**:
```python
def evaluate_schema_modification_tracking():
    """Test schema modification tracking and consistency"""
    
    modification_session = SchemaModificationSession()
    
    # Apply series of modifications
    modifications = [
        {"action": "rename", "field": "user_id", "new_name": "customer_id"},
        {"action": "change_type", "field": "age", "new_type": "INTEGER"},
        {"action": "add_field", "field": "created_at", "type": "TIMESTAMP"},
        {"action": "remove_field", "field": "deprecated_field"}
    ]
    
    for modification in modifications:
        result = modification_session.apply_modification(modification)
        
        # Validate consistency after each change
        consistency_check = modification_session.validate_consistency()
        assert consistency_check.is_consistent == True
        
        # Ensure change tracking
        change_history = modification_session.get_change_history()
        assert len(change_history) == modifications.index(modification) + 1
    
    # Test rollback functionality
    rollback_result = modification_session.rollback_last_change()
    assert rollback_result.success == True
    assert modification_session.validate_consistency().is_consistent == True
```

**Modification Tracking Success Criteria**:
- 100% consistency validation after each modification
- Complete change history with rollback capability
- Impact analysis provided for significant changes
- Final schema coherence validation > 95%

### 3.4 Error Recovery and Adaptation Metrics

**Purpose**: Evaluate the agent's ability to recover from errors and adapt based on user feedback.

**Error Recovery Scenarios**:
- **Data type conflicts**: Handling cases where inferred types don't match data
- **Schema validation failures**: Recovery from BigQuery DDL validation errors
- **CSV generation errors**: Handling transformation failures gracefully
- **User correction integration**: Learning from user corrections to prevent similar errors

**Recovery Assessment Framework**:
```python
def evaluate_error_recovery_adaptation():
    """Test error recovery and learning capabilities"""
    
    error_scenarios = [
        {
            "error_type": "type_mismatch",
            "trigger": "INTEGER field contains 'N/A' values",
            "expected_recovery": "suggest STRING type or null handling",
            "learning_test": "apply similar fix to other fields with null markers"
        },
        {
            "error_type": "ddl_validation_failure", 
            "trigger": "invalid BigQuery column name with spaces",
            "expected_recovery": "automatically fix column naming",
            "learning_test": "prevent similar naming issues in future schemas"
        }
    ]
    
    for scenario in error_scenarios:
        # Trigger error condition
        error_result = trigger_error_scenario(scenario)
        
        # Test recovery capability
        recovery_result = agent.recover_from_error(error_result)
        assert recovery_result.successful_recovery == True
        
        # Test learning and adaptation
        learning_result = test_error_pattern_learning(agent, scenario)
        assert learning_result.prevents_similar_errors == True
```

**Error Recovery Success Criteria**:
- 90%+ successful automatic error recovery for common issues
- Learning from user corrections prevents similar errors > 80% of the time
- Clear error explanations with actionable resolution steps
- Graceful degradation when automatic recovery fails

## 4. ETL Domain-Specific Test Scenarios

### 4.1 Complex Nested JSON Structures

**Purpose**: Test agent performance with realistic enterprise JSON data containing complex nesting patterns.

**Nested Structure Test Categories**:
```json
{
  "test_scenarios": {
    "deep_nesting": {
      "description": "JSON with 5+ levels of nesting",
      "example": {
        "user": {
          "profile": {
            "personal": {
              "address": {
                "billing": {
                  "street": "123 Main St",
                  "coordinates": {"lat": 40.7128, "lng": -74.0060}
                }
              }
            }
          }
        }
      },
      "evaluation_criteria": {
        "flattening_accuracy": ">90%",
        "field_naming_consistency": ">95%",
        "data_preservation": ">98%"
      }
    },
    "mixed_array_types": {
      "description": "Arrays containing different object structures",
      "example": {
        "events": [
          {"type": "click", "element": "button", "timestamp": "2024-01-01T10:00:00Z"},
          {"type": "purchase", "amount": 99.99, "currency": "USD", "items": []}
        ]
      },
      "evaluation_criteria": {
        "schema_generalization": ">85%",
        "data_loss_prevention": ">95%"
      }
    }
  }
}
```

**Complex Structure Evaluation Framework**:
```python
def test_complex_nested_structures():
    """Test handling of complex nested JSON structures"""
    
    complex_json_datasets = load_complex_test_data()
    
    for dataset in complex_json_datasets:
        # Test schema inference for complex structures
        schema_result = agent.infer_schema(dataset.json_files)
        
        # Evaluate nesting handling decisions
        nesting_quality = evaluate_nesting_decisions(schema_result, dataset.expected_structure)
        assert nesting_quality.flattening_appropriateness > 0.85
        assert nesting_quality.information_preservation > 0.90
        
        # Test CSV generation with complex data
        csv_result = agent.generate_csv(schema_result)
        assert csv_result.structural_integrity > 0.95
        
        # Test BigQuery DDL for complex schemas
        ddl_result = agent.generate_bigquery_ddl(csv_result.schema)
        assert ddl_result.handles_complex_types == True
```

**Success Criteria for Complex Structures**:
- Appropriate flattening decisions for nested objects > 85%
- Array handling preserves data integrity > 95%
- Generated BigQuery schemas support complex query patterns
- Performance remains acceptable for deeply nested structures

### 4.2 Schema Conflicts and Ambiguities

**Purpose**: Evaluate agent's handling of ambiguous or conflicting schema patterns in JSON data.

**Conflict Scenario Categories**:
- **Type inconsistencies**: Same field appears as different types across files
- **Structure variations**: Same field sometimes object, sometimes primitive
- **Missing field patterns**: Fields present in some files but not others
- **Array cardinality conflicts**: Fields that are sometimes arrays, sometimes single values

**Conflict Resolution Test Framework**:
```python
def test_schema_conflict_resolution():
    """Test agent's handling of schema conflicts and ambiguities"""
    
    conflict_scenarios = [
        {
            "name": "mixed_type_fields",
            "files": [
                {"user_id": "12345", "age": 25},  # age as integer
                {"user_id": "67890", "age": "unknown"},  # age as string
                {"user_id": "11111", "age": None}  # age as null
            ],
            "expected_resolution": {
                "type_choice": "STRING",
                "justification": "accommodates all value patterns",
                "confidence_level": 0.7
            }
        },
        {
            "name": "structure_inconsistency",
            "files": [
                {"address": {"street": "123 Main", "city": "NYC"}},  # object
                {"address": "123 Main St, NYC, NY"}  # string
            ],
            "expected_resolution": {
                "type_choice": "STRING",
                "alternative_suggestion": "separate object and string address fields",
                "confidence_level": 0.6
            }
        }
    ]
    
    for scenario in conflict_scenarios:
        resolution_result = agent.resolve_schema_conflicts(scenario["files"])
        
        # Validate resolution quality
        assert resolution_result.type_choice == scenario["expected_resolution"]["type_choice"]
        assert resolution_result.confidence >= scenario["expected_resolution"]["confidence_level"]
        
        # Check for alternative suggestions when confidence is low
        if resolution_result.confidence < 0.7:
            assert resolution_result.alternatives is not None
            assert len(resolution_result.alternatives) > 0
```

**Conflict Resolution Success Criteria**:
- Appropriate resolution strategy for type conflicts > 85%
- Alternative solutions provided for low-confidence decisions (< 70%)
- Data loss minimization in conflict resolution > 95%
- Clear explanations of resolution rationale to users

### 4.3 Data Type Inference Challenges

**Purpose**: Test the agent's accuracy in inferring appropriate data types from JSON values with edge cases.

**Type Inference Challenge Categories**:
```python
type_inference_challenges = {
    "numeric_edge_cases": {
        "test_values": [
            "01234",  # Leading zeros (should be STRING, not INTEGER)
            "3.14159",  # Float as string
            "1.0",  # Integer-like float
            "1e5",  # Scientific notation
            "$1,234.56",  # Currency format
            "NaN", "Infinity", "-Infinity"  # Special numeric values
        ],
        "success_criteria": {
            "preserves_leading_zeros": True,
            "recognizes_currency": True,
            "handles_special_values": True
        }
    },
    "datetime_patterns": {
        "test_values": [
            "2024-01-15T10:30:00Z",  # ISO format
            "01/15/2024",  # US date format
            "15-01-2024",  # EU date format
            "2024-01-15 10:30:00",  # SQL timestamp
            "1642248600",  # Unix timestamp
            "Mon, Jan 15 2024"  # RFC format
        ],
        "success_criteria": {
            "recognizes_iso_datetime": True,
            "detects_timestamp_patterns": True,
            "suggests_appropriate_bigquery_type": True
        }
    },
    "boolean_variations": {
        "test_values": [
            True, False,  # JSON boolean
            "true", "false",  # String boolean
            "True", "False",  # Python-style
            "yes", "no",  # Natural language
            "Y", "N",  # Single character
            1, 0,  # Numeric boolean
            "on", "off"  # Status indicators
        ],
        "success_criteria": {
            "consolidates_boolean_patterns": True,
            "suggests_standardization": True
        }
    }
}
```

**Type Inference Evaluation Framework**:
```python
def test_data_type_inference_challenges():
    """Test agent's accuracy with challenging type inference scenarios"""
    
    for challenge_category, challenge_data in type_inference_challenges.items():
        # Create test JSON with challenging values
        test_json = create_test_json_with_values(challenge_data["test_values"])
        
        # Test type inference
        inference_result = agent.infer_types(test_json)
        
        # Validate against success criteria
        for criterion, expected in challenge_data["success_criteria"].items():
            actual_result = getattr(inference_result, criterion)
            assert actual_result == expected, f"Failed {criterion} for {challenge_category}"
        
        # Test explanation quality for edge cases
        explanations = inference_result.get_type_explanations()
        explanation_quality = assess_explanation_clarity(explanations)
        assert explanation_quality > 0.8
```

**Type Inference Success Criteria**:
- 95%+ accuracy for standard type patterns
- 85%+ accuracy for edge cases and ambiguous patterns
- Appropriate suggestions for data standardization
- Clear explanations for non-obvious type choices

### 4.4 Real-World Edge Cases

**Purpose**: Test agent performance with real-world data quality issues and edge cases commonly found in enterprise datasets.

**Real-World Edge Case Scenarios**:
```python
real_world_edge_cases = {
    "data_quality_issues": {
        "missing_values": ["", "null", "NULL", "N/A", "n/a", "None", "-", "TBD"],
        "encoding_issues": ["caf\u00e9", "résumé", "naïve"],
        "inconsistent_formats": [
            {"phone": "+1-555-123-4567"},
            {"phone": "(555) 123-4567"},
            {"phone": "5551234567"},
            {"phone": "555.123.4567"}
        ]
    },
    "structural_variations": {
        "optional_fields": [
            {"id": 1, "name": "John", "email": "john@example.com"},
            {"id": 2, "name": "Jane"},  # missing email
            {"id": 3, "name": "Bob", "email": "bob@example.com", "phone": "555-0123"}  # extra field
        ],
        "array_cardinality": [
            {"tags": ["red", "blue", "green"]},  # multiple values
            {"tags": "red"},  # single value as string
            {"tags": ["yellow"]},  # single value as array
            {"tags": []}  # empty array
        ]
    },
    "performance_challenges": {
        "large_files": "10MB+ JSON files with 100k+ records",
        "wide_schemas": "JSON objects with 100+ fields",
        "deep_nesting": "Nested structures with 10+ levels"
    }
}
```

**Edge Case Evaluation Framework**:
```python
def test_real_world_edge_cases():
    """Test agent performance with real-world data edge cases"""
    
    # Test data quality issue handling
    data_quality_results = test_data_quality_handling(
        real_world_edge_cases["data_quality_issues"]
    )
    assert data_quality_results.null_detection_accuracy > 0.95
    assert data_quality_results.encoding_preservation > 0.90
    assert data_quality_results.format_standardization_suggestions > 0.80
    
    # Test structural variation handling
    structural_results = test_structural_variation_handling(
        real_world_edge_cases["structural_variations"]
    )
    assert structural_results.optional_field_handling > 0.90
    assert structural_results.array_normalization > 0.85
    
    # Test performance with challenging datasets
    performance_results = test_performance_edge_cases(
        real_world_edge_cases["performance_challenges"]
    )
    assert performance_results.large_file_processing_time < 60  # seconds
    assert performance_results.wide_schema_accuracy > 0.90
    assert performance_results.deep_nesting_handling > 0.85
```

**Real-World Edge Case Success Criteria**:
- Null value detection accuracy > 95% across different representations
- Encoding issue preservation > 90% (no data corruption)
- Performance SLA maintained even with challenging datasets
- Graceful degradation with clear user guidance for unsupported cases
- Proactive suggestions for data quality improvements

## 5. End-to-End Pipeline Evaluation

### 5.1 Two-Step Process Validation

**Purpose**: Validate the complete JSON→CSV→BigQuery pipeline works correctly.

**Test Scenarios**:
- **Happy path**: Clean JSON files through complete pipeline
- **Basic error handling**: Malformed JSON, missing fields, type mismatches
- **Schema consistency**: Same schema inference from JSON to final BigQuery table

**Key Metrics**:
- **End-to-end accuracy**: >95% successful pipeline completion
- **Schema consistency**: >90% schema match between JSON inference and BigQuery table
- **Data integrity**: >98% data preservation through pipeline

**Basic Integration Tests**:
```python
def test_end_to_end_pipeline():
    # Step 1: JSON to CSV
    csv_result = pipeline.json_to_csv(json_files)
    assert csv_result.accuracy > 0.95
    
    # Step 2: CSV to BigQuery
    bq_result = pipeline.csv_to_bigquery(csv_result)
    assert bq_result.success_rate > 0.95
    
    # Validate data integrity
    original_count = count_json_records(json_files)
    final_count = count_bigquery_records(bq_result.table)
    assert final_count / original_count > 0.98
```

## 3. Basic User Interface Evaluation

### 3.1 Web IDE Functionality

**Purpose**: Ensure basic functionality of the web IDE for code editing and file management.

**Core Features to Test**:
- **File display**: Show generated CSV and ETL code
- **Basic editing**: Allow users to modify generated code
- **Preview functionality**: Display CSV preview before BigQuery deployment
- **Basic error display**: Show validation errors clearly

**Success Criteria**:
- All generated files display correctly
- Basic code editing works without errors
- CSV preview loads within 3 seconds
- Error messages are clear and actionable

### 3.2 Conversational Interface

**Purpose**: Basic validation that the chat interface can handle common ETL tasks.

**Core Scenarios**:
- **Schema questions**: "What columns will be created?"
- **Data type clarification**: "Why is this field a STRING instead of INTEGER?"
- **Error resolution**: "How do I fix this transformation error?"

**Success Criteria**:
- Responds to basic schema questions with >90% accuracy
- Provides actionable error resolution steps
- Maintains conversation context for follow-up questions

## 4. Implementation Priority

### Phase 1A: JSON to CSV Schema Preview and Validation (Step 1)
**Goal**: User can upload JSON files and see inferred CSV schema before any transformation

**Components to Evaluate**:
1. **JSON Schema Analysis**: Parse JSON files and infer field types and structure
2. **CSV Schema Generation**: Generate proposed CSV column definitions
3. **Schema Preview UI**: Display inferred schema in web interface for user validation
4. **Schema Editing**: Allow users to modify field names and types before proceeding

**Success Criteria**:
- JSON parsing accuracy >98% for flat structures
- Schema inference accuracy >95% for basic types
- Schema preview loads within 2 seconds
- Users can modify schema and see updates immediately

**Test Framework**:
```python
def test_schema_inference_preview():
    json_files = load_test_json_files("flat_basic/")
    schema_result = schema_engine.infer_csv_schema(json_files)
    
    assert schema_result.parsing_success_rate > 0.98
    assert schema_result.type_inference_accuracy > 0.95
    assert len(schema_result.proposed_columns) > 0
    assert schema_result.preview_data is not None
```

### Phase 1B: ETL Script Generation for Valid CSV Output (Step 2)
**Goal**: Generate Python ETL scripts that transform JSON to valid CSV files

**Components to Evaluate**:
1. **ETL Code Generation**: Create Python scripts based on validated schema
2. **CSV File Generation**: Execute scripts to produce actual CSV files
3. **Data Validation**: Verify CSV files match expected schema and contain correct data
4. **Error Handling**: Handle malformed JSON records gracefully

**Success Criteria**:
- Generated CSV files are 100% syntactically valid
- Data transformation accuracy >98%
- Generated Python code passes basic quality checks
- Handles at least 90% of malformed records without crashing

**Test Framework**:
```python
def test_etl_script_generation():
    schema = validated_csv_schema
    etl_script = code_generator.generate_etl_script(schema)
    
    # Test script syntax
    assert is_valid_python_syntax(etl_script)
    
    # Test execution
    csv_output = execute_etl_script(etl_script, test_json_files)
    assert is_valid_csv(csv_output)
    assert csv_matches_schema(csv_output, schema)
```

### Phase 1C: Query Generation and Execution Against CSV (Step 3)
**Goal**: Generate Python scripts that can answer user questions using CSV files and pandas

**Components to Evaluate**:
1. **Question Interpretation**: Parse natural language questions about data
2. **Query Code Generation**: Generate pandas/Python code to answer questions
3. **CSV Query Execution**: Run generated code against CSV files
4. **Results Validation**: Verify query results are accurate and meaningful

**Success Criteria**:
- Successfully interprets >85% of basic analytical questions
- Generated pandas code executes without errors >95% of the time
- Query results accuracy >90% for simple aggregations and filters
- Supports basic question types (count, sum, average, group by, filter)

**Test Framework**:
```python
def test_csv_query_generation():
    questions = [
        "How many records are there?",
        "What is the average age?",
        "Show me users by city",
        "Count users by status"
    ]
    
    for question in questions:
        query_code = query_generator.generate_pandas_query(question, csv_schema)
        result = execute_query(query_code, csv_file)
        
        assert result.success == True
        assert result.has_meaningful_output == True
```

### Phase 1D: Results Preview with Tables and Charts (Step 4)
**Goal**: Display query results in both tabular format and basic visualizations

**Components to Evaluate**:
1. **Table Display**: Show query results in formatted tables
2. **Chart Generation**: Create appropriate visualizations (bar, line, pie charts)
3. **Chart Selection Logic**: Choose suitable chart types based on data and query type
4. **Interactive Preview**: Allow users to see results before BigQuery deployment

**Success Criteria**:
- Tables display correctly for all result types
- Charts are generated for >80% of queries where visualization makes sense
- Chart type selection is appropriate >90% of the time
- Preview loads within 3 seconds for typical query results

**Test Framework**:
```python
def test_results_visualization():
    query_results = [
        {"type": "count", "data": [{"category": "A", "count": 100}]},
        {"type": "timeseries", "data": [{"date": "2024-01", "value": 50}]},
        {"type": "summary", "data": [{"metric": "avg_age", "value": 35.2}]}
    ]
    
    for result in query_results:
        table_html = table_generator.create_table(result)
        assert is_valid_html_table(table_html)
        
        if should_have_chart(result):
            chart = chart_generator.create_chart(result)
            assert chart.chart_type is not None
            assert chart.is_valid == True
```

### Phase 2: BigQuery Integration (Next Priority)
1. CSV to BigQuery DDL generation validation
2. BigQuery table creation and data loading
3. BigQuery query generation and execution
4. End-to-end pipeline data integrity testing

### Phase 3: Polish and Advanced Features (Future)
1. Complex nested structure support
2. Performance optimization
3. Advanced error scenarios
4. User experience improvements

## 6. Success Metrics Summary

### Core Functional Requirements (Must-Have)

**Phase 1A - JSON Schema Inference & Preview**:
- JSON parsing accuracy > 98%
- Schema inference accuracy > 95%
- Schema preview functionality working
- User can modify schema before processing
- **Agentic**: Decision confidence > 85% for straightforward structures
- **Agentic**: Alternative options provided for ambiguous cases (confidence < 70%)

**Phase 1B - ETL Code Generation**:
- Generated CSV files 100% syntactically valid
- Data transformation accuracy > 98%
- ETL scripts execute without syntax errors
- **Agentic**: Code readability score > 0.8 for non-technical users
- **Agentic**: Error handling coverage > 85%

**Phase 1C - Query Generation & Execution**:
- Basic question interpretation > 85%
- Pandas query generation success > 95%
- Query execution accuracy > 90%
- **Agentic**: Intent understanding accuracy > 80% for user modifications

**Phase 1D - Results Preview & Visualization**:
- Tables display correctly 100% of the time
- Charts generated for appropriate queries > 80%
- Preview loads within 3 seconds
- **Agentic**: Decision explanations understandable to non-technical users (>80% comprehension)

### Agentic Decision Quality Requirements (High Priority)

**Schema Inference Decision Quality**:
- Type inference confidence > 85% for clear patterns
- Structure decisions align with user intent > 90%
- Alternative suggestions for low-confidence decisions
- Reasoning transparency for all major choices

**Workflow Context Management**:
- Modification tracking accuracy: 100%
- User preference consistency across workflow steps
- Error recovery success rate > 90%
- Intent inference accuracy > 80%

**ETL Domain Expertise**:
- Complex nested structure handling > 85%
- Schema conflict resolution > 85%
- Real-world edge case handling > 90%
- Type inference accuracy for edge cases > 85%

### Later Phases (Nice-to-Have)

**BigQuery Integration with Agentic Features**:
- DDL generation with optimization suggestions
- Performance consideration recommendations
- Schema evolution guidance
- Cost implication warnings

**Advanced Agentic Capabilities**:
- Cross-session learning and preference retention
- Industry-specific schema pattern recognition
- Proactive data quality issue identification
- Advanced error pattern learning

This comprehensive evaluation framework ensures both functional accuracy and intelligent agentic behavior that provides genuine value to non-technical users throughout the ETL workflow.