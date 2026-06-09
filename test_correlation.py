"""
==========================================================
MetricGuard — Correlation Engine Tests (test_correlation.py)
==========================================================

Phase 10: Metric-Log Correlation Engine

Tests covering:
  1. Cause Mapper — keyword matching, no-match, confidence levels
  2. Correlation Service — scoring algorithm, cause inference
  3. API Endpoints — GET/POST correlation routes

Usage:
    .venv\\Scripts\\python -m pytest test_correlation.py -v
"""

import sys
import os
from datetime import datetime, timedelta

# Add workspace root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ==========================================================
# TEST 1: Cause Mapper
# ==========================================================

class TestCauseMapper:
    """Tests for backend.utils.cause_mapper.infer_root_cause()"""

    def test_database_timeout_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Database timeout while processing payment")
        assert result["cause"] == "Database Bottleneck"
        assert result["confidence"] == 0.9  # multi-word → high confidence

    def test_connection_refused_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Connection refused from 192.168.1.100:3306")
        assert result["cause"] == "Database Connectivity Issue"
        assert result["confidence"] == 0.9

    def test_out_of_memory_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Out of memory: Java heap space exceeded 2048MB limit")
        assert result["cause"] == "Memory Exhaustion"
        assert result["confidence"] == 0.9

    def test_disk_full_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Data directory full: cannot write to /var/lib/mysql/")
        assert result["cause"] == "Disk Saturation"
        assert result["confidence"] == 0.9

    def test_service_unavailable_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("HTTP 503 Service Unavailable: all upstream servers are down")
        assert result["cause"] == "Service Failure"
        assert result["confidence"] == 0.9

    def test_single_keyword_deadlock(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Deadlock found when trying to get lock")
        assert result["cause"] == "Database Deadlock"
        assert result["confidence"] == 0.7  # single-word → medium confidence

    def test_no_match_returns_unknown(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Application started successfully on port 8080")
        assert result["cause"] == "Unknown"
        assert result["confidence"] == 0.0

    def test_empty_message(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("")
        assert result["cause"] == "Unknown"
        assert result["confidence"] == 0.0

    def test_case_insensitive_matching(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("DATABASE TIMEOUT on primary cluster")
        assert result["cause"] == "Database Bottleneck"

    def test_gc_overhead_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("GC overhead limit exceeded in production JVM")
        assert result["cause"] == "JVM Memory Pressure"
        assert result["confidence"] == 0.9

    def test_cpu_throttling_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("CPU throttling detected on container-01")
        assert result["cause"] == "CPU Saturation"
        assert result["confidence"] == 0.9

    def test_network_timeout_match(self):
        from backend.utils.cause_mapper import infer_root_cause
        result = infer_root_cause("Network timeout connecting to payment gateway")
        assert result["cause"] == "Network Latency Issue"
        assert result["confidence"] == 0.9


# ==========================================================
# TEST 2: Correlation Service — Scoring Algorithm
# ==========================================================

class TestCorrelationScoring:
    """Tests for CorrelationService.calculate_score() using mock objects."""

    class MockAnomaly:
        """Minimal mock for the Anomaly ORM model."""
        def __init__(self, id, timestamp, severity, root_cause="CPU Usage"):
            self.id = id
            self.timestamp = timestamp
            self.severity = severity
            self.root_cause = root_cause

    class MockLog:
        """Minimal mock for the Log ORM model."""
        def __init__(self, id, timestamp, level, message, service_name="test-service"):
            self.id = id
            self.timestamp = timestamp
            self.level = level
            self.message = message
            self.service_name = service_name

    def _get_service(self):
        from backend.services.correlation_service import CorrelationService
        return CorrelationService()

    def test_perfect_score(self):
        """All 3 factors match → score = 1.0"""
        service = self._get_service()
        now = datetime.utcnow()
        metric = self.MockAnomaly(1, now, "warning")
        log = self.MockLog(1, now - timedelta(seconds=10), "ERROR",
                           "Database timeout while processing payment")
        # Time: within 60s → +0.4
        # Severity: ERROR maps to 'warning' → +0.2
        # Keyword: 'database timeout' → +0.4
        score = service.calculate_score(metric, log)
        assert score == 1.0

    def test_time_match_only(self):
        """Only time proximity matches."""
        service = self._get_service()
        now = datetime.utcnow()
        metric = self.MockAnomaly(1, now, "critical")  # severity mismatch
        log = self.MockLog(1, now - timedelta(seconds=30), "ERROR",
                           "Application started successfully")  # no keyword match
        # Time: within 60s → +0.4
        # Severity: critical != warning(ERROR) → +0.0
        # Keyword: no match → +0.0
        score = service.calculate_score(metric, log)
        assert score == 0.4

    def test_no_time_match(self):
        """Timestamp difference > 60 seconds → no time score."""
        service = self._get_service()
        now = datetime.utcnow()
        metric = self.MockAnomaly(1, now, "warning")
        log = self.MockLog(1, now - timedelta(seconds=120), "ERROR",
                           "Database timeout while processing payment")
        # Time: > 60s → +0.0
        # Severity: warning == warning(ERROR) → +0.2
        # Keyword: 'database timeout' → +0.4
        score = service.calculate_score(metric, log)
        assert score == 0.6

    def test_severity_match_critical(self):
        """CRITICAL log maps to 'critical' anomaly severity."""
        service = self._get_service()
        now = datetime.utcnow()
        metric = self.MockAnomaly(1, now, "critical")
        log = self.MockLog(1, now - timedelta(seconds=5), "CRITICAL",
                           "Some normal message")
        # Time: within 60s → +0.4
        # Severity: critical == critical(CRITICAL) → +0.2
        # Keyword: no match → +0.0
        score = service.calculate_score(metric, log)
        assert score == 0.6

    def test_keyword_match_only(self):
        """Only keyword matches (time out of range, severity mismatch)."""
        service = self._get_service()
        now = datetime.utcnow()
        metric = self.MockAnomaly(1, now, "low")
        log = self.MockLog(1, now - timedelta(seconds=120), "ERROR",
                           "Out of memory: heap space exceeded")
        # Time: > 60s → +0.0
        # Severity: low != warning(ERROR) → +0.0
        # Keyword: 'out of memory' → +0.4
        score = service.calculate_score(metric, log)
        assert score == 0.4

    def test_zero_score(self):
        """Nothing matches → score = 0.0"""
        service = self._get_service()
        now = datetime.utcnow()
        metric = self.MockAnomaly(1, now, "critical")
        log = self.MockLog(1, now - timedelta(seconds=120), "ERROR",
                           "Application started successfully on port 8080")
        score = service.calculate_score(metric, log)
        assert score == 0.0


# ==========================================================
# TEST 3: Cause Inference via Service
# ==========================================================

class TestCorrelationCauseInference:
    """Tests for CorrelationService.infer_cause()."""

    def _get_service(self):
        from backend.services.correlation_service import CorrelationService
        return CorrelationService()

    def test_infer_known_cause(self):
        service = self._get_service()
        result = service.infer_cause("Database timeout while processing payment")
        assert result["cause"] == "Database Bottleneck"
        assert result["confidence"] > 0

    def test_infer_unknown_cause(self):
        service = self._get_service()
        result = service.infer_cause("Health check endpoint responded with status=UP")
        assert result["cause"] == "Unknown"
        assert result["confidence"] == 0.0


# ==========================================================
# TEST 4: Correlation Record Creation
# ==========================================================

class TestCorrelationRecordCreation:
    """Tests for CorrelationService.create_correlation()."""

    class MockAnomaly:
        def __init__(self):
            self.id = 10
            self.timestamp = datetime(2026, 6, 1, 10, 15, 0)
            self.severity = "warning"

    class MockLog:
        def __init__(self):
            self.id = 5
            self.timestamp = datetime(2026, 6, 1, 10, 14, 45)
            self.level = "ERROR"
            self.message = "Database timeout while processing payment"
            self.service_name = "database-service"

    def test_create_correlation_record(self):
        from backend.services.correlation_service import CorrelationService
        service = CorrelationService()

        metric = self.MockAnomaly()
        log = self.MockLog()
        score = 0.95
        cause_info = {"cause": "Database Bottleneck", "confidence": 0.9}

        result = service.create_correlation(metric, log, score, cause_info)

        assert result["metric_anomaly_id"] == 10
        assert result["log_anomaly_id"] == 5
        assert result["correlation_score"] == 0.95
        assert result["inferred_cause"] == "Database Bottleneck"
        assert result["confidence"] == 95.0  # score * 100


# ==========================================================
# TEST 5: Pydantic Schema Validation
# ==========================================================

class TestCorrelationSchemas:
    """Tests for backend.schemas Pydantic models."""

    def test_correlation_response_schema(self):
        from backend.schemas import CorrelationResponse
        data = {
            "id": 1,
            "metric_anomaly_id": 10,
            "log_anomaly_id": 5,
            "correlation_score": 0.95,
            "inferred_cause": "Database Bottleneck",
            "confidence": 95.0,
            "created_at": datetime.now(),
        }
        response = CorrelationResponse(**data)
        assert response.metric_anomaly_id == 10
        assert response.correlation_score == 0.95

    def test_correlation_run_response_schema(self):
        from backend.schemas import CorrelationRunResponse
        response = CorrelationRunResponse(status="success", correlations_created=15)
        assert response.status == "success"
        assert response.correlations_created == 15


# ==========================================================
# TEST 6: CAUSE_MAP Completeness
# ==========================================================

class TestCauseMapCompleteness:
    """Verify all required entries exist in CAUSE_MAP."""

    def test_required_entries_present(self):
        from backend.utils.cause_mapper import CAUSE_MAP
        required_keys = [
            "database timeout",
            "connection refused",
            "out of memory",
            "disk full",
            "gc overhead",
            "cpu throttling",
            "service unavailable",
            "network timeout",
        ]
        for key in required_keys:
            assert key in CAUSE_MAP, f"Missing required CAUSE_MAP key: '{key}'"

    def test_all_values_are_strings(self):
        from backend.utils.cause_mapper import CAUSE_MAP
        for key, value in CAUSE_MAP.items():
            assert isinstance(value, str), f"CAUSE_MAP['{key}'] is not a string"
            assert len(value) > 0, f"CAUSE_MAP['{key}'] is empty"
