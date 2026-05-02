"""
Trainer : entraine XGBoost (churn) + K-Means (segmentation) et sauvegarde les modeles.
Lancement : cd backend/src && python -m services.ml.trainer
"""
import sys, os, json
from pathlib import Path

# Charger .env
ROOT = Path(__file__).resolve().parents[4]
from dotenv import load_dotenv
load_dotenv(ROOT / ".env", override=True)

import joblib
import numpy as np
from xgboost import XGBClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.metrics import silhouette_score

from services.ml.feature_engineering import load_features_from_db, FEATURE_COLS

MODELS_DIR = Path(__file__).parent / "models"
MODELS_DIR.mkdir(exist_ok=True)

XGB_PATH     = MODELS_DIR / "churn_model.pkl"
KMEANS_PATH  = MODELS_DIR / "kmeans_model.pkl"
SCALER_PATH  = MODELS_DIR / "scaler.pkl"

SEGMENT_MAP = {0: "power_user", 1: "casual", 2: "at_risk", 3: "dormant"}

def train_churn_model(df):
    print("[XGB] Entrainement XGBoost (Churn)...")
    X = df[FEATURE_COLS + ["plan_encoded"]]
    y = df["churned"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"  [OK] Accuracy : {acc:.4f}")
    print(classification_report(y_test, preds, target_names=["Retained", "Churned"]))

    joblib.dump(model, XGB_PATH)
    print(f"  [SAVED] churn_model.pkl -> {XGB_PATH}")
    return model, acc

def train_segmentation_model(df):
    print("[KMEANS] Entrainement K-Means (Segmentation)...")
    X = df[FEATURE_COLS].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    sil = silhouette_score(X_scaled, labels)
    print(f"  [OK] Silhouette Score : {sil:.4f}")

    cluster_counts = np.bincount(labels)
    for i, count in enumerate(cluster_counts):
        print(f"  Cluster {i} ({SEGMENT_MAP[i]}) : {count} users")

    joblib.dump(kmeans, KMEANS_PATH)
    joblib.dump(scaler, SCALER_PATH)
    print(f"  [SAVED] kmeans_model.pkl + scaler.pkl -> {KMEANS_PATH.parent}")
    return kmeans, scaler, sil

if __name__ == "__main__":
    print("[START] Chargement des features depuis PostgreSQL...")
    df = load_features_from_db()
    print(f"  [OK] {len(df)} users charges.")

    model, acc  = train_churn_model(df)
    kmeans, scaler, sil = train_segmentation_model(df)

    # Sauvegarder les metriques pour l'API
    metrics = {
        "xgboost": {"accuracy": round(acc, 4), "status": "trained", "n_estimators": 200},
        "kmeans":  {"silhouette": round(sil, 4), "status": "trained", "n_clusters": 4},
    }
    with open(MODELS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print("\n[DONE] Entrainement termine !")
    print(f"  XGBoost accuracy    : {acc:.2%}")
    print(f"  K-Means silhouette  : {sil:.4f}")
    print(f"  [SAVED] metrics.json -> {MODELS_DIR / 'metrics.json'}")
