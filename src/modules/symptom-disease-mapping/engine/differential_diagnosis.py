import pandas as pd
from typing import List, Dict, Any
from database.connection import get_collections

from engine.probability_calc import (
    calculate_likelihood_ratios,
    calculate_posterior_probability
)

def get_differential_diagnosis(symptom_ids: List[str]) -> pd.DataFrame:
    """
    Generate a ranked list of differential diagnoses based on inputted symptoms.
    Uses Bayesian probability mapping.
    
    Args:
        symptom_ids: List of symptom UUIDs the patient is experiencing.
        
    Returns:
        pd.DataFrame containing ranked diseases and their probabilities.
    """
    cols = get_collections()
    
    if not symptom_ids:
        return pd.DataFrame()
        
    # Fetch all unique diseases associated with ANY of the inputted symptoms
    associations_cursor = cols['symptom_disease_associations'].find({
        "symptom_id": {"$in": symptom_ids}
    })
    
    associations = list(associations_cursor)
    if not associations:
        return pd.DataFrame()
        
    # Group associations by disease
    # disease_id -> list of association dictionaries
    disease_assoc_map: Dict[str, List[Dict[str, Any]]] = {}
    disease_ids = set()
    
    for assoc in associations:
        did = assoc["disease_id"]
        disease_ids.add(did)
        if did not in disease_assoc_map:
            disease_assoc_map[did] = []
        disease_assoc_map[did].append(assoc)
        
    # Fetch required disease data (specifically  prevalence rate)
    diseases_cursor = cols['diseases'].find({
        "disease_id": {"$in": list(disease_ids)}
    })
    
    # Map disease info for quick lookup
    disease_map = {d["disease_id"]: d for d in diseases_cursor}
    
    results = []
    
    # Calculate posterior probability for each potential disease
    for disease_id, assoc_list in disease_assoc_map.items():
        disease_info = disease_map.get(disease_id)
        if not disease_info:
            continue
            
        # Get prior probability (prevalence rate)
        prior_prob = float(disease_info.get("prevalence_rate", 0.01))
        
        lr_plus_list = []
        matched_symptoms = []
        
        # Calculate Likelihood Ratios for each mapping
        for assoc in assoc_list:
            sens = float(assoc.get("sensitivity", 0.5))
            spec = float(assoc.get("specificity", 0.5))
            
            lr_plus, lr_minus = calculate_likelihood_ratios(sens, spec)
            lr_plus_list.append(lr_plus)
            matched_symptoms.append(assoc["symptom_id"])
            
        # Calculate final Bayesian probability
        posterior_prob = calculate_posterior_probability(prior_prob, lr_plus_list)
        
        # Calculate match percentage (how many of inputted symptoms match this disease?)
        match_percentage = (len(matched_symptoms) / len(symptom_ids)) * 100.0
        
        results.append({
            "disease_id": disease_id,
            "disease_name": disease_info.get("disease_name", "Unknown"),
            "icd11_code": disease_info.get("icd11_code", "N/A"),
            "matched_symptoms_count": len(matched_symptoms),
            "match_percentage": round(match_percentage, 1),
            "prior_probability": prior_prob,
            "posterior_probability_pct": round(posterior_prob * 100, 2)
        })
        
    if not results:
        return pd.DataFrame()
        
    # Create DataFrame and sort by posterior probability descending
    df = pd.DataFrame(results)
    df = df.sort_values(by="posterior_probability_pct", ascending=False).reset_index(drop=True)
    
    return df
