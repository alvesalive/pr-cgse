import logging
import os
import uuid
from database import SessionLocal, engine, Base
from models import Product
from storage import upload_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("seed")

def upload_seed_image(file_path: str, product_id: uuid.UUID) -> str:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            file_bytes = f.read()
        filename = f"{product_id}_{os.path.basename(file_path)}"
        try:
            url = upload_image(file_bytes, filename, content_type="image/png")
            return url
        except Exception as e:
            logger.error(f"Erro ao subir imagem {file_path}: {e}")
            return None
    return None

def main():
    logger.info("Checando DDL...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    count = db.query(Product).count()
    if count == 0:
        logger.info("Base zerada. Rodando Seed dos top 3 produtos com imagens...")
        
        p1 = Product(nome="Laptop Corporativo", descricao="Workstation 16GB RAM i7", preco_atual=4500.00, id=uuid.uuid4())
        p2 = Product(nome="Monitor 27 UltraWide", descricao="Monitor secundario para devs", preco_atual=1200.50, id=uuid.uuid4())
        p3 = Product(nome="Cadeira Ergonomica", descricao="Cadeira com apoio lombar", preco_atual=890.00, id=uuid.uuid4())
        
        p1.anexo_url = upload_seed_image("assets/laptop.png", p1.id)
        p2.anexo_url = upload_seed_image("assets/monitor.png", p2.id)
        p3.anexo_url = upload_seed_image("assets/cadeira.png", p3.id)

        db.add_all([p1, p2, p3])
        db.commit()
        logger.info("Seed feito e commitado com imagens.")
    else:
        logger.info(f"O banco ja listava {count} produtos. Seed pulado.")
        
    db.close()

if __name__ == "__main__":
    main()
