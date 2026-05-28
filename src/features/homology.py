import numpy as np
import pandas as pd
from pathlib import Path

def compute_mibig_similarity(candidate_features: dict, mibig_features_path: Path) -> float:
    mibig_df = pd.read_parquet(mibig_features_path)
    cols = mibig_df.columns.tolist()
    candidate_vec = np.array([candidate_features.get(c, 0.0) for c in cols], dtype=float)
    candidate_norm = np.linalg.norm(candidate_vec)
    if candidate_norm == 0.0:
        return 0.0
    mibig_vecs = mibig_df.values.astype(float)
    row_norms = np.linalg.norm(mibig_vecs, axis=1)
    safe_norms = np.where(row_norms == 0, 1e-8, row_norms)
    similarities = (mibig_vecs @ candidate_vec) / (safe_norms * candidate_norm)
    return float(np.clip(np.max(similarities), 0.0, 1.0))
