from __future__ import annotations

from typing import Dict, List, Union

from pydantic import BaseModel


class ConstituencyPrediction(BaseModel):
    constituency: str
    district: str
    urban_index: float
    turnout: float
    tvk_influence: float
    trend_score: float
    sentiment_score: float
    youth_population_index: float
    anti_incumbency_score: float
    historical_voting_patterns: float
    winner: str
    display_winner: str
    winner_color: str
    vote_share: Dict[str, float]
    probabilities: Dict[str, float]
    confidence: float
    margin: float


class SummaryResponse(BaseModel):
    total_constituencies: int
    model_backend: str
    seat_projection: Dict[str, int]
    vote_share_projection: Dict[str, float]
    leading_seats: List[Dict]
    tvk_impact_summary: Dict[str, Union[float, int]]
