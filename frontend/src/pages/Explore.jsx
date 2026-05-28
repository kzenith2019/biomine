import { useState, useEffect, useCallback } from 'react'
import { ResultsTable } from '../components/ResultsTable'
import { API } from '../api'

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
      const res = await fetch(API.explore(params))
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
      <h1>BGC Database</h1>
      <p className="page-subtitle">Browse and filter predicted biosynthetic gene clusters</p>

      <div className="filters">
        <select value={bioClass} onChange={e => setBioClass(e.target.value)}>
          <option value="">All classes</option>
          {CLASSES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        <label>
          BGC Score ≥ <span className="filter-val">{minBgc.toFixed(2)}</span>
          <input type="range" min="0" max="1" step="0.05" value={minBgc}
            onChange={e => setMinBgc(+e.target.value)} />
        </label>

        <label>
          Novelty ≥ <span className="filter-val">{minNovelty.toFixed(2)}</span>
          <input type="range" min="0" max="1" step="0.05" value={minNovelty}
            onChange={e => setMinNovelty(+e.target.value)} />
        </label>

        <label>
          Drug Potential ≥ <span className="filter-val">{minDrug.toFixed(2)}</span>
          <input type="range" min="0" max="1" step="0.05" value={minDrug}
            onChange={e => setMinDrug(+e.target.value)} />
        </label>

        <button onClick={downloadCSV} disabled={!results.length}>↓ Export CSV</button>
      </div>

      <p className="results-count">
        Showing <span>{results.length}</span> of <span>{total}</span> predictions
      </p>

      <ResultsTable results={results} />
    </div>
  )
}
