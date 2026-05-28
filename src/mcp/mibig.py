import asyncio
from pathlib import Path
import httpx
from src.pipeline.mibig import BGCRecord, download_mibig, load_all_mibig

MIBIG_API = "https://mibig.secondarymetabolites.org/api/v1"
MIBIG_LOCAL_DIR = Path("data/mibig")


def _format_api_hit(hit: dict) -> dict:
    return {
        "bgc_id": hit.get("accession", ""),
        "organism": hit.get("organism_name", ""),
        "compounds": [c.get("compound", "") for c in hit.get("compounds", [])],
        "biosynthetic_class": hit.get("biosyn_class", []),
        "accession": hit.get("loci", {}).get("accession", ""),
    }


def _format_local_record(r: BGCRecord) -> dict:
    return {
        "bgc_id": r.bgc_id,
        "organism": r.organism,
        "compounds": r.compounds,
        "biosynthetic_class": r.biosynthetic_class,
        "accession": r.accession,
    }


async def _search_api(query: str, biosyn_class: str, max_results: int) -> list[dict]:
    params: dict = {"term": query, "limit": max_results}
    if biosyn_class:
        params["type"] = biosyn_class
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(f"{MIBIG_API}/search", params=params)
        resp.raise_for_status()
        return [_format_api_hit(h) for h in resp.json().get("results", [])[:max_results]]


async def _search_local(query: str, biosyn_class: str, max_results: int) -> list[dict]:
    loop = asyncio.get_event_loop()
    if not MIBIG_LOCAL_DIR.exists():
        await loop.run_in_executor(None, lambda: download_mibig(MIBIG_LOCAL_DIR))
    records = await loop.run_in_executor(None, lambda: load_all_mibig(MIBIG_LOCAL_DIR))
    q = query.lower()
    bc = biosyn_class.lower()
    matches = [
        r for r in records
        if (any(q in c.lower() for c in r.compounds) or q in r.organism.lower())
        and (not bc or any(bc in c.lower() for c in r.biosynthetic_class))
    ]
    return [_format_local_record(r) for r in matches[:max_results]]


async def search_compounds(query: str, biosyn_class: str = "", max_results: int = 10) -> list[dict]:
    try:
        return await _search_api(query, biosyn_class, max_results)
    except Exception:
        return await _search_local(query, biosyn_class, max_results)
