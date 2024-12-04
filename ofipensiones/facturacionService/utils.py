import pika
import json

def send_to_rabbitmq(exchange, routing_key, message, rabbit_host='10.142.0.12', rabbit_user='microservicios_user', rabbit_password='password'):
    """
    Publica un mensaje en RabbitMQ.
    """
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=rabbit_host,
            credentials=pika.PlainCredentials(rabbit_user, rabbit_password)
        )
    )
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, exchange_type='topic')

    channel.basic_publish(
        exchange=exchange,
        routing_key=routing_key,
        body=json.dumps(message)
    )

    connection.close()
