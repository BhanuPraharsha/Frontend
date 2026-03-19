"""
Disease CRUD routes – GET /diseases, POST /diseases,
PUT /diseases/{id}, DELETE /diseases/{id}
"""

from fastapi import APIRouter, HTTPException
from typing import List
from api.models import DiseaseCreate, DiseaseUpdate, DiseaseOut
from database.connection import get_collections

router = APIRouter(prefix="/diseases", tags=["Diseases"])


@router.get("", response_model=List[DiseaseOut])
def get_diseases():
    """Return all diseases, sorted by prevalence_rate descending."""
    cols = get_collections()
    return list(cols["diseases"].find({}, {"_id": 0}).sort("prevalence_rate", -1))


@router.post("", response_model=DiseaseOut, status_code=201)
def create_disease(disease: DiseaseCreate):
    """Insert a new disease. Returns 409 if disease_id already exists."""
    cols = get_collections()
    if cols["diseases"].find_one({"disease_id": disease.disease_id}):
        raise HTTPException(status_code=409, detail=f"disease_id '{disease.disease_id}' already exists")
    cols["diseases"].insert_one(disease.model_dump())
    return disease


@router.put("/{disease_id}", response_model=DiseaseOut)
def update_disease(disease_id: str, payload: DiseaseUpdate):
    """Update the disease_name for a given disease_id."""
    cols = get_collections()
    result = cols["diseases"].find_one_and_update(
        {"disease_id": disease_id},
        {"$set": {"disease_name": payload.disease_name}},
        projection={"_id": 0},
        return_document=True,
    )
    if result is None:
        raise HTTPException(status_code=404, detail=f"disease_id '{disease_id}' not found")
    return result


@router.delete("/{disease_id}", status_code=204)
def delete_disease(disease_id: str):
    """Delete a disease by disease_id."""
    cols = get_collections()
    result = cols["diseases"].delete_one({"disease_id": disease_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"disease_id '{disease_id}' not found")
