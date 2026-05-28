# MIBiG Real Data Seed Script Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the synthetic training data generator with one that uses real MIBiG BGC records, producing realistic GC content and bioactivity labels while keeping the same output schema.

**Architecture:** `scripts/seed_mibig.py` downloads MIBiG (cached), converts each `BGCRecord` into a `BGCCandidate` with a synthetic sequence of the correct length and organism-appropriate GC content, runs the existing feature extractor, then saves the parquet. Negative examples are generated at 3:1 ratio with shorter lengths and lower GC. `render.yaml` is updated to call the new script.

**Tech Stack:** Biopython MIBiG pipeline (existing), NumPy, pandas, pyarrow, pytest + pytest-mock.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `scripts/__init__.py` | Makes scripts importable in tests |
| Create | `scripts/seed_mibig.py` | MIBiG-based dataset generator |
| Create | `tests/test_scripts/__init__.py` | Package marker |
| Create | `tests/test_scripts/test_seed_mibig.py` | Unit + integration tests |
| Modify | `render.yaml` | Use seed_mibig instead of seed_dataset |

---

## Task 1: Helper Functions + Tests

**Files:**
- Create: `scripts/__init__.py`
- Create: `scripts/seed_mibig.py` (helpers only)
- Create: `tests/test_scripts/__init__.py`
- Create: `tests/test_scripts/test_seed_mibig.py` (helper tests only)

- [ ] **Step 1: Create package markers**

Create `scripts/__init__.py` — empty file.
Create `tests/test_scripts/__init__.py` — empty file.

- [ ] **Step 2: Write failing tests for helper functions**

Create `tests/test_scripts/test_seed_mibig.py`:
```python
import pytest


def test_gc_for_actinomycete_organisms():
    from scripts.seed_mibig import _gc_for_organism
    assert _gc_for_organism("Streptomyces coelicolor") == 0.70
    assert _gc_for_organism("Saccharopolyspora erythraea") == 0.70
    assert _gc_for_organism("Amycolatopsis mediterranei") == 0.70
    assert _gc_for_organism("Actinomyces odontolyticus") == 0.70


def test_gc_for_other_organisms():
    from scripts.seed_mibig import _gc_for_organism
    assert _gc_for_organism("Bacillus subtilis") == 0.52
    assert _gc_for_organism("Escherichia coli") == 0.52
    assert _gc_for_organism("Unknown organism") == 0.52


def test_map_bioactivity_compound_override_antifungal():
    from scripts.seed_mibig import _map_bioactivity
    assert _map_bioactivity(["amphotericin", "antifungal agent"], ["Polyketide"]) == "antifungal"
    assert _map_bioactivity(["fluconazole"], ["NRP"]) == "antifungal"


def test_map_bioactivity_compound_override_anticancer():
    from scripts.seed_mibig import _map_bioactivity
    assert _map_bioactivity(["cytotoxic compound"], ["Polyketide"]) == "anticancer"
    assert _map_bioactivity(["tumor inhibitor"], ["NRP"]) == "anticancer"


def test_map_bioactivity_compound_override_immunosuppressant():
    from scripts.seed_mibig import _map_bioactivity
    assert _map_bioactivity(["cyclosporin A"], ["NRP"]) == "immunosuppressant"
    assert _map_bioactivity(["rapamycin"], ["Polyketide"]) == "immunosuppressant"


def test_map_bioactivity_biosyn_class_fallback():
    from scripts.seed_mibig import _map_bioactivity
    assert _map_bioactivity(["actinorhodin"], ["Polyketide"]) == "antibiotic"
    assert _map_bioactivity(["some compound"], ["Terpene"]) == "other"
    assert _map_bioactivity(["unknown"], ["UnknownClass"]) == "other"


def test_generate_sequence_length_and_gc():
    from scripts.seed_mibig import _generate_sequence
    seq = _generate_sequence(1000, 0.70)
    assert len(seq) == 1000
    assert all(c in "ATGC" for c in seq)
    gc = (seq.count("G") + seq.count("C")) / len(seq)
    assert 0.60 <= gc <= 0.80  # allow variance from 0.70 target


def test_generate_sequence_low_gc():
    from scripts.seed_mibig import _generate_sequence
    seq = _generate_sequence(1000, 0.45)
    gc = (seq.count("G") + seq.count("C")) / len(seq)
    assert 0.35 <= gc <= 0.55
```

- [ ] **Step 3: Run tests to verify they fail**

```powershell
cd c:\Users\agara\Desktop\biomine
python -m pytest tests/test_scripts/test_seed_mibig.py -v
```
Expected: `ModuleNotFoundError: No module named 'scripts.seed_mibig'`

- [ ] **Step 4: Create scripts/seed_mibig.py with helpers only**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

```powershell
python -m pytest tests/test_scripts/test_seed_mibig.py -v
```
Expected: 8 tests PASS.

- [ ] **Step 6: Commit**

