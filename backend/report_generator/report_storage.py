import os
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger("metricguard.report_storage")

# Root directory calculations
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
METADATA_DIR = os.path.join(REPORTS_DIR, "metadata")
GENERATED_DIR = os.path.join(REPORTS_DIR, "generated")

# Ensure folders exist
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)


class ReportStorage:
    """
    Manages metadata serialization/deserialization for reports.
    """

    def __init__(self) -> None:
        self.metadata_dir = METADATA_DIR
        self.generated_dir = GENERATED_DIR

    def generate_report_id(self) -> str:
        """
        Generate sequential report ID in format REP-XXX.
        """
        try:
            files = [f for f in os.listdir(self.metadata_dir) if f.startswith("REP-") and f.endswith(".json")]
            if not files:
                return "REP-001"
            
            ids = []
            for f in files:
                try:
                    num = int(f.split(".")[0].split("-")[-1])
                    ids.append(num)
                except ValueError:
                    pass
            next_num = max(ids) + 1 if ids else 1
            return f"REP-{next_num:03d}"
        except Exception as e:
            logger.error("[REPORT_STORAGE] Failed to generate report ID: %s", e)
            import uuid
            return f"REP-{uuid.uuid4().hex[:6].upper()}"

    def save_metadata(self, metadata: dict) -> bool:
        """
        Save report metadata payload to JSON file.
        """
        report_id = metadata.get("report_id")
        if not report_id:
            logger.error("[REPORT_STORAGE] Missing report_id in metadata")
            return False

        file_path = os.path.join(self.metadata_dir, f"{report_id}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
            logger.info("[REPORT_STORAGE] Persisted metadata for report %s", report_id)
            return True
        except Exception as e:
            logger.error("[REPORT_STORAGE] Failed to save metadata for %s: %s", report_id, e)
            return False

    def get_metadata(self, report_id: str) -> Optional[dict]:
        """
        Retrieve report metadata by its ID.
        """
        file_path = os.path.join(self.metadata_dir, f"{report_id}.json")
        if not os.path.exists(file_path):
            logger.warning("[REPORT_STORAGE] Metadata not found for report ID %s", report_id)
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("[REPORT_STORAGE] Failed to read metadata for %s: %s", report_id, e)
            return None

    def get_all_reports(self) -> List[dict]:
        """
        Return history of all generated report metadata.
        """
        reports = []
        try:
            files = [f for f in os.listdir(self.metadata_dir) if f.startswith("REP-") and f.endswith(".json")]
            for f in files:
                path = os.path.join(self.metadata_dir, f)
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        reports.append(json.load(file))
                except Exception as read_err:
                    logger.error("[REPORT_STORAGE] Failed to read metadata file %s: %s", f, read_err)
            
            # Sort by created_at descending
            reports.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        except Exception as e:
            logger.error("[REPORT_STORAGE] Failed to list report history: %s", e)
        return reports


# Global Singleton accessor
_storage_instance: Optional[ReportStorage] = None

def get_report_storage() -> ReportStorage:
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = ReportStorage()
    return _storage_instance
