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
