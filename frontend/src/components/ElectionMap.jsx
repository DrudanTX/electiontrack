import { useEffect } from "react";
import { GeoJSON, MapContainer, useMap } from "react-leaflet";

function FitGeoBounds({ geojson }) {
  const map = useMap();

  useEffect(() => {
    const points = geojson.features.flatMap((feature) =>
      feature.geometry.coordinates[0].map(([lng, lat]) => [lat, lng]),
    );

    if (!points.length) {
      return;
    }

    map.fitBounds(points, {
      padding: [18, 18],
    });
  }, [geojson, map]);

  return null;
}

function MapBounds({ geojson, onSelect, selectedConstituency, filteredNames }) {
  const onEachFeature = (feature, layer) => {
    const props = feature.properties;
    layer.on({
      click: () => onSelect(props),
    });
    layer.bindTooltip(
      `${props.constituency} - ${props.display_winner} (${Math.round(props.confidence * 100)}%)`,
    );
  };

  return (
    <GeoJSON
      key={geojson.features.length}
      data={geojson}
      onEachFeature={onEachFeature}
      style={(feature) => ({
        color: "#f6f3eb",
        weight: feature.properties.constituency === selectedConstituency ? 2.4 : 1,
        fillOpacity: filteredNames.size && !filteredNames.has(feature.properties.constituency) ? 0.22 : 0.86,
        fillColor: feature.properties.winner_color,
        opacity: filteredNames.size && !filteredNames.has(feature.properties.constituency) ? 0.35 : 1,
      })}
    />
  );
}

export default function ElectionMap({ geojson, onSelect, selectedConstituency, filteredNames }) {
  return (
    <div className="card map-card">
      <div className="map-header">
        <div>
          <p className="eyebrow">Interactive Map</p>
          <h3>Constituency winner projection</h3>
        </div>
        <div className="legend">
          <span><i style={{ background: "#c62828" }} />DMK</span>
          <span><i style={{ background: "#1565c0" }} />AIADMK</span>
          <span><i style={{ background: "#ef6c00" }} />TVK</span>
          <span><i style={{ background: "#8d8d8d" }} />Tossup</span>
        </div>
      </div>

      <MapContainer
        center={[10.8, 78.3]}
        zoom={7}
        scrollWheelZoom
        style={{ height: "100%", width: "100%" }}
      >
        <FitGeoBounds geojson={geojson} />
        <MapBounds
          geojson={geojson}
          onSelect={onSelect}
          selectedConstituency={selectedConstituency}
          filteredNames={filteredNames}
        />
      </MapContainer>
    </div>
  );
}
