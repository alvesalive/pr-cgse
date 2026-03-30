import os
import io
from minio import Minio
from minio.error import S3Error
import logging

logger = logging.getLogger("storage")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "admin_minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "senha_minio_segura")
# Usaremos o localhost exposto para o browser cliente poder bater direto:
MINIO_PUBLIC_URL_PREFIX = "http://localhost:9000" 
BUCKET_NAME = "catalogo-imagens"

try:
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False 
    )
    
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
        logger.info(f"Bucket '{BUCKET_NAME}' ativado localmente via SDK.")
except Exception as e:
    logger.error(f"MinIO Client boot error: {e}")
    minio_client = None

def upload_image(file_data: bytes, file_name: str, content_type: str = "image/jpeg") -> str:
    if not minio_client:
        raise Exception("Object Storage não disponivel")
        
    data_stream = io.BytesIO(file_data)
    data_length = len(file_data)
    
    try:
        minio_client.put_object(
            BUCKET_NAME,
            file_name,
            data_stream,
            length=data_length,
            content_type=content_type
        )
        return f"{MINIO_PUBLIC_URL_PREFIX}/{BUCKET_NAME}/{file_name}"
    except S3Error as err:
        logger.error(f"S3 Erro de upload: {err}")
        raise err
