from df import activity_log_df, vehicle_df
import pyspark.sql.functions as F

tracked_vehicle_df = activity_log_df \
    .join(vehicle_df, activity_log_df.vehicle_id == vehicle_df.id, how="left") \
    .filter("is_tracked = true") \
    .select("vehicle_id", "license_plate", "parking_lot_id", "timestamp", "activity_type") \
    .withColumn("value", F.to_json(
        F.struct("vehicle_id", "license_plate", "parking_lot_id", "timestamp", "activity_type"))) \
    .selectExpr("CAST(vehicle_id AS STRING) AS key", "value")
