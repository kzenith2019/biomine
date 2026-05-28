export function ScoreCard({ label, score, color = '#38bdf8' }) {
  const pct = Math.round(score * 100)
  return (
    <div className="score-card">
      <div className="score-label">{label}</div>
      <div className="score-bar-container">
        <div className="score-bar" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <div className="score-value">{pct}%</div>
    </div>
  )
}
