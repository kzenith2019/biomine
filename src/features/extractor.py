import pandas as pd
from src.pipeline.parser import BGCCandidate
from src.features.cluster_structure import extract_cluster_features
from src.features.sequence_stats import extract_sequence_features
from src.features.domain_profiles import extract_domain_features

def extract_all_features(candidate: BGCCandidate) -> dict:
    features = {}
    features.update(extract_cluster_features(candidate))
    features.update(extract_sequence_features(candidate))
    features.update(extract_domain_features(candidate))
    return features

def build_feature_matrix(
    candidates: list[BGCCandidate],
    labels: list[int] | None = None,
) -> pd.DataFrame:
    rows = []
    index = []
    for candidate in candidates:
        rows.append(extract_all_features(candidate))
        index.append(candidate.region_id)
    df = pd.DataFrame(rows, index=index)
    if labels is not None:
        df["label"] = labels
    return df
