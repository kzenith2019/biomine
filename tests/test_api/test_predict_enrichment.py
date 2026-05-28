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
