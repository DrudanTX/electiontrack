from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "working"}

@app.get("/predict")
def predict():
    return {
        "message": "prediction endpoint alive",
        "note": "we will add model next"
    }
