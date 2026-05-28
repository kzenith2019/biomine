from src.pipeline.parser import BGCCandidate

# PKS = polyketide synthase; NRPS = nonribosomal peptide synthetase; RiPP = ribosomally synthesized peptides
BGC_PFAM_DOMAINS = [
    "PF00109",  # Beta-ketoacyl synthase (PKS)
    "PF02801",  # Beta-ketoacyl synthase, C-terminal
    "PF00698",  # Acyl transferase domain (PKS)
    "PF00501",  # AMP-binding enzyme (NRPS adenylation)
    "PF00550",  # Phosphopantetheine-binding (NRPS/PKS carrier)
    "PF13193",  # AMP-binding enzyme C-terminal
    "PF00668",  # Condensation domain (NRPS)
    "PF01397",  # Terpene synthase, N-terminal
    "PF03936",  # Terpene synthase, C-terminal
    "PF00535",  # Glycosyl transferase group 2
    "PF02458",  # Transferase
    "PF02364",  # Chitin synthase
    "PF02576",  # RiPP recognition element
    "PF05402",  # Coenzyme A ligase
    "PF00106",  # Short-chain dehydrogenase/reductase
]

def extract_domain_features(candidate: BGCCandidate) -> dict:
    present = set()
    for gene in candidate.genes:
        for domain in gene.get("domains", []):
            pfam_id = domain.get("pfam_id", "")
            if pfam_id:
                present.add(pfam_id)
    return {f"domain_{d}": int(d in present) for d in BGC_PFAM_DOMAINS}
