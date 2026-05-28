from pydantic import BaseModel

class PredictionResponse(BaseModel):
    region_id: str
    bgc_score: float
    bioactivity_class: str
    bioactivity_score: float
    novelty_score: float
    drug_potential_score: float
    top_features: dict[str, float]

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
