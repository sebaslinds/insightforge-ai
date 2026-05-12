"""
Trainer : entraine XGBoost (churn) + K-Means (segmentation) et sauvegarde les modeles.
Lancement : cd backend/src && python -m services.ml.trainer
"""
import sys, os, json
from pathlib import Path
from datetime import datetime

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
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA

from services.ml.feature_engineering import load_features_from_db, FEATURE_COLS
from core.database import SessionLocal
from core.models import User
from sqlalchemy import text
from services.storage_service import upload_model_to_gcs

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

    # Calculer l'importance des features
    importance = model.feature_importances_
    feature_names = X.columns.tolist()
    feat_imp = {name: float(imp) for name, imp in zip(feature_names, importance)}

    joblib.dump(model, XGB_PATH)
    upload_model_to_gcs(str(XGB_PATH), "models/churn_model.pkl")
    print(f"  [SAVED] churn_model.pkl -> {XGB_PATH}")
    return model, acc, feat_imp

def train_segmentation_model(df):
    print("[KMEANS] Entrainement K-Means (Segmentation)...")
    X = df[FEATURE_COLS].copy()
    X = X.fillna(0)

    # RobustScaler est plus resistant aux outliers que StandardScaler
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)

    # PCA aide a reduire le bruit et a mieux separer les clusters
    pca = PCA(n_components=3, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    # KMeans avec meilleure initialisation
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=20, init='k-means++')
    labels = kmeans.fit_predict(X_pca)

    sil = silhouette_score(X_pca, labels)
    print(f"  [OK] Silhouette Score (PCA) : {sil:.4f}")

    cluster_counts = np.bincount(labels)
    for i, count in enumerate(cluster_counts):
        print(f"  Cluster {i} ({SEGMENT_MAP[i]}) : {count} users")

    joblib.dump(kmeans, KMEANS_PATH)
    joblib.dump(scaler, SCALER_PATH)
    joblib.dump(pca, MODELS_DIR / "pca.pkl")
    
    upload_model_to_gcs(str(KMEANS_PATH), "models/kmeans_model.pkl")
    upload_model_to_gcs(str(SCALER_PATH), "models/scaler.pkl")
    upload_model_to_gcs(str(MODELS_DIR / "pca.pkl"), "models/pca.pkl")
    
    print(f"  [SAVED] kmeans + scaler + pca -> {KMEANS_PATH.parent}")
    return kmeans, scaler, pca, sil

if __name__ == "__main__":
    print("[START] Chargement des features depuis PostgreSQL...")
    df = load_features_from_db()
    print(f"  [OK] {len(df)} users charges.")

    model, acc, feat_imp  = train_churn_model(df)
    kmeans, scaler, pca, sil = train_segmentation_model(df)

    # Sauvegarder les metriques pour l'API
    metrics = {
        "xgboost": {
            "accuracy": round(acc, 4), 
            "status": "trained", 
            "n_estimators": 200,
            "feature_importance": feat_imp
        },
        "kmeans":  {"silhouette": round(sil, 4), "status": "trained", "n_clusters": 4},
        "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(MODELS_DIR / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    upload_model_to_gcs(str(MODELS_DIR / "metrics.json"), "models/metrics.json")

    print("\n[PERSISTENCE] Sauvegarde des rAsultats dans PostgreSQL...")
    db = SessionLocal()
    try:
        # PrAdiction des segments finaux pour tous les utilisateurs
        X_feats = df[FEATURE_COLS]
        X_scaled = scaler.transform(X_feats)
        X_pca = pca.transform(X_scaled)
        df["cluster"] = kmeans.predict(X_pca)
        
        # Mapping dynamique (identique A predictor.py)
        cluster_stats = df.groupby("cluster")["engagement_score"].mean().sort_values(ascending=False)
        dynamic_map = {cluster_id: name for cluster_id, name in zip(cluster_stats.index, ["power_user", "casual", "at_risk", "dormant"])}
        df["segment_name"] = df["cluster"].map(dynamic_map)
        
        # PrAdiction des scores de churn
        X_xgb = df[FEATURE_COLS + ["plan_encoded"]]
        df["churn_score"] = model.predict_proba(X_xgb)[:, 1]
        
        # Mise A jour par lots (bulk update) pour la performance
        print(f"  [DB] Synchronisation de {len(df)} utilisateurs...")
        update_data = [
            {"seg": row["segment_name"], "churn": float(row["churn_score"]), "uid": row["user_id"]}
            for _, row in df.iterrows()
        ]
        
        # Utilisation de bindparam pour une mise a jour groupée efficace
        db.execute(
            text("UPDATE users SET segment = :seg, churn_score = :churn WHERE user_id = :uid"),
            update_data
        )
        db.commit()
        print(f"  [OK] {len(df)} utilisateurs mis A jour dans la base.")
    except Exception as e:
        print(f"  [ERROR] Erreur persistence : {e}")
        db.rollback()
    finally:
        db.close()

    print("\n[DONE] Entrainement et synchronisation terminAs !")
    print(f"  XGBoost accuracy    : {acc:.2%}")
    print(f"  K-Means silhouette  : {sil:.4f}")
    print(f"  [SAVED] metrics.json -> {MODELS_DIR / 'metrics.json'}")
