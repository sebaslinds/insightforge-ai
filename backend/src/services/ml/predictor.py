"""
ML Predictor : charge les modèles entraînés et expose des fonctions d'inférence.
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import List, Dict

from services.ml.feature_engineering import FEATURE_COLS, load_features_from_db
from services.storage_service import download_model_from_gcs

MODELS_DIR  = Path(__file__).parent / "models"
XGB_PATH    = MODELS_DIR / "churn_model.pkl"
KMEANS_PATH = MODELS_DIR / "kmeans_model.pkl"
SCALER_PATH = MODELS_DIR / "scaler.pkl"

SEGMENT_MAP = {0: "power_user", 1: "casual", 2: "at_risk", 3: "dormant"}

def _load_models():
    # Téléchargement depuis GCS si nécessaire
    if not XGB_PATH.exists():
        print("[GCS] Modèles manquants, téléchargement...")
        download_model_from_gcs("models/churn_model.pkl", str(XGB_PATH))
        download_model_from_gcs("models/kmeans_model.pkl", str(KMEANS_PATH))
        download_model_from_gcs("models/scaler.pkl", str(SCALER_PATH))

    if not XGB_PATH.exists():
        raise FileNotFoundError("Modèles introuvables sur GCS ou localement.")
        
    return (
        joblib.load(XGB_PATH),
        joblib.load(KMEANS_PATH),
        joblib.load(SCALER_PATH),
    )

def get_churn_scores() -> List[Dict]:
    """Retourne les scores de churn XGBoost pour tous les users."""
    xgb, _, _ = _load_models()
    df = load_features_from_db()
    
    # Correction : Forcer la conversion numérique pour éviter ValueError
    for col in FEATURE_COLS + ["plan_encoded"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    X = df[FEATURE_COLS + ["plan_encoded"]]
    probs = xgb.predict_proba(X)[:, 1]
    df["churn_score"] = probs
    df["risk"] = pd.cut(probs, bins=[0, 0.3, 0.6, 1.0], labels=["low", "medium", "high"])

    return df[["user_id", "churn_score", "risk", "plan", "engagement_score"]]\
             .sort_values("churn_score", ascending=False)\
             .head(50)\
             .to_dict(orient="records")

def get_segments() -> List[Dict]:
    """Retourne les segments K-Means pour tous les users avec mapping dynamique."""
    _, kmeans, scaler = _load_models()
    df = load_features_from_db()
    
    for col in FEATURE_COLS:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    X_scaled = scaler.transform(df[FEATURE_COLS])
    df["cluster"] = kmeans.predict(X_scaled)

    # Calculer le score moyen par cluster pour mapper dynamiquement
    cluster_stats = df.groupby("cluster")["engagement_score"].mean().sort_values(ascending=False)
    
    # Mapping: Plus haut score -> power_user, etc.
    dynamic_map = {}
    names = ["power_user", "casual", "at_risk", "dormant"]
    for i, cluster_id in enumerate(cluster_stats.index):
        if i < len(names):
            dynamic_map[cluster_id] = names[i]
        else:
            dynamic_map[cluster_id] = f"cluster_{cluster_id}"

    df["segment_name"] = df["cluster"].map(dynamic_map)

    # Agrégation
    summary = df.groupby("segment_name").agg({
        "user_id": "count",
        "engagement_score": "mean",
        "days_since_last_use": "mean"
    }).reset_index()

    summary = summary.rename(columns={
        "segment_name": "name",
        "user_id": "count",
        "engagement_score": "avg_score",
        "days_since_last_use": "avg_churn_days"
    })

    total_users = summary["count"].sum()
    if total_users > 0:
        summary["percentage"] = (summary["count"] / total_users) * 100
    else:
        summary["percentage"] = 0

    return summary.to_dict(orient="records")

def get_ml_metrics() -> Dict:
    """Retourne les métriques des modèles (chargées depuis un fichier de métriques)."""
    metrics_path = MODELS_DIR / "metrics.json"
    if not metrics_path.exists():
        download_model_from_gcs("models/metrics.json", str(metrics_path))
        
    if metrics_path.exists():
        import json
        with open(metrics_path) as f:
            return json.load(f)
    # Fallback si pas encore entraîné
    return {
        "xgboost": {"accuracy": None, "status": "not_trained"},
        "kmeans":  {"silhouette": None, "status": "not_trained"},
    }

def get_churn_distribution() -> List[Dict]:
    """Retourne la distribution des scores de churn par buckets de 10%."""
    xgb, _, _ = _load_models()
    df = load_features_from_db()
    
    for col in FEATURE_COLS + ["plan_encoded"]:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    X = df[FEATURE_COLS + ["plan_encoded"]]
    probs = xgb.predict_proba(X)[:, 1]
    
    # Bucketizing par déciles
    bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    labels = ["0-10%", "10-20%", "20-30%", "30-40%", "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "90-100%"]
    dist = pd.cut(probs, bins=bins, labels=labels, include_lowest=True).value_counts().sort_index()
    
    return [{"name": k, "count": int(v)} for k, v in dist.items()]
