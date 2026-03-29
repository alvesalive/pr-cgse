from fastapi import FastAPI

app = FastAPI(title="SVC Pedidos - Sprint 1 Stub")

@app.get("/")
def read_root():
    return {"status": "ok", "service": "pedidos"}
