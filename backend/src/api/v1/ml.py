from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from services.ml.predictor import get_churn_scores, get_segments, get_ml_metrics
from services.ml.recommender import get_personalized_recommendation
from core.database import SessionLocal, get_db
from core.models import RecommendationFeedback
from core.security import get_current_user
from core.tenant_models import AdminUser
from sqlalchemy.orm import Session
from sqlalchemy import text
import pandas as pd
import io

router = APIRouter()

@router.get("/churn-scores")
def churn_scores():
    """Top 50 users par risque de churn."""
    return get_churn_scores()

@router.get("/segments")
def segments():
    """Distribution des segments K-Means."""
    return get_segments()

@router.get("/metrics")
def ml_metrics():
    """Métriques de performance des modèles."""
    return get_ml_metrics()

@router.post("/train")
def train_models(background_tasks: BackgroundTasks):
    """Lance un ré-entraînement en arrière-plan."""
    def _train():
        from datetime import datetime
        from services.ml.feature_engineering import load_features_from_db
        from services.ml.trainer import train_churn_model, train_segmentation_model
        from services.ml.feature_updater import update_user_features
        import json
        from pathlib import Path

        # 1. Mettre à jour les features depuis les événements réels
        update_user_features()

        # 2. Charger les données et entraîner
        df = load_features_from_db()
        model, acc   = train_churn_model(df)
        _, _, sil    = train_segmentation_model(df)

        metrics = {
            "xgboost": {"accuracy": round(acc, 4), "status": "trained"},
            "kmeans":  {"silhouette": round(sil, 4), "status": "trained"},
            "last_trained": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        models_dir = Path(__file__).parent.parent.parent / "services" / "ml" / "models"
        with open(models_dir / "metrics.json", "w") as f:
            json.dump(metrics, f)

    background_tasks.add_task(_train)
    return {"status": "training_started", "message": "Les modèles sont en cours d'entraînement."}

@router.get("/users")
def get_ml_users(segment: str = None):
    """Retourne la liste des utilisateurs avec leurs scores ML, filtrable par segment."""
    db = SessionLocal()
    try:
        query = db.query(text("user_id, segment, churn_score, engagement_score, plan, days_since_last_use")).from_statement(
            text("SELECT user_id, segment, churn_score, engagement_score, plan, days_since_last_use FROM users")
        )
        
        # Charger dans un DataFrame pour faciliter le tri/filtrage si besoin
        df = pd.read_sql(query.statement, db.bind)
        
        if segment:
            df = df[df["segment"] == segment]
            
        return df.sort_values("churn_score", ascending=False).head(100).to_dict(orient="records")
    finally:
        db.close()

@router.get("/export-segments")
def export_segments():
    """Génère un export CSV de tous les utilisateurs avec leurs scores ML."""
    db = SessionLocal()
    try:
        sql = text("SELECT * FROM users")
        df = pd.read_sql(sql, db.bind)
        
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=insightforge_segments_export.csv"}
        )
    finally:
        db.close()

@router.get("/recommendations/{user_id}")
async def recommendations(user_id: str, lang: str = "en"):
    """Retourne une recommandation personnalisée pour un utilisateur."""
    return await get_personalized_recommendation(user_id, lang)

@router.post("/recommendations/trigger")
async def trigger_recommendation_campaign(payload: dict):
    """Simule le déclenchement d'une campagne de recommandation."""
    user_id = payload.get("user_id")
    feature = payload.get("feature")
    # Simulation d'envoi d'email ou notification
    return {
        "status": "success",
        "message": f"Campaign triggered for user {user_id} regarding feature '{feature}'",
        "timestamp": pd.Timestamp.now().isoformat()
    }

@router.post("/recommendations/feedback")
async def recommendation_feedback(
    payload: dict,
    current_user: AdminUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enregistre le feedback de l'utilisateur sur une recommandation (Module 9)."""
    user_id = payload.get("user_id")
    feature = payload.get("feature")
    is_helpful = payload.get("is_helpful")
    
    feedback = RecommendationFeedback(
        user_id=user_id,
        feature=feature,
        is_helpful=is_helpful,
        tenant_id=current_user.tenant_id
    )
    db.add(feedback)
    db.commit()
    
    return {"status": "success", "message": "Feedback recorded"}
