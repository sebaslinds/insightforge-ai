from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.ensemble import IsolationForest

app = FastAPI()


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
