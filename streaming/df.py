import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, BooleanType
from spark_session import spark
import os

kafka_brokers = os.getenv("KAFKA_BROKERS")

activity_log_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("activity_type", StringType(), False),
    StructField("vehicle_id", IntegerType(), False),
    StructField("timestamp", StringType(), False),
    StructField("parking_lot_id", IntegerType(), False)
])

parking_space_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("longitude", FloatType(), False),
    StructField("latitude", FloatType(), False),
    StructField("created_at", StringType(), False),
    StructField("updated_at", StringType(), True),
    StructField("referred_at", StringType(), True),
    StructField("is_active", BooleanType(), False),
    StructField("deleted_at", StringType(), True),
    StructField("vehicle_type", StringType(), False),
    StructField("vehicle_id", IntegerType(), True),
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

rating_feedback_schema = StructType([
    StructField("id", IntegerType(), False),
    StructField("user_id", IntegerType(), False),
    StructField("parking_lot_id", IntegerType(), False),
    StructField("rating", IntegerType(), False),
    StructField("feedback", StringType(), True),
    StructField("created_at", StringType(), False),
    StructField("updated_at", StringType(), True),
    StructField("is_active", BooleanType(), False),
    StructField("deleted_at", StringType(), True)
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
    .withColumn("timestamp", F.to_timestamp("timestamp")) \
    .persist()

parking_space_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "jdbc_parking_spaces") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING) AS json") \
    .withColumn("data", F.from_json("json", parking_space_schema)) \
    .selectExpr("data.id AS id",
                "data.is_active AS is_active",
                "data.vehicle_type AS vehicle_type",
                "data.vehicle_id AS vehicle_id",
                "data.parking_lot_id AS parking_lot_id") \
    .filter("is_active = true") \
    .drop("is_active") \
    .persist()

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
                "data.is_tracked AS is_tracked") \
    .persist()

rating_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", "jdbc_rating_feedbacks") \
    .option("startingOffsets", "earliest") \
    .load() \
    .selectExpr("CAST(value AS STRING) AS json") \
    .withColumn("data", F.from_json("json", rating_feedback_schema)) \
    .selectExpr("data.id AS id",
                "data.is_active AS is_active",
                "data.user_id AS user_id",
                "data.parking_lot_id AS parking_lot_id",
                "data.rating AS rating") \
    .filter("is_active = true") \
    .drop("is_active") \
    .persist()
