const PARTY_LABELS = {
  DMK: "DMK",
  AIADMK: "AIADMK",
  TVK: "TVK",
  BJP: "BJP",
  TOSSUP: "Tossup",
};

export default function DashboardStats({ summary }) {
  const seats = Object.entries(summary.seat_projection);
  const votes = Object.entries(summary.vote_share_projection);

  return (
    <section className="stats-grid">
      <div className="card hero-card">
        <p className="eyebrow">Seat Projection</p>
        <h2>{summary.total_constituencies} Constituencies</h2>
        <div className="seat-strip">
          {seats.map(([party, count]) => (
            <div key={party} className="seat-chip">
              <span>{PARTY_LABELS[party]}</span>
              <strong>{count}</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <p className="eyebrow">Vote Share Projection</p>
        <div className="metric-list">
          {votes.map(([party, value]) => (
            <div key={party} className="metric-row">
              <span>{PARTY_LABELS[party]}</span>
              <strong>{value}%</strong>
            </div>
          ))}
        </div>
      </div>

      <div className="card">
        <p className="eyebrow">TVK Influence</p>
        <div className="metric-list">
          <div className="metric-row">
            <span>Average TVK factor</span>
            <strong>{summary.tvk_impact_summary.average_tvk_influence}</strong>
          </div>
          <div className="metric-row">
            <span>Projected TVK vote share</span>
            <strong>{summary.tvk_impact_summary.tvk_projected_vote_share}%</strong>
          </div>
          <div className="metric-row">
            <span>Projected TVK seats</span>
            <strong>{summary.tvk_impact_summary.tvk_projected_seats}</strong>
          </div>
        </div>
      </div>
    </section>
  );
}

