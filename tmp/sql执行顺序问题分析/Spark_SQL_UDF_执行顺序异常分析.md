# Spark SQL 2.x UDF 与过滤条件执行顺序异常分析

## 1. 问题背景

在执行 `dm_complaintgrid_neighbor_cell_m.sql` 时，遇到一个反直觉的问题：
内层查询中已经对经纬度进行了严格的过滤（`lon > 73.0 AND lon < 136.0 AND lat > 2.0 AND lat < 54.0`），但外层的 UDF 函数 `MultiLonLatToGrid(lon,lat,500)` 依然报错，提示接收到了非法的经纬度数据（如 `lon=145.245`）。

```sql
create temporary function MultiLonLatToGrid as 'com.gstools.impala.MultiLonLatToGrid';
create temporary function MultiGridToLonLat as 'com.gstools.impala.MultiGridToLonLat';
-- auth:goupengcheng
-- since:2026-04-08
-- algorithm:投诉栅格周边小区清单；A为dm_complaintgrid_detail_m；B为近7天MR汇聚；C为4G/5G工参按cellkey去重
-- comment:MR数据只取一天，但要取到有数据的天
set spark.sql.adaptive.enabled = true;
set spark.sql.adaptive.coalescePartitions.enabled = true;
set spark.sql.adaptive.coalescePartitions.maxPartitionSize = 256m;
set spark.sql.adaptive.coalescePartitions.minPartitionSize = 128m;
set mapreduce.fileoutputcommitter.marksuccessfuljobs = false;
-- 45G电联工参合并
CACHE TABLE cache_cm AS
SELECT
    network_class
    ,cellkey
    ,indoor_flag
    ,freq
    ,master_operators
    ,azimuth
    ,celllon
    ,celllat
FROM
(
    SELECT
        '4G' AS network_class
        ,reportcellkey AS cellkey
        ,CASE WHEN covertype = '2' THEN 1 ELSE 0 END AS indoor_flag
        ,bandclass AS freq
        ,CASE WHEN master_operators IN ('联通','联通承建') THEN '联通承建' ELSE '电信承建' END AS master_operators
        ,azimuth
        ,celllon
        ,celllat
        ,ROW_NUMBER() OVER(PARTITION BY reportcellkey ORDER BY celllon DESC) AS rn
    FROM
        lte_cm_projdata_refactor
    WHERE p_provincecode = 440000
    UNION ALL
    SELECT
        '5G' AS network_class
        ,cellkey
        ,CASE WHEN indoor_flag = 1 THEN 1 ELSE 0 END AS indoor_flag
        ,freq
        ,CASE WHEN master_operators IN ('联通','联通承建') THEN '联通承建' ELSE '电信承建' END AS master_operators
        ,cell_azimuth AS azimuth
        ,cell_longitude AS celllon
        ,cell_latitude AS celllat
        ,ROW_NUMBER() OVER(PARTITION BY cellkey ORDER BY cell_longitude DESC) AS rn
    FROM
        fact_nr_cm_projdata_refactor
    WHERE p_provincecode = 440000
) A
WHERE rn = 1
;
INSERT OVERWRITE TABLE dm_complaintgrid_neighbor_cell_m
PARTITION (
    p_provincecode = 440000
    ,p_year = 2025
    ,p_month = 12
)
SELECT
    2025 AS year -- 年
    ,12 AS month -- 月
    ,CONCAT(2025, '_', 12) AS year_month -- 年_月
    ,440000 AS province_code -- 省份编码
    ,A1.city_code AS city_code -- 地市编码
    ,A1.data_cycle AS data_cycle -- 账期
    ,A1.province_name AS province_name -- 省份
    ,A1.city_name AS city_name -- 本地网
    ,A1.grid_number AS grid_number -- 栅格编号
    ,A1.grid_rank AS grid_rank -- 栅格排序
    ,A1.grid_center_lon AS grid_center_lon -- 栅格中心经度
    ,A1.grid_center_lat AS grid_center_lat -- 栅格中心纬度
    ,A1.regionid_500 AS regionid_500 -- 500m栅格ID
    ,A1.x_offset_500 AS x_offset_500 -- 500m栅格X偏移
    ,A1.y_offset_500 AS y_offset_500 -- 500m栅格Y偏移
    ,A2.network_class AS network_class -- 网络类型 4G 5G
    ,A2.cellkey AS cellkey -- cellkey
    ,A3.indoor_flag AS indoor_flag -- 室内外 1-室内 0-室外
    ,A3.freq AS freq -- 频段 1.8G 2.1G
    ,A3.master_operators AS master_operators -- 承建方 电信承建 联通承建
    ,A3.azimuth AS azimuth -- 方位角
    ,A3.celllon AS celllon -- 小区经度
    ,A3.celllat AS celllat -- 小区纬度
FROM
(
    SELECT
        city_code
        ,data_cycle
        ,province_name
        ,city_name
        ,grid_number
        ,grid_rank
        ,grid_center_lon
        ,grid_center_lat
        ,regionid_500
        ,x_offset_500
        ,y_offset_500
    FROM
        dm_complaintgrid_detail_m
    WHERE p_provincecode = 440000
        AND p_year = 2025
        AND p_month = 12
) A1
LEFT JOIN
(
    SELECT
        network_class
        ,cellkey
        ,CAST(grid_info[0] AS INT) AS regionid_500
        ,CAST(grid_info[1] AS INT) AS x_offset_500
        ,CAST(grid_info[2] AS INT) AS y_offset_500
        ,SUM(rsrpcount) AS rsrpcount
    FROM
    (
        SELECT
            network_class
            ,cellkey
            ,split(MultiLonLatToGrid(lon,lat,500),',') as grid_info
            ,rsrpcount
        FROM
        (
            SELECT
                network_class
                ,cellkey
                ,lon
                ,lat
                ,rsrpcount
            FROM
            (
                -- 45GMR取最新天数据(3天内)
                SELECT
                    network_class AS network_class
                    ,cellkey AS cellkey
                    ,(cast(arr_lonlat[0] as double)+cast(arr_lonlat[2] as double))/2 AS lon
                    ,(cast(arr_lonlat[1] as double)+cast(arr_lonlat[3] as double))/2 AS lat
                    ,rsrpcount
                FROM
                (
                    SELECT
                        '4G' AS network_class
                        ,cellkey AS cellkey
                        ,p_date
                        ,split(MultiGridToLonLat(regionid,x_offset,y_offset,20),',') AS arr_lonlat
                        ,SUM(rsrpcount) AS rsrpcount
                    FROM
                        aggr_lte_coverage_base_refactor_d
                    WHERE p_provincecode = 440000
                        AND p_date = date_sub(current_date(), 3)
                        AND regionid IS NOT NULL
                        AND x_offset IS NOT NULL
                        AND y_offset IS NOT NULL
                    GROUP BY
                        cellkey
                        ,regionid
                        ,x_offset
                        ,y_offset
                        ,p_date
                    UNION ALL
                    SELECT
                        '5G' AS network_class
                        ,cellkey AS cellkey
                        ,p_date
                        ,split(MultiGridToLonLat(regionid,x_offset_20,y_offset_20,20),',') AS arr_lonlat
                        ,SUM(ssrsrpcount) AS rsrpcount
                    FROM
                        aggr_nr_coverage_celgrd_refactor_d
                    WHERE p_provincecode = 440000
                        AND p_date = date_sub(current_date(), 3)
                        AND regionid IS NOT NULL
                        AND x_offset_20 IS NOT NULL
                        AND y_offset_20 IS NOT NULL
                    GROUP BY
                        cellkey
                        ,regionid
                        ,x_offset_20
                        ,y_offset_20
                        ,p_date
                ) D
            ) C
            WHERE lon > 73.0
                AND lon < 136.0
                AND lat > 2.0
                AND lat < 54.0
        ) E
    ) B
    GROUP BY
        network_class
        ,cellkey
        ,grid_info
    HAVING rsrpcount >= 10
) A2
ON A1.regionid_500 = A2.regionid_500
    AND A1.x_offset_500 = A2.x_offset_500
    AND A1.y_offset_500 = A2.y_offset_500
LEFT JOIN
    cache_cm A3
ON A2.cellkey = A3.cellkey
DISTRIBUTE BY rand()
;
```

