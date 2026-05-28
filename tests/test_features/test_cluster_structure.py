import pytest
from src.pipeline.parser import BGCCandidate
from src.features.cluster_structure import extract_cluster_features

@pytest.fixture
def candidate_with_genes():
    return BGCCandidate(
        source_accession="TEST", region_id="TEST_0_10000",
        start=0, end=10000, sequence="ATGC" * 2500,
        genes=[
            {"start": 0, "end": 1000, "strand": 1, "domains": []},
            {"start": 1500, "end": 2500, "strand": 1, "domains": []},
            {"start": 3000, "end": 4000, "strand": -1, "domains": []},
        ],
        predicted_class=["polyketide"], contig_edge=False,
    )

@pytest.fixture
def empty_candidate():
    return BGCCandidate(
        source_accession="TEST", region_id="TEST_0_5000",
        start=0, end=5000, sequence="ATGC" * 1250,
        genes=[], predicted_class=[], contig_edge=True,
    )

def test_cluster_length(candidate_with_genes):
    assert extract_cluster_features(candidate_with_genes)["cluster_length"] == 10000

def test_gene_count(candidate_with_genes):
    assert extract_cluster_features(candidate_with_genes)["gene_count"] == 3

def test_gene_density(candidate_with_genes):
    assert abs(extract_cluster_features(candidate_with_genes)["gene_density"] - 0.3) < 0.01

def test_strand_ratio(candidate_with_genes):
    assert abs(extract_cluster_features(candidate_with_genes)["strand_ratio"] - (2/3)) < 0.01

def test_contig_edge_flag(candidate_with_genes, empty_candidate):
    assert extract_cluster_features(candidate_with_genes)["contig_edge"] == 0
    assert extract_cluster_features(empty_candidate)["contig_edge"] == 1

def test_empty_candidate_safe(empty_candidate):
    features = extract_cluster_features(empty_candidate)
    assert features["gene_count"] == 0
    assert features["gene_density"] == 0.0
    assert features["strand_ratio"] == 0.5
