# MIBiG Real Data Seed Script — Design Spec
**Date:** 2026-05-28

## Overview

Replace the uniform-random synthetic training data with realistic data derived from the MIBiG database. A new script `scripts/seed_mibig.py` downloads MIBiG, parses ~3,000 real BGC records, generates synthetic DNA sequences with realistic GC content per organism type, extracts features using the existing pipeline, and saves the result to the same parquet path that `scripts/train.py` already reads.

The original `scripts/seed_dataset.py` is kept as a fallback. Nothing downstream (training, API, frontend) changes.

---

## What Changes

| File | Action |
|------|--------|
| `scripts/seed_mibig.py` | New script — the MIBiG-based seed |
| `scripts/seed_dataset.py` | Unchanged — kept as fallback |
| `render.yaml` | Update build command to use `seed_mibig.py` instead |

All other files untouched.

---

## Design

### Step 1: Download MIBiG

Reuse `src/pipeline/mibig.py`:
```python
from src.pipeline.mibig import download_mibig, load_all_mibig

mibig_dir = Path("data/mibig")
if not mibig_dir.exists():
    download_mibig(mibig_dir)
records = load_all_mibig(mibig_dir)
```
Cached after first run — subsequent runs skip the download.

### Step 2: Positive Examples (label=1)

One row per MIBiG record (~3,000 total). For each `BGCRecord`:

- **Sequence length:** `max(record.gene_cluster_length, 5000)` — use real cluster length, floor at 5,000 bp to avoid degenerate short sequences
- **GC content:** determined by checking `record.organism` string (case-insensitive):
  - Contains "Streptomyces", "Saccharopolyspora", "Amycolatopsis", or "Actinomyces" → `gc = 0.70`
  - All others → `gc = 0.52`
- **Sequence generation:** random DNA of the target length, nucleotide frequencies set to match target GC
- **BGCCandidate construction:** uses `src/pipeline/parser.BGCCandidate` — same type the API uses
- **Feature extraction:** `src/features/extractor.extract_all_features(candidate)` — identical to live prediction
- **Bioactivity label:** mapped from MIBiG compound class:
  - "Polyketide" or "NRP" containing antibiotic compounds → `"antibiotic"`
  - "Terpene" → `"other"`
  - compound name contains "fungicide" or "antifungal" → `"antifungal"`
  - Default: first biosynthetic class lowercased, capped to known set `{antibiotic, antifungal, anticancer, immunosuppressant, other}`

### Step 3: Negative Examples (label=0)

3× as many negatives as positives (ratio matches current synthetic dataset). Each negative:

- **Length:** random uniform 2,000–8,000 bp
- **GC:** random uniform 0.40–0.50
- **Bioactivity:** `"none"`
- **genes/predicted_class:** empty (no domain hits)

### Step 4: Output

```python
df.to_parquet("data/features/dataset.parquet")
```

Same path, same column schema as `seed_dataset.py`. `train.py` reads this without any changes.

---

## Bioactivity Mapping

```python
BIOSYN_TO_ACTIVITY = {
    "Polyketide": "antibiotic",
    "NRP": "antibiotic",
    "RiPP": "antibiotic",
    "Terpene": "other",
    "Saccharide": "other",
    "Alkaloid": "other",
    "Other": "other",
}
```

Compound name overrides apply first (checked against all compound names joined, case-insensitive), then biosyn class fallback:
1. Contains "fungicide", "antifungal", or "azole" → `"antifungal"`
2. Contains "tumor", "cancer", or "cytotoxic" → `"anticancer"`
3. Contains "immunosuppressant", "cyclosporin", or "rapamycin" → `"immunosuppressant"`
4. Else: use `BIOSYN_TO_ACTIVITY` lookup on first biosynthetic class, default `"other"`

---

## Running It

```bash
python -m scripts.seed_mibig    # ~5 minutes (includes download)
python -m scripts.train         # unchanged
python -m scripts.precompute 200  # unchanged
```

### render.yaml update

```yaml
buildCommand: pip install -r requirements.txt && python -m scripts.seed_mibig && python -m scripts.train && python -m scripts.precompute 200
```

---

## Testing

- One unit test: `tests/test_scripts/test_seed_mibig.py`
- Mocks `load_all_mibig` to return 3 fake records
- Asserts output parquet has correct columns, correct label distribution, and no NaN values
