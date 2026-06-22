import os
import sys
from datetime import datetime, timedelta, timezone
import random

# Ensure root of project is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, Base, engine
from backend.services.incident_service import get_incident_service
from backend.knowledge_base.knowledge_service import get_knowledge_service
from app.models import Metric, Anomaly, Log
from backend.models.correlation import Correlation

def seed_database():
    print("==========================================")
    print("🌱 MetricGuard Demo Data Seeder")
    print("==========================================")
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        incident_service = get_incident_service()
        knowledge_service = get_knowledge_service()
        
        # Check if already seeded
        existing = db.query(Metric).count()
        if existing > 100:
            print(f"Database already has {existing} metrics. Skipping seed to prevent bloat.")
            return
 
        print("Generating historical incidents...")
        
        past_issues = [
            ("Disk Full on DataNode", "datanode", "High disk usage detected exceeding 95% threshold."),
            ("JVM Garbage Collection Pause", "namenode", "Long GC pause detected causing timeout."),
            ("Network Partition", "client", "Loss of heartbeat from client node."),
            ("High Memory Consumption", "storage", "OOM Killer terminated background worker."),
            ("Database Connection Timeout", "storage", "TiDB cluster unresponsive for 30s.")
        ]
        
        for i, (cause, service, log_msg) in enumerate(past_issues):
            print(f"  -> Seeding Incident: {cause}")
            # Past timestamp
            ts = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=5 - i, hours=random.randint(1, 10))
            
            # 1. Metric
            metric = Metric(
                timestamp=ts,
                cpu_usage=random.uniform(70.0, 99.0),
                memory_usage=random.uniform(80.0, 99.0),
                disk_usage=random.uniform(50.0, 99.0)
            )
            db.add(metric)
            db.flush()
            
            # 2. Anomaly
            anomaly = Anomaly(
                timestamp=ts,
                anomaly_score=random.uniform(0.85, 0.99),
                root_cause=cause,
                severity="critical",
                detected_by="AI Engine",
                metric_id=metric.id
            )
            db.add(anomaly)
            
            # 3. Log
            log_entry = Log(
                timestamp=ts,
                level="ERROR",
                service_name=service,
                message=log_msg
            )
            db.add(log_entry)
            db.flush()
            
            # 4. Correlation
            corr = Correlation(
                metric_anomaly_id=anomaly.id,
                log_anomaly_id=log_entry.id,
                correlation_score=random.uniform(0.90, 0.99),
                inferred_cause=cause,
                confidence=random.uniform(85.0, 99.0),
                service_name=service
            )
            db.add(corr)
            db.commit()
            
            # 5. Create Incident
            incident = incident_service.create_incident(
                db=db,
                root_cause=cause,
                impacted_services=[service]
            )
            
            # 6. Archive to Knowledge Base (Simulating a resolved historical issue)
            # Update status to RESOLVED
            incident.status = "RESOLVED"
            incident.resolved_at = ts + timedelta(hours=random.randint(1, 4))
            db.commit()
            
            knowledge_service.archive_incident(db, incident.incident_id)
            
        print("\n✅ Seeding complete! Database is populated with historical data.")

    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