按照常理，内层的 `WHERE` 过滤条件应该先执行，外层的 `SELECT` 中的 UDF 应该后执行。被过滤掉的数据不应该进入到 UDF 中。

## 2. 执行计划深度分析

通过分析 `plan.txt` 中的物理执行计划，我们可以得出以下结论：

### 2.1 过滤条件确实先执行了

在物理执行计划中，Spark 确实是**先执行了过滤条件，后执行了 UDF**。

- **过滤条件在 Map 阶段（Shuffle 前）执行**：
在执行计划的第 26 行和第 32 行，可以看到 `Filter` 节点被直接下推到了 `FileScan`（读取 Parquet 文件）之上。
- **UDF 在 Reduce 阶段（Shuffle 后）执行**：
外层的 `split(MultiLonLatToGrid(lon,lat,500),',') as grid_info` 被作为了最外层 `GROUP BY` 的 key。在执行计划的第 20 行 `HashAggregate` 中，Spark 才开始计算这个 `grid_info`。而这个 `HashAggregate` 是在第 23 行的 `Exchange`（Shuffle 操作）之后的。

**结论**：物理层面上，过滤条件确实先于 `MultiLonLatToGrid` 执行。中间隔了一个 Shuffle 屏障，被过滤掉的数据绝对不可能进入到 Shuffle 之后的阶段。

