from confluent_kafka import Consumer

# running the script outside the docker container
# so, connecting to LISTENER_EXTERNAL://localhost:29092
c = Consumer({
    'bootstrap.servers': 'localhost:29092',
    'group.id': 'my-app',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['user-login'])

print('Consuming messages')

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))

c.close()
