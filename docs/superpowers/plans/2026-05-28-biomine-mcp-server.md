# BioMine MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an MCP server mounted at `/mcp` inside the FastAPI app, exposing 5 real-time data tools (NCBI search/fetch, MIBiG search, PubMed search/fetch) and auto-enriching prediction results with related papers and similar BGCs.

**Architecture:** `src/mcp/` holds four modules — `ncbi.py`, `pubmed.py`, `mibig.py`, and `server.py`. The server registers all 5 tools via FastMCP and exposes an ASGI app mounted into the existing FastAPI app. The predict route calls two enrichment functions in parallel via `asyncio.gather` and adds results to `PredictionResponse`.

**Tech Stack:** Python MCP SDK (`mcp>=1.0.0`), FastMCP, Biopython Entrez (NCBI + PubMed), httpx (MIBiG HTTP), asyncio, pyyaml, pytest + pytest-mock.

---

## File Map

| Action | Path | Responsibility |
|--------|------|---------------|
| Create | `src/mcp/__init__.py` | Package marker |
| Create | `src/mcp/ncbi.py` | Token bucket, `search_genomes`, `fetch_sequence` |
| Create | `src/mcp/pubmed.py` | `search_pubmed`, `fetch_abstract` |
| Create | `src/mcp/mibig.py` | `search_compounds` (REST API + local fallback) |
| Create | `src/mcp/server.py` | FastMCP instance, 5 tool registrations, `mcp_asgi_app` |
| Create | `tests/test_mcp/__init__.py` | Package marker |
| Create | `tests/test_mcp/test_ncbi.py` | NCBI client tests |
| Create | `tests/test_mcp/test_pubmed.py` | PubMed client tests |
| Create | `tests/test_mcp/test_mibig.py` | MIBiG client tests |
| Create | `tests/test_mcp/test_server.py` | Tools list smoke test |
| Modify | `requirements.txt` | Add mcp, httpx, pyyaml |
| Modify | `config.yaml` | Add `ncbi_api_key` field |
| Modify | `src/api/main.py` | Mount MCP ASGI app at `/mcp` |
| Modify | `src/api/schemas.py` | Add `related_papers`, `similar_bgcs` to `PredictionResponse` |
| Modify | `src/api/routes/predict.py` | Call enrichment after prediction |

---

## Task 1: Dependencies and Config

**Files:**
- Modify: `requirements.txt`
- Modify: `config.yaml`

- [ ] **Step 1: Update requirements.txt**

Replace the contents of `requirements.txt` with:
```
biopython>=1.84
requests>=2.31.0
pandas>=2.2.3
pyarrow>=18.0.0
pytest>=8.0.0
pytest-mock>=3.12.0
numpy>=2.1.0
scikit-learn>=1.5.0
fastapi>=0.115.0
uvicorn>=0.30.0
python-multipart>=0.0.9
mcp>=1.0.0
httpx>=0.27.0
pyyaml>=6.0.0
```

- [ ] **Step 2: Add ncbi_api_key to config.yaml**

Add one line to `config.yaml` after the existing `entrez_email` line:
```yaml
entrez_email: "your.email@example.com"
ncbi_api_key: ""
```

- [ ] **Step 3: Install new deps**

```powershell
pip install mcp httpx pyyaml
```
Expected: packages install without error.

- [ ] **Step 4: Commit**

```powershell
git add requirements.txt config.yaml
git commit -m "feat: add mcp, httpx, pyyaml deps and ncbi_api_key config"
```

---

## Task 2: NCBI Client

**Files:**
- Create: `src/mcp/__init__.py`
- Create: `src/mcp/ncbi.py`
- Create: `tests/test_mcp/__init__.py`
- Create: `tests/test_mcp/test_ncbi.py`

- [ ] **Step 1: Create package markers**

Create `src/mcp/__init__.py` — empty file.
Create `tests/test_mcp/__init__.py` — empty file.

- [ ] **Step 2: Write failing tests**

