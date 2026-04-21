# Tamil Nadu Election Prediction System

A full-stack demo for projecting Tamil Nadu assembly election outcomes across 234 constituencies.

This project includes:

- `FastAPI` backend for model training and prediction APIs
- `XGBoost` classification and regression models
- synthetic but structured election dataset generation for all 234 seats
- `React + Leaflet` frontend with an interactive constituency map
- seat projection and vote-share summary tables

## Stack

- Backend: FastAPI, pandas, numpy, scikit-learn, xgboost
- Frontend: React, Vite, Leaflet, react-leaflet

## Project Structure

```text
backend/
  app/
    __init__.py
    data.py
    geo.py
    main.py
    model.py
    schemas.py
frontend/
  public/
  src/
    components/
      ConstituencyDetails.jsx
      DashboardStats.jsx
      ElectionMap.jsx
      ProjectionTable.jsx
    hooks/
      useElectionData.js
    App.jsx
    main.jsx
    styles.css
  index.html
  package.json
  vite.config.js
requirements.txt
```

## Notes

- The project ships with a generated seed dataset and synthetic constituency polygons so it works offline without external boundary files.
- Constituency shapes are schematic rectangles laid out over an approximate Tamil Nadu bounding box for visualization.
- `TVK_score` is modeled as an influence factor capturing Vijay's celebrity effect, youth pull, and trend momentum.
- If `xgboost` cannot load on macOS because `libomp` is missing, the backend automatically falls back to sklearn gradient boosting so the app still runs.

## Backend Run

Create an environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn backend.app.main:app --reload
```

Backend will run at `http://127.0.0.1:8000`.

## Frontend Run

```bash
cd frontend
npm install
npm run dev
```

Frontend will run at `http://127.0.0.1:5173`.

## API Endpoints

- `GET /health`
- `GET /api/summary`
- `GET /api/constituencies`
- `GET /api/geojson`

## What the Dashboard Shows

- seat projection by party
- state-wide vote share forecast
- interactive constituency map
- constituency-level probability breakdown on click
