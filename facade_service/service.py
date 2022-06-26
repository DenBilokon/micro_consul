import random
import uuid
import pika
import time
import requests
import consul
import logging
from flask import Flask, request


app = Flask(__name__)


@app.route('/facade_service', methods=['POST'])
def facade_service_post():
    message = request.json.get('Message')
    send_message_to_queue(message)
    logging_service_response = requests.post(
        url=get_rand_logging_service_url(),
        json={
            "UUID": str(uuid.uuid4()),
            "Message": message
        }
    )
    status = logging_service_response.status_code
    return app.response_class(status=status)


@app.route('/facade_service', methods=['GET'])
def facade_service_get():
    ls_response = requests.get(get_rand_logging_service_url())
    ms_request = requests.get(get_rand_messages_service_url())
    return str(ls_response.text) + ' : ' + str(ms_request.text)


@app.route('/health', methods=['GET'])
def health():
    return app.response_class(status=200)


def register(consul_client, port):
    check_http = consul.Check.http(f'http://facade_service:{port}/health', interval='10s')
    consul_client.agent.service.register(
        'facade_service',
        service_id=f'facade_service',
        address="facade_service",
        port=port,
        check=check_http,
    ) 


def get_kv(c, name):
    return c.kv.get(name)[1]['Value'].decode()[1:-1]


def discover_service(name):
    services = []
    while not services:
        for s in consul_client.health.service(name, passing=True)[1]:
            info = s['Service']
            services.append(f"{info['Address']}:{info['Port']}")
        if services:
            break
        time.sleep(2)
    return random.choice(services)


def get_rand_logging_service_url():
    return f"http://{discover_service('logging_service')}/logging-service"


def get_rand_messages_service_url():
    return f"http://{discover_service('messages_service')}/messages-service"


def send_message_to_queue(message):
    mq_connection = pika.BlockingConnection(
        pika.ConnectionParameters(get_kv(consul_client, "rabbit_host"))
    )
    channel = mq_connection.channel()
    queue = get_kv(consul_client, "queue")
    channel.queue_declare(queue=queue)
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=message)
    logging.info(f"Sent message: {message}")
    mq_connection.close()


if __name__ == '__main__':
    port = 8888
    consul_client = consul.Consul(host="consul-server")
    register(consul_client, port)
    app.run(host="0.0.0.0",
            port=port,
            debug=True)
