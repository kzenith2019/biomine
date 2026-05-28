import numpy as np
import pytest
from pathlib import Path
from src.pipeline.parser import BGCCandidate
from src.models.bgc_classifier import BGCClassifier
from src.models.bioactivity import BioactivityClassifier
from src.models.novelty import NoveltyScorer
from src.models.predictor import BioMinePredictor, PredictionResult

@pytest.fixture
def model_dir(tmp_path, X_y, X_pos):
    X, y = X_y
    labels = [["antibiotic"] if yi == 1 else ["none"] for yi in y]

    bgc_clf = BGCClassifier()
    bgc_clf.train(X, y)
    bgc_clf.save(tmp_path / "bgc_classifier.pkl")

    bio_clf = BioactivityClassifier()
    bio_clf.train(X, labels)
    bio_clf.save(tmp_path / "bioactivity.pkl")

    novelty = NoveltyScorer()
    novelty.train(X_pos)
    novelty.save(tmp_path / "novelty.pkl")

    return tmp_path

@pytest.fixture
def sample_candidate():
    return BGCCandidate(
        source_accession="TEST",
        region_id="TEST_0_10000",
        start=0, end=10000,
        sequence="ATGCGCATGCGC" * 833,
        genes=[{"start": 0, "end": 1000, "strand": 1,
                "domains": [{"pfam_id": "PF00109", "name": "ketoacyl-synt"}]}],
        predicted_class=["Polyketide"],
        contig_edge=False,
    )

def test_predictor_loads_without_error(model_dir):
    assert BioMinePredictor(model_dir) is not None

def test_predict_returns_prediction_result(model_dir, sample_candidate):
    result = BioMinePredictor(model_dir).predict(sample_candidate)
    assert isinstance(result, PredictionResult)

def test_prediction_result_has_correct_region_id(model_dir, sample_candidate):
    result = BioMinePredictor(model_dir).predict(sample_candidate)
    assert result.region_id == "TEST_0_10000"

def test_all_scores_between_0_and_1(model_dir, sample_candidate):
    result = BioMinePredictor(model_dir).predict(sample_candidate)
    assert 0.0 <= result.bgc_score <= 1.0
    assert 0.0 <= result.bioactivity_score <= 1.0
    assert 0.0 <= result.novelty_score <= 1.0
    assert 0.0 <= result.drug_potential_score <= 1.0

def test_top_features_is_dict(model_dir, sample_candidate):
    result = BioMinePredictor(model_dir).predict(sample_candidate)
    assert isinstance(result.top_features, dict)
