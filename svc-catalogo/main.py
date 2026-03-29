from fastapi import FastAPI

app = FastAPI(title="SVC Catalogo - Sprint 1 Stub")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "catalogo"}
