import pytest
import pandas as pd


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
    assert 0.60 <= gc <= 0.80


def test_generate_sequence_low_gc():
    from scripts.seed_mibig import _generate_sequence
    seq = _generate_sequence(1000, 0.45)
    gc = (seq.count("G") + seq.count("C")) / len(seq)
    assert 0.35 <= gc <= 0.55


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
    mibig_dir.mkdir()
    output_path = tmp_path / "dataset.parquet"

    mocker.patch.object(mod, "MIBIG_DIR", mibig_dir)
    mocker.patch.object(mod, "OUTPUT_PATH", output_path)
    mocker.patch("scripts.seed_mibig.load_all_mibig", return_value=fake_records)

    mod.main()

    df = pd.read_parquet(output_path)

    assert len(df) == 12
    assert int(df["label"].sum()) == 3
    assert "gc_content" in df.columns
    assert "cluster_length" in df.columns
    assert "bioactivity" in df.columns
    assert df.isna().sum().sum() == 0

    pos_rows = df[df["label"] == 1]
    assert (pos_rows["cluster_length"] >= 5000).all()

    activities = set(pos_rows["bioactivity"].tolist())
    assert "antifungal" in activities
