import json
from datetime import datetime, timezone

from confluent_kafka import KafkaError, Consumer

IN_TOPIC = 'user-login'
CONSUMER_CONFIG = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'my-app',
    'auto.offset.reset': 'earliest'
}

c = Consumer(CONSUMER_CONFIG)
c.subscribe([IN_TOPIC])

print('Consuming messages')

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            # End of partition event
            print('End of partition reached {} [{}]'.format(
                msg.topic(), msg.partition()))
        elif msg.error():
            print('Consumer error: {}'.format(msg.error()))
            continue

    data = json.loads(msg.value().decode('utf-8'))

    # Transform: Mask IP addresses
    ip_parts = data.get("ip", "").split(".")
    if len(ip_parts) == 4:
        data["ip"] = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.xxx"

    # Transform: Convert timestamp to human-readable format
    timestamp = datetime.fromtimestamp(data["timestamp"], tz=timezone.utc)
    data["timestamp"] = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')

    print('Received message: {}'.format(data))

c.close()
