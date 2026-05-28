import json
import pytest
from src.api.db import init_db, insert_prediction, query_predictions

@pytest.fixture
def db_path(tmp_path, monkeypatch):
    import src.api.db as db_module
    path = tmp_path / "test.db"
    monkeypatch.setattr(db_module, "DB_PATH", path)
    init_db()
    return path

def _sample(i):
    return {
        "region_id": f"BGC_{i:04d}",
        "source_accession": f"ACC_{i}",
        "bgc_score": 0.5 + i * 0.1,
        "bioactivity_class": "antibiotic" if i % 2 == 0 else "antifungal",
        "bioactivity_score": 0.6,
        "novelty_score": 0.4 + i * 0.1,
        "drug_potential_score": 0.5 + i * 0.1,
        "top_features": json.dumps({"gc_content": 0.3}),
        "start": 0,
        "end_coord": 10000,
        "predicted_class": json.dumps(["Polyketide"]),
    }

def test_insert_and_query_all(db_path):
    for i in range(3):
        insert_prediction(_sample(i))
    rows, total = query_predictions()
    assert total == 3
    assert len(rows) == 3

def test_filter_by_bioactivity(db_path):
    for i in range(4):
        insert_prediction(_sample(i))
    rows, total = query_predictions(bioactivity_class="antibiotic")
    assert all(r["bioactivity_class"] == "antibiotic" for r in rows)

def test_filter_by_min_novelty(db_path):
    for i in range(5):
        insert_prediction(_sample(i))
    rows, total = query_predictions(min_novelty=0.7)
    assert all(r["novelty_score"] >= 0.7 for r in rows)

def test_results_ordered_by_drug_potential_desc(db_path):
    for i in range(3):
        insert_prediction(_sample(i))
    rows, _ = query_predictions()
    scores = [r["drug_potential_score"] for r in rows]
    assert scores == sorted(scores, reverse=True)
