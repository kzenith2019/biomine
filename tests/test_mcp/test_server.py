import pytest


@pytest.mark.asyncio
async def test_tools_list_returns_five_tools():
    from src.mcp.server import mcp
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert tool_names == {
        "ncbi_search_genomes",
        "ncbi_fetch_sequence",
        "mibig_search_compounds",
        "pubmed_search",
        "pubmed_fetch_abstract",
    }
