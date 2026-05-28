export function ResultsTable({ results }) {
  if (!results.length) return <p style={{ color: '#64748b' }}>No results match your filters.</p>

  const cols = [
    { key: 'region_id', label: 'Region ID' },
    { key: 'source_accession', label: 'Accession' },
    { key: 'bgc_score', label: 'BGC Score' },
    { key: 'bioactivity_class', label: 'Class' },
    { key: 'novelty_score', label: 'Novelty' },
    { key: 'drug_potential_score', label: 'Drug Potential' },
  ]

  return (
    <table className="results-table">
      <thead>
        <tr>{cols.map(c => <th key={c.key}>{c.label}</th>)}</tr>
      </thead>
      <tbody>
        {results.map(row => (
          <tr key={row.region_id}>
            {cols.map(c => (
              <td key={c.key}>
                {typeof row[c.key] === 'number' ? row[c.key].toFixed(3) : row[c.key]}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}
