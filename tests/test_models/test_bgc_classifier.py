import numpy as np
import pytest
from src.models.bgc_classifier import BGCClassifier

def test_train_does_not_raise(X_y):
    X, y = X_y
    clf = BGCClassifier()
    clf.train(X, y)

def test_predict_proba_returns_1d_array(X_y):
    X, y = X_y
    clf = BGCClassifier()
    clf.train(X, y)
    scores = clf.predict_proba(X)
    assert scores.ndim == 1
    assert len(scores) == len(X)

def test_scores_between_0_and_1(X_y):
    X, y = X_y
    clf = BGCClassifier()
    clf.train(X, y)
    scores = clf.predict_proba(X)
    assert (scores >= 0.0).all() and (scores <= 1.0).all()

def test_save_and_load_produces_identical_scores(X_y, tmp_path):
    X, y = X_y
    clf = BGCClassifier()
    clf.train(X, y)
    path = tmp_path / "bgc.pkl"
    clf.save(path)
    loaded = BGCClassifier.load(path)
    np.testing.assert_array_almost_equal(loaded.predict_proba(X), clf.predict_proba(X))

def test_positive_class_scores_higher_than_negative(X_y):
    X, y = X_y
    clf = BGCClassifier()
    clf.train(X, y)
    scores = clf.predict_proba(X)
    assert scores[y == 1].mean() > scores[y == 0].mean()
