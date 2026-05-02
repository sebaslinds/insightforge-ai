import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import uuid
import os

def generate_data():
    # Création du dossier data s'il n'existe pas
    os.makedirs('data', exist_ok=True)

    # Configuration des seeds pour reproductibilité
    np.random.seed(42)
    random.seed(42)

    NUM_USERS = 2000
    PLANS = ['free', 'pro', 'enterprise']
    COUNTRIES = ['US', 'FR', 'UK', 'DE', 'CA', 'ES', 'IT', 'BR', 'AU', 'IN']
    EVENT_TYPES = ['page_view', 'feature_used', 'settings_changed', 'invite_sent', 'export_done']

    users = []
    events = []

    now = datetime.now()
    plan_probs = [0.70, 0.25, 0.05]

    for _ in range(NUM_USERS):
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        signup_date = now - timedelta(days=random.randint(1, 90))
        plan = np.random.choice(PLANS, p=plan_probs)
        country = random.choice(COUNTRIES)
        
        # Règles de réalisme : Les users pro/enterprise ont un engagement_score plus élevé
        if plan == 'enterprise':
            base_engagement = np.random.normal(85, 10)
            feature_breadth = min(10, max(6, int(np.random.normal(8, 2))))
            avg_session_duration_min = max(10.0, np.random.normal(30, 10))
        elif plan == 'pro':
            base_engagement = np.random.normal(65, 15)
            feature_breadth = min(10, max(3, int(np.random.normal(6, 2))))
            avg_session_duration_min = max(5.0, np.random.normal(15, 8))
        else: # free
            base_engagement = np.random.normal(35, 20)
            feature_breadth = min(6, max(0, int(np.random.normal(3, 2))))
            avg_session_duration_min = max(1.0, np.random.normal(8, 5))
            
        engagement_score = min(100, max(0, int(base_engagement)))
        
        # Corrélations réalistes pour les sessions
        session_count_30d = max(0, int(np.random.normal(engagement_score / 2, 5)))
        session_count_7d = max(0, min(session_count_30d, int(np.random.normal(session_count_30d / 4, 2))))
        
        # Corrélation jours depuis dernière utilisation
        if engagement_score > 75:
            days_since_last_use = random.randint(0, 3)
        elif engagement_score > 40:
            days_since_last_use = random.randint(2, 10)
        else:
            days_since_last_use = random.randint(10, 30)
            
        # Règles de réalisme pour le churn
        if feature_breadth >= 8:
            churn_prob = 0.04 # power users churnent rarement (< 5%)
        elif engagement_score < 30:
            churn_prob = 0.70 # < 30 ont 70% de chance de churner
        else:
            # Probabilité de base pour le reste
            churn_prob = max(0.05, 0.50 - (engagement_score * 0.005))
            
        churned = 1 if random.random() < churn_prob else 0
        
        users.append({
            'user_id': user_id,
            'signup_date': signup_date.strftime('%Y-%m-%d'),
            'plan': plan,
            'country': country,
            'session_count_30d': session_count_30d,
            'session_count_7d': session_count_7d,
            'avg_session_duration_min': round(avg_session_duration_min, 1),
            'feature_breadth': feature_breadth,
            'days_since_last_use': days_since_last_use,
            'engagement_score': engagement_score,
            'churned': churned
        })
        
        # Générer 50 events par user en moyenne
        num_events = max(1, int(np.random.normal(50 * (engagement_score / 50), 15)))
        if churned:
            num_events = int(num_events * 0.4)
            
        last_active_date = now - timedelta(days=days_since_last_use)
        
        for _ in range(num_events):
            event_id = f"evt_{uuid.uuid4().hex[:12]}"
            
            if signup_date < last_active_date:
                random_seconds = random.randint(0, int((last_active_date - signup_date).total_seconds()))
                event_time = signup_date + timedelta(seconds=random_seconds)
            else:
                event_time = signup_date
                
            event_type = np.random.choice(EVENT_TYPES, p=[0.4, 0.25, 0.15, 0.1, 0.1])
            feature_name = f"feature_{random.randint(1, max(1, feature_breadth))}" if event_type == 'feature_used' else ""
            session_id = f"ses_{uuid.uuid4().hex[:8]}"
            
            events.append({
                'event_id': event_id,
                'user_id': user_id,
                'timestamp': event_time.isoformat(),
                'event_type': event_type,
                'feature_name': feature_name,
                'session_id': session_id
            })

    df_users = pd.DataFrame(users)
    df_events = pd.DataFrame(events)

    df_users.to_csv('data/users.csv', index=False)
    df_events.to_csv('data/events.csv', index=False)

    print(f"Génération terminée : {len(df_users)} users et {len(df_events)} events.")
    print("Fichiers sauvegardés : data/users.csv, data/events.csv")

if __name__ == "__main__":
    generate_data()
