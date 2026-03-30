import os
import time
import pika
import logging
from database import SessionLocal
from models import User

logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq-broker:5672/")
QUEUE_NAME = "notificacoes_pedidos"

def callback(ch, method, properties, body):
    import json
    try:
        data = json.loads(body)
        user_uuid  = data.get("user_uuid")
        pedido_id  = data.get("pedido_id")
        event_type = data.get("type", "ORDER_CREATED")
        status     = data.get("status", "")
        total      = data.get("total", 0)

        event_labels = {
            "ORDER_CREATED": "CRIADO",
            "ORDER_UPDATED": "ALTERADO",
            "ORDER_DELETED": "CANCELADO/EXCLUÍDO",
        }
        label = event_labels.get(event_type, event_type)

        db = SessionLocal()
        user = db.query(User).filter(User.id == str(user_uuid)).first()
        db.close()

        if user:
            logger.info(f"[RabbitMQ] Evento: {event_type}")
            logger.info(f"[RabbitMQ] Para: {user.nome_completo} <{user.email}>")
            logger.info(f"[RabbitMQ] Pedido {pedido_id} foi {label} | Status: {status} | Total: R$ {total:.2f}")
        else:
            logger.warning(f"[RabbitMQ] Usuario UUID '{user_uuid}' nao encontrado para o pedido {pedido_id}.")

    except Exception as e:
        logger.error(f"Falha ao processar a notificacao: {e}")


def run_worker():
    parameters = pika.URLParameters(RABBITMQ_URL)
    while True:
        try:
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            logger.info(f"Conectado ao RabbitMQ: Fila '{QUEUE_NAME}'. Aguardando...")
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("Worker desconectado (AMQP). Reconectando em 5 segundos...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Erro inesperado no thread do RabbitMQ: {e}")
            time.sleep(5)
