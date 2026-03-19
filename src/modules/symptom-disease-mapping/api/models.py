"""
Pydantic models for Module M7 API request/response validation.
"""

from typing import List, Optional
from pydantic import BaseModel


# Symptom Models

class SymptomCreate(BaseModel):
    symptom_id: str
    symptom_code: str
    symptom_name: str
    body_system: str


class SymptomUpdate(BaseModel):
    symptom_name: str


class SymptomOut(BaseModel):
    symptom_id: str
    symptom_code: str
    symptom_name: str
    body_system: str


# Disease Models

class DiseaseCreate(BaseModel):
    disease_id: str
    icd11_code: str
    disease_name: str
    prevalence_rate: float


class DiseaseUpdate(BaseModel):
    disease_name: str


class DiseaseOut(BaseModel):
    disease_id: str
    icd11_code: str
    disease_name: str
    prevalence_rate: float


# Association Model 

class AssociationOut(BaseModel):
    symptom_id: str
    symptom_name: Optional[str] = None
    disease_id: str
    disease_name: Optional[str] = None
    association_strength: Optional[float] = None
    sensitivity: Optional[float] = None
    specificity: Optional[float] = None


# Diagnosis Rule Model 

class DiagnosisRuleOut(BaseModel):
    rule_id: str
    rule_name: str
    symptom_combination: List[str]         
    suggested_disease: str                  
    confidence_modifier: float
    priority: int


# Diagnostic Engine Models 

class DiagnosisRequest(BaseModel):
    symptom_ids: List[str]


class DiagnosisResult(BaseModel):
    disease_id: str
    disease_name: str
    icd11_code: str
    matched_symptoms_count: int
    match_percentage: float
    prior_probability: float
    posterior_probability_pct: float


# Stats Model 

class StatsOut(BaseModel):
    symptoms: int
    diseases: int
    associations: int
    diagnosis_rules: int
