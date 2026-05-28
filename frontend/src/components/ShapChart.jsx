export function ShapChart({ features }) {
  const sorted = Object.entries(features)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 8)
  const max = sorted[0]?.[1] || 1

  return (
    <div className="shap-chart">
      <h3>Feature Importance (SHAP)</h3>
      {sorted.map(([name, value]) => (
        <div key={name} className="shap-row">
          <div className="shap-name" title={name}>{name}</div>
          <div className="shap-bar-container">
            <div className="shap-bar" style={{ width: `${(value / max) * 100}%` }} />
          </div>
          <div className="shap-value">{value.toFixed(3)}</div>
        </div>
      ))}
    </div>
  )
}
