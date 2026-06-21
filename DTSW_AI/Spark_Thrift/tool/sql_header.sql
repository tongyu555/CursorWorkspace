-- SQL 头：USE + 变量 + 可选 UDF（与 -f 本体拼接后提交 Thrift）

USE jwy_dito_dtsw;

set hivevar:p_date=2026-05-01;

-- ADD JAR hdfs:///user/hdfs/udf/your_udf.jar;
-- CREATE TEMPORARY FUNCTION your_udf AS 'com.example.YourUdf'
-- USING JAR 'hdfs:///user/hdfs/udf/your_udf.jar';
