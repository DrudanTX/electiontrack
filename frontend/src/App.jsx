import { useDeferredValue, useEffect, useMemo, useState } from "react";
import ConstituencyDetails from "./components/ConstituencyDetails";
import DashboardStats from "./components/DashboardStats";
import ElectionMap from "./components/ElectionMap";
import ProjectionTable from "./components/ProjectionTable";
import SearchPanel from "./components/SearchPanel";
import { useElectionData } from "./hooks/useElectionData";

export default function App() {
  const { summary, geojson, constituencies, loading, error } = useElectionData();
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query.trim().toLowerCase());

  const filteredConstituencies = useMemo(() => {
    if (!deferredQuery) {
      return constituencies;
    }

    return constituencies.filter((seat) =>
      `${seat.constituency} ${seat.district}`.toLowerCase().includes(deferredQuery),
    );
  }, [constituencies, deferredQuery]);

  const filteredGeojson = useMemo(() => {
    if (!geojson) {
      return null;
    }

    if (!deferredQuery) {
      return geojson;
    }

    const allowed = new Set(filteredConstituencies.map((seat) => seat.constituency));
    return {
      ...geojson,
      features: geojson.features.filter((feature) => allowed.has(feature.properties.constituency)),
    };
  }, [geojson, filteredConstituencies, deferredQuery]);

  const defaultSelection = filteredConstituencies.length
    ? [...filteredConstituencies].sort((a, b) => b.confidence - a.confidence)[0]
    : constituencies.length
      ? [...constituencies].sort((a, b) => b.confidence - a.confidence)[0]
      : null;

  const activeSelection = selected || defaultSelection;
  const filteredNames = useMemo(
    () => new Set(filteredConstituencies.map((seat) => seat.constituency)),
    [filteredConstituencies],
  );
  const searchResults = filteredConstituencies.slice(0, 8);

  useEffect(() => {
    if (!selected || !deferredQuery) {
      return;
    }

    const isStillVisible = filteredConstituencies.some(
      (seat) => seat.constituency === selected.constituency,
    );

    if (!isStillVisible) {
      setSelected(null);
    }
  }, [selected, deferredQuery, filteredConstituencies]);

  if (loading) {
    return (
      <main className="app-shell loading-shell">
        <div className="loading-card">
          <p className="eyebrow">Loading</p>
          <h1>Building Tamil Nadu election forecast...</h1>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="app-shell loading-shell">
        <div className="loading-card error-card">
          <p className="eyebrow">Connection Error</p>
          <h1>{error}</h1>
          <p>Start the FastAPI backend at <code>http://127.0.0.1:8000</code> and refresh.</p>
        </div>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <section className="page-header">
        <div>
          <p className="eyebrow">Tamil Nadu Election Prediction System</p>
          <h1>234-seat forecast with TVK celebrity-effect modeling</h1>
          <p className="lead">
            XGBoost models combine historical voting, sentiment, trend proxies, youth
            concentration, and anti-incumbency to estimate winners and vote share.
          </p>
        </div>
      </section>

      <DashboardStats summary={summary} />
      <SearchPanel
        query={query}
        onQueryChange={setQuery}
        results={searchResults}
        onSelect={setSelected}
        resultCount={filteredConstituencies.length}
      />

      <section className="main-grid">
        <ElectionMap
          geojson={filteredGeojson || geojson}
          onSelect={setSelected}
          selectedConstituency={activeSelection?.constituency}
          filteredNames={deferredQuery ? filteredNames : new Set()}
        />
        <ConstituencyDetails selected={activeSelection} />
      </section>

      <ProjectionTable
        constituencies={filteredConstituencies}
        onSelect={setSelected}
        query={query}
      />
    </main>
  );
}
