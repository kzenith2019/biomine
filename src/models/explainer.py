import numpy as np
import pandas as pd
import shap

class SHAPExplainer:
    def __init__(self, model):
        self.explainer = shap.TreeExplainer(model)

    def explain(self, X: pd.DataFrame, top_n: int = 10) -> dict[str, float]:
        shap_values = self.explainer.shap_values(X)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        mean_abs = np.abs(shap_values).mean(axis=0)
        top_indices = mean_abs.argsort()[::-1][:top_n]
        feature_names = X.columns.tolist()
        return {feature_names[i]: float(mean_abs[i]) for i in top_indices}
