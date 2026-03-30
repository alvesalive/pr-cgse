import os
import pika
import json
import logging

logger = logging.getLogger("messaging")

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq-broker:5672/")

def publish_order_notification(user_uuid: str, order_id: str, status: str, total: float, event_type: str = "ORDER_CREATED"):
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        queue_name = "notificacoes_pedidos"
        channel.queue_declare(queue_name, durable=True)
        
        message = {
            "type": event_type,
            "user_uuid": str(user_uuid),
            "pedido_id": str(order_id),
            "status": status,
            "total": total
        }
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        connection.close()
        logger.info(f"Notificacao do Pedido {order_id} viazada pro RabbitMQ.")
    except Exception as e:
        logger.error(f"Erro RabbitMQ: {e}")
