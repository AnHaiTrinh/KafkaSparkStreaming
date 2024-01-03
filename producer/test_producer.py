import time
from datetime import datetime

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

    producer.produce('jdbc_vehicles', value=json.dumps({
        "id": 1,
        "license_plate": "12345678",
        "vehicle_type": "car",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "is_tracked": True,
        "owner_id": 2
    }), callback=acked)
    producer.poll(1)
    time.sleep(5)
    producer.produce('jdbc_activity_logs', value=json.dumps({
        "id": 4,
        "activity_type": "in",
        "vehicle_id": 1,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
        "parking_lot_id": 1,
    }), callback=acked)
    producer.poll(1)
    time.sleep(2)
