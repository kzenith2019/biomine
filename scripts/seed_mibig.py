import numpy as np
import pandas as pd
from pathlib import Path
from src.pipeline.mibig import BGCRecord, download_mibig, load_all_mibig
from src.pipeline.parser import BGCCandidate
from src.features.extractor import extract_all_features

MIBIG_DIR = Path("data/mibig")
OUTPUT_PATH = Path("data/features/dataset.parquet")

BIOSYN_TO_ACTIVITY = {
    "Polyketide": "antibiotic",
    "NRP": "antibiotic",
    "RiPP": "antibiotic",
    "Terpene": "other",
    "Saccharide": "other",
    "Alkaloid": "other",
    "Other": "other",
}

_ACTINO_KEYWORDS = ["streptomyces", "saccharopolyspora", "amycolatopsis", "actinomyces"]


def _gc_for_organism(organism: str) -> float:
    org_lower = organism.lower()
    if any(kw in org_lower for kw in _ACTINO_KEYWORDS):
        return 0.70
    return 0.52


def _map_bioactivity(compounds: list[str], biosyn_class: list[str]) -> str:
    joined = " ".join(compounds).lower()
    if any(kw in joined for kw in ["fungicide", "antifungal", "azole"]):
        return "antifungal"
    if any(kw in joined for kw in ["tumor", "cancer", "cytotoxic"]):
        return "anticancer"
    if any(kw in joined for kw in ["immunosuppressant", "cyclosporin", "rapamycin"]):
        return "immunosuppressant"
    first_class = biosyn_class[0] if biosyn_class else "Other"
    return BIOSYN_TO_ACTIVITY.get(first_class, "other")


def _generate_sequence(length: int, gc: float) -> str:
    gc_half = gc / 2
    at_half = (1 - gc) / 2
    probs = [at_half, at_half, gc_half, gc_half]
    rng = np.random.default_rng()
    bases = rng.choice(list("ATGC"), size=length, p=probs)
    return "".join(bases)


def _record_to_candidate(record: BGCRecord) -> BGCCandidate:
    length = max(record.gene_cluster_length, 5000)
    gc = _gc_for_organism(record.organism)
    seq = _generate_sequence(length, gc)
    return BGCCandidate(
        source_accession=record.accession,
        region_id=record.bgc_id,
        start=0,
        end=length,
        sequence=seq,
        genes=[],
        predicted_class=record.biosynthetic_class,
        contig_edge=False,
    )


def main() -> None:
    if not MIBIG_DIR.exists():
        print("Downloading MIBiG...")
        download_mibig(MIBIG_DIR)

    print("Loading MIBiG records...")
    records = load_all_mibig(MIBIG_DIR)
    print(f"  {len(records)} BGC records loaded")

    rng = np.random.default_rng(42)
    rows = []

    for record in records:
        candidate = _record_to_candidate(record)
        features = extract_all_features(candidate)
        features["label"] = 1
        features["bioactivity"] = _map_bioactivity(record.compounds, record.biosynthetic_class)
        rows.append(features)

    n_pos = len(rows)
    print(f"  {n_pos} positive examples extracted")

    n_neg = n_pos * 3
    for i in range(n_neg):
        length = int(rng.integers(2000, 8001))
        gc = float(rng.uniform(0.40, 0.50))
        seq = _generate_sequence(length, gc)
        candidate = BGCCandidate(
            source_accession="NEG",
            region_id=f"NEG_{i}",
            start=0,
            end=length,
            sequence=seq,
            genes=[],
            predicted_class=[],
            contig_edge=False,
        )
        features = extract_all_features(candidate)
        features["label"] = 0
        features["bioactivity"] = "none"
        rows.append(features)

    print(f"  {n_neg} negative examples generated")

    df = pd.DataFrame(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUTPUT_PATH)
    print(f"Saved {len(df)} rows -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
