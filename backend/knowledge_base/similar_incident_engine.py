"""
==========================================================
MetricGuard — Similar Incident Comparison Engine (similar_incident_engine.py)
==========================================================

Phase 17: Historical Incident Knowledge Base
"""

import logging
import difflib
from typing import List, Dict, Any

logger = logging.getLogger("metricguard.knowledge.similar_engine")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("[SimilarIncidentEngine] scikit-learn is not available in current python context. Falling back to SequenceMatcher.")


class SimilarIncidentEngine:
    """
    Compares incident properties (title, description, root cause, service name)
    to find similar past incidents using TF-IDF / Cosine Similarity or SequenceMatcher.
    """

    @staticmethod
    def _calculate_sklearn_similarity(text1: str, text2: str) -> float:
        """Compute cosine similarity of TF-IDF vectors for text1 and text2."""
        try:
            vectorizer = TfidfVectorizer().fit_transform([text1, text2])
            vectors = vectorizer.toarray()
            # If vocabulary is empty or only has unique words, vectors might be empty
            if vectors.shape[1] == 0:
                return 0.0
            score = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
            return float(score)
        except Exception as e:
            logger.error("[SimilarIncidentEngine] sklearn similarity failed: %s", e)
            return 0.0

    @staticmethod
    def _calculate_difflib_similarity(text1: str, text2: str) -> float:
        """Compute character sequence match ratio between text1 and text2."""
        try:
            return difflib.SequenceMatcher(None, text1, text2).ratio()
        except Exception as e:
            logger.error("[SimilarIncidentEngine] difflib similarity failed: %s", e)
            return 0.0

    def find_similar_incidents(
        self,
        target_title: str,
        target_description: str,
        target_root_cause: str,
        target_service: str,
        historical_incidents: List[Any],
    ) -> List[Dict[str, Any]]:
        """
        Compare target properties against all archived incidents.
        Only return matches with a similarity score >= 0.70, sorted descending by score.
        """
        logger.info(
            "[SimilarIncidentEngine] Finding matches for title='%s', service='%s'",
            target_title, target_service
        )

        t_title = (target_title or "").strip().lower()
        t_desc = (target_description or "").strip().lower()
        target_text = f"{t_title} {t_desc}".strip()
        if not target_text:
            return []

        matches = []
        for hist in historical_incidents:
            h_title = (hist.title or "").strip().lower()
            h_desc = (hist.description or "").strip().lower()
            hist_text = f"{h_title} {h_desc}".strip()
            if not hist_text:
                continue

            # Compute text similarity
            if SKLEARN_AVAILABLE:
                base_score = self._calculate_sklearn_similarity(target_text, hist_text)
            else:
                base_score = self._calculate_difflib_similarity(target_text, hist_text)

            # Apply domain boosts:
            # +0.25 if root causes match exactly or share key words of length >= 3
            # +0.25 if service names match exactly or service name is mentioned in search text
            boost = 0.0
            
            # Root Cause Boost
            if target_root_cause and hist.root_cause:
                trc_clean = target_root_cause.strip().lower()
                hrc_clean = hist.root_cause.strip().lower()
                if trc_clean == hrc_clean:
                    boost += 0.25
                else:
                    trc_tokens = set([t for t in trc_clean.split() if len(t) >= 3])
                    hrc_tokens = set([t for t in hrc_clean.split() if len(t) >= 3])
                    if trc_tokens.intersection(hrc_tokens):
                        boost += 0.25

            # Service Name Boost
            if hist.service_name:
                h_srv_clean = hist.service_name.strip().lower()
                if target_service and target_service.strip().lower() == h_srv_clean:
                    boost += 0.25
                elif h_srv_clean in target_text:
                    boost += 0.25

            score = min(base_score + boost, 1.0)
            score = round(score, 2)

            if score >= 0.70:
                matches.append({
                    "incident_id": hist.incident_id,
                    "similarity_score": score,
                    "root_cause": hist.root_cause,
                    "resolution": hist.resolution
                })

        # Sort matches descending by score
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        logger.info("[SimilarIncidentEngine] Found %d similar matches >= 0.70", len(matches))
        return matches


# Global Singleton accessor
_engine_instance = None

def get_similar_incident_engine() -> SimilarIncidentEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SimilarIncidentEngine()
    return _engine_instance
