import pandas as pd
import pytest
from src.pipeline.parser import BGCCandidate
from src.features.extractor import extract_all_features, build_feature_matrix

@pytest.fixture
def simple_candidate():
    return BGCCandidate(
        source_accession="TEST", region_id="TEST_0_5000",
        start=0, end=5000, sequence="ATGCATGC" * 625,
        genes=[{"start": 0, "end": 1000, "strand": 1,
                "domains": [{"pfam_id": "PF00109", "name": "ketoacyl-synt"}]}],
        predicted_class=["polyketide"], contig_edge=False,
    )

def test_extract_all_features_returns_dict(simple_candidate):
    assert isinstance(extract_all_features(simple_candidate), dict)

def test_extract_all_features_has_all_groups(simple_candidate):
    features = extract_all_features(simple_candidate)
    assert "cluster_length" in features
    assert "gc_content" in features
    assert "domain_PF00109" in features

def test_extract_all_features_no_region_id_key(simple_candidate):
    assert "region_id" not in extract_all_features(simple_candidate)

def test_build_feature_matrix_shape(simple_candidate):
    df = build_feature_matrix([simple_candidate, simple_candidate], [1, 0])
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "label" in df.columns

def test_build_feature_matrix_index_is_region_id(simple_candidate):
    df = build_feature_matrix([simple_candidate], [1])
    assert df.index[0] == "TEST_0_5000"

def test_build_feature_matrix_no_label_column_when_omitted(simple_candidate):
    df = build_feature_matrix([simple_candidate])
    assert "label" not in df.columns
