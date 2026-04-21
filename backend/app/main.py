from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .geo import build_constituency_geojson
from .model import ElectionPredictor
from .schemas import ConstituencyPrediction, SummaryResponse


app = FastAPI(title="Tamil Nadu Election Prediction API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = ElectionPredictor()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "constituencies": len(predictor.get_constituencies())}


@app.get("/api/summary", response_model=SummaryResponse)
def summary() -> dict:
    return predictor.get_summary()


@app.get("/api/constituencies", response_model=list[ConstituencyPrediction])
def constituencies() -> list[dict]:
    return predictor.get_constituencies()


@app.get("/api/geojson")
def geojson() -> dict:
    return build_constituency_geojson(predictor.get_constituencies())

