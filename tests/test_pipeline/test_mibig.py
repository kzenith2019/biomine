import json
from pathlib import Path
import pytest
from src.pipeline.mibig import parse_mibig_record, load_all_mibig, BGCRecord

@pytest.fixture
def sample_json(tmp_path):
    data = {
        "cluster": {
            "mibig_accession": "BGC0000001",
            "organism_name": "Streptomyces coelicolor",
            "taxonomy": ["Bacteria", "Actinobacteria", "Streptomyces"],
            "compounds": [{"compound": "actinorhodin"}],
            "biosyn_class": ["Polyketide"],
            "loci": {"accession": "AL645882", "start_coord": 1000, "end_coord": 31000}
        }
    }
    p = tmp_path / "BGC0000001.json"
    p.write_text(json.dumps(data))
    return p

def test_parse_mibig_record_returns_bgc_record(sample_json):
    record = parse_mibig_record(sample_json)
    assert isinstance(record, BGCRecord)
    assert record.bgc_id == "BGC0000001"
    assert record.organism == "Streptomyces coelicolor"
    assert record.biosynthetic_class == ["Polyketide"]
    assert record.gene_cluster_length == 30000

def test_parse_mibig_record_handles_empty_cluster(tmp_path):
    p = tmp_path / "empty.json"
    p.write_text(json.dumps({"cluster": {}}))
    record = parse_mibig_record(p)
    assert record.bgc_id == ""
    assert record.gene_cluster_length == 0

def test_load_all_mibig_returns_list(tmp_path, sample_json):
    records = load_all_mibig(tmp_path)
    assert len(records) == 1
    assert records[0].bgc_id == "BGC0000001"
