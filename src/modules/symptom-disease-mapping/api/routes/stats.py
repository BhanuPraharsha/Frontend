"""
Stats route – GET /stats
Returns document counts for all four M7 collections.
"""

from fastapi import APIRouter
from api.models import StatsOut
from database.connection import get_collections

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("", response_model=StatsOut)
def get_stats():
    """Return the number of documents in each M7 collection."""
    cols = get_collections()
    return {
        "symptoms":      cols["symptoms"].count_documents({}),
        "diseases":      cols["diseases"].count_documents({}),
        "associations":  cols["symptom_disease_associations"].count_documents({}),
        "diagnosis_rules": cols["diagnosis_rules"].count_documents({}),
    }
