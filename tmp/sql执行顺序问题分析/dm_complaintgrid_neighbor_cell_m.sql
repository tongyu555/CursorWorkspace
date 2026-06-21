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