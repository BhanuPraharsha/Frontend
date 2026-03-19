"""
Diagnosis Rules read route – GET /diagnosis-rules
Returns all rules with symptom names and disease names resolved.
"""

from fastapi import APIRouter
from typing import List
from api.models import DiagnosisRuleOut
from database.connection import get_collections

router = APIRouter(prefix="/diagnosis-rules", tags=["Diagnosis Rules"])


@router.get("", response_model=List[DiagnosisRuleOut])
def get_diagnosis_rules():
    """
    Return all diagnosis rules sorted by priority (ascending).
    symptom_combination is resolved to symptom names, suggested_disease
    is resolved to a disease name.
    """
    cols = get_collections()

    dis_map = {d["disease_id"]: d["disease_name"] for d in cols["diseases"].find({}, {"_id": 0})}
    sym_map = {s["symptom_id"]: s["symptom_name"] for s in cols["symptoms"].find({}, {"_id": 0})}

    results = []
    for r in cols["diagnosis_rules"].find({}, {"_id": 0}).sort("priority", 1):
        sym_names = [sym_map.get(sid, sid) for sid in r.get("symptom_combination", [])]
        results.append({
            "rule_id":             r["rule_id"],
            "rule_name":           r["rule_name"],
            "symptom_combination": sym_names,
            "suggested_disease":   dis_map.get(r.get("suggested_disease_id"), r.get("suggested_disease_id", "")),
            "confidence_modifier": r["confidence_modifier"],
            "priority":            r["priority"],
        })
    return results
