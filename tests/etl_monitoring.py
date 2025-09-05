"""
Real-time Monitoring and Debugging System for Agentic ETL Processes
Provides observability into agent decisions, file operations, and pipeline execution.
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass 
class FileEvent:
    """Represents a file system event."""
    timestamp: float
    event_type: str  # created, modified, deleted, moved
    file_path: str
    file_size: Optional[int] = None
    agent_context: Optional[str] = None


@dataclass
class PerformanceMetric:
    """Represents a performance measurement."""
    timestamp: float
    metric_name: str
    value: float
    unit: str
    context: Dict[str, Any]


@dataclass
class ValidationResult:
    """Represents a validation check result."""
    timestamp: float
    validator_name: str
    file_path: str
    passed: bool
    score: float
    issues: List[str]
    details: Dict[str, Any]


class ETLFileWatcher(FileSystemEventHandler):
    """Monitors file system events in the ETL workspace."""
    
    def __init__(self, callback: Callable[[FileEvent], None]):
        self.callback = callback
        
    def on_created(self, event):
        if not event.is_directory:
            file_event = FileEvent(
                timestamp=time.time(),
                event_type="created",
                file_path=event.src_path,
                file_size=Path(event.src_path).stat().st_size if Path(event.src_path).exists() else None
            )
            self.callback(file_event)
            
    def on_modified(self, event):
        if not event.is_directory:
            file_event = FileEvent(
                timestamp=time.time(),
                event_type="modified", 
                file_path=event.src_path,
                file_size=Path(event.src_path).stat().st_size if Path(event.src_path).exists() else None
            )
            self.callback(file_event)
    
    def on_deleted(self, event):
        if not event.is_directory:
            file_event = FileEvent(
                timestamp=time.time(),
                event_type="deleted",
                file_path=event.src_path
            )
            self.callback(file_event)


class RealTimeETLMonitor:
    """Real-time monitoring system for agentic ETL processes."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.file_events: List[FileEvent] = []
        self.performance_metrics: List[PerformanceMetric] = []
        self.validation_results: List[ValidationResult] = []
        self.observer = Observer()
        self.monitoring_active = False
        
        # File validators
        self.validators = {
            "schema": self._validate_schema_file,
            "etl": self._validate_etl_script,
            "csv": self._validate_csv_output,
            "ddl": self._validate_ddl_file
        }
        
    def start_monitoring(self):
        """Start real-time monitoring of the workspace."""
        print(f"🔍 Starting real-time monitoring of {self.workspace_dir}")
        
        # Setup file watcher
        event_handler = ETLFileWatcher(self._handle_file_event)
        self.observer.schedule(event_handler, str(self.workspace_dir), recursive=True)
        self.observer.start()
        self.monitoring_active = True
        
        print("✓ File system monitoring active")
        
    def stop_monitoring(self):
        """Stop monitoring."""
        if self.monitoring_active:
            self.observer.stop()
            self.observer.join()
            self.monitoring_active = False
            print("⏹️ Monitoring stopped")
            
    def _handle_file_event(self, event: FileEvent):
        """Handle a file system event."""
        self.file_events.append(event)
        
        # Real-time logging
        rel_path = Path(event.file_path).relative_to(self.workspace_dir)
        logger.info(f"📁 {event.event_type.upper()}: {rel_path} ({event.file_size} bytes)")
        
        # Trigger validation for relevant files
        if event.event_type in ["created", "modified"]:
            self._auto_validate_file(event.file_path)
            
    def _auto_validate_file(self, file_path: str):
        """Automatically validate a file based on its type."""
        path = Path(file_path)
        
        # Determine file type and run appropriate validator
        if path.parent.name == "schema" and path.suffix == ".json":
            self._run_validator("schema", file_path)
        elif path.parent.name == "etl" and path.suffix == ".py":
            self._run_validator("etl", file_path)
        elif path.parent.name == "output" and path.suffix == ".csv":
            self._run_validator("csv", file_path)
        elif path.parent.name == "ddl" and path.suffix == ".sql":
            self._run_validator("ddl", file_path)
            
    def _run_validator(self, validator_type: str, file_path: str):
        """Run a specific validator on a file."""
        try:
            validator_func = self.validators.get(validator_type)
            if validator_func:
                result = validator_func(file_path)
                self.validation_results.append(result)
                
                # Real-time feedback
                status = "✅ PASS" if result.passed else "❌ FAIL"
                rel_path = Path(file_path).relative_to(self.workspace_dir)
                logger.info(f"🔍 {validator_type.upper()} validation: {rel_path} - {status} ({result.score:.1f}/5)")
                
                if not result.passed and result.issues:
                    for issue in result.issues:
                        logger.warning(f"  ⚠️ {issue}")
                        
        except Exception as e:
            logger.error(f"Validation failed for {file_path}: {str(e)}")
            
    def _validate_schema_file(self, file_path: str) -> ValidationResult:
        """Validate a schema JSON file."""
        issues = []
        score = 5.0
        details = {}
        
        try:
            with open(file_path) as f:
                schema = json.load(f)
            
            # Check required schema-generator format
            if "entities" not in schema:
                issues.append("Missing 'entities' section")
                score -= 2.0
                
            if "tables" not in schema:
                issues.append("Missing 'tables' section")
                score -= 2.0
                
            if "transformations" not in schema:
                issues.append("Missing 'transformations' section") 
                score -= 1.0
                
            # Count fields and validate structure
            field_count = 0
            if "tables" in schema:
                for table_name, table_data in schema["tables"].items():
                    if "fields" in table_data:
                        field_count += len(table_data["fields"])
                        
                        # Validate field definitions
                        for field_name, field_data in table_data["fields"].items():
                            if "type" not in field_data:
                                issues.append(f"Field {field_name} missing type")
                                score -= 0.2
                                
            details = {
                "total_fields": field_count,
                "entities_count": len(schema.get("entities", [])),
                "tables_count": len(schema.get("tables", {}))
            }
            
        except json.JSONDecodeError:
            issues.append("Invalid JSON format")
            score = 0.0
        except Exception as e:
            issues.append(f"Validation error: {str(e)}")
            score = 0.0
            
        return ValidationResult(
            timestamp=time.time(),
            validator_name="schema_validator",
            file_path=file_path,
            passed=score >= 3.0,
            score=max(0.0, score),
            issues=issues,
            details=details
        )
        
    def _validate_etl_script(self, file_path: str) -> ValidationResult:
        """Validate an ETL Python script."""
        issues = []
        score = 5.0
        details = {}
        
        try:
            with open(file_path) as f:
                code = f.read()
                
            # Check for essential components
            if "import pandas" not in code and "import csv" not in code:
                issues.append("Missing data processing imports")
                score -= 1.0
                
            if "def " not in code:
                issues.append("No function definitions found")
                score -= 1.0
                
            if "with open" not in code and "pd.read_" not in code:
                issues.append("No file reading operations found")
                score -= 1.0
                
            if ".to_csv" not in code and "csv.writer" not in code:
                issues.append("No CSV output generation found")
                score -= 1.0
                
            # Check for error handling
            if "try:" not in code or "except:" not in code:
                issues.append("Missing error handling")
                score -= 0.5
                
            # Basic syntax check
            try:
                compile(code, file_path, 'exec')
            except SyntaxError as e:
                issues.append(f"Syntax error: {str(e)}")
                score = 0.0
                
            details = {
                "lines_of_code": len(code.splitlines()),
                "has_main_function": "if __name__" in code,
                "import_count": code.count("import ")
            }
            
        except Exception as e:
            issues.append(f"Script validation error: {str(e)}")
            score = 0.0
            
        return ValidationResult(
            timestamp=time.time(),
            validator_name="etl_validator", 
            file_path=file_path,
            passed=score >= 3.0,
            score=max(0.0, score),
            issues=issues,
            details=details
        )
        
    def _validate_csv_output(self, file_path: str) -> ValidationResult:
        """Validate a CSV output file."""
        issues = []
        score = 5.0
        details = {}
        
        try:
            import pandas as pd
            
            df = pd.read_csv(file_path)
            
            # Basic structure checks
            if df.empty:
                issues.append("CSV file is empty")
                score = 0.0
            else:
                # Check for reasonable data
                if len(df.columns) < 2:
                    issues.append("Too few columns (less than 2)")
                    score -= 1.0
                    
                if df.shape[0] < 1:
                    issues.append("No data rows")
                    score -= 2.0
                    
                # Check for data quality issues
                null_percentage = df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
                if null_percentage > 0.5:
                    issues.append(f"High null percentage: {null_percentage:.1%}")
                    score -= 1.0
                    
                # Check column names
                if any(col.strip() != col for col in df.columns):
                    issues.append("Column names have leading/trailing spaces")
                    score -= 0.5
                    
            details = {
                "rows": df.shape[0] if not df.empty else 0,
                "columns": len(df.columns),
                "column_names": list(df.columns),
                "null_percentage": null_percentage if not df.empty else 0.0
            }
            
        except Exception as e:
            issues.append(f"CSV validation error: {str(e)}")
            score = 0.0
            
        return ValidationResult(
            timestamp=time.time(),
            validator_name="csv_validator",
            file_path=file_path,
            passed=score >= 3.0,
            score=max(0.0, score),
            issues=issues,
            details=details
        )
        
    def _validate_ddl_file(self, file_path: str) -> ValidationResult:
        """Validate a DDL SQL file."""
        issues = []
        score = 5.0
        details = {}
        
        try:
            with open(file_path) as f:
                sql = f.read()
                
            sql_upper = sql.upper()
            
            # Check for basic DDL structure
            if "CREATE TABLE" not in sql_upper:
                issues.append("Missing CREATE TABLE statement")
                score -= 2.0
                
            if "(" not in sql or ")" not in sql:
                issues.append("Missing column definitions")
                score -= 2.0
                
            # Check for BigQuery-specific elements
            bigquery_indicators = ["STRING", "INTEGER", "FLOAT64", "TIMESTAMP", "DATASET"]
            if not any(indicator in sql_upper for indicator in bigquery_indicators):
                issues.append("Doesn't appear to be BigQuery-specific DDL")
                score -= 1.0
                
            # Count column definitions
            column_count = sql.count(",") + 1 if "CREATE TABLE" in sql_upper else 0
            if column_count < 2:
                issues.append("Too few columns defined")
                score -= 1.0
                
            details = {
                "estimated_columns": column_count,
                "has_primary_key": "PRIMARY KEY" in sql_upper,
                "has_constraints": "NOT NULL" in sql_upper,
                "is_bigquery": any(ind in sql_upper for ind in bigquery_indicators)
            }
            
        except Exception as e:
            issues.append(f"DDL validation error: {str(e)}")
            score = 0.0
            
        return ValidationResult(
            timestamp=time.time(),
            validator_name="ddl_validator",
            file_path=file_path,
            passed=score >= 3.0,
            score=max(0.0, score),
            issues=issues,
            details=details
        )
        
    def record_performance_metric(self, metric_name: str, value: float, unit: str, context: Dict = None):
        """Record a performance metric."""
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_name=metric_name,
            value=value,
            unit=unit,
            context=context or {}
        )
        self.performance_metrics.append(metric)
        logger.info(f"📊 {metric_name}: {value} {unit}")
        
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate a comprehensive monitoring report."""
        
        # Analyze file events
        event_summary = {}
        for event in self.file_events:
            event_type = event.event_type
            event_summary[event_type] = event_summary.get(event_type, 0) + 1
            
        # Analyze validation results
        validation_summary = {}
        for result in self.validation_results:
            validator = result.validator_name
            if validator not in validation_summary:
                validation_summary[validator] = {"passed": 0, "failed": 0, "avg_score": 0.0}
                
            if result.passed:
                validation_summary[validator]["passed"] += 1
            else:
                validation_summary[validator]["failed"] += 1
                
        # Calculate average scores
        for validator in validation_summary:
            relevant_results = [r for r in self.validation_results if r.validator_name == validator]
            if relevant_results:
                avg_score = sum(r.score for r in relevant_results) / len(relevant_results)
                validation_summary[validator]["avg_score"] = avg_score
                
        # Performance metrics summary
        performance_summary = {}
        for metric in self.performance_metrics:
            name = metric.metric_name
            if name not in performance_summary:
                performance_summary[name] = {"values": [], "unit": metric.unit}
            performance_summary[name]["values"].append(metric.value)
            
        for name in performance_summary:
            values = performance_summary[name]["values"]
            performance_summary[name].update({
                "count": len(values),
                "avg": sum(values) / len(values),
                "min": min(values),
                "max": max(values)
            })
            
        return {
            "monitoring_duration": time.time() - (self.file_events[0].timestamp if self.file_events else time.time()),
            "file_events": {
                "total": len(self.file_events),
                "by_type": event_summary
            },
            "validation_results": {
                "total": len(self.validation_results),
                "by_validator": validation_summary
            },
            "performance_metrics": performance_summary,
            "latest_files": self._get_latest_files()
        }
        
    def _get_latest_files(self) -> Dict[str, List[str]]:
        """Get the most recently created/modified files by type."""
        latest_files = {
            "schema": [],
            "etl": [], 
            "csv": [],
            "ddl": []
        }
        
        for event in sorted(self.file_events, key=lambda x: x.timestamp, reverse=True)[:20]:
            path = Path(event.file_path)
            file_type = None
            
            if path.parent.name == "schema" and path.suffix == ".json":
                file_type = "schema"
            elif path.parent.name == "etl" and path.suffix == ".py":
                file_type = "etl"
            elif path.parent.name == "output" and path.suffix == ".csv":
                file_type = "csv"
            elif path.parent.name == "ddl" and path.suffix == ".sql":
                file_type = "ddl"
                
            if file_type and event.file_path not in latest_files[file_type]:
                latest_files[file_type].append(event.file_path)
                
        return latest_files
        
    def print_live_dashboard(self):
        """Print a live monitoring dashboard."""
        print("\n" + "=" * 60)
        print("🔍 REAL-TIME ETL MONITORING DASHBOARD")
        print("=" * 60)
        
        # File events summary
        if self.file_events:
            recent_events = self.file_events[-5:]  # Last 5 events
            print("\n📁 RECENT FILE EVENTS:")
            for event in recent_events:
                rel_path = Path(event.file_path).relative_to(self.workspace_dir)
                timestamp = datetime.fromtimestamp(event.timestamp).strftime("%H:%M:%S")
                print(f"  {timestamp} - {event.event_type.upper()}: {rel_path}")
                
        # Validation results
        if self.validation_results:
            recent_validations = self.validation_results[-3:]  # Last 3 validations
            print("\n🔍 RECENT VALIDATIONS:")
            for result in recent_validations:
                rel_path = Path(result.file_path).relative_to(self.workspace_dir)
                status = "✅ PASS" if result.passed else "❌ FAIL"
                print(f"  {result.validator_name}: {rel_path} - {status} ({result.score:.1f}/5)")
                
        # Performance metrics
        if self.performance_metrics:
            recent_metrics = self.performance_metrics[-3:]  # Last 3 metrics  
            print("\n📊 RECENT PERFORMANCE METRICS:")
            for metric in recent_metrics:
                print(f"  {metric.metric_name}: {metric.value} {metric.unit}")
                
        print("=" * 60)


class ETLPerformanceProfiler:
    """Performance profiling for ETL processes."""
    
    def __init__(self, monitor: RealTimeETLMonitor):
        self.monitor = monitor
        self.start_times = {}
        
    def start_timer(self, operation_name: str):
        """Start timing an operation."""
        self.start_times[operation_name] = time.time()
        
    def end_timer(self, operation_name: str, context: Dict = None):
        """End timing an operation and record the metric."""
        if operation_name in self.start_times:
            duration = time.time() - self.start_times[operation_name]
            self.monitor.record_performance_metric(
                f"{operation_name}_duration",
                duration,
                "seconds",
                context
            )
            del self.start_times[operation_name]
            return duration
        return None