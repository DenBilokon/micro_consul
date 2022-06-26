import hazelcast
import sys
import consul
import logging
from flask import Flask, request


app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    return app.response_class(status=200)


@app.route('/logging-service', methods=['POST'])
def log():
    m = get_key_value(consul_client, 'map')
    uuid = str(request.json['UUID'])
    message = str(request.json['Message'])
    logging.info(f"UUID: {uuid}\nMessage: {message}")
    dist_map = client.get_map(m)
    dist_map.set(uuid, message)
    return app.response_class(status=200)


@app.route('/logging-service', methods=['GET'])
def list_log():
    m = get_key_value(consul_client, 'map')
    distributed_map = client.get_map(m)
    messages = distributed_map.values().result()
    return ','.join([msg for msg in messages]) or ''


def get_key_value(c, name):
    return c.kv.get(name)[1]['Value'].decode()[1:-1]


def register(consul_client, service_id, port):
    check_http = consul.Check.http(f'http://logging_service_{service_id}:{port}/health', interval='10s')
    consul_client.agent.service.register(
        'logging_service',
        service_id=f'logging_service_{service_id}',
        address=f"logging_service_{service_id}",
        port=port,
        check=check_http,)


if __name__ == '__main__':
    service_id = int(sys.argv[1])
    port = 8890
    consul_client = consul.Consul(host="consul-server")
    client = hazelcast.HazelcastClient(
        cluster_members=get_key_value(consul_client, "hazelcast_addrs").split(',')
    )
    register(consul_client, service_id, port)
    app.run(host="0.0.0.0",
            port=port,
            debug=True)
