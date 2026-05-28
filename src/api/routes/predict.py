import io
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile
from Bio import SeqIO
from src.api.schemas import PredictionResponse
from src.models.predictor import BioMinePredictor
from src.pipeline.parser import BGCCandidate

router = APIRouter()
_predictor: BioMinePredictor | None = None

def get_predictor() -> BioMinePredictor:
    global _predictor
    if _predictor is None:
        _predictor = BioMinePredictor(Path("models"))
    return _predictor

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
    return PredictionResponse(
        region_id=result.region_id,
        bgc_score=result.bgc_score,
        bioactivity_class=result.bioactivity_class,
        bioactivity_score=result.bioactivity_score,
        novelty_score=result.novelty_score,
        drug_potential_score=result.drug_potential_score,
        top_features=result.top_features,
    )
