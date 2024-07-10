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

7. Processed the received message

- Masked the IP address `156.125.84.xxx`
- Converted the timestamp to a human-readable format `2024-07-10T15:18:55+0000`

8. Analyzed the output of the processed message and realized the `device_type` is missing in few messages. Updated the processing logic to add a default value (`unknown`) for the `device_type` if it's missing.

```bash
Received message: {"user_id": "d0cf416d-bed2-4077-befb-eb323d643424", "app_version": "2.3.0", "ip": "42.119.222.168", "locale": "WV", "device_id": "1b717fee-50da-44f4-a143-610b2af38048", "timestamp": 1720614565, "device_type": "android"}
Received message: {"user_id": "912be752-589d-4b7a-a253-ed4b2f067dfe", "app_version": "2.3.0", "ip": "118.254.247.117", "locale": "IN", "device_id": "41662b55-b365-4322-8d43-8177e73781d4", "timestamp": 1720614565}
```

9. The processed message is then sent to a new Kafka topic `processed-user-login`.

```bash
(.venv) $ python consumer.py
user-login >>> processed-user-login
Received message: {"user_id": "ec7eb61a-65ca-4059-ba09-800b5a594f00", "app_version": "2.3.0", "ip": "156.125.84.252", "locale": "AR", "device_id": "e16dfeae-077e-4af1-bc85-68d4de452ef1", "timestamp": 1720624735, "device_type": "android"}
Processed message: {"user_id": "ec7eb61a-65ca-4059-ba09-800b5a594f00", "app_version": "2.3.0", "ip": "156.125.84.xxx", "locale": "AR", "device_id": "e16dfeae-077e-4af1-bc85-68d4de452ef1", "timestamp": "2024-07-10T15:18:55+0000", "device_type": "android"}
Message delivered to processed-user-login [0]
```
