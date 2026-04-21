import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export function useElectionData() {
  const [summary, setSummary] = useState(null);
  const [geojson, setGeojson] = useState(null);
  const [constituencies, setConstituencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const [summaryRes, geoRes, constituencyRes] = await Promise.all([
          fetch(`${API_BASE}/api/summary`),
          fetch(`${API_BASE}/api/geojson`),
          fetch(`${API_BASE}/api/constituencies`),
        ]);

        if (!summaryRes.ok || !geoRes.ok || !constituencyRes.ok) {
          throw new Error("Unable to load election prediction data.");
        }

        const [summaryJson, geoJson, constituencyJson] = await Promise.all([
          summaryRes.json(),
          geoRes.json(),
          constituencyRes.json(),
        ]);

        setSummary(summaryJson);
        setGeojson(geoJson);
        setConstituencies(constituencyJson);
        setError("");
      } catch (err) {
        setError(err.message || "Unexpected error");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return { summary, geojson, constituencies, loading, error };
}

