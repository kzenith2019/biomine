import time
from pathlib import Path
import requests

ANTISMASH_API = "https://antismash.secondarymetabolites.org/api/v2.0"

def submit_genome(fasta_path: Path) -> str:
    with open(fasta_path, "rb") as f:
        response = requests.post(
            f"{ANTISMASH_API}/submit",
            files={"seq": f},
            data={"taxon": "bacteria", "minlength": 1000},
        )
    response.raise_for_status()
    return response.json()["job_id"]

def poll_job(job_id: str, interval: int = 30, timeout: int = 3600) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(f"{ANTISMASH_API}/job/{job_id}")
        response.raise_for_status()
        data = response.json()
        if data["status"] == "done":
            return data
        if data["status"] == "failed":
            raise RuntimeError(f"antiSMASH job {job_id} failed: {data.get('error', '')}")
        time.sleep(interval)
    raise TimeoutError(f"antiSMASH job {job_id} timed out after {timeout}s")

def download_results(job_id: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    response = requests.get(f"{ANTISMASH_API}/results/{job_id}/results.json")
    response.raise_for_status()
    result_path = output_dir / f"{job_id}.json"
    result_path.write_text(response.text)
    return result_path