Create `tests/test_mcp/test_ncbi.py`:
```python
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture(autouse=True)
def reset_bucket():
    import importlib
    import src.mcp.ncbi as ncbi_mod
    importlib.reload(ncbi_mod)

@pytest.mark.asyncio
async def test_search_genomes_returns_list(mocker):
    mock_search = MagicMock(return_value=MagicMock())
    mock_read_search = MagicMock(return_value={"IdList": ["123", "456"]})
    mock_summary = MagicMock(return_value=MagicMock())
    mock_read_summary = MagicMock(return_value=[
        {"AccessionVersion": "CP001234.1", "Organism": "Streptomyces coelicolor",
         "Title": "Complete genome", "Length": 8667507, "TaxId": 100226},
    ])
    mocker.patch("src.mcp.ncbi.Entrez.esearch", mock_search)
    mocker.patch("src.mcp.ncbi.Entrez.read", side_effect=[mock_read_search.return_value, mock_read_summary.return_value])
    mocker.patch("src.mcp.ncbi.Entrez.esummary", mock_summary)

    from src.mcp.ncbi import search_genomes
    results = await search_genomes("Streptomyces", max_results=2)
    assert isinstance(results, list)
    assert results[0]["accession"] == "CP001234.1"
    assert results[0]["organism"] == "Streptomyces coelicolor"

@pytest.mark.asyncio
async def test_search_genomes_empty_ids(mocker):
    mocker.patch("src.mcp.ncbi.Entrez.esearch", return_value=MagicMock())
    mocker.patch("src.mcp.ncbi.Entrez.read", return_value={"IdList": []})
    from src.mcp.ncbi import search_genomes
    results = await search_genomes("zzznomatch")
    assert results == []

@pytest.mark.asyncio
async def test_fetch_sequence_returns_fasta(mocker):
    fake_handle = MagicMock()
    fake_handle.read.return_value = ">CP001234.1\nATGCATGC\n"
    mocker.patch("src.mcp.ncbi.Entrez.efetch", return_value=fake_handle)
    from src.mcp.ncbi import fetch_sequence
    result = await fetch_sequence("CP001234.1")
    assert result["accession"] == "CP001234.1"
    assert result["fasta"].startswith(">CP001234.1")
    assert result["length"] == 8
```

- [ ] **Step 3: Run tests to verify they fail**

```powershell
cd c:\Users\agara\Desktop\biomine
pytest tests/test_mcp/test_ncbi.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.mcp.ncbi'`

- [ ] **Step 4: Create src/mcp/ncbi.py**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

```powershell
pytest tests/test_mcp/test_ncbi.py -v
```
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```powershell
git add src/mcp/__init__.py src/mcp/ncbi.py tests/test_mcp/__init__.py tests/test_mcp/test_ncbi.py
git commit -m "feat: add NCBI client with token bucket rate limiter"
```

---

## Task 3: PubMed Client

**Files:**
- Create: `src/mcp/pubmed.py`
- Create: `tests/test_mcp/test_pubmed.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_mcp/test_pubmed.py`:
```python
import pytest
from unittest.mock import MagicMock


@pytest.mark.asyncio
async def test_search_pubmed_returns_list(mocker):
    mocker.patch("src.mcp.pubmed.Entrez.esearch", return_value=MagicMock())
    mocker.patch("src.mcp.pubmed.Entrez.read", side_effect=[
        {"IdList": ["38000001"]},
        {"PubmedArticle": [{
            "MedlineCitation": {
                "PMID": "38000001",
                "Article": {
                    "ArticleTitle": "Streptomyces BGC discovery",
                    "Abstract": {"AbstractText": ["Novel BGC found in soil bacteria."]},
                    "Journal": {"Title": "Nature", "JournalIssue": {"PubDate": {"Year": "2024"}}},
                    "AuthorList": [{"LastName": "Smith", "ForeName": "J"}],
                },
            }
        }]},
    ])
    mocker.patch("src.mcp.pubmed.Entrez.efetch", return_value=MagicMock())

    from src.mcp.pubmed import search_pubmed
    results = await search_pubmed("Streptomyces antibiotic", max_results=1)
    assert len(results) == 1
    assert results[0]["pmid"] == "38000001"
    assert results[0]["title"] == "Streptomyces BGC discovery"
    assert results[0]["year"] == "2024"


@pytest.mark.asyncio
async def test_search_pubmed_empty(mocker):
    mocker.patch("src.mcp.pubmed.Entrez.esearch", return_value=MagicMock())
    mocker.patch("src.mcp.pubmed.Entrez.read", return_value={"IdList": []})

    from src.mcp.pubmed import search_pubmed
    results = await search_pubmed("zzznomatch")
    assert results == []


@pytest.mark.asyncio
async def test_fetch_abstract_returns_dict(mocker):
    mocker.patch("src.mcp.pubmed.Entrez.efetch", return_value=MagicMock())
    mocker.patch("src.mcp.pubmed.Entrez.read", return_value={"PubmedArticle": [{
        "MedlineCitation": {
            "PMID": "38000001",
            "Article": {
                "ArticleTitle": "BGC paper",
                "Abstract": {"AbstractText": ["Full abstract text here."]},
                "Journal": {"Title": "Science", "JournalIssue": {"PubDate": {"Year": "2023"}}},
                "AuthorList": [{"LastName": "Jones", "ForeName": "A"}],
            },
        }
    }]})

    from src.mcp.pubmed import fetch_abstract
    result = await fetch_abstract("38000001")
    assert result["pmid"] == "38000001"
    assert result["abstract"] == "Full abstract text here."
    assert result["journal"] == "Science"
```

