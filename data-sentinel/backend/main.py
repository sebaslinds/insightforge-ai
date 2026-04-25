from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DetectRequest(BaseModel):
    data: list[float]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/detect")
def detect(req: DetectRequest):
    model = IsolationForest(contamination=0.1, random_state=42)
    X = [[x] for x in req.data]
    model.fit(X)
    preds = model.predict(X)  # -1 = anomaly
    anomalies = [req.data[i] for i, p in enumerate(preds) if p == -1]
    return {"anomalies": anomalies}
