import asyncio
import io
import logging
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from Bio import SeqIO
from src.api.schemas import PredictionResponse, PaperResult, SimilarBGC
from src.models.predictor import BioMinePredictor
from src.pipeline.parser import BGCCandidate
from src.mcp.pubmed import search_pubmed
from src.mcp.mibig import search_compounds

logger = logging.getLogger(__name__)
router = APIRouter()
_predictor: BioMinePredictor | None = None


def get_predictor() -> BioMinePredictor:
    global _predictor
    if _predictor is None:
        _predictor = BioMinePredictor(Path("models"))
    return _predictor


async def _enrich(bioactivity_class: str) -> tuple[list[PaperResult], list[SimilarBGC]]:
    try:
        papers_raw, bgcs_raw = await asyncio.gather(
            search_pubmed(bioactivity_class, max_results=3),
            search_compounds(bioactivity_class, max_results=3),
            return_exceptions=True,
        )
        papers = [PaperResult(**p) for p in papers_raw] if isinstance(papers_raw, list) else []
        bgcs = [SimilarBGC(**b) for b in bgcs_raw] if isinstance(bgcs_raw, list) else []
    except Exception:
        logger.exception("Enrichment failed")
        papers, bgcs = [], []
    return papers, bgcs


@router.post("/predict", response_model=PredictionResponse)
async def predict_bgc(file: UploadFile = File(...)):
    content = await file.read()
    if not content.strip():
        raise HTTPException(status_code=400, detail="Empty file — provide a FASTA sequence")
    try:
        records = list(SeqIO.parse(io.StringIO(content.decode()), "fasta"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid FASTA: {exc}")
    if not records:
        raise HTTPException(status_code=400, detail="No sequences found in FASTA file")

    record = records[0]
    candidate = BGCCandidate(
        source_accession=record.id,
        region_id=f"{record.id}_submitted",
        start=0,
        end=len(record.seq),
        sequence=str(record.seq),
        genes=[],
        predicted_class=[],
        contig_edge=False,
    )
    result = get_predictor().predict(candidate)
    papers, bgcs = await _enrich(result.bioactivity_class)

    return PredictionResponse(
        region_id=result.region_id,
        bgc_score=result.bgc_score,
        bioactivity_class=result.bioactivity_class,
        bioactivity_score=result.bioactivity_score,
        novelty_score=result.novelty_score,
        drug_potential_score=result.drug_potential_score,
        top_features=result.top_features,
        related_papers=papers,
        similar_bgcs=bgcs,
    )
