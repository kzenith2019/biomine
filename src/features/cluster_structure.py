from src.pipeline.parser import BGCCandidate

def extract_cluster_features(candidate: BGCCandidate) -> dict:
    length = candidate.end - candidate.start
    genes = candidate.genes
    gene_count = len(genes)

    if gene_count == 0:
        return {
            "cluster_length": length,
            "gene_count": 0,
            "gene_density": 0.0,
            "strand_ratio": 0.5,
            "contig_edge": int(candidate.contig_edge),
            "avg_gene_length": 0.0,
        }

    forward = sum(1 for g in genes if g.get("strand", 1) > 0)
    gene_lengths = [
        g["end"] - g["start"]
        for g in genes
        if g.get("end", 0) > g.get("start", 0)
    ]

    return {
        "cluster_length": length,
        "gene_count": gene_count,
        "gene_density": gene_count / max(length, 1) * 1000,
        "strand_ratio": forward / gene_count,
        "contig_edge": int(candidate.contig_edge),
        "avg_gene_length": sum(gene_lengths) / len(gene_lengths) if gene_lengths else 0.0,
    }
