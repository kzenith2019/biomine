const CLASS_COLORS = {
  antibiotic: '#00e8a2',
  antifungal: '#4da6ff',
  anticancer: '#ff4466',
  immunosuppressant: '#b794f4',
  other: '#f5c542',
  none: '#2e4a5e',
}

function ScoreCell({ value }) {
  const pct = value.toFixed(3)
  const opacity = 0.4 + value * 0.6
  return (
    <span style={{ color: `rgba(0, 232, 162, ${opacity})`, fontWeight: 600 }}>
      {pct}
    </span>
  )
}

export function ResultsTable({ results }) {
  if (!results.length) return (
    <p className="no-results">— no results match your filters —</p>
  )

  return (
    <table className="results-table">
      <thead>
        <tr>
          <th>Region ID</th>
          <th>Accession</th>
          <th>BGC Score</th>
          <th>Class</th>
          <th>Novelty</th>
          <th>Drug Potential</th>
        </tr>
      </thead>
      <tbody>
        {results.map(row => (
          <tr key={row.region_id}>
            <td style={{ color: 'var(--text-bright)', fontFamily: 'var(--mono)', fontSize: '0.75rem' }}>
              {row.region_id}
            </td>
            <td style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>
              {row.source_accession}
            </td>
            <td className="score-cell"><ScoreCell value={row.bgc_score} /></td>
            <td>
              <span style={{
                color: CLASS_COLORS[row.bioactivity_class] || 'var(--text-muted)',
                fontSize: '0.72rem',
                fontWeight: 600,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
              }}>
                {row.bioactivity_class}
              </span>
            </td>
            <td className="score-cell"><ScoreCell value={row.novelty_score} /></td>
            <td className="score-cell"><ScoreCell value={row.drug_potential_score} /></td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
