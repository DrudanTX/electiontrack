from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


DISTRICTS = [
    "Ariyalur",
    "Chengalpattu",
    "Chennai",
    "Coimbatore",
    "Cuddalore",
    "Dharmapuri",
    "Dindigul",
    "Erode",
    "Kallakurichi",
    "Kancheepuram",
    "Kanyakumari",
    "Karur",
    "Krishnagiri",
    "Madurai",
    "Mayiladuthurai",
    "Nagapattinam",
    "Namakkal",
    "Nilgiris",
    "Perambalur",
    "Pudukkottai",
    "Ramanathapuram",
    "Ranipet",
    "Salem",
    "Sivaganga",
    "Tenkasi",
    "Thanjavur",
    "Theni",
    "Thoothukudi",
    "Tiruchirappalli",
    "Tirunelveli",
    "Tirupattur",
    "Tiruppur",
    "Tiruvallur",
    "Tiruvannamalai",
    "Tiruvarur",
    "Vellore",
    "Viluppuram",
    "Virudhunagar",
    "Sankarankoil",
]


@dataclass
class ConstituencyProfile:
    constituency: str
    district: str
    urban_index: float
    youth_population_index: float
    district_wave: float
    dmk_lean: float
    aiadmk_lean: float
    bjp_lean: float


def build_constituencies() -> List[str]:
    constituencies = []
    for district in DISTRICTS:
        for segment in range(1, 7):
            constituencies.append(f"{district} Segment {segment}")
    return constituencies


def _build_profiles(seed: int = 42) -> List[ConstituencyProfile]:
    rng = np.random.default_rng(seed)
    profiles: List[ConstituencyProfile] = []
    for district in DISTRICTS:
        district_wave = rng.normal(0, 1.8)
        urban_center = np.clip(rng.uniform(0.15, 0.92), 0, 1)
        youth_center = np.clip(rng.uniform(0.25, 0.95), 0, 1)
        for segment in range(1, 7):
            urban_index = float(np.clip(urban_center + rng.normal(0, 0.1), 0.05, 0.98))
            youth_index = float(np.clip(youth_center + rng.normal(0, 0.12), 0.05, 0.98))
            dmk_lean = rng.normal(0.5, 0.9) + district_wave * 0.35 + urban_index * 0.85
            aiadmk_lean = rng.normal(0.4, 0.95) - urban_index * 0.3 + (1 - urban_index) * 0.45
            bjp_lean = rng.normal(-0.7, 0.8) + urban_index * 0.55 + youth_index * 0.2
            profiles.append(
                ConstituencyProfile(
                    constituency=f"{district} Segment {segment}",
                    district=district,
                    urban_index=urban_index,
                    youth_population_index=youth_index,
                    district_wave=district_wave,
                    dmk_lean=dmk_lean,
                    aiadmk_lean=aiadmk_lean,
                    bjp_lean=bjp_lean,
                )
            )
    return profiles


def _normalize_vote_shares(scores: Dict[str, float]) -> Dict[str, float]:
    clipped = {party: max(value, 1.0) for party, value in scores.items()}
    total = sum(clipped.values())
    return {party: round(value * 100.0 / total, 2) for party, value in clipped.items()}


