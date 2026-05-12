import pandas as pd
import numpy as np
import uuid

def generate_perfect_data(n_users=2000):
    data = []
    
    # Proportions
    counts = {
        'power_user': int(n_users * 0.25),
        'casual': int(n_users * 0.35),
        'at_risk': int(n_users * 0.25),
        'dormant': int(n_users * 0.15)
    }
    
    for segment, count in counts.items():
        for _ in range(count):
            user_id = f"usr_{uuid.uuid4().hex[:8]}"
            
            if segment == 'power_user':
                session_count_7d = np.random.randint(10, 21)
                feature_breadth = np.random.randint(6, 11)
                avg_session_duration_min = np.random.uniform(20, 60)
                days_since_last_use = np.random.randint(0, 2)
                engagement_score = np.random.uniform(80, 100)
                churned = 0
                plan = np.random.choice(['pro', 'enterprise'], p=[0.4, 0.6])
                
            elif segment == 'casual':
                session_count_7d = np.random.randint(3, 8)
                feature_breadth = np.random.randint(3, 6)
                avg_session_duration_min = np.random.uniform(10, 25)
                days_since_last_use = np.random.randint(2, 6)
                engagement_score = np.random.uniform(40, 65)
                churned = 1 if np.random.random() < 0.05 else 0
                plan = np.random.choice(['free', 'pro'], p=[0.7, 0.3])
                
            elif segment == 'at_risk':
                session_count_7d = np.random.randint(0, 3)
                feature_breadth = np.random.randint(1, 3)
                avg_session_duration_min = np.random.uniform(5, 15)
                days_since_last_use = np.random.randint(7, 15)
                engagement_score = np.random.uniform(15, 35)
                churned = 1 if np.random.random() < 0.6 else 0
                plan = 'free'
                
            else: # dormant
                session_count_7d = 0
                feature_breadth = 0
                avg_session_duration_min = 0
                days_since_last_use = np.random.randint(15, 61)
                engagement_score = np.random.uniform(0, 10)
                churned = 1 if np.random.random() < 0.95 else 0
                plan = 'free'
                
            data.append({
                'user_id': user_id,
                'session_count_7d': session_count_7d,
                'feature_breadth': feature_breadth,
                'avg_session_duration_min': round(avg_session_duration_min, 2),
                'days_since_last_use': days_since_last_use,
                'engagement_score': round(engagement_score, 2),
                'churned': churned,
                'plan': plan,
                'segment': segment
            })
            
    df = pd.DataFrame(data)
    df.to_csv('perfect_users.csv', index=False)
    print(f"[OK] 2000 users generated in perfect_users.csv")

if __name__ == "__main__":
    generate_perfect_data()
