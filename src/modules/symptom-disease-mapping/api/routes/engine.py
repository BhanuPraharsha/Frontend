"""
Diagnostic Engine route – POST /engine/differential-diagnosis
Accepts a list of symptom IDs, returns ranked Bayesian differential diagnosis.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from api.models import DiagnosisRequest, DiagnosisResult
from engine.differential_diagnosis import get_differential_diagnosis

router = APIRouter(prefix="/engine", tags=["Diagnostic Engine"])


@router.post("/differential-diagnosis", response_model=List[DiagnosisResult])
def differential_diagnosis(payload: DiagnosisRequest):
    """
    Generate a ranked differential diagnosis for the provided symptom IDs.
    Uses Bayesian posterior probability (sensitivity / specificity from associations).
    """
    if not payload.symptom_ids:
        raise HTTPException(status_code=422, detail="symptom_ids must not be empty")

    df = get_differential_diagnosis(payload.symptom_ids)

    if df.empty:
        return []

    return df.to_dict(orient="records")
