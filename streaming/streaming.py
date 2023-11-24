from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, count, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType
import os

checkpoint_path = "/tmp/kafka/checkpoint"
os.makedirs(checkpoint_path, exist_ok=True)

spark = SparkSession \
    .builder \
    .appName("Spark Kafka Streaming") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

# spark.sparkContext.setLogLevel("ERROR")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:29092,kafka2:29093") \
    .option("subscribe", "jdbc_activity_logs") \
    .option("startingOffsets", "earliest") \
    .load()

schema = StructType([
    StructField("parking_lot_id", IntegerType(), False),
    StructField("license_plate", StringType(), False),
    StructField("vehicle_type", StringType(), False),
    StructField("activity_type", StringType(), False),
    StructField("created_at", DateType(), False)
])

aggregate = df.selectExpr("CAST(value AS STRING) AS json") \
    .withColumn("data", from_json("json", schema)) \
    .selectExpr("data.parking_lot_id AS parking_lot_id",
                "data.license_plate AS license_plate",
                "data.vehicle_type AS vehicle_type",
                "data.activity_type AS activity_type",
                "data.created_at AS created_at") \
    .groupby("parking_lot_id") \
    .agg(count("license_plate").alias("visit_count")) \
    .withColumn('value', to_json(struct("parking_lot_id", "visit_count")))

query = aggregate \
    .selectExpr("CAST(parking_lot_id AS STRING) AS key", "value") \
    .writeStream \
    .outputMode("update") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:29092,kafka2:29093") \
    .option("topic", "parking_lot_agg") \
    .option("checkpointLocation", checkpoint_path) \
    .start()

query.awaitTermination()
