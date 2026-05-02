from sqlalchemy import text, func
from core.database import SessionLocal
from core.models import User, Event
from datetime import datetime, timedelta
import pandas as pd

def update_user_features():
    """
    Module 2 : Feature Engineering
    Transforme les événements bruts en features agrégées dans la table users.
    """
    db = SessionLocal()
    try:
        print("[Feature Updater] Démarrage de la mise à jour des features...")
        
        # 1. Calculer les sessions (approximé par session_start ou feature_use distinct par jour/heure)
        # Pour faire simple : nombre d'événements distincts par jour sur les 7 derniers jours
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        # Requête SQL pour agréger les features par utilisateur
        # - session_count_7d : jours distincts avec activité
        # - feature_breadth : features distinctes utilisées
        # - days_since_last_use : différence entre aujourd'hui et le dernier événement
        
        sql = text("""
            SELECT 
                user_id,
                COUNT(DISTINCT DATE(timestamp)) as session_count_7d,
                COUNT(DISTINCT feature) as feature_breadth,
                MAX(timestamp) as last_event
            FROM events
            WHERE timestamp >= :start_date
            GROUP BY user_id
        """)
        
        results = db.execute(sql, {"start_date": seven_days_ago}).fetchall()
        
        updated_count = 0
        for row in results:
            user_id = row[0]
            sessions_7d = row[1]
            breadth = row[2]
            last_event = row[3]
            
            days_since = (datetime.utcnow() - last_event).days
            
            # Mise à jour de l'utilisateur
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.session_count_7d = sessions_7d
                user.feature_breadth = breadth
                user.days_since_last_use = days_since
                
                # Calcul d'un score d'engagement simple (0-100)
                # Max théorique : 7 jours * 10 features = 70. On normalise.
                engagement = min(100, (sessions_7d * 10) + (breadth * 3))
                user.engagement_score = engagement
                
                updated_count += 1
        
        db.commit()
        print(f"[Feature Updater] Succès : {updated_count} utilisateurs mis à jour.")
        
    except Exception as e:
        print(f"[Feature Updater] Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_user_features()
