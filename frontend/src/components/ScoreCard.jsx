export function ScoreCard({ label, score, color = '#00e8a2' }) {
  const pct = Math.round(score * 100)
  const r = 38
  const circ = 2 * Math.PI * r
  const dash = (pct / 100) * circ

  return (
    <div className="score-card">
      <div className="score-ring-wrap">
        <svg viewBox="0 0 96 96" width="96" height="96" style={{ overflow: 'visible' }}>
          <circle cx="48" cy="48" r={r} fill="none"
            stroke="rgba(255,255,255,0.04)" strokeWidth="6" />
          <circle cx="48" cy="48" r={r} fill="none"
            stroke={color} strokeWidth="6"
            strokeDasharray={`${dash} ${circ - dash}`}
            strokeLinecap="round"
            transform="rotate(-90 48 48)"
            style={{
              filter: `drop-shadow(0 0 6px ${color})`,
              transition: 'stroke-dasharray 1s cubic-bezier(0.4,0,0.2,1)',
            }}
          />
        </svg>
        <div className="score-ring-value" style={{ color }}>
          {pct}<span>%</span>
        </div>
      </div>
      <div className="score-card-label">{label}</div>
    </div>
  )
}
