from fastapi import APIRouter, BackgroundTasks
from services.ml.predictor import get_churn_scores, get_segments, get_ml_metrics

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
        from services.ml.feature_engineering import load_features_from_db
        from services.ml.trainer import train_churn_model, train_segmentation_model
        import json
        from pathlib import Path

        df = load_features_from_db()
        model, acc   = train_churn_model(df)
        _, _, sil    = train_segmentation_model(df)

        metrics = {
            "xgboost": {"accuracy": round(acc, 4), "status": "trained"},
            "kmeans":  {"silhouette": round(sil, 4), "status": "trained"},
        }
        models_dir = Path(__file__).parent.parent.parent / "services" / "ml" / "models"
        with open(models_dir / "metrics.json", "w") as f:
            json.dump(metrics, f)

    background_tasks.add_task(_train)
    return {"status": "training_started", "message": "Les modèles sont en cours d'entraînement."}
