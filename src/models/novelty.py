import pickle
from pathlib import Path
import numpy as np
import pandas as pd

class NoveltyScorer:
    def __init__(self):
        self.feature_cols: list[str] = []
        self._mean: np.ndarray | None = None
        self._std: np.ndarray | None = None
        self._max_distance: float = 1.0

    def train(self, mibig_features: pd.DataFrame) -> None:
        self.feature_cols = mibig_features.columns.tolist()
        vals = mibig_features.values.astype(float)
        self._mean = vals.mean(axis=0)
        self._std = vals.std(axis=0) + 1e-8
        normalized = (vals - self._mean) / self._std
        distances = np.linalg.norm(normalized, axis=1)
        self._max_distance = float(distances.max()) if len(distances) > 0 else 1.0

    def score(self, X: pd.DataFrame) -> np.ndarray:
        vals = X[self.feature_cols].values.astype(float)
        normalized = (vals - self._mean) / self._std
        distances = np.linalg.norm(normalized, axis=1)
        return np.clip(distances / (self._max_distance + 1e-8), 0.0, 1.0)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump((self.feature_cols, self._mean, self._std, self._max_distance), f)

    @classmethod
    def load(cls, path: Path) -> "NoveltyScorer":
        instance = cls()
        with open(path, "rb") as f:
            instance.feature_cols, instance._mean, instance._std, instance._max_distance = pickle.load(f)
        return instance
