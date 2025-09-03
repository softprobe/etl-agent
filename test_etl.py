#!/usr/bin/env python3
"""
Test script for ETL pipeline - runs locally without BigQuery
"""

import json
import pandas as pd
from pathlib import Path
from etl_pipeline import BigQueryETL
import logging

# Configure logging for testing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBigQueryETL(BigQueryETL):
    """Mock ETL class for testing without actual BigQuery connection."""
    
    def __init__(self, project_id: str, dataset_id: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        # Skip BigQuery client initialization for testing
        
    def _create_dataset_if_not_exists(self):
        """Mock dataset creation."""
        logger.info(f"Mock: Dataset {self.dataset_id} would be created")
    
    def load_to_bigquery(self, table_name: str, df: pd.DataFrame, write_disposition: str = 'WRITE_TRUNCATE'):
        """Mock BigQuery load - just print DataFrame info."""
        logger.info(f"Mock BigQuery Load - Table: {table_name}")
        logger.info(f"Shape: {df.shape}")
        logger.info(f"Columns: {list(df.columns)}")
        logger.info(f"Sample data:\n{df.head()}")
        logger.info("-" * 50)
    
    def execute_ddl(self, ddl_statements):
        """Mock DDL execution."""
        for table_name, ddl in ddl_statements.items():
            logger.info(f"Mock DDL for {table_name}:")
            logger.info(ddl)
            logger.info("-" * 50)


def test_ecommerce_transformation():
    """Test ecommerce data transformation."""
    logger.info("Testing ecommerce data transformation...")
    
    # Load test data
    with open('ecommerce_sample.json', 'r') as f:
        test_data = json.load(f)
    
    # Initialize mock ETL
    etl = MockBigQueryETL('test-project', 'test_dataset')
    
    # Transform data
    tables = etl.transform_ecommerce_data(test_data)
    
    # Validate transformations
    assert 'users' in tables
    assert 'orders' in tables
    assert 'order_items' in tables
    
    users_df = tables['users']
    orders_df = tables['orders']
    items_df = tables['order_items']
    
    # Basic validations
    assert len(users_df) == 2  # 2 users in sample
    assert len(orders_df) == 2  # 2 orders total
    assert len(items_df) == 3   # 3 items total
    
    # Check required columns
    assert 'user_id' in users_df.columns
    assert 'name' in users_df.columns
    assert 'email' in users_df.columns
    
    assert 'order_id' in orders_df.columns
    assert 'user_id' in orders_df.columns
    assert 'total' in orders_df.columns
    
    assert 'order_id' in items_df.columns
    assert 'product' in items_df.columns
    assert 'price' in items_df.columns
    
    logger.info("✅ Ecommerce transformation test passed!")
    
    return tables


def test_sensor_transformation():
    """Test sensor data transformation."""
    logger.info("Testing sensor data transformation...")
    
    # Load test data
    with open('sensor_data_sample.json', 'r') as f:
        test_data = json.load(f)
    
    # Initialize mock ETL
    etl = MockBigQueryETL('test-project', 'test_dataset')
    
    # Transform data
    tables = etl.transform_sensor_data(test_data)
    
    # Validate transformations
    assert 'sensor_readings' in tables
    
    readings_df = tables['sensor_readings']
    
    # Basic validations
    assert len(readings_df) == 2  # 2 sensor readings in sample
    
    # Check required columns
    required_cols = ['device_id', 'timestamp', 'latitude', 'longitude', 
                    'temperature', 'humidity', 'pressure', 'battery_level']
    
    for col in required_cols:
        assert col in readings_df.columns, f"Missing column: {col}"
    
    # Check data types
    assert readings_df['temperature'].dtype in ['float64', 'Float64']
    assert readings_df['humidity'].dtype in ['float64', 'Float64']
    assert readings_df['battery_level'].dtype in ['float64', 'Float64']
    
    logger.info("✅ Sensor transformation test passed!")
    
    return tables


def test_ddl_generation():
    """Test DDL statement generation."""
    logger.info("Testing DDL generation...")
    
    etl = MockBigQueryETL('test-project', 'test_dataset')
    
    # Test ecommerce DDL
    ecommerce_ddl = etl.create_ecommerce_tables_ddl()
    assert len(ecommerce_ddl) == 3
    assert 'users' in ecommerce_ddl
    assert 'orders' in ecommerce_ddl
    assert 'order_items' in ecommerce_ddl
    
    # Test sensor DDL
    sensor_ddl = etl.create_sensor_tables_ddl()
    assert len(sensor_ddl) == 1
    assert 'sensor_readings' in sensor_ddl
    
    logger.info("✅ DDL generation test passed!")


def main():
    """Run all tests."""
    logger.info("Starting ETL pipeline tests...")
    
    try:
        # Test transformations
        ecommerce_tables = test_ecommerce_transformation()
        sensor_tables = test_sensor_transformation()
        
        # Test DDL generation
        test_ddl_generation()
        
        # Test mock BigQuery operations
        logger.info("Testing mock BigQuery operations...")
        etl = MockBigQueryETL('test-project', 'test_dataset')
        
        # Test ecommerce pipeline
        for table_name, df in ecommerce_tables.items():
            etl.load_to_bigquery(table_name, df)
        
        # Test sensor pipeline
        for table_name, df in sensor_tables.items():
            etl.load_to_bigquery(table_name, df)
        
        logger.info("🎉 All tests passed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        raise


if __name__ == '__main__':
    main()