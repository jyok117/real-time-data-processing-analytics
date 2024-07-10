# Steps

1. Ran all the services (kafka, zookeeper, and the producer script) with `docker-compose up`

2. Analyzed the logs of the producer script to understand the data being sent to the Kafka topic. The producer script generates random user login data and sends it to the Kafka topic `user-login`.

3. Created a Python script to consume messages from the Kafka topic `user-login`. Bumped into an error while trying this.

```bash
(.venv) $ python consumer.py
Consuming messages
%3|1720589406.370|FAIL|rdkafka#consumer-1| [thrd:GroupCoordinator]: GroupCoordinator: kafka:9092: Failed to resolve 'kafka:9092': nodename nor servname provided, or not known (after 14ms in state CONNECT)
```

4. Realized something was wrong with the connection (configuration). Checked the `docker-compose.yml` file and found the following:

```yml
  kafka:
    ...
    ...
    environment:
        KAFKA_ADVERTISED_LISTENERS: LISTENER_INTERNAL://kafka:9092,LISTENER_EXTERNAL://localhost:29092
```

5. Since, I'm running the consumer script outside the Docker network, I need to connect to the Kafka broker using the external listener. Updated the `consumer.py` script to use the external listener.

6. Ran the consumer script again and successfully consumed messages from the Kafka topic `user-login`.

```bash
(.venv) $ python consumer.py
Consuming messages
Received message: {"user_id": "b22a51d5-0f2f-42e3-8505-f2f8d2b01060", "app_version": "2.3.0", "ip": "25.67.253.124", "locale": "WA", "device_id": "37e8136e-b36d-4717-aa68-dbfcaef4d499", "timestamp": 1720589697, "device_type": "iOS"}
```