```powershell
git add scripts/__init__.py scripts/seed_mibig.py tests/test_scripts/__init__.py tests/test_scripts/test_seed_mibig.py
git commit -m "feat: add seed_mibig helper functions with tests"
```

---

## Task 2: Main Function + Integration Test

**Files:**
- Modify: `scripts/seed_mibig.py` — add `_record_to_candidate` and `main`
- Modify: `tests/test_scripts/test_seed_mibig.py` — add integration test

- [ ] **Step 1: Add integration test to test_seed_mibig.py**

Append to `tests/test_scripts/test_seed_mibig.py`:
```python
def test_main_produces_correct_dataset(mocker, tmp_path):
    from src.pipeline.mibig import BGCRecord
    import scripts.seed_mibig as mod

    fake_records = [
        BGCRecord(
            bgc_id="BGC0000001",
            organism="Streptomyces coelicolor",
            taxonomy=[],
            compounds=["actinorhodin"],
            biosynthetic_class=["Polyketide"],
            gene_cluster_length=12000,
            accession="AL645882",
        ),
        BGCRecord(
            bgc_id="BGC0000002",
            organism="Bacillus subtilis",
            taxonomy=[],
            compounds=["iturin"],
            biosynthetic_class=["NRP"],
            gene_cluster_length=8000,
            accession="AB123456",
        ),
        BGCRecord(
            bgc_id="BGC0000003",
            organism="Unknown organism",
            taxonomy=[],
            compounds=["antifungal compound"],
            biosynthetic_class=["Terpene"],
            gene_cluster_length=0,
            accession="XY999999",
        ),
    ]

    mibig_dir = tmp_path / "mibig"
    mibig_dir.mkdir()  # exists so download is skipped
    output_path = tmp_path / "dataset.parquet"

    mocker.patch.object(mod, "MIBIG_DIR", mibig_dir)
    mocker.patch.object(mod, "OUTPUT_PATH", output_path)
    mocker.patch("scripts.seed_mibig.load_all_mibig", return_value=fake_records)

    mod.main()

    df = pd.read_parquet(output_path)

    # 3 positives + 9 negatives = 12 total
    assert len(df) == 12
    assert int(df["label"].sum()) == 3
    assert "gc_content" in df.columns
    assert "cluster_length" in df.columns
    assert "bioactivity" in df.columns
    assert df.isna().sum().sum() == 0

    # BGC0000003 has gene_cluster_length=0 so should use floor of 5000
    pos_rows = df[df["label"] == 1]
    assert (pos_rows["cluster_length"] >= 5000).all()

    # Bioactivity mapping: BGC0000003 compounds contain "antifungal"
    activities = set(pos_rows["bioactivity"].tolist())
    assert "antifungal" in activities
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
python -m pytest tests/test_scripts/test_seed_mibig.py::test_main_produces_correct_dataset -v
```
Expected: `AttributeError` or `ImportError` — `main` not yet defined.

- [ ] **Step 3: Add _record_to_candidate and main to scripts/seed_mibig.py**

Append to `scripts/seed_mibig.py`:
```python
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
```

- [ ] **Step 4: Run all tests to verify they pass**

```powershell
python -m pytest tests/test_scripts/test_seed_mibig.py -v
```
Expected: 9 tests PASS.

- [ ] **Step 5: Run full test suite to confirm nothing broke**

```powershell
python -m pytest --tb=short -q
```
Expected: all tests pass (previous 96 + 9 new = 105).

- [ ] **Step 6: Commit**

```powershell
git add scripts/seed_mibig.py tests/test_scripts/test_seed_mibig.py
git commit -m "feat: add MIBiG-based dataset seed script"
```

---

## Task 3: Update render.yaml

**Files:**
- Modify: `render.yaml`

- [ ] **Step 1: Update the build command**

Replace line 5 of `render.yaml`:
```yaml
buildCommand: pip install -r requirements.txt && python -m scripts.seed_mibig && python -m scripts.train && python -m scripts.precompute 200
```

Full updated `render.yaml`:
```yaml
services:
  - type: web
    name: biomine-api
    runtime: python
    buildCommand: pip install -r requirements.txt && python -m scripts.seed_mibig && python -m scripts.train && python -m scripts.precompute 200
    startCommand: uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: "3.13.0"

  - type: web
    name: biomine-frontend
    runtime: static
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: frontend/dist
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

- [ ] **Step 2: Verify render.yaml is valid**

```powershell
python -c "import yaml; yaml.safe_load(open('render.yaml')); print('render.yaml OK')"
```
Expected: `render.yaml OK`

- [ ] **Step 3: Commit**

```powershell
git add render.yaml
git commit -m "feat: use seed_mibig for real MIBiG training data on Render"
```

---

## Running Locally

After all tasks complete:

```powershell
python -m scripts.seed_mibig   # ~5 min first run (downloads MIBiG), ~2 min after
python -m scripts.train
python -m scripts.precompute 200
uvicorn src.api.main:app --reload
```

The MIBiG tarball is cached in `data/mibig/` — subsequent runs skip the download.
