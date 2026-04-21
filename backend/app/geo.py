from __future__ import annotations

from typing import Dict, List, Sequence, Tuple


MIN_LAT, MAX_LAT = 8.05, 13.58
MIN_LNG, MAX_LNG = 76.05, 80.38
ROWS = 18
CELLS_PER_ROW = 13

# Stylized Tamil Nadu outer boundary in normalized coordinates.
# The points follow the state clockwise from the north-west shoulder.
TN_OUTLINE: List[Tuple[float, float]] = [
    (0.30, 0.98),
    (0.38, 0.995),
    (0.48, 0.985),
    (0.57, 0.97),
    (0.67, 0.955),
    (0.76, 0.94),
    (0.83, 0.90),
    (0.87, 0.84),
    (0.90, 0.77),
    (0.92, 0.70),
    (0.93, 0.63),
    (0.94, 0.56),
    (0.95, 0.49),
    (0.94, 0.42),
    (0.92, 0.35),
    (0.90, 0.29),
    (0.88, 0.23),
    (0.86, 0.18),
    (0.82, 0.13),
    (0.78, 0.09),
    (0.73, 0.06),
    (0.67, 0.03),
    (0.61, 0.02),
    (0.56, 0.03),
    (0.51, 0.05),
    (0.46, 0.08),
    (0.41, 0.12),
    (0.36, 0.17),
    (0.31, 0.23),
    (0.27, 0.30),
    (0.23, 0.38),
    (0.20, 0.46),
    (0.18, 0.55),
    (0.18, 0.63),
    (0.19, 0.72),
    (0.22, 0.80),
    (0.25, 0.88),
]


def _scale_lng(value: float) -> float:
    return MIN_LNG + ((MAX_LNG - MIN_LNG) * value)


def _scale_lat(value: float) -> float:
    return MIN_LAT + ((MAX_LAT - MIN_LAT) * value)


def _scanline_intersections(y_value: float, polygon: Sequence[Tuple[float, float]]) -> List[float]:
    intersections: List[float] = []
    total_points = len(polygon)

    for index in range(total_points):
        x1, y1 = polygon[index]
        x2, y2 = polygon[(index + 1) % total_points]

        if y1 == y2:
            continue

        if (y1 <= y_value < y2) or (y2 <= y_value < y1):
            t = (y_value - y1) / (y2 - y1)
            intersections.append(x1 + (t * (x2 - x1)))

    return sorted(intersections)


def _row_span(row_index: int) -> Tuple[float, float, float, float]:
    top_fraction = 1 - (row_index / ROWS)
    bottom_fraction = 1 - ((row_index + 1) / ROWS)

    top_hits = _scanline_intersections(top_fraction, TN_OUTLINE)
    bottom_hits = _scanline_intersections(bottom_fraction, TN_OUTLINE)

    top_left, top_right = top_hits[0], top_hits[-1]
    bottom_left, bottom_right = bottom_hits[0], bottom_hits[-1]
    return top_left, top_right, bottom_left, bottom_right


def _row_latitudes(row_index: int) -> Tuple[float, float]:
    top_fraction = 1 - (row_index / ROWS)
    bottom_fraction = 1 - ((row_index + 1) / ROWS)
    return _scale_lat(top_fraction), _scale_lat(bottom_fraction)


def _curve_offset(row_index: int, position: float, east_edge: bool) -> float:
    # Shape the western ghats inward and the delta/east coast outward so the
    # constituencies trace a more recognizable Tamil Nadu profile.
    if east_edge:
        if position < 0.48:
            return 0.0
        if 5 <= row_index <= 11:
            base = 0.028
        elif 12 <= row_index <= 15:
            base = 0.014
        elif row_index >= 16:
            base = -0.012
        else:
            base = 0.006
        strength = (position - 0.48) / 0.52
        return base * (strength ** 1.15)

    if position > 0.52:
        return 0.0
    if 4 <= row_index <= 10:
        base = 0.022
    elif 11 <= row_index <= 14:
        base = 0.012
    elif row_index >= 15:
        base = -0.006
    else:
        base = 0.004
    strength = (0.52 - position) / 0.52
    return base * (strength ** 1.1)


def _cell_polygon(row_index: int, column_index: int) -> List[List[float]]:
    top_left, top_right, bottom_left, bottom_right = _row_span(row_index)
    top_lat, bottom_lat = _row_latitudes(row_index)

    start = column_index / CELLS_PER_ROW
    end = (column_index + 1) / CELLS_PER_ROW

    top_west = top_left + ((top_right - top_left) * start) + _curve_offset(row_index, start, east_edge=False)
    top_east = top_left + ((top_right - top_left) * end) + _curve_offset(row_index, end, east_edge=True)
    bottom_west = bottom_left + ((bottom_right - bottom_left) * start) + _curve_offset(row_index + 1, start, east_edge=False)
    bottom_east = bottom_left + ((bottom_right - bottom_left) * end) + _curve_offset(row_index + 1, end, east_edge=True)

    return [
        [_scale_lng(top_west), top_lat],
        [_scale_lng(top_east), top_lat],
        [_scale_lng(bottom_east), bottom_lat],
        [_scale_lng(bottom_west), bottom_lat],
        [_scale_lng(top_west), top_lat],
    ]


def build_constituency_geojson(constituencies: List[Dict]) -> Dict:
    features = []
    for index, record in enumerate(constituencies):
        row = index // CELLS_PER_ROW
        col = index % CELLS_PER_ROW
        polygon = [_cell_polygon(row, col)]
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": polygon},
                "properties": record,
            }
        )

    return {"type": "FeatureCollection", "features": features}
