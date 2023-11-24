import sys
import json

from confluent_kafka import Consumer, KafkaError, KafkaException


consumer = Consumer({
    'bootstrap.servers': 'localhost:9092,localhost:9093',
    'group.id': 'parking_lot_agg',
    'enable.auto.commit': False,
    'auto.offset.reset': 'earliest'
})

running = True


def basic_consume_loop(consumer, topics):
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                print(f'Offset: {msg.offset()}')
                result = json.loads(msg.value().decode('utf-8'))
                print(result)
                consumer.commit(asynchronous=False)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


def shutdown():
    running = False
    print('Shutting down consumer...')


if __name__ == '__main__':
    try:
        basic_consume_loop(consumer, ["parking_lot_agg"])
    except KeyboardInterrupt:
        shutdown()
        sys.exit(0)
