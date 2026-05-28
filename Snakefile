configfile: "config.yaml"

from pathlib import Path

rule all:
    input:
        "data/features/dataset.parquet"

rule download_mibig:
    output:
        directory("data/raw/mibig")
    run:
        from src.pipeline.mibig import download_mibig
        download_mibig(Path(output[0]))

rule build_dataset:
    input:
        mibig="data/raw/mibig"
    output:
        "data/features/dataset.parquet"
    run:
        from pathlib import Path
        from Bio import Entrez, SeqIO
        from src.pipeline.mibig import load_all_mibig
        from src.pipeline.parser import BGCCandidate
        from src.pipeline.dataset import build_labeled_dataset, sample_negative_regions

        Entrez.email = config["entrez_email"]

        mibig_records = load_all_mibig(Path(input.mibig))

        positives = []
        for r in mibig_records:
            if not r.bgc_id or not r.accession:
                continue
            handle = Entrez.efetch(db="nucleotide", id=r.accession, rettype="fasta", retmode="text")
            seq_record = SeqIO.read(handle, "fasta")
            seq = str(seq_record.seq)[0:r.gene_cluster_length]
            positives.append(BGCCandidate(
                source_accession=r.accession,
                region_id=r.bgc_id,
                start=0,
                end=len(seq),
                sequence=seq,
                genes=[],
                predicted_class=r.biosynthetic_class,
                contig_edge=False,
            ))

        negatives = []
        for r in mibig_records[:config["n_ncbi_genomes"]]:
            if not r.accession:
                continue
            handle = Entrez.efetch(db="nucleotide", id=r.accession, rettype="fasta", retmode="text")
            seq_record = SeqIO.read(handle, "fasta")
            full_seq = str(seq_record.seq)
            bgc_span = [(0, r.gene_cluster_length)]
            negatives.extend(sample_negative_regions(
                sequence=full_seq,
                accession=r.accession,
                bgc_regions=bgc_span,
                region_length=config["region_length"],
                n_samples=config["n_negative_per_genome"],
            ))

        build_labeled_dataset(
            positives=positives,
            negatives=negatives,
            output_path=Path(output[0]),
        )
