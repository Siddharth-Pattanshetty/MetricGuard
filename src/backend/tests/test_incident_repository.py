import os
import sys
import pytest
from datetime import datetime, timedelta

# Ensure root of project is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal, Base, engine
from backend.knowledge_base.models import IncidentHistory, RcaHistory, ResolutionHistory
from backend.knowledge_base.incident_repository import get_incident_repository


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    # No teardown needed, let database tables persist or roll back transactions


@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


def test_repository_save_and_get_incident(db_session):
    repo = get_incident_repository()
    
    # Save a new incident
    inc_hist = repo.save_incident(
        db=db_session,
        incident_id="INC-TEST-001",
        title="Test Incident Title",
        description="Test description detailed",
        service_name="payment-service",
        severity="Critical",
        status="RESOLVED",
        root_cause="Database deadlock",
        resolution="Killed long running transaction",
        recommendation="Optimize query indexes",
        impact_summary="Payment flow blocked",
        created_at=datetime.utcnow() - timedelta(hours=2),
        resolved_at=datetime.utcnow()
    )
    
    assert inc_hist is not None
    assert inc_hist.incident_id == "INC-TEST-001"
    assert inc_hist.title == "Test Incident Title"

    # Get by ID
    fetched = repo.get_incident(db_session, "INC-TEST-001")
    assert fetched is not None
    assert fetched.service_name == "payment-service"
    assert fetched.severity == "Critical"


def test_repository_update_incident(db_session):
    repo = get_incident_repository()
    
    # Create first
    repo.save_incident(
        db=db_session,
        incident_id="INC-TEST-002",
        title="Original Title",
        description="Original desc",
        service_name="auth-service",
        severity="Medium",
        status="RESOLVED",
        root_cause="Memory leak",
        resolution="Restart container",
        recommendation="None",
        impact_summary="Auth latency",
        created_at=datetime.utcnow(),
        resolved_at=datetime.utcnow()
    )

    # Update title and status
    updated = repo.update_incident(
        db=db_session,
        incident_id="INC-TEST-002",
        updates={"title": "Updated Title", "status": "CLOSED"}
    )
    assert updated is not None
    assert updated.title == "Updated Title"
    assert updated.status == "CLOSED"

    # Verify via query
    fetched = repo.get_incident(db_session, "INC-TEST-002")
    assert fetched.title == "Updated Title"
    assert fetched.status == "CLOSED"


def test_repository_get_all_and_history(db_session):
    repo = get_incident_repository()
    
    repo.save_incident(
        db=db_session,
        incident_id="INC-TEST-003",
        title="Incident 3",
        description="d3",
        service_name="s",
        severity="Low",
        status="RESOLVED",
        root_cause="r",
        resolution="res",
        recommendation="rec",
        impact_summary="i",
        created_at=datetime.utcnow(),
        resolved_at=datetime.utcnow()
    )

    all_incs = repo.get_all_incidents(db_session)
    assert len(all_incs) >= 1
    assert any(x.incident_id == "INC-TEST-003" for x in all_incs)

    hist_incs = repo.get_incident_history(db_session, limit=10)
    assert len(hist_incs) >= 1


def test_repository_save_rca_and_resolution(db_session):
    repo = get_incident_repository()
    
    rca = repo.save_rca(
        db=db_session,
        incident_id="INC-TEST-004",
        root_cause="Out of Disk Space",
        confidence=95.0
    )
    assert rca.id is not None
    assert rca.incident_id == "INC-TEST-004"
    assert rca.confidence == 95.0

    res = repo.save_resolution(
        db=db_session,
        incident_id="INC-TEST-004",
        resolution="Expanded storage volume size",
        action_taken="Ran AWS CLI command to expand disk space"
    )
    assert res.id is not None
    assert res.incident_id == "INC-TEST-004"
    assert res.resolution == "Expanded storage volume size"
