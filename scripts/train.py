import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from src.models.bgc_classifier import BGCClassifier
from src.models.bioactivity import BioactivityClassifier
from src.models.novelty import NoveltyScorer

def load_bioactivity_labels(df: pd.DataFrame) -> list[list[str]]:
    if "bioactivity" not in df.columns:
        return [["other"] if row["label"] == 1 else ["none"] for _, row in df.iterrows()]
    return [[b] for b in df["bioactivity"]]

def main() -> None:
    parser = argparse.ArgumentParser(description="Train BioMine ML models")
    parser.add_argument("--dataset", default="data/features/dataset.parquet")
    parser.add_argument("--model-dir", default="models")
    parser.add_argument("--test-size", type=float, default=0.2)
    args = parser.parse_args()

    df = pd.read_parquet(args.dataset)
    feature_cols = [c for c in df.columns if c not in ("label", "bioactivity")]
    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )

    model_dir = Path(args.model_dir)
    model_dir.mkdir(parents=True, exist_ok=True)

    print("Training BGC classifier...")
    bgc_clf = BGCClassifier()
    bgc_clf.train(X_train, y_train)
    bgc_clf.save(model_dir / "bgc_classifier.pkl")

    print("Training novelty scorer...")
    novelty = NoveltyScorer()
    novelty.train(X_train[y_train == 1])
    novelty.save(model_dir / "novelty.pkl")

    print("Training bioactivity classifier...")
    bio_labels = load_bioactivity_labels(df.loc[X_train.index])
    bio_clf = BioactivityClassifier()
    bio_clf.train(X_train, bio_labels)
    bio_clf.save(model_dir / "bioactivity.pkl")

    print(f"All models saved to {model_dir}/")
    print(f"Training set: {len(X_train)} samples ({int(y_train.sum())} positive)")
    print(f"Test set:     {len(X_test)} samples ({int(y_test.sum())} positive)")

if __name__ == "__main__":
    main()
