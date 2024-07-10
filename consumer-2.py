import json
import os

from confluent_kafka import Consumer, KafkaError
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.auth import HTTPBasicAuth

IN_TOPIC = 'processed-user-login'
OS_INDEX = 'processed-user-login-index'

# Kafka consumer configuration
CONSUMER_CONFIG = {
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'my-app',
    'auto.offset.reset': 'earliest'
}

# Kafka consumer
c = Consumer(CONSUMER_CONFIG)
c.subscribe([IN_TOPIC])

# OpenSearch configuration
opensearch_host = os.getenv('OPENSEARCH_HOST', 'localhost')
opensearch_port = int(os.getenv('OPENSEARCH_PORT', 9200))
opensearch_user = os.getenv('OPENSEARCH_USER', 'admin')
opensearch_password = os.getenv('OPENSEARCH_PASSWORD', 'admin')

# OpenSearch client
opensearch = OpenSearch(
    hosts=[{'host': opensearch_host, 'port': opensearch_port}],
    http_auth=HTTPBasicAuth(opensearch_user, opensearch_password),
    use_ssl=True,
    verify_certs=False,
    connection_class=RequestsHttpConnection
)


def index_message_to_opensearch(message):
    """Function to index messages to OpenSearch"""
    doc_id = message["user_id"]
    response = opensearch.index(
        index=OS_INDEX,
        id=doc_id,
        body=message
    )
    print(f"Indexed message {doc_id}: {response['result']}")


print('kafka topic ({}) >>> opensearch index ({})'.format(IN_TOPIC, OS_INDEX))
try:
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

        # Deserialize the message
        message = json.loads(msg.value().decode('utf-8'))

        # Index the message to OpenSearch
        index_message_to_opensearch(message)

except KeyboardInterrupt:
    pass
finally:
    c.close()
