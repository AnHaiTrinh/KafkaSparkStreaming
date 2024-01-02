import sys

from confluent_kafka import Producer
import time
import random
import datetime
import json


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
    producer = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'})
    schema = {
        "type": "struct",
        "fields": [
            {
                "type": "string",
                "optional": False,
                "field": "state"
            }, {
                "type": "int64",
                "optional": False,
                "field": "vehicle_id"
            }, {
                "type": "string",
                "optional": False,
                "field": "updated_at"
            },
        ],
        "optional": False,
        "name": "parking_state_schema"
    }

    for i in range(12, 21):
        payload = {
            'state': 'in',
            'vehicle_id': 1,
            'updated_at': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        }
        producer.produce(topic, key=json.dumps({
            "schema": {
                "type": "struct",
                "fields": [
                    {
                        "type": "int64",
                        "optional": False,
                        "field": "id"
                    }
                ],
                "optional": False,
                "name": "parking_space_id_schema"
            },
            "payload": {
                "id": i
            }
        }), value=json.dumps({
            "schema": schema,
            "payload": payload
        }), callback=acked)
        time.sleep(random.uniform(1, 2))
        # Wait up to 1 second for events. Callbacks will be invoked during
        # this method call if the message is acknowledged.
        producer.poll(1)
