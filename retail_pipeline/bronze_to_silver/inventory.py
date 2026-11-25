from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name='retail_q.bronze_to_silver.inventory'
    ,comment='this inventory silver table'
)

@dp.expect_or_drop('valid_product_id','product_id IS NOT NULL AND LENGTH(TRIM(product_id))>0')
@dp.expect('valid_inventory_id','inventory_id IS NOT NULL ')
@dp.expect('valid_store_id','store_id IS NOT NULL ')

def inventory_transaction():
    return(
        spark.readStream.table('retail_q.postgesql_nronze.inventory')
             .select(
                 F.col('inventory_id'),
                 F.col('product_id'),
                 F.col('store_id'),
                 F.col('stock_quantity'),
                 F.col('reorder_level'),
                 F.when(F.col('stock_quantity')<F.col('reorder_level'),'LOW_STOCK').otherwise('HEALTHY').alias('inventory_status'),
                 F.col('warehouse_location'),
                 F.col('last_stock_update'),
                 F.current_timestamp().alias('processed_at')
             )
    )