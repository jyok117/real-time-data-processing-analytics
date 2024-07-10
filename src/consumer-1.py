import os
import json

from datetime import datetime, timezone
from confluent_kafka import KafkaError, Consumer, Producer

IN_TOPIC = os.getenv('KAFKA_IN_TOPIC', 'user-login')
OUT_TOPIC = os.getenv('KAFKA_OUT_TOPIC', 'processed-user-login')
BOOTSTRAP_SERVERS = os.getenv('BOOTSTRAP_SERVERS', 'localhost:29092')

CONSUMER_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVERS,
    'group.id': 'my-app',
    'auto.offset.reset': 'earliest'
}
PRODUCER_CONFIG = {
    'bootstrap.servers': BOOTSTRAP_SERVERS
}


def process_message(message):
    data = json.loads(message)

    # Missing field: Set device_type to "unknown" if it's missing
    if "device_type" not in data:
        data["device_type"] = "unknown"

    # Transform: Mask IP addresses
    ip_parts = data.get("ip", "").split(".")
    if len(ip_parts) == 4:
        data["ip"] = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.xxx"

    # Transform: Convert timestamp to human-readable format
    timestamp = datetime.fromtimestamp(data["timestamp"], tz=timezone.utc)
    data["timestamp"] = timestamp.strftime('%Y-%m-%dT%H:%M:%S%z')

    return json.dumps(data)


def error_handler(msg):
    if msg.error().code() == KafkaError._PARTITION_EOF:
        # End of partition event
        print('End of partition reached {} [{}]'.format(
            msg.topic(), msg.partition()))
    elif msg.error():
        print('Consumer error: {}'.format(msg.error()))
        pass


def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(
            msg.topic(), msg.partition()))


def main():
    c = Consumer(CONSUMER_CONFIG)
    p = Producer(PRODUCER_CONFIG)

    c.subscribe([IN_TOPIC])

    print("kafka topic ({}) >>> kafka topic ({})".format(IN_TOPIC, OUT_TOPIC))
    try:
        while True:
            msg = c.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                error_handler(msg)

            # Consume the message from IN_TOPIC and process it
            original_message = msg.value().decode('utf-8')
            processed_message = process_message(original_message)

            # Produce the processed message to OUT_TOPIC
            if processed_message:
                p.produce(
                    OUT_TOPIC,
                    key=msg.key(),
                    value=processed_message.encode('utf-8'),
                    callback=delivery_report
                )
                p.flush()

            # print('Received message: {}'.format(original_message))
            # print('Processed message: {}'.format(processed_message))

    except KeyboardInterrupt:
        pass
    finally:
        # Close the consumer and producer to commit final offsets and clean up
        c.close()
        p.flush()
        p.close()


if __name__ == '__main__':
    main()
