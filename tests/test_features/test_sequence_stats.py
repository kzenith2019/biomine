import pytest
from src.pipeline.parser import BGCCandidate
from src.features.sequence_stats import compute_gc_content, extract_sequence_features

def test_gc_content_all_gc():
    assert compute_gc_content("GCGCGCGC") == 1.0

def test_gc_content_all_at():
    assert compute_gc_content("ATATATAT") == 0.0

def test_gc_content_half():
    assert compute_gc_content("ATGC") == 0.5

def test_gc_content_empty():
    assert compute_gc_content("") == 0.0

def test_extract_sequence_features_returns_all_keys():
    candidate = BGCCandidate(
        source_accession="T", region_id="T_0_12",
        start=0, end=12, sequence="ATGCATGCATGC",
        genes=[], predicted_class=[], contig_edge=False,
    )
    features = extract_sequence_features(candidate)
    assert "gc_content" in features
    assert "gc1_content" in features
    assert "gc2_content" in features
    assert "gc3_content" in features
    assert "sequence_length" in features

def test_extract_sequence_features_values():
    candidate = BGCCandidate(
        source_accession="T", region_id="T_0_9",
        start=0, end=9, sequence="ATGATGATG",
        genes=[], predicted_class=[], contig_edge=False,
    )
    features = extract_sequence_features(candidate)
    assert features["gc_content"] < 0.5
    assert features["sequence_length"] == 9
