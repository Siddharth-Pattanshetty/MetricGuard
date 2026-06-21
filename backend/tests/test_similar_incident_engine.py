import os
import sys
import pytest

# Ensure root of project is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.knowledge_base.similar_incident_engine import get_similar_incident_engine


class MockIncident:
    def __init__(self, incident_id, title, description, root_cause, service_name, resolution):
        self.incident_id = incident_id
        self.title = title
        self.description = description
        self.root_cause = root_cause
        self.service_name = service_name
        self.resolution = resolution


def test_similar_incident_engine_matching():
    engine = get_similar_incident_engine()

    # Create mock historical incidents
    history = [
        MockIncident("INC-001", "Out of Memory", "JVM heap memory exhausted causing datanode failure", "OOM", "datanode", "Restarted JVM with larger heap"),
        MockIncident("INC-002", "Disk Saturation", "Write capacity saturated on HDFS block storage", "Disk Full", "storage", "Expanded volume size"),
        MockIncident("INC-003", "Auth Latency", "Database connection pool timeout causing slow logins", "DB Timeout", "auth-service", "Optimized connection pool parameters")
    ]

    # Search for an OOM incident
    matches_oom = engine.find_similar_incidents(
        target_title="JVM memory leak OOM",
        target_description="Datanode jvm heap memory is fully exhausted",
        target_root_cause="OOM",
        target_service="datanode",
        historical_incidents=history
    )

    assert len(matches_oom) >= 1
    assert matches_oom[0]["incident_id"] == "INC-001"
    assert matches_oom[0]["similarity_score"] >= 0.70
    assert matches_oom[0]["resolution"] == "Restarted JVM with larger heap"

    # Search with completely unrelated fields (should return no matches due to >= 0.70 threshold)
    matches_unrelated = engine.find_similar_incidents(
        target_title="Network latency spike",
        target_description="Switch overload in datacenter rack",
        target_root_cause="Switch down",
        target_service="network",
        historical_incidents=history
    )
    assert len(matches_unrelated) == 0
