## Installation
Create virtual environment and install neccesary library:
```bash
python -m venv venv
source venv/bin/activate # Linux
venv\Scripts\activate # Windows
pip install confluent-kafka
```

Start the docker container with the following command:
```bash
docker compose up -d
```

In a new terminal, start the producer:
```bash
cd producer
python producer.py
```
If the producer is running, the output should be like this:
```bash
Message produced
Offset: 0
Topic: parking-lot-log
Key: b'2'
Value: b'{"parking_lot_id": 2, "license_plate": "6725601a-c9de-448b-8a5f-01672b95d4dd", "vehicle_type": "car", "activity_type": "exit", "created_at": "2023-11-21 19:54:40.147413"}'
____________________
```

In a new terminal, start the consumer (You need to set the consumer group ID):
```bash
$env:KAFKA_CONSUMER_GROUP_ID="MY_CONSUMER_GROUP_ID" # Windows PC
set KAFKA_CONSUMER_GROUP_ID="MY_CONSUMER_GROUP_ID" # Windows CMD
export KAFKA_CONSUMER_GROUP_ID="MY_CONSUMER_GROUP_ID" # Linux
cd consumer
python consumer.py
```
When a message is consumed, the output should be like this:
```bash
Offset: 0
{'parking_lot_id': 2, 'license_plate': '6725601a-c9de-448b-8a5f-01672b95d4dd', 'vehicle_type': 'car', 'activity_type': 'exit', 'created_at': '2023-11-21 19:54:40.147413'}
____________________
````

In a new terminal, wait for the Spark Streaming job to begin, then start the aggregator:
```bash
cd consumer
python agg_consumer.py
```  
The result should be like this:
```bash
Offset: 0
{'parking_lot_id': 2, 'visit_count': 1}
Offset: 1
{'parking_lot_id': 5, 'visit_count': 3}
Offset: 2
{'parking_lot_id': 6, 'visit_count': 2}
Offset: 3
{'parking_lot_id': 2, 'visit_count': 2}
```

## Clean up
```bash
docker compose down
```