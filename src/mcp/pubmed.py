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
