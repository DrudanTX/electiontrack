from __future__ import annotations

from fastapi import APIRouter, FastAPI
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
api_router = APIRouter(prefix="/api")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "constituencies": len(predictor.get_constituencies())}


def _summary_payload() -> dict:
    return predictor.get_summary()


def _constituencies_payload() -> list[dict]:
    return predictor.get_constituencies()


def _geojson_payload() -> dict:
    return build_constituency_geojson(predictor.get_constituencies())


@app.get("/summary", response_model=SummaryResponse)
@api_router.get("/summary", response_model=SummaryResponse)
def summary() -> dict:
    return _summary_payload()


@app.get("/constituencies", response_model=list[ConstituencyPrediction])
@api_router.get("/constituencies", response_model=list[ConstituencyPrediction])
def constituencies() -> list[dict]:
    return _constituencies_payload()


@app.get("/geojson")
@api_router.get("/geojson")
def geojson() -> dict:
    return _geojson_payload()


app.include_router(api_router)
