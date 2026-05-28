import json
import tarfile
from dataclasses import dataclass
from pathlib import Path
import requests

MIBIG_DOWNLOAD_URL = "https://dl.secondarymetabolites.org/mibig/mibig_json_3.1.tar.gz"

@dataclass
class BGCRecord:
    bgc_id: str
    organism: str
    taxonomy: list[str]
    compounds: list[str]
    biosynthetic_class: list[str]
    gene_cluster_length: int
    accession: str

def parse_mibig_record(json_path: Path) -> BGCRecord:
    with open(json_path) as f:
        data = json.load(f)
    cluster = data.get("cluster", {})
    loci = cluster.get("loci", {})
    length = loci.get("end_coord", 0) - loci.get("start_coord", 0)
    return BGCRecord(
        bgc_id=cluster.get("mibig_accession", ""),
        organism=cluster.get("organism_name", ""),
        taxonomy=cluster.get("taxonomy", []),
        compounds=[c.get("compound", "") for c in cluster.get("compounds", [])],
        biosynthetic_class=cluster.get("biosyn_class", []),
        gene_cluster_length=max(length, 0),
        accession=loci.get("accession", ""),
    )

def download_mibig(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    tarball = output_dir / "mibig.tar.gz"
    response = requests.get(MIBIG_DOWNLOAD_URL, stream=True)
    response.raise_for_status()
    with open(tarball, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    with tarfile.open(tarball) as tar:
        tar.extractall(output_dir)
    return output_dir

def load_all_mibig(data_dir: Path) -> list[BGCRecord]:
    records = []
    for json_file in data_dir.glob("**/*.json"):
        record = parse_mibig_record(json_file)
        if record.bgc_id:
            records.append(record)
    return records
