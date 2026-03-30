from contextlib import asynccontextmanager
from fastapi import FastAPI
import threading
from database import engine, Base
from routes import router
from worker import run_worker
import auth
import models

# Cria as tabelas do banco no arranque caso não existam
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa thread do rabbitmq para notificação de pedidos
    worker_thread = threading.Thread(target=run_worker, daemon=True)
    worker_thread.start()
    yield

app = FastAPI(title="SVC Auth - Nuvem Soberana", lifespan=lifespan)

# Registro do router local
app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "auth"}
