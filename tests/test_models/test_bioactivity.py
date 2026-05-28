import numpy as np
import pytest
from src.models.bioactivity import BioactivityClassifier, BIOACTIVITY_CLASSES

@pytest.fixture
def trained_clf(X_y):
    X, y = X_y
    labels = [["antibiotic"] if yi == 1 else ["none"] for yi in y]
    clf = BioactivityClassifier()
    clf.train(X, labels)
    return clf, X

def test_train_does_not_raise(X_y):
    X, y = X_y
    labels = [["antibiotic"] if yi == 1 else ["none"] for yi in y]
    clf = BioactivityClassifier()
    clf.train(X, labels)

def test_predict_proba_returns_dict_of_arrays(trained_clf):
    clf, X = trained_clf
    result = clf.predict_proba(X)
    assert isinstance(result, dict)
    assert set(result.keys()) == set(BIOACTIVITY_CLASSES)
    for arr in result.values():
        assert len(arr) == len(X)

def test_probabilities_between_0_and_1(trained_clf):
    clf, X = trained_clf
    for cls, arr in clf.predict_proba(X).items():
        assert (arr >= 0.0).all() and (arr <= 1.0).all(), f"{cls} out of range"

def test_predict_max_class_returns_string_and_score(trained_clf):
    clf, X = trained_clf
    classes, scores = clf.predict_max_class(X)
    assert len(classes) == len(X)
    assert all(c in BIOACTIVITY_CLASSES for c in classes)
    assert (scores >= 0.0).all() and (scores <= 1.0).all()

def test_save_and_load_matches(trained_clf, tmp_path):
    clf, X = trained_clf
    path = tmp_path / "bio.pkl"
    clf.save(path)
    loaded = BioactivityClassifier.load(path)
    original = clf.predict_proba(X)
    reloaded = loaded.predict_proba(X)
    for cls in BIOACTIVITY_CLASSES:
        np.testing.assert_array_almost_equal(original[cls], reloaded[cls])
