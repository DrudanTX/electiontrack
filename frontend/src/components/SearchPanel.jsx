export default function SearchPanel({
  query,
  onQueryChange,
  results,
  onSelect,
  resultCount,
}) {
  return (
    <section className="search-panel card">
      <div className="search-copy">
        <p className="eyebrow">Area Search</p>
        <h3>Find a constituency or district</h3>
        <p className="muted">
          Search across all 234 constituencies and jump the map to the area you want.
        </p>
      </div>

      <div className="search-controls">
        <input
          className="search-input"
          type="search"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search: Chennai, Madurai, Coimbatore Segment 2..."
        />
        <div className="search-meta">
          <span>{resultCount} matches</span>
          {query ? (
            <button className="clear-search" type="button" onClick={() => onQueryChange("")}>
              Clear
            </button>
          ) : null}
        </div>
      </div>

      <div className="search-results">
        {results.length ? (
          results.map((result) => (
            <button
              key={result.constituency}
              type="button"
              className="search-result"
              onClick={() => onSelect(result)}
            >
              <span className="search-result-title">{result.constituency}</span>
              <span className="search-result-meta">
                {result.district} · {result.display_winner} · {Math.round(result.confidence * 100)}%
              </span>
            </button>
          ))
        ) : (
          <div className="search-empty">No matching constituency or district.</div>
        )}
      </div>
    </section>
  );
}
