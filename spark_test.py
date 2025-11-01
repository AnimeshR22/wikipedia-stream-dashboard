from pyspark.sql import SparkSession

# Create a simple Spark session
spark = SparkSession.builder.appName("SetupTest").getOrCreate()

# Create a sample dataframe
df = spark.createDataFrame([(1, "Animesh"), (2, "Raj")], ["id", "name"])

# Show the dataframe
df.show()

# Stop the session
spark.stop()
