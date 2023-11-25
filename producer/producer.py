import sys

from confluent_kafka import Producer
import time
import random
import datetime
import json
from uuid import uuid4

producer = Producer({
    'bootstrap.servers': 'localhost:9092,localhost:9093',
})


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg), str(err)))
    else:
        print("Message produced")
        print(f'Offset: {msg.offset()}')
        print(f'Key: {msg.key()}')
        print(f'Value: {msg.value()}')
        print('_' * 20)


if __name__ == '__main__':
    topic = sys.argv[1]
    while True:
        parking_lot_id = random.randint(1, 10)
        payload = {
            'parking_lot_id': parking_lot_id,
            'license_plate': str(uuid4()),
            'vehicle_type': random.choice(['car', 'motorbike', 'bicycle']),
            'activity_type': random.choice(['enter', 'exit']),
            'created_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        producer.produce(topic, key=str(parking_lot_id), value=json.dumps(payload), callback=acked)
        time.sleep(random.uniform(1, 2))
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.poll(30)