- [ ] **Step 2: Run tests to verify they fail**

```powershell
pytest tests/test_mcp/test_pubmed.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.mcp.pubmed'`

- [ ] **Step 3: Create src/mcp/pubmed.py**

```python
import asyncio
from Bio import Entrez
from src.mcp.ncbi import _bucket


async def search_pubmed(query: str, max_results: int = 5) -> list[dict]:
    await _bucket.acquire()
    loop = asyncio.get_event_loop()

    handle = await loop.run_in_executor(
        None, lambda: Entrez.esearch(db="pubmed", term=query, retmax=max_results)
    )
    record = await loop.run_in_executor(None, Entrez.read, handle)
    ids = record["IdList"]
    if not ids:
        return []

    await _bucket.acquire()
    handle = await loop.run_in_executor(
        None, lambda: Entrez.efetch(db="pubmed", id=",".join(ids), rettype="xml", retmode="xml")
    )
    data = await loop.run_in_executor(None, Entrez.read, handle)

    results = []
    for article in data.get("PubmedArticle", []):
        cit = article["MedlineCitation"]
        art = cit["Article"]
        abstract_texts = art.get("Abstract", {}).get("AbstractText", [""])
        abstract = str(abstract_texts[0]) if abstract_texts else ""
        pub_date = art.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
        authors = [
            f"{a['LastName']}, {a.get('ForeName', '')}"
            for a in art.get("AuthorList", [])
            if "LastName" in a
        ]
        results.append({
            "pmid": str(cit["PMID"]),
            "title": str(art.get("ArticleTitle", "")),
            "authors": authors[:3],
            "journal": str(art.get("Journal", {}).get("Title", "")),
            "year": str(pub_date.get("Year", "")),
            "abstract_snippet": abstract[:200],
        })
    return results


async def fetch_abstract(pmid: str) -> dict:
    await _bucket.acquire()
    loop = asyncio.get_event_loop()

    handle = await loop.run_in_executor(
        None, lambda: Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="xml")
    )
    data = await loop.run_in_executor(None, Entrez.read, handle)
    article = data["PubmedArticle"][0]
    cit = article["MedlineCitation"]
    art = cit["Article"]
    abstract_texts = art.get("Abstract", {}).get("AbstractText", [""])
    abstract = str(abstract_texts[0]) if abstract_texts else ""
    pub_date = art.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {})
    authors = [
        f"{a['LastName']}, {a.get('ForeName', '')}"
        for a in art.get("AuthorList", [])
        if "LastName" in a
    ]
    return {
        "pmid": str(cit["PMID"]),
        "title": str(art.get("ArticleTitle", "")),
        "abstract": abstract,
        "authors": authors,
        "journal": str(art.get("Journal", {}).get("Title", "")),
        "year": str(pub_date.get("Year", "")),
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```powershell
pytest tests/test_mcp/test_pubmed.py -v
```
Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```powershell
git add src/mcp/pubmed.py tests/test_mcp/test_pubmed.py
git commit -m "feat: add PubMed client (search + fetch abstract)"
```

---

## Task 4: MIBiG Client

**Files:**
- Create: `src/mcp/mibig.py`
- Create: `tests/test_mcp/test_mibig.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_mcp/test_mibig.py`:
```python
import pytest
import httpx


@pytest.mark.asyncio
async def test_search_via_api_success(respx_mock):
    respx_mock.get("https://mibig.secondarymetabolites.org/api/v1/search").mock(
        return_value=httpx.Response(200, json={"results": [
            {
                "accession": "BGC0000001",
                "organism_name": "Streptomyces coelicolor",
                "compounds": [{"compound": "actinorhodin"}],
                "biosyn_class": ["Polyketide"],
                "loci": {"accession": "AL645882"},
            }
        ]})
    )
    from src.mcp.mibig import search_compounds
    results = await search_compounds("actinorhodin")
    assert len(results) == 1
    assert results[0]["bgc_id"] == "BGC0000001"
    assert "actinorhodin" in results[0]["compounds"]


