"""
ML Predictor : charge les modèles entraînés et expose des fonctions d'inférence.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict

from services.ml.feature_engineering import FEATURE_COLS, load_features_from_db

MODELS_DIR  = Path(__file__).parent / "models"
XGB_PATH    = MODELS_DIR / "churn_model.pkl"
KMEANS_PATH = MODELS_DIR / "kmeans_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

SEGMENT_MAP = {0: "power_user", 1: "casual", 2: "at_risk", 3: "dormant"}

def _load_models():
    if not XGB_PATH.exists():
        raise FileNotFoundError("Modèles introuvables — lance d'abord le trainer.py")
    return (
        joblib.load(XGB_PATH),
        joblib.load(KMEANS_PATH),
        joblib.load(SCALER_PATH),
    )

def get_churn_scores() -> List[Dict]:
    """Retourne les scores de churn XGBoost pour tous les users."""
    xgb, _, _ = _load_models()
    df = load_features_from_db()
    X = df[FEATURE_COLS + ["plan_encoded"]]
    probs = xgb.predict_proba(X)[:, 1]
    df["churn_score"] = probs
    df["risk"] = pd.cut(probs, bins=[0, 0.3, 0.6, 1.0], labels=["low", "medium", "high"])

    return df[["user_id", "churn_score", "risk", "plan", "engagement_score"]]\
             .sort_values("churn_score", ascending=False)\
             .head(50)\
             .to_dict(orient="records")

def get_segments() -> List[Dict]:
    """Retourne les segments K-Means pour tous les users."""
    _, kmeans, scaler = _load_models()
    df = load_features_from_db()
    X_scaled = scaler.transform(df[FEATURE_COLS])
    labels = kmeans.predict(X_scaled)
    df["segment"] = [SEGMENT_MAP[l] for l in labels]

    summary = df.groupby("segment").agg(
        count=("user_id", "count"),
        avg_engagement=("engagement_score", "mean"),
        avg_churn_days=("days_since_last_use", "mean"),
    ).reset_index()

    return summary.to_dict(orient="records")

def get_ml_metrics() -> Dict:
    """Retourne les métriques des modèles (chargées depuis un fichier de métriques)."""
    metrics_path = MODELS_DIR / "metrics.json"
    if metrics_path.exists():
        import json
        with open(metrics_path) as f:
            return json.load(f)
    # Fallback si pas encore entraîné
    return {
        "xgboost": {"accuracy": None, "status": "not_trained"},
        "kmeans":  {"silhouette": None, "status": "not_trained"},
    }
