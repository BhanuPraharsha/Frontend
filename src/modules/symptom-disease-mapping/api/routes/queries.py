"""
Query routes – five aggregate/analytical queries (Q1–Q5).
Each endpoint mirrors the MongoDB aggregation pipelines from the original app.py.

GET /queries/top-diseases-by-symptoms          → Q1
GET /queries/high-sensitivity-symptoms         → Q2
GET /queries/diseases-by-prevalence            → Q3
GET /queries/associations-by-body-system       → Q4
GET /queries/top-rules-by-confidence           → Q5
"""

from fastapi import APIRouter
from typing import Any, Dict, List
from database.connection import get_collections

router = APIRouter(prefix="/queries", tags=["Queries"])


def _get_maps(cols):
    sym_map = {s["symptom_id"]: s["symptom_name"] for s in cols["symptoms"].find({}, {"_id": 0})}
    dis_map = {d["disease_id"]: d["disease_name"] for d in cols["diseases"].find({}, {"_id": 0})}
    return sym_map, dis_map


@router.get("/top-diseases-by-symptoms", response_model=List[Dict[str, Any]])
def q1_top_diseases_by_symptoms():
    """Q1 – Top diseases by number of associated symptoms."""
    cols = get_collections()
    _, dis_map = _get_maps(cols)

    raw = list(cols["symptom_disease_associations"].aggregate([
        {"$group": {"_id": "$disease_id", "symptom_count": {"$sum": 1}}},
        {"$sort":  {"symptom_count": -1}},
    ]))
    return [{"disease_name": dis_map.get(r["_id"], r["_id"]),
             "symptom_count": r["symptom_count"]} for r in raw]


@router.get("/high-sensitivity-symptoms", response_model=List[Dict[str, Any]])
def q2_high_sensitivity_symptoms():
    """Q2 – Symptoms with high sensitivity (>= 0.85)."""
    cols = get_collections()
    sym_map, dis_map = _get_maps(cols)

    raw = list(cols["symptom_disease_associations"].find(
        {"sensitivity": {"$gte": 0.85}}, {"_id": 0}
    ))
    rows = [
        {
            "symptom_name": sym_map.get(r["symptom_id"], r["symptom_id"]),
            "disease_name": dis_map.get(r["disease_id"], r["disease_id"]),
            "sensitivity":  r["sensitivity"],
            "specificity":  r["specificity"],
        }
        for r in raw
    ]
    rows.sort(key=lambda x: -x["sensitivity"])
    return rows


@router.get("/diseases-by-prevalence", response_model=List[Dict[str, Any]])
def q3_diseases_by_prevalence():
    """Q3 – Diseases sorted by prevalence rate (descending)."""
    cols = get_collections()
    return list(cols["diseases"].find(
        {}, {"_id": 0, "disease_name": 1, "icd11_code": 1, "prevalence_rate": 1}
    ).sort("prevalence_rate", -1))


@router.get("/associations-by-body-system", response_model=List[Dict[str, Any]])
def q4_associations_by_body_system():
    """Q4 – Associations grouped by body system, avg association_strength."""
    cols = get_collections()
    pipeline = [
        {"$lookup": {"from": "symptoms", "localField": "symptom_id",
                     "foreignField": "symptom_id", "as": "sym"}},
        {"$unwind": "$sym"},
        {"$group": {"_id": "$sym.body_system",
                    "association_count": {"$sum": 1},
                    "avg_strength":      {"$avg": "$association_strength"}}},
        {"$sort": {"association_count": -1}},
        {"$project": {"_id": 0,
                      "body_system":       "$_id",
                      "association_count": 1,
                      "avg_strength":      {"$round": ["$avg_strength", 3]}}},
    ]
    return list(cols["symptom_disease_associations"].aggregate(pipeline))


@router.get("/top-rules-by-confidence", response_model=List[Dict[str, Any]])
def q5_top_rules_by_confidence():
    """Q5 – Diagnosis rules sorted by confidence_modifier descending."""
    cols = get_collections()
    _, dis_map = _get_maps(cols)

    raw = list(cols["diagnosis_rules"].find({}, {"_id": 0}).sort("confidence_modifier", -1))
    return [
        {
            "rule_name":           r["rule_name"],
            "suggested_disease":   dis_map.get(r.get("suggested_disease_id"), r.get("suggested_disease_id", "")),
            "confidence_modifier": r["confidence_modifier"],
            "priority":            r["priority"],
        }
        for r in raw
    ]

@router.get("/symptom-set-intersection", response_model=List[Dict[str, Any]])
def get_set_intersection(s1: str = "S001", s2: str = "S003"):
    """Find diseases that share a specific set of symptoms (Set Operation: Intersection)"""
    cols = get_collections()
    _, dis_map = _get_maps(cols)
    
    # We find diseases associated with BOTH s1 and s2
    pipeline = [
        {"$match": {"symptom_id": {"$in": [s1, s2]}}},
        {"$group": {"_id": "$disease_id", "matched_symptoms": {"$addToSet": "$symptom_id"}}},
        {"$match": {"matched_symptoms": {"$all": [s1, s2]}}} # This is the 'Intersection' part
    ]
    raw = list(cols["symptom_disease_associations"].aggregate(pipeline))
    return [{"disease_name": dis_map.get(r["_id"], "Unknown"), "match": "Common Intersection"} for r in raw]
