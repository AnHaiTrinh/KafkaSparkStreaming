from pyspark.sql import SparkSession

spark = SparkSession \
    .builder \
    .appName("Spark Kafka Streaming") \
    .master("spark://spark-master:7077") \
    .getOrCreate()