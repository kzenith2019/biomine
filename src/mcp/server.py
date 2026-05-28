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
