import os
import sys

# 如果需要手动添加 pyspark 到环境变量（通过 spark-submit 执行时通常不需要）
# sys.path.insert(0, os.path.join(os.environ.get('SPARK_HOME', ''), 'python'))

from pyspark.sql import SparkSession

def main():
    print("=========================================")
    print(" 初始化 Local SparkSession")
    print("=========================================")
    # 启用 Hive 支持以使用 CREATE DATABASE 等 DDL 操作
    spark = SparkSession.builder \
        .appName("LocalSparkTest") \
        .master("local[*]") \
        .config("spark.sql.warehouse.dir", os.path.abspath("spark-warehouse")) \
        .enableHiveSupport() \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("WARN")

    print("\n[1/4] 建库 (CREATE DATABASE)...")
    spark.sql("CREATE DATABASE IF NOT EXISTS local_test_db")
    print("数据库 'local_test_db' 已准备就绪。")
    
    print("\n[2/4] 建表 (CREATE TABLE)...")
    spark.sql("USE local_test_db")
    spark.sql("DROP TABLE IF EXISTS local_test_table")
    spark.sql("""
        CREATE TABLE IF NOT EXISTS local_test_table (
            id INT,
            name STRING,
            age INT
        ) USING parquet
    """)
    print("表 'local_test_table' 创建成功。")
    
    print("\n[3/4] 插入数据 (INSERT INTO)...")
    spark.sql("""
        INSERT INTO local_test_table VALUES
        (1, 'Alice', 25),
        (2, 'Bob', 30),
        (3, 'Charlie', 35),
        (4, 'David', 40)
    """)
    print("数据插入完成。")
    
    print("\n[4/4] 查询数据 (SELECT)...")
    df = spark.sql("SELECT * FROM local_test_table WHERE age >= 30 ORDER BY id")
    print("查询结果 (age >= 30):")
    df.show()

    print("\n=========================================")
    print(" 清理资源")
    print("=========================================")
    # 可选：如果在本地测试不想保留，可以取消注释下面两行来清理
    # spark.sql("DROP TABLE IF EXISTS local_test_table")
    # spark.sql("DROP DATABASE IF EXISTS local_test_db CASCADE")
    
    spark.stop()
    print("Local Spark 测试执行完毕！")

if __name__ == "__main__":
    main()
