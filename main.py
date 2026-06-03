from fastapi import FastAPI

app = FastAPI()

@app.post("/load")

@app.post("/transfer")

@app.get("/health")
def health():
    return {"status": "ok"}