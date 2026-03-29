from fastapi import FastAPI

app = FastAPI(title="SVC Auth - Sprint 1 Stub")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "auth"}
