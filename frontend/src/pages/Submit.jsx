import { useState } from 'react'
import { ScoreCard } from '../components/ScoreCard'
import { ShapChart } from '../components/ShapChart'
import { GenomeBrowser } from '../components/GenomeBrowser'

export function Submit() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(e) {
    e.preventDefault()
    const file = e.target.fasta.files[0]
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await fetch('/api/predict', { method: 'POST', body: formData })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Prediction failed')
      }
      setResult(await res.json())
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h1>Submit Genome</h1>
      <div className="submit-form">
        <label>Upload a FASTA file to score for BGC potential</label>
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <input type="file" name="fasta" accept=".fasta,.fa,.fna" required />
          <button type="submit" disabled={loading}>
            {loading ? 'Analyzing...' : 'Analyze Sequence'}
          </button>
        </form>
      </div>

      {error && <div className="error">{error}</div>}

      {result && (
        <div>
          <p className="result-meta">
            Results for <strong>{result.region_id}</strong> &mdash; Predicted class: <strong>{result.bioactivity_class}</strong>
          </p>
          <div className="score-cards">
            <ScoreCard label="BGC Score" score={result.bgc_score} color="#3b82f6" />
            <ScoreCard label="Bioactivity" score={result.bioactivity_score} color="#10b981" />
            <ScoreCard label="Novelty" score={result.novelty_score} color="#f59e0b" />
            <ScoreCard label="Drug Potential" score={result.drug_potential_score} color="#8b5cf6" />
          </div>
          <GenomeBrowser regionLength={result.region_length || 10000} genes={result.genes || []} />
          <ShapChart features={result.top_features} />
        </div>
      )}
    </div>
  )
}
