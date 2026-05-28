from src.pipeline.parser import BGCCandidate

def compute_gc_content(sequence: str) -> float:
    if not sequence:
        return 0.0
    seq = sequence.upper()
    return (seq.count("G") + seq.count("C")) / len(seq)

def extract_sequence_features(candidate: BGCCandidate) -> dict:
    seq = candidate.sequence.upper()
    return {
        "gc_content": compute_gc_content(seq),
        "gc1_content": compute_gc_content(seq[0::3]),
        "gc2_content": compute_gc_content(seq[1::3]),
        "gc3_content": compute_gc_content(seq[2::3]),
        "sequence_length": len(seq),
    }