### 2.2 核心问题：为什么 UDF 还是收到了非法数据？

既然非法数据会被过滤掉，为什么它还能出现在 Shuffle 之后的 UDF 中？原因在于 **Spark 的表达式下推（PushDownPredicates）优化** 与 **UDF 的重复计算（且极可能存在线程安全问题）**。

1. **节省 Shuffle 带宽的优化**：
  在内层的 `GROUP BY` 中，key 是 `regionid, x_offset, y_offset`。Spark 优化器知道 `lon` 和 `lat` 是通过这三个字段算出来的（即函数依赖）。为了节省 Shuffle 阶段的网络传输带宽，Spark 决定在 Shuffle 时**只传输 `regionid, x_offset, y_offset`**，不传输算好的 `lon` 和 `lat`。
2. **灾难的发生（重复计算 + UDF 非确定性）**：
  当数据经过 Shuffle 到达 Reduce 阶段时，Spark 需要计算 `MultiLonLatToGrid(lon, lat, 500)`。此时它发现手里没有 `lon` 和 `lat`，于是它**再次调用了底层的 `MultiGridToLonLat`** 来重新计算经纬度！
   **致命点就在这里**：自定义的 Hive UDF（`com.gstools.impala.MultiGridToLonLat`）极大概率存在**线程安全问题**（例如内部使用了静态变量、共享的 `SimpleDateFormat` 或全局数组）。

### 2.3 深度解析：UDF 的线程安全问题如何导致异常数据穿透？

这是最容易让人困惑的地方：**既然已经限制了经纬度范围，就算在 Reduce 端重算 `lon` 和 `lat`，算出来如果是异常值，难道不应该再次被过滤掉吗？**

答案是：**Spark 不会在 Reduce 端再次执行过滤！**

以下是数据流转的完整生命周期，解释了脏数据是如何“骗过” Spark 的：

#### 第一阶段：Map 端的过滤（第一次计算）

1. Spark 在读取 Parquet 文件时，遇到了 `regionid=A, x_offset=B, y_offset=C` 这条数据。
2. Spark 需要判断这条数据是否满足 `lon > 73.0 AND ...` 的条件。
3. 于是，Spark 调用了 `MultiGridToLonLat(A, B, C)`。
4. **关键点 1**：此时 UDF 内部发生了**线程竞争**（例如多个 Task 共享了一个静态的中间计算变量），但**碰巧**，这次计算返回了一个**正常**的经纬度，比如 `lon=110.0, lat=30.0`。
5. Spark 判断：`110.0 > 73.0`，条件成立！
6. 于是，这条数据（`regionid=A, x_offset=B, y_offset=C`）被标记为**合法数据**，并被发送到了 Shuffle 阶段。

