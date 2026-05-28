import numpy as np
import pytest
from src.models.drug_potential import compute_drug_potential, BGC_WEIGHT, BIOACTIVITY_WEIGHT, NOVELTY_WEIGHT

def test_weights_sum_to_one():
    assert abs(BGC_WEIGHT + BIOACTIVITY_WEIGHT + NOVELTY_WEIGHT - 1.0) < 1e-9

def test_all_zeros_returns_zero():
    result = compute_drug_potential(np.array([0.0]), np.array([0.0]), np.array([0.0]))
    assert result[0] == 0.0

def test_all_ones_returns_one():
    result = compute_drug_potential(np.array([1.0]), np.array([1.0]), np.array([1.0]))
    assert abs(result[0] - 1.0) < 1e-9

def test_output_shape_matches_input():
    result = compute_drug_potential(np.random.rand(10), np.random.rand(10), np.random.rand(10))
    assert result.shape == (10,)

def test_higher_scores_produce_higher_potential():
    low = compute_drug_potential(np.array([0.2]), np.array([0.2]), np.array([0.2]))
    high = compute_drug_potential(np.array([0.9]), np.array([0.9]), np.array([0.9]))
    assert high[0] > low[0]
