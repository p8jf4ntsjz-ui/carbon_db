"""
Data Quality Assessment — GHG Protocol Tier system.
"""

TIER_WEIGHTS = {
    'supplier_specific': 1.0,   # Tier 1 — meilleure qualité
    'fuel_based':        0.9,
    'average_data':      0.7,   # Tier 2
    'hybrid':            0.75,
    'spend_based':       0.5,   # Tier 3 — estimation
}

def assess_quality(calc_method: str, has_supplier_data: bool,
                   is_verified: bool, data_age_years: int) -> dict:
    base_score = TIER_WEIGHTS.get(calc_method, 0.5)

    # Bonus/malus
    if has_supplier_data:  base_score = min(1.0, base_score + 0.1)
    if is_verified:        base_score = min(1.0, base_score + 0.05)
    if data_age_years > 2: base_score = max(0.1, base_score - 0.1 * (data_age_years - 2))

    if   base_score >= 0.85: tier, label = 1, 'Élevée'
    elif base_score >= 0.65: tier, label = 2, 'Moyenne'
    else:                    tier, label = 3, 'Faible (estimation)'

    return {
        'score':     round(base_score, 2),
        'tier':      tier,
        'label':     label,
        'confidence': round(base_score, 2),
    }