@pytest.mark.asyncio
async def test_search_falls_back_to_local_on_api_error(mocker, respx_mock):
    respx_mock.get("https://mibig.secondarymetabolites.org/api/v1/search").mock(
        return_value=httpx.Response(500)
    )
    from src.pipeline.mibig import BGCRecord
    fake_record = BGCRecord(
        bgc_id="BGC0000002",
        organism="Streptomyces avermitilis",
        taxonomy=[],
        compounds=["avermectin"],
        biosynthetic_class=["Polyketide"],
        gene_cluster_length=80000,
        accession="BA000030",
    )
    mocker.patch("src.mcp.mibig.load_all_mibig", return_value=[fake_record])
    mocker.patch("src.mcp.mibig.MIBIG_LOCAL_DIR")

    from src.mcp.mibig import search_compounds
    results = await search_compounds("avermectin")
    assert len(results) == 1
    assert results[0]["bgc_id"] == "BGC0000002"


@pytest.mark.asyncio
async def test_search_empty_api_results(respx_mock):
    respx_mock.get("https://mibig.secondarymetabolites.org/api/v1/search").mock(
        return_value=httpx.Response(200, json={"results": []})
    )
    from src.mcp.mibig import search_compounds
    results = await search_compounds("zzznomatch")
    assert results == []
```

- [ ] **Step 2: Install respx for httpx mocking**

```powershell
pip install respx pytest-asyncio
```
Expected: installs without error.

Also add to `requirements.txt`:
```
respx>=0.21.0
pytest-asyncio>=0.23.0
```

- [ ] **Step 3: Run tests to verify they fail**

```powershell
pytest tests/test_mcp/test_mibig.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.mcp.mibig'`

- [ ] **Step 4: Create src/mcp/mibig.py**

```python
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
```

- [ ] **Step 5: Run tests to verify they pass**

```powershell
pytest tests/test_mcp/test_mibig.py -v
```
Expected: 3 tests PASS.

- [ ] **Step 6: Commit**

```powershell
git add src/mcp/mibig.py tests/test_mcp/test_mibig.py requirements.txt
git commit -m "feat: add MIBiG client with REST API and local fallback"
```

---

## Task 5: MCP Server

**Files:**
- Create: `src/mcp/server.py`
- Create: `tests/test_mcp/test_server.py`

- [ ] **Step 1: Write failing test**

Create `tests/test_mcp/test_server.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport


@pytest.mark.asyncio
async def test_tools_list_returns_five_tools():
    from src.mcp.server import mcp_asgi_app
    async with AsyncClient(transport=ASGITransport(app=mcp_asgi_app), base_url="http://test") as client:
        resp = await client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
            headers={"Content-Type": "application/json"},
        )
    assert resp.status_code == 200
    body = resp.json()
    tool_names = {t["name"] for t in body["result"]["tools"]}
    assert tool_names == {
        "ncbi_search_genomes",
        "ncbi_fetch_sequence",
        "mibig_search_compounds",
        "pubmed_search",
        "pubmed_fetch_abstract",
    }
```

- [ ] **Step 2: Run test to verify it fails**

```powershell
pytest tests/test_mcp/test_server.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.mcp.server'`

- [ ] **Step 3: Create src/mcp/server.py**

```python
from mcp.server.fastmcp import FastMCP
from src.mcp.ncbi import search_genomes, fetch_sequence
from src.mcp.mibig import search_compounds
from src.mcp.pubmed import search_pubmed, fetch_abstract

mcp = FastMCP("biomine")


@mcp.tool()
async def ncbi_search_genomes(query: str, organism: str = "", max_results: int = 10) -> list[dict]:
    """Search NCBI GenBank for bacterial genome sequences by keyword and optional organism filter."""
    return await search_genomes(query, organism, max_results)


@mcp.tool()
async def ncbi_fetch_sequence(accession: str) -> dict:
    """Fetch a FASTA sequence from NCBI GenBank by accession number."""
    return await fetch_sequence(accession)


@mcp.tool()
async def mibig_search_compounds(query: str, biosyn_class: str = "", max_results: int = 10) -> list[dict]:
    """Search MIBiG for known biosynthetic gene clusters by compound name or organism."""
    return await search_compounds(query, biosyn_class, max_results)


@mcp.tool()
async def pubmed_search(query: str, max_results: int = 5) -> list[dict]:
    """Search PubMed for research papers related to a compound name or bioactivity class."""
    return await search_pubmed(query, max_results)


@mcp.tool()
async def pubmed_fetch_abstract(pmid: str) -> dict:
    """Fetch the full abstract and metadata for a PubMed article by PMID."""
    return await fetch_abstract(pmid)


mcp_asgi_app = mcp.streamable_http_app()
```

