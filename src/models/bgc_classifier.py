import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

class BGCClassifier:
    def __init__(self):
        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            eval_metric="logloss",
        )

    def train(self, X: pd.DataFrame, y: pd.Series) -> None:
        self.model.fit(X, y)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X)[:, 1]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self.model, f)

    @classmethod
    def load(cls, path: Path) -> "BGCClassifier":
        instance = cls()
        with open(path, "rb") as f:
            instance.model = pickle.load(f)
        return instance
