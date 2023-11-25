## Kafka consumer and producer
Create virtual environment and install neccesary library:
```bash
python -m venv venv
source venv/bin/activate # Linux\MacOS
venv\Scripts\activate # Windows
pip install confluent-kafka
```

Start the docker containers with the following command:
```bash
docker compose up -d
```

In a new terminal, start the producer:
```bash
cd producer
python producer.py jdbc_activity_logs
```
If the producer is running, the output should be like this:
```bash
Message produced
Offset: 0
Key: b'2'
Value: b'{"parking_lot_id": 2, "license_plate": "6725601a-c9de-448b-8a5f-01672b95d4dd", "vehicle_type": "car", "activity_type": "exit", "created_at": "2023-11-21 19:54:40.147413"}'
____________________
```

In a new terminal, start the consumer (You need to set the consumer group ID):
```bash
$env:KAFKA_CONSUMER_GROUP_ID="MY_CONSUMER_GROUP_ID" # Windows PC
set KAFKA_CONSUMER_GROUP_ID="MY_CONSUMER_GROUP_ID" # Windows CMD
export KAFKA_CONSUMER_GROUP_ID="MY_CONSUMER_GROUP_ID" # Linux\MacOS
cd consumer
python consumer.py jdbc_activity_logs
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
python consumer.py parking_lot_agg
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
## Kafka connect
Unzip the zip file in *connectors* folder then move the *lib* folder (the ones containing .jar files) to the *connectors* folder

Wait for the kafka-connect container to start, then run the following command to create the connector:
```bash
docker exec -it kafka-connect bash
curl -i -X POST -H "Content-Type: application/json" -d @/connectors/jdbc-source-connect.json http://localhost:8083/connectors
# The response code should be 201
```
Check the result using kafka console consumer:
```bash
docker exec -it kafka1 bash
# Check if the topic from kafka-connect is created or not
# There should be a topic named "jdbc_activity_logs"
/bin/kafka-topics --list --bootstrap-server kafka1:29092,kafka2:29093

# List the messages in the specified topic
/bin/kafka-console-consumer --bootstrap-server kafka1:29092,kafka2:29093 --topic jdbc_activity_logs --from-beginning
# Or alternatively with consumer.py program
cd consumer
python consumer.py 
```
Try insert more data into the database, then check updated output in the kafka console consumer

## Clean up
```bash
docker compose down
```

## Note

If you are running on Linux\MacOS, you might need to change the volume mount path in the docker-compose.yml file, for example:
- .\connectors:/connectors -> ./connectors:/connectors
- .\postgres:/var/lib/postgresql/data -> ./postgres:/var/lib/postgresql/data
