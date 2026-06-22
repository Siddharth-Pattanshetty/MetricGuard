"""
==========================================================
MetricGuard — Knowledge Base Repository  (incident_repository.py)
==========================================================

Phase 17: Historical Incident Knowledge Base
"""

import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.knowledge_base.models import IncidentHistory, RcaHistory, ResolutionHistory

logger = logging.getLogger("metricguard.knowledge.repository")


class IncidentRepository:
    """
    CRUD repository for database operations on resolved incident history,
    RCA history, and resolution history tables.
    """

    @staticmethod
    def save_incident(
        db: Session,
        incident_id: str,
        title: str,
        description: str,
        service_name: str,
        severity: str,
        status: str,
        root_cause: str,
        resolution: str,
        recommendation: str,
        impact_summary: str,
        created_at,
        resolved_at
    ) -> IncidentHistory:
        """
        Create and persist a resolved incident history record.
        """
        logger.info("[Repository] Saving incident history for ID %s", incident_id)
        db_history = IncidentHistory(
            incident_id=incident_id,
            title=title,
            description=description,
            service_name=service_name,
            severity=severity,
            status=status,
            root_cause=root_cause,
            resolution=resolution,
            recommendation=recommendation,
            impact_summary=impact_summary,
            created_at=created_at,
            resolved_at=resolved_at,
        )
        try:
            db.merge(db_history)
            db.commit()
            logger.info("[Repository] Incident %s saved to incident_history", incident_id)
            return db_history
        except Exception as e:
            db.rollback()
            logger.error("[Repository] Failed to save incident history for %s: %s", incident_id, e, exc_info=True)
            raise

    @staticmethod
    def update_incident(db: Session, incident_id: str, updates: dict) -> Optional[IncidentHistory]:
        """
        Update fields in an existing archived incident history record.
        """
        logger.info("[Repository] Updating incident history for ID %s", incident_id)
        db_history = db.query(IncidentHistory).filter(IncidentHistory.incident_id == incident_id).first()
        if not db_history:
            logger.warning("[Repository] Incident history record %s not found for update", incident_id)
            return None

        try:
            for key, val in updates.items():
                if hasattr(db_history, key):
                    setattr(db_history, key, val)
            db.commit()
            db.refresh(db_history)
            logger.info("[Repository] Updated incident history %s successfully", incident_id)
            return db_history
        except Exception as e:
            db.rollback()
            logger.error("[Repository] Failed to update incident history for %s: %s", incident_id, e, exc_info=True)
            raise

    @staticmethod
    def get_incident(db: Session, incident_id: str) -> Optional[IncidentHistory]:
        """
        Fetch a single archived incident by its ID.
        """
        try:
            return db.query(IncidentHistory).filter(IncidentHistory.incident_id == incident_id).first()
        except Exception as e:
            logger.error("[Repository] Failed to get incident history %s: %s", incident_id, e)
            return None

    @staticmethod
    def get_all_incidents(db: Session) -> List[IncidentHistory]:
        """
        Fetch all archived incident history records.
        """
        try:
            return db.query(IncidentHistory).order_by(desc(IncidentHistory.resolved_at)).all()
        except Exception as e:
            logger.error("[Repository] Failed to list archived incidents: %s", e)
            return []

    @staticmethod
    def get_incident_history(db: Session, limit: int = 100) -> List[IncidentHistory]:
        """
        Retrieve incident history records with a specified limit.
        """
        try:
            return db.query(IncidentHistory).order_by(desc(IncidentHistory.resolved_at)).limit(limit).all()
        except Exception as e:
            logger.error("[Repository] Failed to retrieve incident history: %s", e)
            return []

    @staticmethod
    def save_rca(db: Session, incident_id: str, root_cause: str, confidence: float) -> RcaHistory:
        """
        Save an RCA history record.
        """
        logger.info("[Repository] Saving RCA history for incident %s", incident_id)
        db_rca = RcaHistory(
            incident_id=incident_id,
            root_cause=root_cause,
            confidence=confidence,
        )
        try:
            db.add(db_rca)
            db.commit()
            db.refresh(db_rca)
            logger.info("[Repository] RCA history record saved for incident %s", incident_id)
            return db_rca
        except Exception as e:
            db.rollback()
            logger.error("[Repository] Failed to save RCA history for %s: %s", incident_id, e, exc_info=True)
            raise

    @staticmethod
    def save_resolution(db: Session, incident_id: str, resolution: str, action_taken: str) -> ResolutionHistory:
        """
        Save a resolution history record.
        """
        logger.info("[Repository] Saving resolution history for incident %s", incident_id)
        db_res = ResolutionHistory(
            incident_id=incident_id,
            resolution=resolution,
            action_taken=action_taken,
        )
        try:
            db.add(db_res)
            db.commit()
            db.refresh(db_res)
            logger.info("[Repository] Resolution history record saved for incident %s", incident_id)
            return db_res
        except Exception as e:
            db.rollback()
            logger.error("[Repository] Failed to save resolution history for %s: %s", incident_id, e, exc_info=True)
            raise


# Global Singleton accessor
_repo_instance: Optional[IncidentRepository] = None

def get_incident_repository() -> IncidentRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = IncidentRepository()
    return _repo_instance
