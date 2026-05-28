import { useState, useEffect, useCallback } from 'react'
import { ResultsTable } from '../components/ResultsTable'

const CLASSES = ['antibiotic', 'antifungal', 'anticancer', 'immunosuppressant', 'other']

export function Explore() {
  const [results, setResults] = useState([])
  const [total, setTotal] = useState(0)
  const [bioClass, setBioClass] = useState('')
  const [minNovelty, setMinNovelty] = useState(0)
  const [minBgc, setMinBgc] = useState(0)
  const [minDrug, setMinDrug] = useState(0)

  const fetchResults = useCallback(async () => {
    const params = new URLSearchParams({ limit: 100 })
    if (bioClass) params.set('bioactivity_class', bioClass)
    if (minNovelty > 0) params.set('min_novelty', minNovelty)
    if (minBgc > 0) params.set('min_bgc_score', minBgc)
    if (minDrug > 0) params.set('min_drug_potential', minDrug)
    try {
      const res = await fetch(`/api/explore?${params}`)
      const data = await res.json()
      setResults(data.results)
      setTotal(data.total)
    } catch {
      setResults([])
      setTotal(0)
    }
  }, [bioClass, minNovelty, minBgc, minDrug])

  useEffect(() => { fetchResults() }, [fetchResults])

  function downloadCSV() {
    const keys = ['region_id', 'source_accession', 'bgc_score', 'bioactivity_class', 'novelty_score', 'drug_potential_score']
    const rows = results.map(r => keys.map(k => r[k]).join(','))
    const csv = [keys.join(','), ...rows].join('\n')
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }))
    a.download = 'biomine_results.csv'
    a.click()
  }

  return (
    <div>
      <h1>Explore BGC Database</h1>
      <div className="filters">
        <select value={bioClass} onChange={e => setBioClass(e.target.value)}>
          <option value="">All classes</option>
          {CLASSES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <label>Min BGC Score: {minBgc}
          <input type="range" min="0" max="1" step="0.05" value={minBgc}
            onChange={e => setMinBgc(+e.target.value)} style={{ marginLeft: '0.5rem' }} />
        </label>
        <label>Min Novelty: {minNovelty}
          <input type="range" min="0" max="1" step="0.05" value={minNovelty}
            onChange={e => setMinNovelty(+e.target.value)} style={{ marginLeft: '0.5rem' }} />
        </label>
        <label>Min Drug Potential: {minDrug}
          <input type="range" min="0" max="1" step="0.05" value={minDrug}
            onChange={e => setMinDrug(+e.target.value)} style={{ marginLeft: '0.5rem' }} />
        </label>
        <button onClick={downloadCSV} disabled={!results.length}>Download CSV</button>
      </div>
      <p style={{ color: '#64748b', marginBottom: '1rem', fontSize: '0.85rem' }}>
        Showing {results.length} of {total} results
      </p>
      <ResultsTable results={results} />
    </div>
  )
}
