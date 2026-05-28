import pickle
from pathlib import Path
import numpy as np
import pandas as pd
from xgboost import XGBClassifier

BIOACTIVITY_CLASSES = ["antibiotic", "antifungal", "anticancer", "immunosuppressant", "other"]

class BioactivityClassifier:
    def __init__(self):
        self.classes = BIOACTIVITY_CLASSES
        self.models: dict[str, XGBClassifier] = {}
        self._trained: set[str] = set()

    def train(self, X: pd.DataFrame, y_labels: list[list[str]]) -> None:
        for cls in self.classes:
            y_binary = np.array([1 if cls in labels else 0 for labels in y_labels])
            if y_binary.sum() == 0:
                continue
            model = XGBClassifier(
                n_estimators=100, max_depth=4,
                learning_rate=0.1, random_state=42,
                eval_metric="logloss",
            )
            model.fit(X, y_binary)
            self.models[cls] = model
            self._trained.add(cls)

    def predict_proba(self, X: pd.DataFrame) -> dict[str, np.ndarray]:
        return {
            cls: self.models[cls].predict_proba(X)[:, 1]
            if cls in self._trained
            else np.zeros(len(X))
            for cls in self.classes
        }

    def predict_max_class(self, X: pd.DataFrame) -> tuple[list[str], np.ndarray]:
        proba = self.predict_proba(X)
        matrix = np.column_stack([proba[cls] for cls in self.classes])
        max_idx = matrix.argmax(axis=1)
        return [self.classes[i] for i in max_idx], matrix.max(axis=1)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump((self.models, self._trained), f)

    @classmethod
    def load(cls, path: Path) -> "BioactivityClassifier":
        instance = cls()
        with open(path, "rb") as f:
            instance.models, instance._trained = pickle.load(f)
        return instance
