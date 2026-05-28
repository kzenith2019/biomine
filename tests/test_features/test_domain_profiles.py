import pytest
from src.pipeline.parser import BGCCandidate
from src.features.domain_profiles import extract_domain_features, BGC_PFAM_DOMAINS

@pytest.fixture
def candidate_with_pks_domain():
    return BGCCandidate(
        source_accession="TEST", region_id="TEST_0_5000",
        start=0, end=5000, sequence="ATGC" * 1250,
        genes=[{"start": 0, "end": 1000, "strand": 1,
                "domains": [{"pfam_id": "PF00109", "name": "ketoacyl-synt"}]}],
        predicted_class=["polyketide"], contig_edge=False,
    )

@pytest.fixture
def candidate_no_domains():
    return BGCCandidate(
        source_accession="TEST", region_id="TEST_0_2000",
        start=0, end=2000, sequence="ATGC" * 500,
        genes=[{"start": 0, "end": 500, "strand": 1, "domains": []}],
        predicted_class=[], contig_edge=False,
    )

def test_known_domain_is_present(candidate_with_pks_domain):
    assert extract_domain_features(candidate_with_pks_domain)["domain_PF00109"] == 1

def test_absent_domain_is_zero(candidate_with_pks_domain):
    assert extract_domain_features(candidate_with_pks_domain)["domain_PF00501"] == 0

def test_no_domains_all_zero(candidate_no_domains):
    assert all(v == 0 for v in extract_domain_features(candidate_no_domains).values())

def test_feature_count_matches_domain_list(candidate_with_pks_domain):
    assert len(extract_domain_features(candidate_with_pks_domain)) == len(BGC_PFAM_DOMAINS)

def test_all_keys_prefixed_with_domain(candidate_with_pks_domain):
    assert all(k.startswith("domain_") for k in extract_domain_features(candidate_with_pks_domain))
