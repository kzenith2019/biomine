from dataclasses import dataclass
from pathlib import Path
import numpy as np
import pandas as pd
from src.models.bgc_classifier import BGCClassifier
from src.models.bioactivity import BioactivityClassifier
from src.models.novelty import NoveltyScorer
from src.models.drug_potential import compute_drug_potential
from src.models.explainer import SHAPExplainer
from src.pipeline.parser import BGCCandidate
from src.features.extractor import extract_all_features

@dataclass
class PredictionResult:
    region_id: str
    bgc_score: float
    bioactivity_class: str
    bioactivity_score: float
    novelty_score: float
    drug_potential_score: float
    top_features: dict[str, float]

class BioMinePredictor:
    def __init__(self, model_dir: Path):
        self.bgc_clf = BGCClassifier.load(model_dir / "bgc_classifier.pkl")
        self.bio_clf = BioactivityClassifier.load(model_dir / "bioactivity.pkl")
        self.novelty = NoveltyScorer.load(model_dir / "novelty.pkl")
        self.explainer = SHAPExplainer(self.bgc_clf.model)

    def predict(self, candidate: BGCCandidate) -> PredictionResult:
        features = extract_all_features(candidate)
        X = pd.DataFrame([features])

        bgc_score = float(self.bgc_clf.predict_proba(X)[0])
        top_class, top_proba = self.bio_clf.predict_max_class(X)
        nov_score = float(self.novelty.score(X)[0])
        drug_score = float(compute_drug_potential(
            np.array([bgc_score]),
            np.array([float(top_proba[0])]),
            np.array([nov_score]),
        )[0])

        return PredictionResult(
            region_id=candidate.region_id,
            bgc_score=bgc_score,
            bioactivity_class=top_class[0],
            bioactivity_score=float(top_proba[0]),
            novelty_score=nov_score,
            drug_potential_score=drug_score,
            top_features=self.explainer.explain(X),
        )
