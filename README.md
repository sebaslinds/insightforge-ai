# 🚀 InsightForge AI

**[🔗 Access Live Application (Demo)](https://frontend-458613429367.northamerica-northeast1.run.app)** | **[📖 User Guide (Documentation)](file:///C:/Users/slind/.gemini/antigravity/brain/fa6aa248-63b7-4d1a-97e6-cd2eefc0c232/user_guide.md)**
*(Use credentials: admin@acme.com / admin123)*

**InsightForge AI** is a multi-tenant B2B SaaS platform that acts as a plug-and-play AI personalization engine for other SaaS companies. It transforms raw behavioral data into actionable insights, predicting churn and segmenting users in real-time, enabling Product and Customer Success teams to trigger the right messages at the right time.

## 🌟 Core Modules

1. **Data Ingestion** 📡
   - Real-time API endpoints designed to ingest simulated user sessions, feature usage, and subscription events (currently seeded via `seed_cloud.py` for over 6,000+ realistic user profiles).
2. **Feature Engine** ⚙️
   - Transforms raw event streams into structured ML features like Feature Breadth, Recency, and Frequency.
3. **Churn Predictor** 📉
   - Advanced **XGBoost** model predicting the exact probability of user departure (Churn Score).
4. **User Segmentation** 👥
   - **K-Means** clustering categorizing users into distinct behavioral profiles (Power Users, Casual, At Risk, Dormant).
5. **Decision Engine** ⚡
   - Rule-based automation engine that triggers smart alerts and webhooks based on real-time ML anomalies.
6. **AI Copilot** 🤖
   - Generative AI assistant powered by **OpenAI GPT-4o** with dynamic Text-to-SQL capabilities, allowing executives to chat directly with their SaaS data.

## ✨ Latest Features (v1.3.8)

- **Stabilized AI Copilot** 🤖: Enhanced response precision using global data summaries and strict conciseness constraints (max 150 words).
- **Interactive AI Charts** 📊: Click on any bar or retention cell to trigger an automated, deep-dive analysis with stable Recharts visualizations.
- **Improved UX & Readability** 📑: Full visibility for all KPI titles (no truncation) and systematic completion of AI sentences.
- **High-Precision Data Summary** 📈: The AI Copilot now utilizes real-time statistical aggregates from the entire PostgreSQL dataset (6,000+ users), ensuring accurate counts and distributions in chat responses.

## 🧠 Tech Stack

- **Frontend**: Next.js 14, React, Tailwind CSS, Recharts (Interactive UI)
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Pydantic, Pandas
- **Machine Learning**: Scikit-Learn, XGBoost, K-Means
- **AI & NLP**: OpenAI GPT-4o
- **Database**: PostgreSQL (Multi-tenant schema)
- **Cloud Infrastructure**: Google Cloud Platform (Cloud Run, Cloud SQL)

## 🛠️ Local Development

### 1. Database Setup
Ensure you have a local PostgreSQL instance running. Create a database named `insightforge`.
Set your environment variables in the `.env` file.
```env
DATABASE_URL=postgresql://user:password@localhost/insightforge
OPENAI_API_KEY=your-openai-api-key
BACKEND_URL=http://localhost:8080
```

### 2. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate  # On Windows: .\.venv\Scripts\activate
pip install -r requirements.txt
# Seed the database with realistic SaaS data
python src/seed_cloud.py
# Run the API server
uvicorn src.main:app --reload --port 8080
```

### 3. Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
The dashboard will be available at `http://localhost:3000`. 
**Demo Credentials:** `admin@acme.com` / `admin123`

## ☁️ Deployment (Google Cloud Platform)

InsightForge is fully containerized and deployed on Google Cloud Run for auto-scaling serverless execution.

We provide automated PowerShell and Bash scripts for deployment:
- `deploy_gcp.ps1 -service all`
- `setup_gcp.sh`

**Production Infrastructure:**
- **Cloud SQL**: Managed PostgreSQL database.
- **Cloud Run (Backend)**: Serving the FastAPI application.
- **Cloud Run (Frontend)**: Serving the Next.js UI.
- **Artifact Registry**: Storing Docker images built via Cloud Build.

For more deployment details, refer to `DEPLOYMENT_GCP.md`.
