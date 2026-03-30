from fastapi import FastAPI
from database import engine, Base
from routes import router

app = FastAPI(title="SVC Catalogo - Produtos")

Base.metadata.create_all(bind=engine)

app.include_router(router)

@app.get("/")
def read_root():
    return {"status": "ok", "service": "catalogo_publico_protegido"}
