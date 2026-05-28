import asyncio
import os
import time
import yaml
from pathlib import Path
from Bio import Entrez


def _load_ncbi_auth() -> dict:
    api_key = os.environ.get("NCBI_API_KEY", "").strip()
    if not api_key:
        config_path = Path("config.yaml")
        if config_path.exists():
            with open(config_path) as f:
                cfg = yaml.safe_load(f)
            api_key = cfg.get("ncbi_api_key", "").strip()
            email = cfg.get("entrez_email", "")
        else:
            email = ""
    else:
        email = ""

    if api_key:
        Entrez.api_key = api_key
        return {"rate": 10.0}
    Entrez.email = email
    return {"rate": 3.0}


class _TokenBucket:
    def __init__(self, rate: float):
        self.rate = rate
        self.tokens = rate
        self.last = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last
            self.tokens = min(self.rate, self.tokens + elapsed * self.rate)
            self.last = now
            if self.tokens < 1:
                wait = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait)
                self.tokens = 0.0
            else:
                self.tokens -= 1.0


_auth = _load_ncbi_auth()
_bucket = _TokenBucket(_auth["rate"])


async def search_genomes(query: str, organism: str = "", max_results: int = 10) -> list[dict]:
    await _bucket.acquire()
    loop = asyncio.get_event_loop()
    search_term = f"{query} AND {organism}[Organism]" if organism else query

    handle = await loop.run_in_executor(
        None, lambda: Entrez.esearch(db="nucleotide", term=search_term, retmax=max_results)
    )
    record = await loop.run_in_executor(None, Entrez.read, handle)
    ids = record["IdList"]
    if not ids:
        return []

    await _bucket.acquire()
    handle = await loop.run_in_executor(
        None, lambda: Entrez.esummary(db="nucleotide", id=",".join(ids))
    )
    summaries = await loop.run_in_executor(None, Entrez.read, handle)
    return [
        {
            "accession": str(s.get("AccessionVersion", "")),
            "organism": str(s.get("Organism", "")),
            "title": str(s.get("Title", "")),
            "length": int(s.get("Length", 0)),
            "taxid": str(s.get("TaxId", "")),
        }
        for s in summaries
    ]


async def fetch_sequence(accession: str) -> dict:
    await _bucket.acquire()
    loop = asyncio.get_event_loop()
    handle = await loop.run_in_executor(
        None, lambda: Entrez.efetch(db="nucleotide", id=accession, rettype="fasta", retmode="text")
    )
    fasta = await loop.run_in_executor(None, handle.read)
    length = sum(len(line) for line in fasta.splitlines() if not line.startswith(">"))
    return {"accession": accession, "fasta": fasta, "length": length}
