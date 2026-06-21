"""
==========================================================
MetricGuard — Knowledge Base Service  (knowledge_service.py)
==========================================================

Phase 17: Historical Incident Knowledge Base
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.knowledge_base.models import IncidentHistory, RcaHistory, ResolutionHistory
from backend.knowledge_base.incident_repository import get_incident_repository
from backend.knowledge_base.similar_incident_engine import get_similar_incident_engine
from backend.services.incident_service import get_incident_service
from backend.recommendation_engine.recommendation_service import get_recommendation_service
from backend.models.correlation import Correlation

logger = logging.getLogger("metricguard.knowledge.service")


class KnowledgeService:
    """
    Service layer coordinating repository writes, resolved incident archival hooks,
    and similar incident matching engine access.
    """

    def __init__(self) -> None:
        self.repo = get_incident_repository()
        self.engine = get_similar_incident_engine()

    def archive_incident(self, db: Session, incident_id: str) -> Optional[IncidentHistory]:
        """
        Pulls completed Incident, RCA, and Recommendations info and archives them in TiDB.
        """
        logger.info("[KnowledgeService] Archiving incident %s", incident_id)

        # 1. Fetch source incident
        incident_service = get_incident_service()
        incident = incident_service.get_incident(db, incident_id)
        if not incident:
            logger.error("[KnowledgeService] Source incident %s not found", incident_id)
            raise ValueError(f"Incident '{incident_id}' not found.")

        # 2. Retrieve RCA Confidence Details
        correlation = db.query(Correlation).filter(
            Correlation.inferred_cause == incident.root_cause
        ).order_by(Correlation.created_at.desc()).first()

        if not correlation:
            services_lower = [s.strip().lower() for s in incident.impacted_services.split(",") if s.strip()]
            if services_lower:
                correlation = db.query(Correlation).filter(
                    Correlation.service_name.in_(services_lower)
                ).order_by(Correlation.created_at.desc()).first()

        rca_confidence = correlation.confidence if correlation else 85.0
        rca_score = correlation.correlation_score if correlation else 0.85

        # 3. Fetch recommendations
        rec_service = get_recommendation_service()
        recs = rec_service.get_recommendations(
            root_cause=incident.root_cause,
            severity=incident.severity,
            impacted_services=[s.strip() for s in incident.impacted_services.split(",") if s.strip()],
            confidence=rca_score,
        )

        all_recs_str = "; ".join([r["action"] for r in recs]) if recs else "Monitor affected services."
        top_rec_action = recs[0]["action"] if recs else "Restart failing services."

        primary_service = incident.impacted_services.split(",")[0] if incident.impacted_services else "system"

        # 4. Check & Persist Incident History
        existing_hist = self.repo.get_incident(db, incident_id)
        if not existing_hist:
            title = f"{incident.root_cause.title()} on {primary_service.title()}"
            description = f"Incident details: severity={incident.severity}, root_cause={incident.root_cause}, impacted_services={incident.impacted_services}."
            
            existing_hist = self.repo.save_incident(
                db=db,
                incident_id=incident.incident_id,
                title=title,
                description=description,
                service_name=primary_service,
                severity=incident.severity,
                status=incident.status,
                root_cause=incident.root_cause,
                resolution=top_rec_action,
                recommendation=all_recs_str,
                impact_summary=f"Affected services: {incident.impacted_services}.",
                created_at=incident.created_at,
                resolved_at=datetime.utcnow()
            )
            logger.info("[KnowledgeService] Incident archived in incident_history: %s", incident_id)
        else:
            logger.info("[KnowledgeService] Incident history %s already archived. Skipping duplicate insert.", incident_id)

        # 5. Check & Persist RCA History
        existing_rca = db.query(RcaHistory).filter(RcaHistory.incident_id == incident_id).first()
        if not existing_rca:
            self.repo.save_rca(
                db=db,
                incident_id=incident_id,
                root_cause=incident.root_cause,
                confidence=rca_confidence,
            )
            logger.info("[KnowledgeService] RCA history archived for incident %s", incident_id)

        # 6. Check & Persist Resolution History
        existing_res = db.query(ResolutionHistory).filter(ResolutionHistory.incident_id == incident_id).first()
        if not existing_res:
            self.repo.save_resolution(
                db=db,
                incident_id=incident_id,
                resolution=top_rec_action,
                action_taken=f"Resolved system degradation via: {top_rec_action}",
            )
            logger.info("[KnowledgeService] Resolution history archived for incident %s", incident_id)

        return existing_hist

    def get_incident_history(self, db: Session, limit: int = 100) -> List[IncidentHistory]:
        """Fetch historical incident list."""
        logger.info("[KnowledgeService] Knowledge lookup completed for archived incidents")
        return self.repo.get_incident_history(db, limit)

    def get_rca_history(self, db: Session, limit: int = 100) -> List[RcaHistory]:
        """Fetch historical RCA list."""
        try:
            return db.query(RcaHistory).order_by(RcaHistory.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error("[KnowledgeService] Failed to fetch RCA history: %s", e)
            return []

    def get_resolution_history(self, db: Session, limit: int = 100) -> List[ResolutionHistory]:
        """Fetch historical resolution list."""
        try:
            return db.query(ResolutionHistory).order_by(ResolutionHistory.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error("[KnowledgeService] Failed to fetch resolution history: %s", e)
            return []

    def search_similar_incidents(self, db: Session, title: str, description: str) -> List[Dict[str, Any]]:
        """
        Compare active incident title and description against all archived incident history.
        """
        logger.info("[KnowledgeService] Similarity search executed for title='%s'", title)
        history_list = self.repo.get_all_incidents(db)
        # Compare: title, description, root_cause, service_name
        return self.engine.find_similar_incidents(
            target_title=title,
            target_description=description,
            target_root_cause=title,
            target_service="",
            historical_incidents=history_list
        )


# Global Singleton accessor
_service_instance: Optional[KnowledgeService] = None

def get_knowledge_service() -> KnowledgeService:
    global _service_instance
    if _service_instance is None:
        _service_instance = KnowledgeService()
    return _service_instance
