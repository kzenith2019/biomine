import json
from dataclasses import dataclass
from pathlib import Path

@dataclass
class BGCCandidate:
    source_accession: str
    region_id: str
    start: int
    end: int
    sequence: str
    genes: list[dict]
    predicted_class: list[str]
    contig_edge: bool

def parse_antismash_output(result_path: Path) -> list[BGCCandidate]:
    with open(result_path) as f:
        data = json.load(f)
    candidates = []
    for record in data.get("records", []):
        accession = record.get("id", "unknown")
        full_sequence = record.get("seq", {}).get("data", "")
        for area in record.get("areas", []):
            start = area["start"]
            end = area["end"]
            candidates.append(BGCCandidate(
                source_accession=accession,
                region_id=f"{accession}_{start}_{end}",
                start=start,
                end=end,
                sequence=full_sequence[start:end],
                genes=area.get("cds_detail", []),
                predicted_class=area.get("products", []),
                contig_edge=area.get("contig_edge", False),
            ))
    return candidates
