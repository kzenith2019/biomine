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
