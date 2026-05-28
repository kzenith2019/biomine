import pandas as pd
import pytest
from pathlib import Path
from src.pipeline.parser import BGCCandidate
from src.pipeline.dataset import sample_negative_regions, build_labeled_dataset

@pytest.fixture
def long_sequence():
    return "ATGCATGCATGC" * 5000  # 60,000 bp

def test_sample_negative_returns_candidate_list(long_sequence):
    regions = sample_negative_regions(
        sequence=long_sequence,
        accession="NC_000001",
        bgc_regions=[(1000, 5000)],
        region_length=2000,
        n_samples=3,
    )
    assert isinstance(regions, list)
    assert len(regions) <= 3
    assert all(isinstance(r, BGCCandidate) for r in regions)

def test_negative_regions_avoid_bgc_overlap(long_sequence):
    bgc_regions = [(0, 10000)]
    regions = sample_negative_regions(
        sequence=long_sequence,
        accession="NC_000001",
        bgc_regions=bgc_regions,
        region_length=5000,
        n_samples=5,
    )
    for r in regions:
        assert not (r.start < 10000 and r.end > 0)

def test_build_labeled_dataset_has_both_labels(tmp_path):
    pos = [BGCCandidate("T", "T_0_5000", 0, 5000, "ATGC" * 1250, [], ["polyketide"], False)]
    neg = [BGCCandidate("T", "T_10000_15000", 10000, 15000, "ATGC" * 1250, [], [], False)]
    output_path = tmp_path / "dataset.parquet"
    df = build_labeled_dataset(positives=pos, negatives=neg, output_path=output_path)
    assert set(df["label"].unique()) == {0, 1}
    assert output_path.exists()
