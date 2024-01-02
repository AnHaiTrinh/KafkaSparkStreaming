from pyspark.sql import SparkSession
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType
from pyspark.sql.avro.functions import to_avro
import os

checkpoint_path = "/tmp/kafka/checkpoint"
os.makedirs(checkpoint_path, exist_ok=True)

spark = SparkSession \
    .builder \
    .appName("Spark Kafka Streaming") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

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
    .selectExpr("data.id AS id",
                "data.activity_type AS activity_type",
                "data.parking_lot_id AS parking_lot_id",
                "data.vehicle_id AS vehicle_id",
                "data.timestamp AS timestamp") \
    .withColumn("timestamp", F.to_timestamp("timestamp"))

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
                "data.is_tracked AS is_tracked")

tracked_vehicle_df = activity_log_df \
    .join(vehicle_df, activity_log_df.vehicle_id == vehicle_df.id, how="left") \
    .filter("is_tracked = true") \
    .select("vehicle_id", "license_plate", "parking_lot_id", "timestamp", "activity_type") \
    .withColumn("value", F.to_json(
        F.struct("vehicle_id", "license_plate", "parking_lot_id", "timestamp", "activity_type"))) \
    .selectExpr("CAST(vehicle_id AS STRING) AS key", "value")

tracked_vehicle_query = tracked_vehicle_df \
    .writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("topic", "tracked_vehicles") \
    .option("checkpointLocation", f"{checkpoint_path}/tracked_vehicles") \
    .outputMode("append") \
    .start()

tracked_vehicle_query.awaitTermination()
