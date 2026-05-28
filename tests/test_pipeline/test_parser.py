import json
from pathlib import Path
import pytest
from src.pipeline.parser import parse_antismash_output, BGCCandidate

@pytest.fixture
def antismash_json(tmp_path):
    data = {
        "records": [
            {
                "id": "AL645882",
                "seq": {"data": "ATGC" * 10000},
                "areas": [
                    {
                        "start": 100,
                        "end": 900,
                        "products": ["polyketide"],
                        "contig_edge": False,
                        "cds_detail": [
                            {
                                "start": 100,
                                "end": 500,
                                "strand": 1,
                                "domains": [{"pfam_id": "PF00109", "name": "ketoacyl-synt"}]
                            }
                        ]
                    }
                ]
            }
        ]
    }
    p = tmp_path / "result.json"
    p.write_text(json.dumps(data))
    return p

def test_parse_returns_bgc_candidates(antismash_json):
    candidates = parse_antismash_output(antismash_json)
    assert len(candidates) == 1
    assert isinstance(candidates[0], BGCCandidate)

def test_candidate_has_correct_region(antismash_json):
    candidates = parse_antismash_output(antismash_json)
    c = candidates[0]
    assert c.source_accession == "AL645882"
    assert c.start == 100
    assert c.end == 900
    assert c.predicted_class == ["polyketide"]
    assert c.contig_edge is False

def test_candidate_sequence_sliced_correctly(antismash_json):
    candidates = parse_antismash_output(antismash_json)
    c = candidates[0]
    assert len(c.sequence) == 800

def test_candidate_genes_parsed(antismash_json):
    candidates = parse_antismash_output(antismash_json)
    c = candidates[0]
    assert len(c.genes) == 1
    assert c.genes[0]["domains"][0]["pfam_id"] == "PF00109"

def test_empty_records_returns_empty_list(tmp_path):
    p = tmp_path / "empty.json"
    p.write_text(json.dumps({"records": []}))
    assert parse_antismash_output(p) == []
