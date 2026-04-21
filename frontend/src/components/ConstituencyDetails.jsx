export default function ConstituencyDetails({ selected }) {
  if (!selected) {
    return (
      <div className="card details-card">
        <p className="eyebrow">Constituency Insight</p>
        <h3>Select a constituency</h3>
        <p className="muted">
          Click any constituency on the map to inspect predicted winner, vote share,
          and probability distribution.
        </p>
      </div>
    );
  }

  return (
    <div className="card details-card">
      <p className="eyebrow">{selected.district}</p>
      <h3>{selected.constituency}</h3>
      <div className="badge-row">
        <span className="winner-pill" style={{ background: selected.winner_color }}>
          {selected.display_winner}
        </span>
        <span className="confidence-pill">Confidence {Math.round(selected.confidence * 100)}%</span>
      </div>

      <div className="section-block">
        <p className="section-title">Predicted vote share</p>
        {Object.entries(selected.vote_share).map(([party, share]) => (
          <div key={party} className="metric-row">
            <span>{party}</span>
            <strong>{share}%</strong>
          </div>
        ))}
      </div>

      <div className="section-block">
        <p className="section-title">Winner probabilities</p>
        {Object.entries(selected.probabilities).map(([party, probability]) => (
          <div key={party} className="metric-row">
            <span>{party}</span>
            <strong>{Math.round(probability * 100)}%</strong>
          </div>
        ))}
      </div>

      <div className="section-block">
        <p className="section-title">Signals</p>
        <div className="metric-row">
          <span>TVK celebrity effect</span>
          <strong>{selected.tvk_influence}</strong>
        </div>
        <div className="metric-row">
          <span>Trend score</span>
          <strong>{selected.trend_score}</strong>
        </div>
        <div className="metric-row">
          <span>Sentiment score</span>
          <strong>{selected.sentiment_score}</strong>
        </div>
        <div className="metric-row">
          <span>Youth index</span>
          <strong>{selected.youth_population_index}</strong>
        </div>
        <div className="metric-row">
          <span>Turnout</span>
          <strong>{selected.turnout}%</strong>
        </div>
        <div className="metric-row">
          <span>Anti-incumbency</span>
          <strong>{selected.anti_incumbency_score}</strong>
        </div>
      </div>
    </div>
  );
}
