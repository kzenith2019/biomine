import sqlite3
from pathlib import Path

DB_PATH = Path("data/predictions.db")

def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            region_id TEXT PRIMARY KEY,
            source_accession TEXT,
            bgc_score REAL,
            bioactivity_class TEXT,
            bioactivity_score REAL,
            novelty_score REAL,
            drug_potential_score REAL,
            top_features TEXT,
            start INTEGER,
            end_coord INTEGER,
            predicted_class TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_prediction(p: dict) -> None:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT OR REPLACE INTO predictions VALUES (
            :region_id, :source_accession, :bgc_score, :bioactivity_class,
            :bioactivity_score, :novelty_score, :drug_potential_score,
            :top_features, :start, :end_coord, :predicted_class
        )
    """, p)
    conn.commit()
    conn.close()

def query_predictions(
    bioactivity_class: str | None = None,
    min_novelty: float = 0.0,
    min_bgc_score: float = 0.0,
    min_drug_potential: float = 0.0,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    clauses = ["novelty_score >= ?", "bgc_score >= ?", "drug_potential_score >= ?"]
    params: list = [min_novelty, min_bgc_score, min_drug_potential]

    if bioactivity_class:
        clauses.append("bioactivity_class = ?")
        params.append(bioactivity_class)

    where = " AND ".join(clauses)
    total = conn.execute(f"SELECT COUNT(*) FROM predictions WHERE {where}", params).fetchone()[0]
    rows = conn.execute(
        f"SELECT * FROM predictions WHERE {where} ORDER BY drug_potential_score DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows], total
