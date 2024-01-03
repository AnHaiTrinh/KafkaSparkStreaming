import json

from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, BooleanType
import os

checkpoint_path = "/tmp/kafka/checkpoint"
os.makedirs(checkpoint_path, exist_ok=True)

spark = SparkSession \
    .builder \
    .appName("Spark Kafka Streaming") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")

kafka_brokers = os.getenv("KAFKA_BROKERS")

activity_log_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("activity_type", StringType(), False),
    StructField("vehicle_id", IntegerType(), False),
    StructField("timestamp", StringType(), False),
    StructField("parking_lot_id", IntegerType(), False)
])

vehicle_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("license_plate", StringType(), False),
    StructField("vehicle_type", StringType(), False),
    StructField("created_at", StringType(), False),
    StructField("updated_at", StringType(), True),
    StructField("is_tracked", BooleanType(), False),
    StructField("owner_id", IntegerType(), False)
])

activity_log_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "jdbc_activity_logs") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING) AS json") \
    .withColumn("data", F.from_json("json", activity_log_schema)) \
    .selectExpr("data.id AS activity_log_id",
                "data.activity_type AS activity_type",
                "data.parking_lot_id AS parking_lot_id",
                "data.vehicle_id AS vehicle_id",
                "data.timestamp AS timestamp") \
    .withColumn("timestamp", F.to_timestamp("timestamp")) \
    .withWatermark("timestamp", "1 minute")

vehicle_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "jdbc_vehicles") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING) AS json") \
    .withColumn("data", F.from_json("json", vehicle_schema)) \
    .selectExpr("data.id AS id",
                "data.license_plate AS license_plate",
                "data.vehicle_type AS vehicle_type",
                "data.updated_at AS updated_at",
                "data.is_tracked AS is_tracked") \
    .withColumn("updated_at", F.to_timestamp("updated_at")) \
    .withWatermark("updated_at", "1 minute")

tracked_vehicle_df = activity_log_df \
    .join(vehicle_df, F.expr(
        """vehicle_id = id AND
        timestamp >= updated_at AND
        timestamp <= updated_at + interval 30 days"""), how="leftOuter") \
    .filter("is_tracked = true") \
    .select("activity_log_id", "vehicle_id", "license_plate", "parking_lot_id", "timestamp", "activity_type") \
    .withColumn("value", F.to_json(
        F.struct("vehicle_id", "license_plate", "parking_lot_id", "timestamp", "activity_type"))) \
    .selectExpr("CAST(activity_log_id AS STRING) AS key", "value")

tracked_vehicle_query = tracked_vehicle_df \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("topic", "tracked_vehicles") \
    .option("checkpointLocation", f"{checkpoint_path}/tracked_vehicles") \
    .outputMode("append") \
    .start()

sensors_schema = StructType([
    StructField("id", StringType(), False),
    StructField("vehicle_id", IntegerType(), True),
    StructField("state", StringType(), False),
    StructField("created_at", StringType(), False),
])

sensors_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "sensors") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING) AS json") \
    .withColumn("data", F.from_json("json", sensors_schema)) \
    .selectExpr("data.id AS id",
                "data.vehicle_id AS vehicle_id",
                "data.state AS state",
                "data.created_at AS updated_at")

sensors_jdbc = spark \
    .read \
    .jdbc(os.getenv('DB_URL'), "sensors", properties={
        "user": os.getenv('DB_USER'),
        "password": os.getenv('DB_PASSWORD'),
    }) \
    .filter("is_active = true")


sensors_to_parking_space = sensors_df \
    .join(sensors_jdbc, on='id', how="leftOuter") \
    .select("parking_space_id", "vehicle_id", "state", "updated_at") \
    .withColumn("value", F.to_json(F.struct("vehicle_id", "state", "updated_at"))) \
    .withColumn("key", F.col("parking_space_id").cast(StringType())) \
    .select("key", "value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("topic", "parking_space_state_raw") \
    .option("checkpointLocation", f"{checkpoint_path}/parking_space_state_raw") \
    .outputMode("append") \
    .start()


@F.udf(returnType=StringType())
def add_key_schema(key):
    return json.dumps({
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
            "id": int(key)
        }
    })


@F.udf(returnType=StringType())
def add_value_schema(value):
    return json.dumps({
        "schema": {
            "type": "struct",
            "fields": [
                {
                    "type": "string",
                    "optional": False,
                    "field": "state"
                }, {
                    "type": "int64",
                    "optional": True,
                    "field": "vehicle_id"
                }, {
                    "type": "string",
                    "optional": False,
                    "field": "updated_at"
                },
            ],
            "optional": False,
            "name": "parking_state_schema"
        },
        "payload": json.loads(value)
    })


parking_space_with_schema = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "parking_space_state_raw") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(key AS STRING)", "CAST(value AS STRING)") \
    .withColumn("key", add_key_schema("key")) \
    .withColumn("value", add_value_schema("value")) \
    .select("key", "value") \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("topic", "parking_space_state") \
    .option("checkpointLocation", f"{checkpoint_path}/parking_space_state") \
    .outputMode("append") \
    .start()

spark.streams.awaitAnyTermination()
