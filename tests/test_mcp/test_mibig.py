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
