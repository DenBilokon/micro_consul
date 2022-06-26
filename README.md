# Microservices on Flask with Hazelcast and Consul using

## Docker commands for build
#### Start Hazelcast instances and Consul resources
```
docker-compose up hz1 hz2 hz3 consul-server consul-client rabbitmq
```
#### Start our services
```
docker-compose up --build facade_service logging_service_1 logging_service_2 logging_service_3 messages_service_1 messages_service_2
```

## Consul Key-Value pairs:
```
rabbit_host : "rabbitmq"
queue : "mq_for_messages_service"
map : "distr_map"
hazelcast_addrs : "hz1:5701,hz2:5701,hz3:5701"
```