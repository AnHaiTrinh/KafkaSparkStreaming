import time
from datetime import datetime, timedelta
import random

from confluent_kafka import Producer
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
    producer = Producer({'bootstrap.servers': 'localhost:9092,localhost:9093,localhost:9094'})
    for i in range(100):
        producer.produce('jdbc_vehicles', value=json.dumps({
            "id": 1000 + i,
            "license_plate": "12345678",
            "vehicle_type": random.choice(["car", "motorbike", "bicycle"]),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "is_tracked": True,
            "owner_id": 2
        }), callback=acked)
        producer.poll(1)
        time.sleep(3)
        producer.produce('jdbc_activity_logs', value=json.dumps({
            "id": 60 + i,
            "activity_type": "in",
            "vehicle_id": 1000 + i,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
            "parking_lot_id": 1,
        }), callback=acked)
        producer.poll(1)
        time.sleep(1)

    for i in range(100):
        producer.produce('jdbc_activity_logs', value=json.dumps({
            "id": 600 + i,
            "activity_type": "out",
            "vehicle_id": 1000 + i,
            "timestamp": (datetime.now() + timedelta(days=random.choice([40, 80, 120]))).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "parking_lot_id": 1,
        }), callback=acked)
        producer.poll(1)
        time.sleep(1)
