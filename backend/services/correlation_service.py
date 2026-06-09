"""
==========================================================
MetricGuard — Correlation Service  (correlation_service.py)
==========================================================

Phase 10: Metric-Log Correlation Engine

Purpose
-------
Orchestrates the full correlation pipeline:

    1. Load recent metric anomalies  (from ``anomalies`` table)
    2. Load recent log anomalies     (ERROR/CRITICAL from ``logs`` table)
    3. Match anomalies within 60-second time windows
    4. Calculate a multi-factor correlation score
    5. Infer the probable root cause via keyword matching
    6. Persist correlation records to the ``correlations`` table

Scoring Algorithm
~~~~~~~~~~~~~~~~~
Each (metric_anomaly, log_anomaly) pair is scored on three factors:

    +------+---------------------------+--------+
    | Wt   | Factor                    | Points |
    +------+---------------------------+--------+
    | 0.40 | Time proximity  (≤60 s)   |  0.40  |
    | 0.20 | Severity match            |  0.20  |
    | 0.40 | Keyword / cause match     |  0.40  |
    +------+---------------------------+--------+
    | Max  |                           |  1.00  |
    +------+---------------------------+--------+

Usage
-----
    from backend.services.correlation_service import CorrelationService
    from app.database import SessionLocal

    db = SessionLocal()
    service = CorrelationService()
    count = service.run_correlation_engine(db)
    print(f"Created {count} correlations")
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models import Anomaly, Log
from backend.models.correlation import Correlation
from backend.utils.cause_mapper import infer_root_cause

logger = logging.getLogger("metricguard.correlation.service")


# ==========================================================
# SEVERITY MAPPING
# ==========================================================
# The anomalies table uses: low, warning, critical
# The logs table uses:       DEBUG, INFO, WARNING, ERROR, CRITICAL
#
# For correlation scoring we map log levels to the anomaly
# severity scale so we can compare like-for-like.
# ==========================================================

_LOG_LEVEL_TO_SEVERITY = {
    "ERROR":    "warning",
    "CRITICAL": "critical",
    "WARNING":  "low",
}

# Maximum time difference (seconds) for a time-window match
_TIME_WINDOW_SECONDS = 60

# Scoring weights
_WEIGHT_TIME     = 0.4
_WEIGHT_SEVERITY = 0.2
_WEIGHT_KEYWORD  = 0.4


class CorrelationService:
    """
    Stateless service that correlates metric anomalies with
    log anomalies and persists the results.
    """

    # ----------------------------------------------------------
    # DATA RETRIEVAL
    # ----------------------------------------------------------

    def get_recent_metric_anomalies(
        self,
        db: Session,
        minutes: int = 5,
    ) -> List[Anomaly]:
        """
        Fetch metric anomalies from the last *minutes* minutes.

        Returns rows from the ``anomalies`` table ordered by
        timestamp descending.
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        try:
            anomalies = (
                db.query(Anomaly)
                .filter(Anomaly.timestamp >= cutoff)
                .order_by(desc(Anomaly.timestamp))
                .all()
            )
            logger.info(
                "[Correlation Engine] Metric anomalies found: %d (last %d min)",
                len(anomalies), minutes,
            )
            return anomalies
        except Exception as e:
            logger.error(
                "[Correlation Engine] Failed to fetch metric anomalies: %s",
                e, exc_info=True,
            )
            return []

    def get_recent_log_anomalies(
        self,
        db: Session,
        minutes: int = 5,
    ) -> List[Log]:
        """
        Fetch log-level anomalies from the last *minutes* minutes.

        A "log anomaly" is defined as any log entry with level
        ERROR or CRITICAL — these represent application-level
        failures that may correlate with metric spikes.
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        try:
            logs = (
                db.query(Log)
                .filter(
                    Log.timestamp >= cutoff,
                    Log.level.in_(["ERROR", "CRITICAL"]),
                )
                .order_by(desc(Log.timestamp))
                .all()
            )
            logger.info(
                "[Correlation Engine] Log anomalies found: %d (last %d min)",
                len(logs), minutes,
            )
            return logs
        except Exception as e:
            logger.error(
                "[Correlation Engine] Failed to fetch log anomalies: %s",
                e, exc_info=True,
            )
            return []

    # ----------------------------------------------------------
    # SCORING
    # ----------------------------------------------------------

    def calculate_score(
        self,
        metric_anomaly: Anomaly,
        log_anomaly: Log,
    ) -> float:
        """
        Calculate a correlation score between a metric anomaly
        and a log anomaly based on three factors.

        Parameters
        ----------
        metric_anomaly : Anomaly
            A row from the anomalies table.
        log_anomaly : Log
            A row from the logs table (ERROR or CRITICAL).

        Returns
        -------
        float
            Score in [0.0, 1.0].
        """
        score = 0.0

        # ---- Factor 1: Time proximity (≤60 seconds) ----
        time_diff = abs(
            (metric_anomaly.timestamp - log_anomaly.timestamp).total_seconds()
        )
        if time_diff <= _TIME_WINDOW_SECONDS:
            score += _WEIGHT_TIME

        # ---- Factor 2: Severity match ----
        mapped_severity = _LOG_LEVEL_TO_SEVERITY.get(
            log_anomaly.level, ""
        )
        if (
            metric_anomaly.severity
            and mapped_severity
            and metric_anomaly.severity.lower() == mapped_severity
        ):
            score += _WEIGHT_SEVERITY

        # ---- Factor 3: Keyword / cause match ----
        cause_info = infer_root_cause(log_anomaly.message)
        if cause_info["cause"] != "Unknown":
            score += _WEIGHT_KEYWORD

        logger.debug(
            "[Correlation Engine] Score calculated: %.2f "
            "(time_diff=%.1fs, severity=%s vs %s, cause=%s)",
            score, time_diff,
            metric_anomaly.severity, log_anomaly.level,
            cause_info["cause"],
        )

        return round(score, 2)

    # ----------------------------------------------------------
    # CAUSE INFERENCE
    # ----------------------------------------------------------

    def infer_cause(self, log_message: str) -> Dict[str, Any]:
        """
        Delegate to the cause mapper to infer root cause from
        a log message.

        Returns
        -------
        dict
            ``{"cause": "...", "confidence": float}``
        """
        result = infer_root_cause(log_message)
        if result["cause"] != "Unknown":
            logger.info(
                "[Correlation Engine] Cause inferred: %s (confidence=%.2f)",
                result["cause"], result["confidence"],
            )
        return result

    # ----------------------------------------------------------
    # CORRELATION RECORD CREATION
    # ----------------------------------------------------------

    def create_correlation(
        self,
        metric_anomaly: Anomaly,
        log_anomaly: Log,
        score: float,
        cause_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Build a correlation data dictionary (not yet persisted).
        """
        confidence = round(score * 100, 2)
        return {
            "metric_anomaly_id": metric_anomaly.id,
            "log_anomaly_id":    log_anomaly.id,
            "correlation_score": score,
            "inferred_cause":    cause_info.get("cause", "Unknown"),
            "confidence":        confidence,
        }

    def store_correlation(
        self,
        db: Session,
        correlation_data: Dict[str, Any],
    ) -> Correlation:
        """
        Persist a correlation record to the database.
        """
        try:
            db_corr = Correlation(
                metric_anomaly_id=correlation_data["metric_anomaly_id"],
                log_anomaly_id=correlation_data["log_anomaly_id"],
                correlation_score=correlation_data["correlation_score"],
                inferred_cause=correlation_data["inferred_cause"],
                confidence=correlation_data["confidence"],
            )
            db.add(db_corr)
            db.commit()
            db.refresh(db_corr)

            logger.info(
                "[Correlation Engine] Correlation stored "
                "(ID=%d, metric=%d, log=%d, score=%.2f, cause='%s')",
                db_corr.id,
                db_corr.metric_anomaly_id,
                db_corr.log_anomaly_id,
                db_corr.correlation_score,
                db_corr.inferred_cause,
            )
            return db_corr

        except Exception as e:
            db.rollback()
            logger.error(
                "[Correlation Engine] Failed to store correlation: %s",
                e, exc_info=True,
            )
            raise

    # ----------------------------------------------------------
    # FULL PIPELINE
    # ----------------------------------------------------------

    def run_correlation_engine(
        self,
        db: Session,
        minutes: int = 5,
    ) -> int:
        """
        Execute the complete correlation pipeline:

        1. Fetch recent metric anomalies
        2. Fetch recent log anomalies (ERROR/CRITICAL)
        3. For each (metric, log) pair within the time window:
           - Calculate score
           - Infer cause
           - Store if score > 0
        4. Return the number of correlations created

        Parameters
        ----------
        db : Session
            SQLAlchemy database session.
        minutes : int
            How far back to look for anomalies (default 5 min).

        Returns
        -------
        int
            Number of correlation records created.
        """
        logger.info(
            "[Correlation Engine] Starting correlation run (window=%d min)...",
            minutes,
        )

        metric_anomalies = self.get_recent_metric_anomalies(db, minutes)
        log_anomalies = self.get_recent_log_anomalies(db, minutes)

        if not metric_anomalies:
            logger.info("[Correlation Engine] No metric anomalies found — skipping.")
            return 0

        if not log_anomalies:
            logger.info("[Correlation Engine] No log anomalies found — skipping.")
            return 0

        correlations_created = 0

        for metric_anomaly in metric_anomalies:
            for log_anomaly in log_anomalies:

                # Only correlate if within the time window
                time_diff = abs(
                    (metric_anomaly.timestamp - log_anomaly.timestamp).total_seconds()
                )
                if time_diff > _TIME_WINDOW_SECONDS:
                    continue

                # Calculate score
                score = self.calculate_score(metric_anomaly, log_anomaly)

                # Only store meaningful correlations (score > 0)
                if score <= 0:
                    continue

                # Infer cause
                cause_info = self.infer_cause(log_anomaly.message)

                # Build and store
                corr_data = self.create_correlation(
                    metric_anomaly, log_anomaly, score, cause_info,
                )

                try:
                    self.store_correlation(db, corr_data)
                    correlations_created += 1
                except Exception:
                    # Error already logged inside store_correlation
                    continue

        logger.info(
            "[Correlation Engine] Correlation run complete — %d correlations created.",
            correlations_created,
        )
        return correlations_created

    # ----------------------------------------------------------
    # QUERY METHODS
    # ----------------------------------------------------------

    def get_all_correlations(self, db: Session) -> List[Correlation]:
        """
        Return all stored correlations ordered by created_at descending.
        """
        try:
            return (
                db.query(Correlation)
                .order_by(desc(Correlation.created_at))
                .all()
            )
        except Exception as e:
            logger.error(
                "[Correlation Engine] Failed to query correlations: %s",
                e, exc_info=True,
            )
            return []

    def get_latest_correlations(
        self,
        db: Session,
        limit: int = 20,
    ) -> List[Correlation]:
        """
        Return the most recent *limit* correlations.
        """
        try:
            return (
                db.query(Correlation)
                .order_by(desc(Correlation.created_at))
                .limit(limit)
                .all()
            )
        except Exception as e:
            logger.error(
                "[Correlation Engine] Failed to query latest correlations: %s",
                e, exc_info=True,
            )
            return []
