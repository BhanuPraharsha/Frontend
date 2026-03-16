"""
Bayesian probability engine for symptom-disease mapping.
Calculates association strengths and diagnostic probabilities.
"""

def calculate_likelihood_ratios(sensitivity: float, specificity: float) -> tuple[float, float]:
    """
    Calculate Positive (LR+) and Negative (LR-) Likelihood Ratios.
    
    LR+ = Sensitivity / (1 - Specificity)
    LR- = (1 - Sensitivity) / Specificity
    
    Returns:
        tuple: (LR+, LR-)
    """
    # Handle edge cases to prevent division by zero or infinite ratios
    sens = min(max(sensitivity, 0.001), 0.999)
    spec = min(max(specificity, 0.001), 0.999)
    
    lr_plus = sens / (1.0 - spec)
    lr_minus = (1.0 - sens) / spec
    
    return lr_plus, lr_minus

def odds_to_probability(odds: float) -> float:
    """Convert odds to probability."""
    return odds / (1.0 + odds)

def probability_to_odds(probability: float) -> float:
    """Convert probability to odds."""
    prob = min(max(probability, 0.001), 0.999) # Prevent infinity
    return prob / (1.0 - prob)

def calculate_posterior_probability(prior_probability: float, lr_plus_list: list[float]) -> float:
    """
    Calculate the posterior probability of a disease given a set of present symptoms.
    Uses Naive Bayes assumption (symptoms are conditionally independent).
    
    Args:
        prior_probability: The baseline prevalence of the disease (0.0 to 1.0)
        lr_plus_list: List of Positive Likelihood Ratios for observed symptoms
        
    Returns:
        float: The updated posterior probability (0.0 to 1.0)
    """
    if not lr_plus_list:
        return prior_probability
        
    prior_odds = probability_to_odds(prior_probability)
    
    # Multiply prior odds by the product of all positive likelihood ratios
    posterior_odds = prior_odds
    for lr_plus in lr_plus_list:
        posterior_odds *= lr_plus
        
    return odds_to_probability(posterior_odds)

