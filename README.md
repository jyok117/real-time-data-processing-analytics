# real-time-data-processing-analytics

Fetch Data Ops / Data Engineer Take Home Exercise - Real Time Data Processing and Analytics using Kafka, Docker and OpenSearch

## Requirements

- [docker](https://docs.docker.com/get-docker/)
- [docker-compose](https://docs.docker.com/compose/install/)
- [`confluent-kafka`](https://pypi.org/project/confluent-kafka/)
- [`kafka-python`](https://pypi.org/project/kafka-python/)
- [`openseach-py`](https://pypi.org/project/opensearch-py/)

## Useful Commands

```bash
# Start the services
$ docker-compose up

# Get the details of the running containers
$ docker ps -a

# Consuming messages from the Kafka Topic
$ docker exec -it <kafka> kafka-console-consumer --bootstrap-server localhost:9092 --topic user-login --group my-app

# Get the group id of the Kafka Consumer
$ docker exec -it <kafka> kafka-consumer-groups --bootstrap-server localhost:9092 --list

# List the topics in the Kafka Cluster
$ docker exec -it <kafka> kafka-topics --bootstrap-server localhost:9092 --list
```

## Producer

The producer is a Python script that generates random user login data and sends it to the Kafka topic `user-login`.

### Sample Message

From `my-python-producer`

```json
{
  "user_id": "a6397988-1649-4859-ae5f-a1407b638ca6",
  "app_version": "2.3.0",
  "ip": "108.228.145.239",
  "locale": "RI",
  "device_id": "6221eb3d-89b5-4585-8c98-545b78e24c53",
  "timestamp": 1720576825,
  "device_type": "iOS"
}
```

## Consumer

The consumer-1 is a Python script that reads messages from the Kafka topic `user-login`, processes the messages, and sends the processed messages to the Kafka topic `processed-user-login`.

The consumer-2 is a Python script that reads messages from the Kafka topic `processed-user-login`, indexes the messages to an OpenSearch index `processed-user-login-index`.

```bash
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
(.venv) $ python consumer-1.py &
(.venv) $ python consumer-2.py &
```
