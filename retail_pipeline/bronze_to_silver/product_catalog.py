from pyspark import pipelines as dp
from pyspark.sql import functions as F

@dp.table(
    name ='retail_q.bronze_to_silver.product_catalog'
    ,comment = 'This is the silver table for the retail data'
)

@dp.expect_or_drop('valid_product_id','product_id IS NOT NULL AND LENGTH(TRIM(product_id))>0')
@dp.expect_or_drop('valid_product_name','product_name IS NOT NULL AND LENGTH(TRIM(product_name))>0')
@dp.expect_or_drop('valid_supplier_name','supplier_name IS NOT NULL AND LENGTH(TRIM(supplier_name))>0')
@dp.expect('valid_category','category IS NOT NULL')
@dp.expect('valid_unit_price','unit_price>0')



def tansactions_silver():
    return(
         spark.readStream.table('retail_q.postgesql_nronze.product_catalog')
                         .select(F.upper(F.trim(F.col('product_id'))).alias('product_id'),
                                 F.initcap(F.col('product_name')).alias('product_name'),
                                 F.initcap(F.col('category')).alias('category'),
                                 F.when(F.col('subcategory').isNotNull(),F.initcap(F.trim(F.col('subcategory'))))
                                  .otherwise('known').alias('subcategory'),
                                 F.when(F.col('brand').isNotNull(),F.initcap(F.trim(F.col('brand'))))
                                  .otherwise('unknown').alias('brand'),
                                 F.round(F.col('unit_price'), 2).alias('unit_price'),
                                 F.when(F.col('unit_price')>10000,'PREMIUM')
                                  .when(F.col('unit_price')>5000,'MEDIUM')
                                  .when(F.col('unit_price')>1000,'ECONOMY')
                                  .otherwise('CHEAP').alias('product_sugment'),
                                 F.initcap(F.trim(F.col('supplier_name'))).alias('supplier_name'),
                                 F.col('is_active'),
                                 F.col('updated_at'),
                                 F.col('__START_AT').alias('start_at'),
                                 F.col('__END_AT').alias('end_at'),
                                 F.current_timestamp().alias('processed_at')
                                )
    )
