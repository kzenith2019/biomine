# BioMine MCP Server — Design Spec
**Date:** 2026-05-28

## Overview

Add a Model Context Protocol (MCP) server to BioMine that exposes real-time data-fetching tools for NCBI/GenBank, MIBiG, and PubMed. The server mounts inside the existing FastAPI app at `/mcp` and serves two consumers: Claude (interactive use via Claude Desktop/Code) and the BioMine prediction pipeline (automatic enrichment of prediction results).

---

## Architecture

### New module: `src/mcp/`

```
src/
  mcp/
    __init__.py
    server.py     — MCP server instance, tool registrations, mount point
    ncbi.py       — NCBI Entrez + GenBank search and fetch logic
    mibig.py      — MIBiG live API queries (separate from src/pipeline/mibig.py)
    pubmed.py     — PubMed search and abstract fetch
```

### Mount in FastAPI

One line added to `src/api/main.py`:
```python
app.mount("/mcp", mcp_app)
```

The MCP server uses streamable HTTP transport (stateless JSON), which is the recommended transport for servers embedded in existing web applications.

---

## Tools

### NCBI tools

**`ncbi_search_genomes`**
- Input: `query: str`, `organism: str = ""`, `max_results: int = 10`
- Output: `[{ accession, organism, title, length, taxid }]`
- Uses NCBI Entrez `esearch` + `esummary` on the nucleotide database

**`ncbi_fetch_sequence`**
- Input: `accession: str`
- Output: `{ accession, fasta: str, length: int }`
- Uses NCBI Entrez `efetch` with `rettype=fasta`

### MIBiG tools

**`mibig_search_compounds`**
- Input: `query: str`, `biosyn_class: str = ""`, `max_results: int = 10`
- Output: `[{ bgc_id, organism, compounds, biosynthetic_class, accession }]`
- Primary: hits the MIBiG REST API at `https://mibig.secondarymetabolites.org/api/v1/` if a JSON search endpoint is available
- Fallback: if no suitable REST search endpoint exists, downloads the MIBiG tarball on first use (reusing `src/pipeline/mibig.py`), caches it in `data/mibig/`, and searches in-memory

### PubMed tools

**`pubmed_search`**
- Input: `query: str`, `max_results: int = 5`
- Output: `[{ pmid, title, authors, journal, year, abstract_snippet }]`
- Uses NCBI Entrez `esearch` + `efetch` on the pubmed database

**`pubmed_fetch_abstract`**
- Input: `pmid: str`
- Output: `{ pmid, title, abstract, authors, journal, year }`

---

## Data Flow

### Claude interactive use
```
Claude → POST /mcp (MCP JSON-RPC) → tool handler → NCBI/MIBiG/PubMed API → result to Claude
```
Claude can chain tools: search NCBI for a genome → fetch the FASTA → POST to `/api/predict` to score it.

### BioMine automatic enrichment
```
User uploads FASTA → POST /api/predict
  → ML models score the sequence
  → bioactivity_class from result feeds asyncio.gather():
      pubmed_search(query=bioactivity_class)          → top 3 papers
      mibig_search_compounds(query=bioactivity_class) → top 3 similar BGCs
  → enriched result returned: adds related_papers[] and similar_bgcs[]
```
Enrichment is fire-and-gather — both external calls run in parallel. If either fails (network error, timeout), it fails silently and returns an empty list. The prediction result is always returned.

---

## Configuration

### `config.yaml` addition
```yaml
ncbi_api_key: ""   # optional — leave blank for email-only (3 req/sec), add key for 10 req/sec
```

### Environment variable (Render)
```
NCBI_API_KEY=your_key_here   # optional
```

### Auth resolution order
1. `NCBI_API_KEY` env var (if set and non-empty)
2. `ncbi_api_key` from `config.yaml` (if set and non-empty)
3. Email-only mode using `entrez_email` from `config.yaml`

### Rate limiting
`ncbi.py` maintains a shared async token bucket: 3 tokens/sec without API key, 10/sec with. All NCBI and PubMed calls (both use Entrez) share this bucket.

---

## New Dependencies

```
mcp>=1.0.0          — MCP Python SDK
httpx>=0.27.0       — async HTTP client for MIBiG live API
```
`biopython` (already in requirements) handles all Entrez calls.

---

## Error Handling

- NCBI/PubMed errors: raise descriptive `McpError` with the HTTP status and NCBI error message so Claude can act on it
- MIBiG errors: same pattern
- Enrichment path in `/api/predict`: all errors caught and logged, result always returned with empty enrichment fields

---

## Testing

- Unit tests in `tests/test_mcp/` with `httpx.AsyncClient` mocking external API calls
- One test per tool covering: happy path, empty results, and API error
- Integration smoke: `POST /mcp` with a `tools/list` call returns all 5 tools

---

## Out of Scope

- Caching responses (can be added later)
- Streaming results for large FASTA sequences
- Authentication/authorization on the `/mcp` endpoint itself
