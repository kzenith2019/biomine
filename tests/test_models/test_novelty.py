import numpy as np
import pytest
from src.models.novelty import NoveltyScorer

def test_train_does_not_raise(X_pos):
    scorer = NoveltyScorer()
    scorer.train(X_pos)

def test_score_returns_1d_array(X_pos, X_y):
    X, _ = X_y
    scorer = NoveltyScorer()
    scorer.train(X_pos)
    scores = scorer.score(X)
    assert scores.ndim == 1
    assert len(scores) == len(X)

def test_scores_between_0_and_1(X_pos, X_y):
    X, _ = X_y
    scorer = NoveltyScorer()
    scorer.train(X_pos)
    scores = scorer.score(X)
    assert (scores >= 0.0).all() and (scores <= 1.0).all()

def test_known_bgcs_score_lower_than_novel(X_pos, X_y):
    X, y = X_y
    scorer = NoveltyScorer()
    scorer.train(X_pos)
    scores = scorer.score(X)
    assert scores[y == 1].mean() < scores[y == 0].mean()

def test_save_and_load_produces_identical_scores(X_pos, X_y, tmp_path):
    X, _ = X_y
    scorer = NoveltyScorer()
    scorer.train(X_pos)
    path = tmp_path / "novelty.pkl"
    scorer.save(path)
    loaded = NoveltyScorer.load(path)
    np.testing.assert_array_almost_equal(loaded.score(X), scorer.score(X))
