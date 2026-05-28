import random
from pathlib import Path
import pandas as pd
from src.pipeline.parser import BGCCandidate
from src.features.extractor import build_feature_matrix

def sample_negative_regions(
    sequence: str,
    accession: str,
    bgc_regions: list[tuple[int, int]],
    region_length: int = 10000,
    n_samples: int = 3,
) -> list[BGCCandidate]:
    candidates = []
    attempts = 0
    max_attempts = n_samples * 20

    while len(candidates) < n_samples and attempts < max_attempts:
        attempts += 1
        start = random.randint(0, max(0, len(sequence) - region_length))
        end = start + region_length
        overlaps = any(s < end and e > start for s, e in bgc_regions)
        if not overlaps:
            candidates.append(BGCCandidate(
                source_accession=accession,
                region_id=f"{accession}_{start}_{end}",
                start=start,
                end=end,
                sequence=sequence[start:end],
                genes=[],
                predicted_class=[],
                contig_edge=False,
            ))
    return candidates

def build_labeled_dataset(
    positives: list[BGCCandidate],
    negatives: list[BGCCandidate],
    output_path: Path,
) -> pd.DataFrame:
    pos_df = build_feature_matrix(positives, labels=[1] * len(positives))
    neg_df = build_feature_matrix(negatives, labels=[0] * len(negatives))
    df = pd.concat([pos_df, neg_df]).sample(frac=1, random_state=42)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path)
    return df
