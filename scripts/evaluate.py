import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report
from src.models.bgc_classifier import BGCClassifier
from src.models.bioactivity import BioactivityClassifier
from src.models.novelty import NoveltyScorer
from src.models.drug_potential import compute_drug_potential

def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate BioMine models")
    parser.add_argument("--dataset", default="data/features/dataset.parquet")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--output", default="reports/eval.json")
    args = parser.parse_args()

    df = pd.read_parquet(args.dataset)
    feature_cols = [c for c in df.columns if c not in ("label", "bioactivity")]
    X = df[feature_cols]
    y = df["label"]

    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model_dir = Path(args.model_dir)
    bgc_clf = BGCClassifier.load(model_dir / "bgc_classifier.pkl")
    novelty = NoveltyScorer.load(model_dir / "novelty.pkl")
    bio_clf = BioactivityClassifier.load(model_dir / "bioactivity.pkl")

    bgc_proba = bgc_clf.predict_proba(X_test)
    bgc_pred = (bgc_proba >= 0.5).astype(int)
    bgc_f1 = float(f1_score(y_test, bgc_pred))

    nov_scores = novelty.score(X_test)

    _, bio_max_proba = bio_clf.predict_max_class(X_test)
    drug_scores = compute_drug_potential(bgc_proba, bio_max_proba, nov_scores)

    combined = bgc_proba * nov_scores
    top_idx = combined.argsort()[::-1][:10]
    top_candidates = [
        {
            "index": int(X_test.index[i]),
            "bgc_score": float(bgc_proba[i]),
            "novelty_score": float(nov_scores[i]),
            "drug_potential": float(drug_scores[i]),
        }
        for i in top_idx
    ]

    report = {
        "bgc_classifier": {
            "f1_score": bgc_f1,
            "n_test": len(y_test),
            "n_positive": int(y_test.sum()),
            "classification_report": classification_report(y_test, bgc_pred, output_dict=True),
        },
        "novelty": {
            "mean_known_bgc": float(nov_scores[y_test == 1].mean()),
            "mean_non_bgc": float(nov_scores[y_test == 0].mean()),
        },
        "top_novel_candidates": top_candidates,
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"BGC F1: {bgc_f1:.3f}")
    print(f"Report saved to {out}")

if __name__ == "__main__":
    main()