#### 第二阶段：Shuffle 屏障

- 此时，Spark 已经“确信”所有进入 Shuffle 的数据都是合法的。
- 为了节省网络带宽，Spark 丢弃了刚才算好的 `lon=110.0, lat=30.0`，只把 `regionid=A, x_offset=B, y_offset=C` 传给了 Reduce 端。

#### 第三阶段：Reduce 端的重算（第二次计算，灾难发生）

1. Reduce 端接收到了 `regionid=A, x_offset=B, y_offset=C`。
2. Reduce 端需要执行外层的 `MultiLonLatToGrid(lon, lat, 500)`，但它发现自己没有 `lon` 和 `lat`。
3. 于是，它**再次调用** `MultiGridToLonLat(A, B, C)` 来重算。
4. **关键点 2**：因为 UDF 存在线程安全问题，它的计算结果是**非确定性**的（Non-deterministic）。对于同样的输入 `A, B, C`，这次由于多线程并发导致的内存错乱，UDF 返回了一个**错误**的经纬度：`lon=145.245, lat=23.469`。
5. **关键点 3**：Spark 在 Reduce 端**不会再次检查 `WHERE` 条件**。它认为过滤已经在 Map 端做过了，现在传过来的数据都是“干净”的。
6. 于是，这个错误的 `lon=145.245` 被直接喂给了外层的 `MultiLonLatToGrid`。
7. 外层 UDF 发现经度超出了中国的合理范围，抛出异常，任务崩溃。

#### 总结：

UDF 的线程安全问题导致了**同一个函数，同样的输入，在 Map 端和 Reduce 端返回了不同的结果**。

- Map 端返回了正常值，**骗过了过滤条件**，拿到了进入下游的“通行证”。
- Reduce 端返回了异常值，但此时**已经没有保安（Filter）检查了**，异常值直接导致了程序崩溃。

## 3. 总结与解决方案

**现象本质**：不是过滤条件没生效，而是底层生成经纬度的 UDF (`MultiGridToLonLat`) 被 Spark 优化器执行了两次，且由于 UDF 本身的线程安全/非确定性问题，第二次重算时生成了超出范围的脏数据，直接击穿了外层 UDF。

### 解决方案

#### 方案一：修复 UDF（根本解决）

检查 `com.gstools.impala.MultiGridToLonLat` 的 Java/Scala 源码，消除所有的 `static` 共享变量，确保其是一个纯粹的无状态、线程安全的函数。

#### 方案二：阻断 Spark 的优化，强制物化（SQL 层解决）

不要让 Spark 把计算逻辑合并。可以将过滤后的结果先写入一个临时表或缓存表，强制 Spark 把 `lon` 和 `lat` 算出来并固化，然后再执行外层的 UDF：

```sql
-- 先将过滤后的结果缓存
CACHE TABLE tmp_filtered_data AS
SELECT
    network_class, cellkey, lon, lat, rsrpcount
FROM (
    -- 原本的 C 子查询逻辑
) C
WHERE lon > 73.0 AND lon < 136.0 AND lat > 2.0 AND lat < 54.0;

-- 然后再基于缓存表执行外层 UDF
SELECT
    network_class, cellkey, split(MultiLonLatToGrid(lon,lat,500),',') as grid_info, rsrpcount
FROM tmp_filtered_data
...
```

#### 方案三：添加 DISTRIBUTE BY 打断执行计划

在 `WHERE` 过滤之后，加上 `DISTRIBUTE BY rand()`，强制 Spark 在这里插入一个 Shuffle，把算好的 `lon` 和 `lat` 传下去，避免重算：

```sql
        SELECT
            network_class
            ,cellkey
            ,lon
            ,lat
            ,rsrpcount
        FROM
        ( ... ) C
        WHERE lon > 73.0 AND lon < 136.0 AND lat > 2.0 AND lat < 54.0
        DISTRIBUTE BY rand()  -- 强制阻断，避免下推和重算
```

