import numpy as np
import pandas as pd
import pytest

FEATURE_COLS = [
    "cluster_length", "gene_count", "gene_density", "strand_ratio",
    "contig_edge", "avg_gene_length", "gc_content", "gc1_content",
    "gc2_content", "gc3_content", "sequence_length",
    "domain_PF00109", "domain_PF02801", "domain_PF00698", "domain_PF00501",
    "domain_PF00550", "domain_PF13193", "domain_PF00668", "domain_PF01397",
    "domain_PF03936", "domain_PF00535", "domain_PF02458", "domain_PF02364",
    "domain_PF02576", "domain_PF05402", "domain_PF00106",
]

@pytest.fixture
def synthetic_dataset():
    rng = np.random.default_rng(42)
    n_pos, n_neg = 60, 60
    X_pos = rng.random((n_pos, len(FEATURE_COLS)))
    X_pos[:, 0] *= 30000
    X_pos[:, 6] += 0.4
    X_pos[:, 11:] = rng.integers(0, 2, (n_pos, 15))

    X_neg = rng.random((n_neg, len(FEATURE_COLS)))
    X_neg[:, 0] *= 5000
    X_neg[:, 6] *= 0.3
    X_neg[:, 11:] = 0

    X = np.vstack([X_pos, X_neg])
    y = np.array([1] * n_pos + [0] * n_neg)
    df = pd.DataFrame(X, columns=FEATURE_COLS)
    df["label"] = y
    return df

@pytest.fixture
def feature_cols():
    return FEATURE_COLS

@pytest.fixture
def X_y(synthetic_dataset, feature_cols):
    X = synthetic_dataset[feature_cols]
    y = synthetic_dataset["label"]
    return X, y

@pytest.fixture
def X_pos(synthetic_dataset, feature_cols):
    df = synthetic_dataset
    return df.loc[df["label"] == 1, feature_cols]
