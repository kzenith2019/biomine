from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from src.pipeline.antismash import submit_genome, poll_job, download_results

@pytest.fixture
def fasta_file(tmp_path):
    f = tmp_path / "genome.fasta"
    f.write_text(">seq1\nATGCATGCATGC\n")
    return f

def test_submit_genome_returns_job_id(fasta_file):
    mock_response = MagicMock()
    mock_response.json.return_value = {"job_id": "abc123"}
    with patch("src.pipeline.antismash.requests.post", return_value=mock_response):
        job_id = submit_genome(fasta_file)
    assert job_id == "abc123"

def test_poll_job_returns_data_when_done():
    done_response = MagicMock()
    done_response.json.return_value = {"status": "done", "results_url": "/results/abc123"}
    with patch("src.pipeline.antismash.requests.get", return_value=done_response):
        with patch("src.pipeline.antismash.time.sleep"):
            result = poll_job("abc123", interval=1)
    assert result["status"] == "done"

def test_poll_job_raises_on_failure():
    failed_response = MagicMock()
    failed_response.json.return_value = {"status": "failed", "error": "bad input"}
    with patch("src.pipeline.antismash.requests.get", return_value=failed_response):
        with patch("src.pipeline.antismash.time.sleep"):
            with pytest.raises(RuntimeError, match="failed"):
                poll_job("abc123", interval=1)

def test_download_results_writes_file(tmp_path):
    mock_response = MagicMock()
    mock_response.text = '{"records": []}'
    with patch("src.pipeline.antismash.requests.get", return_value=mock_response):
        result_path = download_results("abc123", tmp_path)
    assert result_path.exists()
    assert result_path.read_text() == '{"records": []}'
