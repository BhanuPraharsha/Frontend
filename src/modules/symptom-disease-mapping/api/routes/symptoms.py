"""
Symptom CRUD routes – GET /symptoms, POST /symptoms,
PUT /symptoms/{id}, DELETE /symptoms/{id}
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from api.models import SymptomCreate, SymptomUpdate, SymptomOut
from database.connection import get_collections

router = APIRouter(prefix="/symptoms", tags=["Symptoms"])


@router.get("", response_model=List[SymptomOut])
def get_symptoms(body_system: Optional[str] = Query(default=None)):
    """Return all symptoms, optionally filtered by body_system."""
    cols = get_collections()
    query = {}
    if body_system:
        query["body_system"] = body_system
    return list(cols["symptoms"].find(query, {"_id": 0}))


@router.post("", response_model=SymptomOut, status_code=201)
def create_symptom(symptom: SymptomCreate):
    """Insert a new symptom. Returns 409 if symptom_id already exists."""
    cols = get_collections()
    if cols["symptoms"].find_one({"symptom_id": symptom.symptom_id}):
        raise HTTPException(status_code=409, detail=f"symptom_id '{symptom.symptom_id}' already exists")
    cols["symptoms"].insert_one(symptom.model_dump())
    return symptom


@router.put("/{symptom_id}", response_model=SymptomOut)
def update_symptom(symptom_id: str, payload: SymptomUpdate):
    """Update the symptom_name for a given symptom_id."""
    cols = get_collections()
    result = cols["symptoms"].find_one_and_update(
        {"symptom_id": symptom_id},
        {"$set": {"symptom_name": payload.symptom_name}},
        projection={"_id": 0},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"symptom_id '{symptom_id}' not found")
    return result


@router.delete("/{symptom_id}", status_code=204)
def delete_symptom(symptom_id: str):
    """Delete a symptom by symptom_id."""
    cols = get_collections()
    result = cols["symptoms"].delete_one({"symptom_id": symptom_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"symptom_id '{symptom_id}' not found")
