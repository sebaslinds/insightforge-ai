\# Projet : Moteur de personnalisation IA pour SaaS



\## Stack

\- SDK      : TypeScript leger, capture events utilisateur

\- Frontend : Next.js 14, TypeScript, Tailwind CSS -> Vercel

\- Backend  : FastAPI Python 3.11 -> Render

\- IA       : OpenAI GPT-4o pour messages personnalises

\- ML       : XGBoost churn, K-Means segments, collaborative filtering

\- DB       : PostgreSQL events + scores + segments



\## Les 6 modules

1\. SDK tracker     : capture clics, pages, features utilisees

2\. Feature eng.    : transforme events en features ML

3\. Churn scoring   : XGBoost predit probabilite churn par user

4\. Segmentation    : K-Means classe users en 4 profils

5\. Recommandation  : collaborative filtering + GPT-4o message

6\. Dashboard       : visualise segments, scores, conversions



\## Les 4 profils utilisateur

\- power\_user : usage intense, toutes les features

\- casual     : usage modere, features de base

\- at\_risk    : baisse engagement recente

\- dormant    : inactif depuis 14j+



\## Features ML par user

\- session\_count\_7d     : nb sessions 7 derniers jours

\- feature\_breadth      : nb features distinctes utilisees

\- avg\_session\_duration : duree moyenne session en minutes

\- days\_since\_last\_use  : recence

\- engagement\_score     : score composite 0-100



\## Variables d'environnement

OPENAI\_API\_KEY

DATABASE\_URL

BACKEND\_URL=http://localhost:8000

NEXT\_PUBLIC\_API\_URL=http://localhost:8000



\## Conventions

\- Python : FastAPI, Pydantic, async/await

\- JS/TS  : fonctions fleches, async/await

\- Reponses en francais, concises et chiffrees

