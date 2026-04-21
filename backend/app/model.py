from __future__ import annotations

from typing import Dict, List

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder

try:
    from xgboost import XGBClassifier, XGBRegressor

    XGBOOST_AVAILABLE = True
except Exception:
    XGBClassifier = None
    XGBRegressor = None
    XGBOOST_AVAILABLE = False

from .data import generate_prediction_frame, generate_training_data


PARTIES = ["DMK", "AIADMK", "BJP", "TVK"]
FEATURE_COLUMNS = [
    "DMK_vote",
    "AIADMK_vote",
    "BJP_vote",
    "TVK_score",
    "turnout",
    "last_margin",
    "urban_index",
    "sentiment_score",
    "trend_score",
    "youth_population_index",
    "anti_incumbency_score",
    "historical_voting_patterns",
]
DISPLAY_COLORS = {
    "DMK": "#c62828",
    "AIADMK": "#1565c0",
    "BJP": "#6d4c41",
    "TVK": "#ef6c00",
    "TOSSUP": "#8d8d8d",
}


class ElectionPredictor:
    def __init__(self) -> None:
        self.label_encoder = LabelEncoder()
        if XGBOOST_AVAILABLE:
            self.classifier = XGBClassifier(
                n_estimators=220,
                max_depth=4,
                learning_rate=0.06,
                subsample=0.92,
                colsample_bytree=0.9,
                objective="multi:softprob",
                num_class=len(PARTIES),
                eval_metric="mlogloss",
                random_state=42,
            )
            self.regressors = {
                party: XGBRegressor(
                    n_estimators=180,
                    max_depth=4,
                    learning_rate=0.055,
                    subsample=0.9,
                    colsample_bytree=0.88,
                    objective="reg:squarederror",
                    random_state=42,
                )
                for party in PARTIES
            }
            self.model_backend = "xgboost"
        else:
            self.classifier = GradientBoostingClassifier(
                n_estimators=180,
                learning_rate=0.06,
                max_depth=3,
                random_state=42,
            )
            self.regressors = {
                party: GradientBoostingRegressor(
                    n_estimators=180,
                    learning_rate=0.055,
                    max_depth=3,
                    random_state=42,
                )
                for party in PARTIES
            }
            self.model_backend = "sklearn-fallback"

        self.training_history, self.training_frame = generate_training_data()
        self.prediction_frame = generate_prediction_frame(self.training_history)
        self._train_models()
        self.predictions = self._predict()

    def _train_models(self) -> None:
        X = self.training_frame[FEATURE_COLUMNS]
        self.label_encoder.fit(PARTIES)
        y = self.label_encoder.transform(self.training_frame["winner"])
        self.classifier.fit(X, y)

        for party in PARTIES:
            target_col = f"{party}_vote_target"
            self.regressors[party].fit(X, self.training_frame[target_col])

    @staticmethod
    def _normalize_vote_row(row: Dict[str, float]) -> Dict[str, float]:
        clipped = {party: max(value, 1.0) for party, value in row.items()}
        total = float(sum(clipped.values()))
        return {party: round(value * 100.0 / total, 2) for party, value in clipped.items()}

    def _predict(self) -> pd.DataFrame:
        X_pred = self.prediction_frame[FEATURE_COLUMNS]
        probability_matrix = self.classifier.predict_proba(X_pred)
        available_class_indexes = list(getattr(self.classifier, "classes_", []))
        probability_lookup = {
            self.label_encoder.inverse_transform([class_index])[0]: position
            for position, class_index in enumerate(available_class_indexes)
        }

        raw_votes = {
            party: self.regressors[party].predict(X_pred)
            for party in PARTIES
        }

        records: List[Dict] = []
        for idx, (_, base_row) in enumerate(self.prediction_frame.iterrows()):
            probabilities = {
                party: round(float(probability_matrix[idx][probability_lookup[party]]), 4)
                if party in probability_lookup
                else 0.0
                for party in PARTIES
            }
            votes = self._normalize_vote_row({party: float(raw_votes[party][idx]) for party in PARTIES})
            ordered_votes = sorted(votes.items(), key=lambda item: item[1], reverse=True)
            ordered_probs = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)
            predicted_winner = ordered_votes[0][0]
            top_probability = ordered_probs[0][1]
            display_winner = "TOSSUP" if top_probability < 0.43 or ordered_votes[0][1] - ordered_votes[1][1] < 1.75 else predicted_winner

            records.append(
                {
                    "constituency": base_row["constituency"],
                    "district": base_row["district"],
                    "urban_index": round(float(base_row["urban_index"]), 3),
                    "turnout": round(float(base_row["turnout"]), 2),
                    "tvk_influence": round(float(base_row["TVK_score"]), 3),
                    "trend_score": round(float(base_row["trend_score"]), 3),
                    "sentiment_score": round(float(base_row["sentiment_score"]), 3),
                    "youth_population_index": round(float(base_row["youth_population_index"]), 3),
                    "anti_incumbency_score": round(float(base_row["anti_incumbency_score"]), 3),
                    "historical_voting_patterns": round(float(base_row["historical_voting_patterns"]), 2),
                    "winner": predicted_winner,
                    "display_winner": display_winner,
                    "winner_color": DISPLAY_COLORS[display_winner],
                    "vote_share": votes,
                    "probabilities": probabilities,
                    "confidence": round(top_probability, 4),
                    "margin": round(ordered_votes[0][1] - ordered_votes[1][1], 2),
                }
            )

        return pd.DataFrame(records)

    def get_constituencies(self) -> List[Dict]:
        return self.predictions.sort_values(["district", "constituency"]).to_dict(orient="records")

    def get_summary(self) -> Dict:
        predictions = self.predictions.copy()
        seat_counts = {
            party: int((predictions["display_winner"] == party).sum())
            for party in ["DMK", "AIADMK", "TVK", "BJP", "TOSSUP"]
        }
        vote_share = {
            party: round(float(predictions["vote_share"].apply(lambda shares: shares[party]).mean()), 2)
            for party in PARTIES
        }
        leaders = predictions.sort_values("confidence", ascending=False).head(10)[
            ["constituency", "winner", "confidence", "margin"]
        ].to_dict(orient="records")
        return {
            "total_constituencies": int(len(predictions)),
            "model_backend": self.model_backend,
            "seat_projection": seat_counts,
            "vote_share_projection": vote_share,
            "leading_seats": leaders,
            "tvk_impact_summary": {
                "average_tvk_influence": round(float(predictions["tvk_influence"].mean()), 3),
                "tvk_projected_vote_share": vote_share["TVK"],
                "tvk_projected_seats": seat_counts["TVK"],
            },
        }
