# Databricks notebook source
# read csv file

df=(
    spark.readStream.format('cloudFiles')
                    .option('cloudFiles.format','csv')
                    .option('cloudFiles.schemaLocation','/Volumes/retail_q/volume/schema')
                    .option('header','true')
                    .option('inferschema','true')
                    .load('/Volumes/retail_q/volume/blob_source')
)

# COMMAND ----------

# write the csv file to brnze table
query = (
    df.writeStream
      .option("checkpointLocation", "/Volumes/retail_q/volume/chekpoint")
      .trigger(availableNow=True)
      .toTable("retail_q.blob_bronze.transactions")
)
query.awaitTermination()

  

# COMMAND ----------

# MAGIC %md
# MAGIC