def generate_training_data(seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    profiles = _build_profiles(seed)
    election_cycles = [2011, 2016, 2021, 2024]

    history_rows: List[Dict[str, float | str | int]] = []
    supervised_rows: List[Dict[str, float | str | int]] = []

    for profile in profiles:
        prev_result: Dict[str, float | str] | None = None
        incumbency_pressure = rng.uniform(0.2, 0.9)

        for idx, year in enumerate(election_cycles):
            cycle_wave = idx * 0.55
            anti_incumbency = float(np.clip(incumbency_pressure + rng.normal(0, 0.12), 0.05, 0.98))
            sentiment_score = float(
                np.clip(
                    0.55 * profile.dmk_lean
                    - 0.35 * anti_incumbency
                    + rng.normal(0, 0.6),
                    -2.5,
                    2.5,
                )
            )
            trend_score = float(
                np.clip(
                    profile.urban_index * 0.9
                    + profile.youth_population_index * 0.8
                    + cycle_wave * 0.12
                    + rng.normal(0, 0.35),
                    0,
                    5,
                )
            )
            tvk_score = float(
                np.clip(
                    0.1 if year < 2024 else 0.45 + profile.youth_population_index * 0.4 + profile.urban_index * 0.15,
                    0,
                    1,
                )
            )
            turnout = float(np.clip(66 + profile.urban_index * 5 + rng.normal(0, 4), 58, 84))

            raw_scores = {
                "DMK": 33 + profile.dmk_lean * 4.1 + sentiment_score * 1.8 - anti_incumbency * 2.2 + rng.normal(0, 2.3),
                "AIADMK": 31 + profile.aiadmk_lean * 3.8 + anti_incumbency * 2.4 - sentiment_score * 1.0 + rng.normal(0, 2.5),
                "BJP": 9 + profile.bjp_lean * 2.4 + trend_score * 1.4 + rng.normal(0, 1.4),
                "TVK": 2 + tvk_score * 18 + profile.youth_population_index * 4.5 + trend_score * 0.9 + rng.normal(0, 1.2),
            }
            votes = _normalize_vote_shares(raw_scores)
            ranking = sorted(votes.items(), key=lambda item: item[1], reverse=True)
            winner = ranking[0][0]
            margin = round(ranking[0][1] - ranking[1][1], 2)

            current_result = {
                "year": year,
                "constituency": profile.constituency,
                "district": profile.district,
                "DMK_vote_actual": votes["DMK"],
                "AIADMK_vote_actual": votes["AIADMK"],
                "BJP_vote_actual": votes["BJP"],
                "TVK_vote_actual": votes["TVK"],
                "turnout_actual": turnout,
                "winner_actual": winner,
                "margin_actual": margin,
                "urban_index": profile.urban_index,
                "youth_population_index": profile.youth_population_index,
                "anti_incumbency_score": anti_incumbency,
                "sentiment_score": sentiment_score,
                "trend_score": trend_score,
                "TVK_score": tvk_score,
            }
            history_rows.append(current_result)

            if prev_result is not None:
                supervised_rows.append(
                    {
                        "year": year,
                        "constituency": profile.constituency,
                        "district": profile.district,
                        "DMK_vote": prev_result["DMK_vote_actual"],
                        "AIADMK_vote": prev_result["AIADMK_vote_actual"],
                        "BJP_vote": prev_result["BJP_vote_actual"],
                        "TVK_score": tvk_score,
                        "turnout": turnout,
                        "last_margin": prev_result["margin_actual"],
                        "urban_index": profile.urban_index,
                        "winner": winner,
                        "sentiment_score": sentiment_score,
                        "trend_score": trend_score,
                        "youth_population_index": profile.youth_population_index,
                        "anti_incumbency_score": anti_incumbency,
                        "historical_voting_patterns": (
                            prev_result["DMK_vote_actual"] - prev_result["AIADMK_vote_actual"]
                        ),
                        "DMK_vote_target": votes["DMK"],
                        "AIADMK_vote_target": votes["AIADMK"],
                        "BJP_vote_target": votes["BJP"],
                        "TVK_vote_target": votes["TVK"],
                    }
                )

            prev_result = current_result

    history_df = pd.DataFrame(history_rows)
    supervised_df = pd.DataFrame(supervised_rows)
    return history_df, supervised_df


def generate_prediction_frame(history_df: pd.DataFrame, seed: int = 99) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    latest = history_df.sort_values(["constituency", "year"]).groupby("constituency").tail(1).copy()

    prediction_rows = []
    for _, row in latest.iterrows():
        trend_score = float(np.clip(row["trend_score"] + rng.normal(0.35, 0.3), 0, 5))
        anti_incumbency = float(np.clip(row["anti_incumbency_score"] + rng.normal(0.1, 0.08), 0.05, 0.99))
        celebrity_boost = 0.18 + row["youth_population_index"] * 0.22 + row["urban_index"] * 0.08
        tvk_score = float(np.clip(row["TVK_score"] + celebrity_boost + rng.normal(0, 0.05), 0, 1))
        sentiment_score = float(np.clip(row["sentiment_score"] + rng.normal(0.1, 0.35), -2.5, 2.5))
        turnout = float(np.clip(row["turnout_actual"] + rng.normal(0.2, 1.7), 58, 84))

        prediction_rows.append(
            {
                "constituency": row["constituency"],
                "district": row["district"],
                "DMK_vote": row["DMK_vote_actual"],
                "AIADMK_vote": row["AIADMK_vote_actual"],
                "BJP_vote": row["BJP_vote_actual"],
                "TVK_score": tvk_score,
                "turnout": turnout,
                "last_margin": row["margin_actual"],
                "urban_index": row["urban_index"],
                "winner": row["winner_actual"],
                "sentiment_score": sentiment_score,
                "trend_score": trend_score,
                "youth_population_index": row["youth_population_index"],
                "anti_incumbency_score": anti_incumbency,
                "historical_voting_patterns": row["DMK_vote_actual"] - row["AIADMK_vote_actual"],
            }
        )

    return pd.DataFrame(prediction_rows)

