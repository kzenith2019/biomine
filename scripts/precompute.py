import json
import sys
from pathlib import Path
import numpy as np
from src.models.predictor import BioMinePredictor
from src.pipeline.parser import BGCCandidate
from src.api.db import init_db, insert_prediction

def main(n: int = 200) -> None:
    init_db()
    predictor = BioMinePredictor(Path("models"))
    rng = np.random.default_rng(99)

    bases = list("ATGCGC")
    for i in range(n):
        length = int(rng.integers(5000, 30000))
        seq = "".join(rng.choice(bases, size=length))
        candidate = BGCCandidate(
            source_accession=f"SYNTH_{i:04d}",
            region_id=f"SYNTH_{i:04d}_0_{length}",
            start=0,
            end=length,
            sequence=seq,
            genes=[],
            predicted_class=[],
            contig_edge=False,
        )
        result = predictor.predict(candidate)
        insert_prediction({
            "region_id": result.region_id,
            "source_accession": candidate.source_accession,
            "bgc_score": result.bgc_score,
            "bioactivity_class": result.bioactivity_class,
            "bioactivity_score": result.bioactivity_score,
            "novelty_score": result.novelty_score,
            "drug_potential_score": result.drug_potential_score,
            "top_features": json.dumps(result.top_features),
            "start": candidate.start,
            "end_coord": candidate.end,
            "predicted_class": json.dumps(candidate.predicted_class),
        })
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{n} processed")

    print(f"Done. {n} predictions stored in data/predictions.db")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    main(n)
