from fastapi import APIRouter, Query
from src.api.db import query_predictions
from src.api.schemas import ExploreResponse, ExploreResult

router = APIRouter()

@router.get("/explore", response_model=ExploreResponse)
def explore(
    bioactivity_class: str | None = None,
    min_novelty: float = Query(default=0.0, ge=0.0, le=1.0),
    min_bgc_score: float = Query(default=0.0, ge=0.0, le=1.0),
    min_drug_potential: float = Query(default=0.0, ge=0.0, le=1.0),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    rows, total = query_predictions(
        bioactivity_class=bioactivity_class,
        min_novelty=min_novelty,
        min_bgc_score=min_bgc_score,
        min_drug_potential=min_drug_potential,
        limit=limit,
        offset=offset,
    )
    return ExploreResponse(results=[ExploreResult(**r) for r in rows], total=total)
