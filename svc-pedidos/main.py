from fastapi import FastAPI
from database import engine, Base
from routes import router

import logging

app = FastAPI(title="SVC Pedidos")

try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    logging.warning(f"Falha inócua na criacao de tabelas via replica: {e}")

app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "pedidos_core_sync_async"}
