import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from src.features.homology import compute_mibig_similarity

@pytest.fixture
def mibig_features_parquet(tmp_path):
    df = pd.DataFrame({
        "cluster_length": [10000, 20000, 5000],
        "gene_count": [10, 20, 5],
        "gc_content": [0.7, 0.65, 0.5],
    })
    path = tmp_path / "mibig_features.parquet"
    df.to_parquet(path)
    return path

def test_identical_candidate_returns_high_similarity(mibig_features_parquet):
    score = compute_mibig_similarity(
        {"cluster_length": 10000, "gene_count": 10, "gc_content": 0.7},
        mibig_features_parquet
    )
    assert score > 0.99

def test_dissimilar_candidate_returns_low_similarity(mibig_features_parquet):
    # All weight on gc_content only → direction [0,0,1], far from MIBiG vectors dominated by cluster_length
    score = compute_mibig_similarity(
        {"cluster_length": 0, "gene_count": 0, "gc_content": 1.0},
        mibig_features_parquet
    )
    assert score < 0.01

def test_score_is_between_zero_and_one(mibig_features_parquet):
    score = compute_mibig_similarity(
        {"cluster_length": 8000, "gene_count": 8, "gc_content": 0.6},
        mibig_features_parquet
    )
    assert 0.0 <= score <= 1.0

def test_zero_vector_returns_zero(mibig_features_parquet):
    score = compute_mibig_similarity(
        {"cluster_length": 0, "gene_count": 0, "gc_content": 0.0},
        mibig_features_parquet
    )
    assert score == 0.0
