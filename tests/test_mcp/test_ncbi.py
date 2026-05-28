import pytest
from unittest.mock import MagicMock


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
