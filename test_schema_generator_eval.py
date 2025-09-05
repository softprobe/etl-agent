#!/usr/bin/env python3
"""
Test script to demonstrate schema-generator sub-agent integration with evaluation.
This script shows how the evaluator works with the schema-generator's existing format.
"""

import asyncio
import sys
from pathlib import Path

# Add tests directory to path
sys.path.append(str(Path(__file__).parent / "tests"))

from eval import JSONToCSVSchemaEvaluator

async def test_schema_generator_integration():
    """Test the schema-generator sub-agent integration with evaluation."""
    print("🚀 SCHEMA-GENERATOR INTEGRATION TEST")
    print("=" * 50)
    
    evaluator = JSONToCSVSchemaEvaluator()
    
    # Test with a sample schema-generator response
    sample_response = """
    I'll use the schema-generator to analyze your ecommerce data and create a schema for finding top products.
    
    Use the schema-generator to analyze the JSON files and create abstract schemas that work for both CSV validation and BigQuery production.
    
    ```json
    {
      "entities": [
        {
          "name": "orders",
          "type": "table",
          "primary_key": "order_id",
          "description": "E-commerce orders with customer and item information"
        },
        {
          "name": "order_items",
          "type": "table", 
          "primary_key": "order_item_id",
          "description": "Individual items within orders (flattened from items array)"
        }
      ],
      "tables": {
        "order_items": {
          "description": "Flattened order items for product analysis",
          "fields": {
            "product_id": {
              "type": "string",
              "nullable": false,
              "description": "Unique product identifier",
              "csv_format": "string",
              "bigquery_type": "STRING"
            },
            "quantity": {
              "type": "integer",
              "nullable": false,
              "description": "Number of units ordered",
              "csv_format": "integer",
              "bigquery_type": "INTEGER"
            },
            "product_name": {
              "type": "string",
              "nullable": false,
              "description": "Human-readable product name",
              "csv_format": "string",
              "bigquery_type": "STRING"
            },
            "category": {
              "type": "string",
              "nullable": false,
              "description": "Product category for grouping",
              "csv_format": "string",
              "bigquery_type": "STRING"
            },
            "order_id": {
              "type": "string",
              "nullable": false,
              "description": "Reference to parent order",
              "csv_format": "string",
              "bigquery_type": "STRING"
            }
          },
          "relationships": [
            {
              "type": "foreign_key",
              "field": "order_id",
              "references": "orders.order_id"
            }
          ]
        }
      },
      "transformations": {
        "csv": {
          "flattening_strategy": "multiple_rows",
          "array_handling": "multiple_rows",
          "null_representation": "empty"
        },
        "bigquery": {
          "nested_handling": "flatten",
          "partition_recommendations": ["order_date"],
          "clustering_recommendations": ["product_id", "category"]
        }
      },
      "confidence": {
        "overall": 0.85,
        "entity_detection": 0.90,
        "type_inference": 0.80,
        "relationships": 0.85
      }
    }
    ```
    
    This schema flattens the items array into individual rows, making it perfect for product-level analysis and aggregation.
    """
    
    expected_columns = ["product_id", "quantity", "product_name", "category"]
    required_flattening = ["items"]
    analytical_intent = "aggregation_by_product"
    
    evaluation = evaluator.evaluate_schema_inference(
        sample_response, 
        expected_columns, 
        required_flattening, 
        analytical_intent
    )
    
    print("📊 EVALUATION RESULTS:")
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
    print(f"- Overall score: {evaluation['overall_score']:.1f}/5")
    print(f"- Pass: {'✓' if evaluation['overall_pass'] else '✗'}")
    
    if evaluation['issues']:
        print(f"Issues: {evaluation['issues']}")
    
    print("\n" + "=" * 50)
    print("This demonstrates how the evaluator now:")
    print("1. Extracts schemas from schema-generator sub-agent output")
    print("2. Parses the existing schema-generator format (entities, tables, transformations)")
    print("3. Validates column presence from table fields")
    print("4. Checks flattening operations from transformation settings")
    print("5. Uses confidence scores for intent evaluation")
    print("6. Provides detailed debugging information")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(test_schema_generator_integration())
