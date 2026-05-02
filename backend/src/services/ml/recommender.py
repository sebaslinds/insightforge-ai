import pandas as pd
import numpy as np
from sqlalchemy import text
from core.database import SessionLocal
from services.ai.ai_service import generate_insight

def get_recommendations(user_id: str, lang: str = "en"):
    """
    Système de recommandation (Module 5) :
    1. Collaborative Filtering simple (basé sur la co-occurrence des features)
    2. Message personnalisé via GPT-4o
    """
    db = SessionLocal()
    try:
        # 1. Charger les interactions
        sql = "SELECT user_id, feature FROM events WHERE event_type = 'feature_use'"
        df = pd.read_sql(sql, con=db.bind)
        
        if df.empty:
            return []

        # 2. Créer la matrice User-Feature
        user_features = df.groupby(['user_id', 'feature']).size().unstack(fill_value=0)
        user_features = (user_features > 0).astype(int)

        if user_id not in user_features.index:
            # Fallback : features les plus populaires non utilisées
            popular = user_features.sum().sort_values(ascending=False).index.tolist()
            return [{"feature": popular[0], "reason": "Popular among users"}]

        # 3. Trouver des utilisateurs similaires (Jaccard similarity simple)
        target_vector = user_features.loc[user_id]
        
        # Intersection / Union
        intersection = (user_features & target_vector).sum(axis=1)
        union = (user_features | target_vector).sum(axis=1)
        similarity = intersection / union
        
        similar_users = similarity.sort_values(ascending=False).iloc[1:6].index # Top 5
        
        # 4. Features utilisées par les similaires mais pas par le target
        similar_features = user_features.loc[similar_users].sum()
        target_features = user_features.loc[user_id]
        
        recommendations = similar_features[target_features == 0].sort_values(ascending=False)
        
        if recommendations.empty:
             # Fallback si l'utilisateur a déjà tout utilisé
             return []

        top_feature = recommendations.index[0]
        
        # 5. Génération du message via GPT-4o
        payload = {
            "user_id": user_id,
            "recommended_feature": top_feature,
            "context": "Collaborative filtering matched you with similar high-engagement users who value this tool."
        }
        
        import asyncio
        # Comme on est dans un endpoint sync (probablement), on peut utiliser asyncio.run ou juste faire un message template
        # Mais on va essayer de le rendre sympa
        
        return [{
            "feature": top_feature,
            "score": float(recommendations.iloc[0]),
            "message": f"Based on users like you, we suggest trying {top_feature}." # Fallback message
        }]

    finally:
        db.close()

async def get_personalized_recommendation(user_id: str, lang: str = "en"):
    """Version async avec GPT-4o."""
    recs = get_recommendations(user_id, lang)
    if not recs:
        return None
        
    top_rec = recs[0]
    feature = top_rec["feature"]
    
    prompt = (
        f"En tant qu'expert en Customer Success, génère un message court et accrocheur (1 phrase) "
        f"pour encourager l'utilisateur {user_id} à essayer la fonctionnalité '{feature}'. "
        f"L'utilisateur ne l'a pas encore utilisée alors que ses pairs l'adorent. Langue: {lang}."
    )
    
    insight = await generate_insight({"task": "recommendation", "feature": feature, "user_id": user_id, "prompt_override": prompt}, language=lang)
    top_rec["message"] = insight
    
    return top_rec
