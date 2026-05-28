import pytest
from src.models.bgc_classifier import BGCClassifier
from src.models.explainer import SHAPExplainer

@pytest.fixture
def trained_bgc_clf(X_y):
    X, y = X_y
    clf = BGCClassifier()
    clf.train(X, y)
    return clf, X

def test_explain_returns_dict(trained_bgc_clf):
    clf, X = trained_bgc_clf
    explainer = SHAPExplainer(clf.model)
    result = explainer.explain(X.iloc[:5])
    assert isinstance(result, dict)

def test_explain_returns_up_to_10_features(trained_bgc_clf):
    clf, X = trained_bgc_clf
    explainer = SHAPExplainer(clf.model)
    result = explainer.explain(X.iloc[:5])
    assert len(result) <= 10

def test_explain_keys_are_feature_names(trained_bgc_clf, feature_cols):
    clf, X = trained_bgc_clf
    explainer = SHAPExplainer(clf.model)
    result = explainer.explain(X)
    assert all(k in feature_cols for k in result)

def test_explain_values_are_non_negative(trained_bgc_clf):
    clf, X = trained_bgc_clf
    explainer = SHAPExplainer(clf.model)
    result = explainer.explain(X)
    assert all(v >= 0.0 for v in result.values())
