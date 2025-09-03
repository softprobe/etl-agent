#!/usr/bin/env python3
"""
Integration tests for the Agentic ETL Engineer backend
Tests the actual FastAPI endpoints with real JSON files
"""

import asyncio
import json
import requests
import websocket
import threading
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
WEBSOCKET_URL = "ws://localhost:8000/ws/chat"

def create_sample_json_files():
    """Create sample JSON files for testing"""
    
    # Sample e-commerce data
    ecommerce_data = [
        {
            "user_id": 123,
            "name": "John Doe",
            "email": "john@example.com",
            "orders": [
                {
                    "order_id": "ord_001",
                    "total": 99.99,
                    "items": [
                        {"product": "Laptop", "price": 899.99, "qty": 1},
                        {"product": "Mouse", "price": 29.99, "qty": 1}
                    ],
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ],
            "profile": {
                "age": 35,
                "city": "San Francisco",
                "preferences": ["electronics", "gadgets"]
            }
        },
        {
            "user_id": 124,
            "name": "Jane Smith", 
            "email": "jane@example.com",
            "orders": [
                {
                    "order_id": "ord_002",
                    "total": 149.50,
                    "items": [
                        {"product": "Keyboard", "price": 149.50, "qty": 1}
                    ],
                    "created_at": "2024-01-16T14:20:00Z"
                }
            ],
            "profile": {
                "age": 28,
                "city": "New York",
                "preferences": ["tech", "productivity"]
            }
        }
    ]
    
    # Sample IoT sensor data
    sensor_data = [
        {
            "device_id": "sensor_001",
            "timestamp": "2024-01-15T10:00:00Z",
            "location": {"lat": 37.7749, "lng": -122.4194, "building": "Office A"},
            "readings": {
                "temperature": 22.5,
                "humidity": 45.2,
                "pressure": 1013.25
            },
            "metadata": {
                "firmware_version": "1.2.3",
                "battery_level": 0.85
            }
        },
        {
            "device_id": "sensor_002", 
            "timestamp": "2024-01-15T10:05:00Z",
            "location": {"lat": 37.7849, "lng": -122.4094, "building": "Office B"},
            "readings": {
                "temperature": 23.1,
                "humidity": 42.8,
                "pressure": 1012.80
            },
            "metadata": {
                "firmware_version": "1.2.3",
                "battery_level": 0.72
            }
        }
    ]
    
    # Write sample files
    with open("ecommerce_sample.json", "w") as f:
        json.dump(ecommerce_data, f, indent=2)
        
    with open("sensor_data_sample.json", "w") as f:
        json.dump(sensor_data, f, indent=2)
    
    print("✓ Created sample JSON files: ecommerce_sample.json, sensor_data_sample.json")

def test_file_upload():
    """Test file upload endpoint"""
    print("\n=== Testing File Upload ===")
    
    files = [
        ("files", ("ecommerce_sample.json", open("ecommerce_sample.json", "rb"), "application/json")),
        ("files", ("sensor_data_sample.json", open("sensor_data_sample.json", "rb"), "application/json"))
    ]
    
    response = requests.post(f"{BASE_URL}/api/upload", files=files)
    
    # Close files
    for _, (_, file_obj, _) in files:
        file_obj.close()
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["files"]) == 2
    print("✓ File upload test passed")

def test_websocket_chat():
    """Test WebSocket chat functionality"""
    print("\n=== Testing WebSocket Chat ===")
    
    messages_received = []
    connection_ready = threading.Event()
    
    def on_message(ws, message):
        print(f"Received: {message}")
        messages_received.append(json.loads(message))
    
    def on_open(ws):
        print("WebSocket connection opened")
        connection_ready.set()
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    # Start WebSocket connection
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    # Run WebSocket in separate thread
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    # Wait for connection
    if not connection_ready.wait(timeout=5):
        raise Exception("WebSocket connection timeout")
    
    # Send test message
    test_message = "Can you analyze the uploaded JSON files and suggest BigQuery schemas? Write the DDL code for the schemas into a file called ddl.sql"
    print(f"Sending: {test_message}")
    ws.send(test_message)
    
    # Wait for responses
    time.sleep(100)  # Give Claude time to analyze and respond
    
    ws.close()
    
    print(f"✓ WebSocket chat test completed. Received {len(messages_received)} messages")
    for msg in messages_received:
        print(f"  - {msg.get('type', 'unknown')}: {msg.get('content', '')}...")

def test_ddl_generation():
    """Test DDL generation endpoint"""
    print("\n=== Testing DDL Generation ===")
    
    request_data = {
        "json_files": ["ecommerce_sample.json", "sensor_data_sample.json"],
        "table_name": "ecommerce_data",
        "dataset_id": "test_dataset", 
        "user_requirements": "Create normalized tables for user data and orders"
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-ddl", json=request_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Generated DDL preview: {data.get('ddl', '')}...")
        print("✓ DDL generation test passed")
    else:
        print(f"Error: {response.text}")

def test_etl_generation():
    """Test ETL code generation endpoint"""
    print("\n=== Testing ETL Generation ===")
    
    request_data = {
        "json_files": ["ecommerce_sample.json", "sensor_data_sample.json"],
        "table_name": "ecommerce_data", 
        "dataset_id": "test_dataset",
        "user_requirements": "Create Python ETL code to load data into BigQuery"
    }
    
    response = requests.post(f"{BASE_URL}/api/generate-etl", json=request_data)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Generated ETL code preview: {data.get('etl_code', '')}...")
        print("✓ ETL generation test passed")
    else:
        print(f"Error: {response.text}")

def test_health_check():
    """Test health check endpoint"""
    print("\n=== Testing Health Check ===")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check test passed")

def run_all_tests():
    """Run all integration tests"""
    print("🚀 Starting Agentic ETL Engineer Integration Tests")
    print(f"Testing against: {BASE_URL}")
    
    try:
        # Setup
        create_sample_json_files()
        
        # Basic tests
        test_health_check()
        test_file_upload()
        
        # AI-powered tests (require Claude API key)
        print("\n⚠️  The following tests require ANTHROPIC_API_KEY environment variable:")
        try:
            test_websocket_chat()
            test_ddl_generation() 
            test_etl_generation()
        except Exception as e:
            print(f"❌ AI tests failed (likely missing API key): {e}")
        
        print("\n🎉 Integration tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

if __name__ == "__main__":
    print("Make sure to start the server first:")
    print("  cd /Users/bill/src/etl")
    print("  uv run python -m app.main")
    print("")
    
    input("Press Enter when the server is running on http://localhost:8000...")
    run_all_tests()