- [ ] **Step 4: Run test to verify it passes**

```powershell
pytest tests/test_mcp/test_server.py -v
```
Expected: 1 test PASS.

> **Note:** If the test fails with `AttributeError: 'FastMCP' object has no attribute 'streamable_http_app'`, run `python -c "from mcp.server.fastmcp import FastMCP; m=FastMCP('x'); print([a for a in dir(m) if 'app' in a.lower() or 'http' in a.lower()])"`  and use whichever method name appears.

- [ ] **Step 5: Commit**

```powershell
git add src/mcp/server.py tests/test_mcp/test_server.py
git commit -m "feat: register 5 MCP tools in FastMCP server"
```

---

## Task 6: Mount MCP Server in FastAPI

**Files:**
- Modify: `src/api/main.py`

- [ ] **Step 1: Update src/api/main.py**

Replace the current contents of `src/api/main.py` with:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import predict, explore
from src.mcp.server import mcp_asgi_app

app = FastAPI(title="BioMine API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(predict.router, prefix="/api")
app.include_router(explore.router, prefix="/api")
app.mount("/mcp", mcp_asgi_app)


@app.get("/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 2: Start the server and verify the mount**

```powershell
uvicorn src.api.main:app --reload
```
In a second terminal:
```powershell
curl http://localhost:8000/health
```
Expected: `{"status":"ok"}`

```powershell
curl -X POST http://localhost:8000/mcp `
  -H "Content-Type: application/json" `
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```
Expected: JSON response with `"tools"` array containing 5 items.

- [ ] **Step 3: Commit**

```powershell
git add src/api/main.py
git commit -m "feat: mount MCP server at /mcp in FastAPI app"
```

---

## Task 7: Prediction Enrichment

**Files:**
- Modify: `src/api/schemas.py`
- Modify: `src/api/routes/predict.py`

- [ ] **Step 1: Update PredictionResponse in schemas.py**

Replace `src/api/schemas.py` with:
```python
from pydantic import BaseModel


class PaperResult(BaseModel):
    pmid: str
    title: str
    authors: list[str]
    journal: str
    year: str
    abstract_snippet: str


class SimilarBGC(BaseModel):
    bgc_id: str
    organism: str
    compounds: list[str]
    biosynthetic_class: list[str]
    accession: str


class PredictionResponse(BaseModel):
    region_id: str
    bgc_score: float
    bioactivity_class: str
    bioactivity_score: float
    novelty_score: float
    drug_potential_score: float
    top_features: dict[str, float]
    related_papers: list[PaperResult] = []
    similar_bgcs: list[SimilarBGC] = []


class ExploreResult(BaseModel):
    region_id: str
    source_accession: str
    bgc_score: float
    bioactivity_class: str
    novelty_score: float
    drug_potential_score: float

    model_config = {"extra": "ignore"}


class ExploreResponse(BaseModel):
    results: list[ExploreResult]
    total: int
```

- [ ] **Step 2: Write failing test**

Create `tests/test_api/test_predict_enrichment.py`:
```python
import pytest
from httpx import AsyncClient, ASGITransport
import io


@pytest.mark.asyncio
async def test_predict_includes_enrichment_fields(mocker):
    mocker.patch("src.api.routes.predict.search_pubmed", return_value=[{
        "pmid": "1", "title": "T", "authors": [], "journal": "J", "year": "2024", "abstract_snippet": "A"
    }])
    mocker.patch("src.api.routes.predict.search_compounds", return_value=[{
        "bgc_id": "BGC0000001", "organism": "S. coelicolor", "compounds": ["act"],
        "biosynthetic_class": ["Polyketide"], "accession": "AL645882"
    }])

    from src.api.main import app
    fasta = b">test_seq\nATGCATGCATGC\n"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/predict",
            files={"file": ("test.fasta", io.BytesIO(fasta), "text/plain")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert "related_papers" in body
    assert "similar_bgcs" in body
    assert isinstance(body["related_papers"], list)
    assert isinstance(body["similar_bgcs"], list)


@pytest.mark.asyncio
async def test_predict_enrichment_fails_silently(mocker):
    mocker.patch("src.api.routes.predict.search_pubmed", side_effect=Exception("network error"))
    mocker.patch("src.api.routes.predict.search_compounds", side_effect=Exception("network error"))

    from src.api.main import app
    fasta = b">test_seq\nATGCATGCATGC\n"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/predict",
            files={"file": ("test.fasta", io.BytesIO(fasta), "text/plain")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["related_papers"] == []
    assert body["similar_bgcs"] == []
```

- [ ] **Step 3: Run tests to verify they fail**

```powershell
pytest tests/test_api/test_predict_enrichment.py -v
```
Expected: tests fail because `related_papers`/`similar_bgcs` are not yet in the response.

- [ ] **Step 4: Update src/api/routes/predict.py**

Replace the current contents with:
```python
import asyncio
import io
import logging
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from Bio import SeqIO
from src.api.schemas import PredictionResponse, PaperResult, SimilarBGC
from src.models.predictor import BioMinePredictor
from src.pipeline.parser import BGCCandidate
from src.mcp.pubmed import search_pubmed
from src.mcp.mibig import search_compounds

logger = logging.getLogger(__name__)
router = APIRouter()
_predictor: BioMinePredictor | None = None


def get_predictor() -> BioMinePredictor:
    global _predictor
    if _predictor is None:
        _predictor = BioMinePredictor(Path("models"))
    return _predictor


async def _enrich(bioactivity_class: str) -> tuple[list[PaperResult], list[SimilarBGC]]:
    try:
        papers_raw, bgcs_raw = await asyncio.gather(
            search_pubmed(bioactivity_class, max_results=3),
            search_compounds(bioactivity_class, max_results=3),
            return_exceptions=True,
        )
        papers = [PaperResult(**p) for p in papers_raw] if isinstance(papers_raw, list) else []
        bgcs = [SimilarBGC(**b) for b in bgcs_raw] if isinstance(bgcs_raw, list) else []
    except Exception:
        logger.exception("Enrichment failed")
        papers, bgcs = [], []
    return papers, bgcs


@router.post("/predict", response_model=PredictionResponse)
async def predict_bgc(file: UploadFile = File(...)):
    content = await file.read()
    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty file — provide a FASTA sequence")
    try:
        records = list(SeqIO.parse(io.StringIO(content.decode()), "fasta"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FASTA: {exc}")
    if not records:
        raise HTTPException(status_code=400, detail="No sequences found in FASTA file")

    record = records[0]
    candidate = BGCCandidate(
        source_accession=record.id,
        region_id=f"{record.id}_submitted",
        start=0,
        end=len(record.seq),
        sequence=str(record.seq),
        genes=[],
        predicted_class=[],
        contig_edge=False,
    )
    result = get_predictor().predict(candidate)
    papers, bgcs = await _enrich(result.bioactivity_class)

    return PredictionResponse(
        region_id=result.region_id,
        bgc_score=result.bgc_score,
        bioactivity_class=result.bioactivity_class,
        bioactivity_score=result.bioactivity_score,
        novelty_score=result.novelty_score,
        drug_potential_score=result.drug_potential_score,
        top_features=result.top_features,
        related_papers=papers,
        similar_bgcs=bgcs,
    )
```

- [ ] **Step 5: Run tests to verify they pass**

```powershell
pytest tests/test_api/test_predict_enrichment.py -v
```
Expected: 2 tests PASS.

- [ ] **Step 6: Run full test suite**

```powershell
pytest --tb=short -q
```
Expected: all existing tests still pass.

- [ ] **Step 7: Commit**

```powershell
git add src/api/schemas.py src/api/routes/predict.py tests/test_api/test_predict_enrichment.py
git commit -m "feat: enrich prediction results with PubMed papers and similar MIBiG BGCs"
```

---

## Done

The MCP server is live at `http://localhost:8000/mcp`. Claude Desktop/Code can connect to it by adding this to its MCP config:
```json
{
  "mcpServers": {
    "biomine": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

On Render, replace `localhost:8000` with the deployed backend URL.
