import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, when
from pyspark.sql.types import StructType, StructField, StringType, BooleanType, LongType, TimestampType
import redis as redis_client

# --- Spark + Kafka + Redis config ---
KAFKA_TOPIC = "wiki-edits"
KAFKA_BOOTSTRAP_SERVER = "localhost:9092"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_KEY = "bot_counts"

KAFKA_PACKAGE = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1"

def main():
    print("Initializing SparkSession with Kafka...")
    spark = (
        SparkSession.builder.appName("WikipediaStreamProcessor")
        .config("spark.jars.packages", f"{KAFKA_PACKAGE}")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    print("SparkSession created successfully.")

    # Read Kafka stream
    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    # Define JSON schema
    schema = StructType([
        StructField("server_name", StringType()),
        StructField("title", StringType()),
        StructField("bot", BooleanType()),
        StructField("user", StringType()),
        StructField("timestamp", LongType())
    ])

    # Transform
    parsed_df = (
        df.select(from_json(col("value").cast("string"), schema).alias("data"))
        .select("data.*")
        .withColumn("edit_type", when(col("bot") == True, "Bot").otherwise("Human"))
        .withColumn("timestamp_col", (col("timestamp") / 1000).cast(TimestampType()))
    )

    # Aggregate
    count_df = parsed_df.groupBy("edit_type").count()

    # Write to Redis
    def write_to_redis(batch_df, batch_id):
        print(f"Writing batch {batch_id}")
        try:
            rows = batch_df.collect()
            mapping = {r['edit_type']: str(r['count']) for r in rows if r['edit_type'] is not None}
            rconn = redis_client.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
            if mapping:
                rconn.hset(REDIS_KEY, mapping=mapping)
                print(f"Batch {batch_id} written to Redis: {mapping}")
            batch_df.show()
        except Exception as e:
            print(f"Error writing batch to Redis: {e}")

    query = (
        count_df.writeStream
        .outputMode("complete")
        .foreachBatch(write_to_redis)
        .start()
    )

    print("Streaming query started. Waiting for data from Kafka...")
    query.awaitTermination()

if __name__ == "__main__":
    main()
