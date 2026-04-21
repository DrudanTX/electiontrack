export default function ProjectionTable({ constituencies, onSelect, query }) {
  const topRows = [...constituencies].sort((a, b) => b.confidence - a.confidence).slice(0, 12);

  return (
    <div className="card table-card">
      <div className="table-header">
        <div>
          <p className="eyebrow">Seat Projection Table</p>
          <h3>{query ? "Search-matched constituencies" : "High-confidence constituencies"}</h3>
        </div>
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Constituency</th>
              <th>District</th>
              <th>Winner</th>
              <th>Confidence</th>
              <th>Margin</th>
            </tr>
          </thead>
          <tbody>
            {topRows.length ? (
              topRows.map((row) => (
                <tr key={row.constituency} onClick={() => onSelect(row)}>
                  <td>{row.constituency}</td>
                  <td>{row.district}</td>
                  <td>{row.display_winner}</td>
                  <td>{Math.round(row.confidence * 100)}%</td>
                  <td>{row.margin}%</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="5">No constituencies matched that search.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
