# Schema-Generator Sub-Agent Integration

## Overview
Updated the evaluation system to work with the existing `schema-generator` sub-agent format instead of modifying the schema output format. This approach maintains compatibility with the existing sub-agent while enabling accurate schema extraction and evaluation.

## Key Changes Made

### 1. Schema Extraction Logic
Added `extract_schema_generator_output()` method that:
- Looks for JSON blocks in agent responses using regex patterns
- Validates the JSON contains `entities` and `tables` fields (schema-generator format)
- Handles both code-blocked JSON and inline JSON
- Provides detailed error reporting for extraction failures

### 2. Evaluation Logic Updates
Updated `evaluate_schema_inference()` to work with schema-generator format:

#### Column Extraction
- Extracts column names from `schema.tables[table_name].fields`
- Iterates through all tables to collect field names
- Compares against expected columns for accuracy scoring

#### Flattening Detection
- Analyzes `schema.transformations.csv.array_handling` setting
- Detects "multiple_rows" handling as indication of flattening
- Maps schema content to required flattening operations (items, shipping_address)

#### Confidence Scoring
- Uses `schema.confidence.overall` as proxy for query intent support
- Leverages schema-generator's built-in confidence assessment
- Converts confidence (0-1) to evaluation score (0-5)

### 3. Enhanced Debugging Output
Added detailed schema information display:
- Extracted columns from schema-generator output
- Detected flattening operations
- Array handling strategy
- Overall confidence score
- Transformation guidance details

## Schema-Generator Format Compatibility

The evaluation works with the existing schema-generator format:

```json
{
  "entities": [...],
  "tables": {
    "table_name": {
      "fields": {
        "field_name": {
          "type": "string|integer|float|boolean|datetime|date|json",
          "nullable": true|false,
          "description": "Field description",
          "csv_format": "string representation for CSV",
          "bigquery_type": "BigQuery-specific type"
        }
      }
    }
  },
  "transformations": {
    "csv": {
      "flattening_strategy": "prefix|separate_columns|json_string",
      "array_handling": "comma_separated|multiple_rows|json_string"
    }
  },
  "confidence": {
    "overall": 0.0-1.0,
    "entity_detection": 0.0-1.0,
    "type_inference": 0.0-1.0,
    "relationships": 0.0-1.0
  }
}
```

## Evaluation Process

### 1. Schema Extraction
- Searches for JSON blocks in agent response
- Validates schema-generator format (entities + tables)
- Returns structured schema data or error details

### 2. Column Analysis
- Extracts field names from all tables
- Compares against expected columns for query
- Calculates column accuracy score (0-5)

### 3. Flattening Analysis
- Checks `array_handling` setting for "multiple_rows"
- Maps schema content to required flattening operations
- Validates proper nested structure handling

### 4. Intent Support
- Uses schema confidence as proxy for query support
- Leverages schema-generator's built-in assessment
- Provides intent support score (0-5)

## Benefits of This Approach

### 1. No Breaking Changes
- Maintains existing schema-generator format
- Preserves sub-agent functionality
- Compatible with existing workflows

### 2. Accurate Extraction
- Structured JSON parsing (vs. text pattern matching)
- Reliable column detection from table fields
- Precise flattening operation detection

### 3. Rich Debugging
- Shows extracted schema details
- Displays confidence scores
- Provides transformation guidance

### 4. Sub-Agent Integration
- Works with existing Claude Code sub-agent system
- Leverages schema-generator's expertise
- Maintains separation of concerns

## Example Usage

### Agent Response
```
Use the schema-generator to analyze JSON files and create abstract schemas...

```json
{
  "entities": [...],
  "tables": {
    "order_items": {
      "fields": {
        "product_id": {"type": "string", ...},
        "quantity": {"type": "integer", ...}
      }
    }
  },
  "transformations": {
    "csv": {"array_handling": "multiple_rows"}
  },
  "confidence": {"overall": 0.85}
}
```
```

### Evaluation Output
```
📊 SCHEMA INFERENCE EVALUATION:
- Schema extraction: ✓ SUCCESS
- Extracted columns: ['product_id', 'quantity', 'product_name', 'category']
- Flattening operations: ['items']
- Array handling: multiple_rows
- Confidence: 0.85
- Column accuracy: 5.0/5
- Flattening correctness: 5.0/5
- Query intent support: 4.25/5
- Overall: ✓ PASS
```

## Files Modified

- `tests/eval.py`: Added schema-generator extraction and evaluation logic
- `test_schema_generator_eval.py`: Created test script demonstrating integration
- `SCHEMA_GENERATOR_INTEGRATION.md`: This documentation

This approach successfully integrates with the existing schema-generator sub-agent while providing accurate and detailed evaluation of JSON to CSV schema inference capabilities.
