import { useState } from 'react'
import { ScoreCard } from '../components/ScoreCard'
import { ShapChart } from '../components/ShapChart'
import { GenomeBrowser } from '../components/GenomeBrowser'
import { API } from '../api'

export function Submit() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [fileName, setFileName] = useState(null)

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
      const res = await fetch(API.predict, { method: 'POST', body: formData })
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
      <p className="page-subtitle">Upload a FASTA sequence to score for BGC potential</p>

      <div className="submit-form">
        <form onSubmit={handleSubmit}>
          <label className="upload-area">
            <div className="upload-icon">⬡ ⬡ ⬡</div>
            <div className="upload-label">
              {fileName
                ? <span style={{ color: 'var(--accent)' }}>{fileName}</span>
                : <>Drop FASTA file or <span style={{ color: 'var(--accent)' }}>click to browse</span></>
              }
            </div>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
              .fasta · .fa · .fna
            </div>
            <input
              type="file"
              name="fasta"
              accept=".fasta,.fa,.fna"
              required
              onChange={e => setFileName(e.target.files[0]?.name || null)}
            />
          </label>

          <button type="submit" disabled={loading} style={{ alignSelf: 'flex-start' }}>
            {loading ? '◌ Analyzing…' : '→ Analyze Sequence'}
          </button>
        </form>
      </div>

      {loading && (
        <div className="analyzing">
          <div className="spinner" />
          Running ML pipeline — extracting features, scoring BGC potential…
        </div>
      )}

      {error && <div className="error">⚠ {error}</div>}

      {result && (
        <div>
          <div className="result-meta">
            <span><strong>{result.region_id}</strong></span>
            <span>Class: <strong>{result.bioactivity_class}</strong></span>
          </div>

          <div className="score-cards">
            <ScoreCard label="BGC Score"      score={result.bgc_score}           color="#4da6ff" />
            <ScoreCard label="Bioactivity"    score={result.bioactivity_score}   color="#00e8a2" />
            <ScoreCard label="Novelty"        score={result.novelty_score}       color="#b794f4" />
            <ScoreCard label="Drug Potential" score={result.drug_potential_score} color="#f5c542" />
          </div>

          <GenomeBrowser regionLength={result.region_length || 10000} genes={result.genes || []} />
          <ShapChart features={result.top_features} />

          {((result.related_papers?.length > 0) || (result.similar_bgcs?.length > 0)) && (
            <div className="enrichment-grid">
              {result.related_papers?.length > 0 && (
                <div className="enrichment-panel">
                  <h3>Related Literature</h3>
                  {result.related_papers.map(p => (
                    <div key={p.pmid} className="enrichment-item">
                      <div className="enrichment-item-title">{p.title}</div>
                      <div className="enrichment-item-meta">
                        {p.journal} · {p.year} · PMID {p.pmid}
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {result.similar_bgcs?.length > 0 && (
                <div className="enrichment-panel">
                  <h3>Similar BGCs (MIBiG)</h3>
                  {result.similar_bgcs.map(b => (
                    <div key={b.bgc_id} className="enrichment-item">
                      <div className="enrichment-item-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span className="badge">{b.bgc_id}</span>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.72rem' }}>{b.organism}</span>
                      </div>
                      <div className="enrichment-item-meta">
                        {b.compounds.slice(0, 3).join(', ')} · {b.biosynthetic_class.join('/')}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
