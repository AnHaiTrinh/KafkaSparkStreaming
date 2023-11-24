import os
import sys
import json

from confluent_kafka import Consumer, KafkaError, KafkaException


consumer = Consumer({
    'bootstrap.servers': 'localhost:9092,localhost:9093',
    'group.id': f'{os.getenv("KAFKA_CONSUMER_GROUP_ID")}',
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
                print('_' * 20)
                consumer.commit(asynchronous=False)
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()


def shutdown():
    running = False
    print('Shutting down consumer...')


if __name__ == '__main__':
    try:
        topics = sys.argv[1]
        topics = topics.split(',')
        basic_consume_loop(consumer, topics)
    except IndexError:
        print('Please provide a topic name to consume')
        sys.exit(1)
    except KeyboardInterrupt:
        shutdown()
        sys.exit(0)
