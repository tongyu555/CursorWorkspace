CREATE DATABASE IF NOT EXISTS local_test_db;
USE local_test_db;

DROP TABLE IF EXISTS local_test_table;
CREATE TABLE local_test_table (
    id INT,
    name STRING,
    age INT
) USING parquet;

INSERT INTO local_test_table VALUES
(1, 'Alice', 25),
(2, 'Bob', 30),
(3, 'Charlie', 35),
(4, 'David', 40);

SELECT * FROM local_test_table WHERE age >= 30 ORDER BY id;
