# Tamil Nadu Election Prediction System

A full-stack demo for projecting Tamil Nadu assembly election outcomes across 234 constituencies.

This project includes:

- `FastAPI` backend for model training and prediction APIs
- `XGBoost` classification and regression
- synthetic but structured election dataset generation for all 234 seats
- `React + Leaflet` frontend with an interactive constituency map
- seat projection and vote-share summary tables

## Stack

- Backend: FastAPI, pandas, numpy, scikit-learn, xgboost
- Frontend: React, Vite, Leaflet, react-leaflet

## Project Structure

```text
api/
  index.py
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
vercel.json
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

For Vercel Python runtime compatibility, the backend also exposes:

- `GET /summary`
- `GET /constituencies`
- `GET /geojson`

## What the Dashboard Shows

- seat projection by party
- state-wide vote share forecast
- interactive constituency map
- constituency-level probability breakdown on click

## Deploy On Vercel

This repo is set up to deploy both the React frontend and FastAPI backend on Vercel.

How it works:

- Vercel builds the frontend from `frontend/`
- the static site is served from `frontend/dist`
- FastAPI is exposed through `api/index.py` as a Python Function
- in production, the frontend calls same-origin `/api/*` endpoints automatically

### Deploy steps

1. Push this repo to GitHub.
2. Import the repository into Vercel.
3. Keep the project root as the repository root.
4. Vercel will use:
   - Build Command: `npm run build --prefix frontend`
   - Output Directory: `frontend/dist`
5. Deploy.

### Optional environment variable

For local overrides or custom API hosts, you can set:

```bash
VITE_API_BASE_URL=https://your-api-host.example.com
```

You do not need this variable on Vercel if frontend and backend are deployed in the same project.
