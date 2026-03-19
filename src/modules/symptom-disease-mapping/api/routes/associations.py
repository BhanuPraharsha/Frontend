"""
Associations read routes – GET /associations
Returns all symptom-disease associations enriched with resolved names.
"""

from fastapi import APIRouter
from typing import List
from api.models import AssociationOut
from database.connection import get_collections

router = APIRouter(prefix="/associations", tags=["Associations"])


@router.get("", response_model=List[AssociationOut])
def get_associations():
    """
    Return all symptom-disease associations with symptom_name and
    disease_name resolved from their respective collections.
    """
    cols = get_collections()

    sym_map = {s["symptom_id"]: s["symptom_name"] for s in cols["symptoms"].find({}, {"_id": 0})}
    dis_map = {d["disease_id"]: d["disease_name"] for d in cols["diseases"].find({}, {"_id": 0})}

    results = []
    for a in cols["symptom_disease_associations"].find({}, {"_id": 0}):
        results.append({
            "symptom_id":           a.get("symptom_id"),
            "symptom_name":         sym_map.get(a.get("symptom_id")),
            "disease_id":           a.get("disease_id"),
            "disease_name":         dis_map.get(a.get("disease_id")),
            "association_strength": a.get("association_strength"),
            "sensitivity":          a.get("sensitivity"),
            "specificity":          a.get("specificity"),
        })
    return results
