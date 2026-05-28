import json
import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.db import init_db, insert_prediction

client = TestClient(app)

def _sample(i):
    return {
        "region_id": f"BGC_{i:04d}",
        "source_accession": f"ACC_{i}",
        "bgc_score": round(0.5 + i * 0.1, 2),
        "bioactivity_class": "antibiotic" if i % 2 == 0 else "antifungal",
        "bioactivity_score": 0.6,
        "novelty_score": round(0.4 + i * 0.1, 2),
        "drug_potential_score": round(0.5 + i * 0.1, 2),
        "top_features": json.dumps({"gc_content": 0.3}),
        "start": 0,
        "end_coord": 10000,
        "predicted_class": json.dumps(["Polyketide"]),
    }

@pytest.fixture(autouse=True)
def seeded_db(tmp_path, monkeypatch):
    import src.api.db as db_module
    test_db = tmp_path / "test.db"
    monkeypatch.setattr(db_module, "DB_PATH", test_db)
    init_db()
    for i in range(5):
        insert_prediction(_sample(i))

def test_explore_returns_200():
    assert client.get("/api/explore").status_code == 200

def test_explore_returns_all_by_default():
    data = client.get("/api/explore").json()
    assert data["total"] == 5
    assert len(data["results"]) == 5

def test_explore_filters_by_bioactivity():
    data = client.get("/api/explore?bioactivity_class=antibiotic").json()
    assert all(r["bioactivity_class"] == "antibiotic" for r in data["results"])

def test_explore_filters_by_min_novelty():
    data = client.get("/api/explore?min_novelty=0.7").json()
    assert all(r["novelty_score"] >= 0.7 for r in data["results"])

def test_explore_respects_limit():
    data = client.get("/api/explore?limit=2").json()
    assert len(data["results"]) == 2
    assert data["total"] == 5
