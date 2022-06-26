import threading
import pika
import sys
import consul
import logging
from flask import Flask


app = Flask(__name__)
LOCK = threading.Lock()
MESSAGES = []


@app.route('/health', methods=['GET'])
def health():
    return app.response_class(status=200)


@app.route('/messages-service',  methods=['GET'])
def messages():
    with LOCK:
        logging.info(MESSAGES)
        return str(MESSAGES)


def threaded(fn):
    def run(*args, **kwargs):
        t = threading.Thread(target=fn, args=args, kwargs=kwargs)
        t.start()
        return t
    return run


@threaded
def write_message():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='rabbitmq')
    )
    channel = connection.channel()
    consul_client = consul.Consul(host="consul-server")
    queue = get_key_value(consul_client, "queue")
    channel.queue_declare(queue=queue)
    for method_frame, properties, body in channel.consume(queue):
        logging.info(f"Retrieved: {body}")
        with LOCK:
            logging.info(f"Before: {MESSAGES}")
            MESSAGES.append(body.decode())
            logging.info(f"After: {MESSAGES}")


def get_key_value(c, name):
    return c.kv.get(name)[1]['Value'].decode()[1:-1]


def register(service_id, port):
    c = consul.Consul(host="consul-server")
    check_http = consul.Check.http(f"http://messages_service_{service_id}:{port}/health", interval='10s')
    c.agent.service.register(
        'messages_service',
        service_id=f"messages_service_{service_id}",
        address=f"messages_service_{service_id}",
        port=port,
        check=check_http)


if __name__ == '__main__':
    port = 8880
    service_id = int(sys.argv[1])
    write_message()
    register(service_id, port)
    app.run(host="0.0.0.0",
            port=port,
            debug=False)
