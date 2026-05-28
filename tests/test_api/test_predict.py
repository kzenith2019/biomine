from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

VALID_FASTA = b">test_seq\nATGCATGCATGCATGCATGCATGCATGCATGCATGC\n"

def _mock_result():
    r = MagicMock()
    r.region_id = "test_seq_submitted"
    r.bgc_score = 0.85
    r.bioactivity_class = "antibiotic"
    r.bioactivity_score = 0.72
    r.novelty_score = 0.91
    r.drug_potential_score = 0.83
    r.top_features = {"gc_content": 0.45}
    return r

def test_predict_returns_200_for_valid_fasta():
    with patch("src.api.routes.predict.get_predictor") as mock:
        mock.return_value.predict.return_value = _mock_result()
        response = client.post(
            "/api/predict",
            files={"file": ("genome.fasta", VALID_FASTA, "text/plain")},
        )
    assert response.status_code == 200

def test_predict_response_has_required_fields():
    with patch("src.api.routes.predict.get_predictor") as mock:
        mock.return_value.predict.return_value = _mock_result()
        response = client.post(
            "/api/predict",
            files={"file": ("genome.fasta", VALID_FASTA, "text/plain")},
        )
    data = response.json()
    for field in ("bgc_score", "bioactivity_class", "novelty_score", "drug_potential_score", "top_features"):
        assert field in data, f"Missing field: {field}"

def test_predict_scores_are_floats():
    with patch("src.api.routes.predict.get_predictor") as mock:
        mock.return_value.predict.return_value = _mock_result()
        response = client.post(
            "/api/predict",
            files={"file": ("genome.fasta", VALID_FASTA, "text/plain")},
        )
    data = response.json()
    assert isinstance(data["bgc_score"], float)
    assert isinstance(data["novelty_score"], float)

def test_predict_returns_400_for_empty_file():
    response = client.post(
        "/api/predict",
        files={"file": ("empty.fasta", b"", "text/plain")},
    )
    assert response.status_code == 400
