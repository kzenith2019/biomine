import numpy as np

BGC_WEIGHT = 0.40
BIOACTIVITY_WEIGHT = 0.35
NOVELTY_WEIGHT = 0.25

def compute_drug_potential(
    bgc_scores: np.ndarray,
    bioactivity_scores: np.ndarray,
    novelty_scores: np.ndarray,
) -> np.ndarray:
    return (
        BGC_WEIGHT * bgc_scores
        + BIOACTIVITY_WEIGHT * bioactivity_scores
        + NOVELTY_WEIGHT * novelty_scores
    )
