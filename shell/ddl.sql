
CREATE EXTERNAL TABLE `ods_nr_mro_northctcc_reduce`(`datetime` string, `imsi` string, `msisdn` string, `imei` string, `gnbid` bigint, `cellid` int, `provincecode` int, `mrlon` double, `mrlat` double, `locationtype` int)
PARTITIONED BY (`p_provincecode` int, `p_date` string, `p_hour` int, `p_quarter` int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'field.delim' = '|',
  'serialization.format' = '|'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION 'viewfs://nsX/zxvmax/telecom/ods/ran/lte/north/ods_nr_mro_northctcc_reduce'
TBLPROPERTIES (
  'transient_lastDdlTime' = '1743156766'
)

CREATE EXTERNAL TABLE `ts_glc_coverageagps_celgrd_refactor_d`(`citycode` int, `districtcode` int, `regionid` int, `x_offset_20` int, `y_offset_20` int, `avgmrlon` double, `avgmrlat` double, `cellkey` string, `dlearfcn` int, `rsrp_level1mrcount` bigint, `rsrp_level2mrcount` bigint, `rsrp_level3mrcount` bigint, `rsrp_level4mrcount` bigint, `rsrp_level5mrcount` bigint, `rsrp_level6mrcount` bigint, `rsrp_level7mrcount` bigint, `totalrsrp` bigint, `avgrsrp` double, `overlap_mrcount` bigint, `overlap_mrratio` double)
PARTITIONED BY (`p_provincecode` int, `p_date` string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION 'viewfs://nsX/vmax_ns1/zxvmax/telecom/lte/aggr/ts_glc_coverageagps_celgrd_refactor_d'
TBLPROPERTIES (
  'transient_lastDdlTime' = '1730272277',
  'parquet.compression' = 'SNAPPY'
)

CREATE EXTERNAL TABLE `aggr_lte_coverage_index_reduce_celgrd_q`(`day` string COMMENT '日期', `hour` int COMMENT '小时', `quarter` int COMMENT '15分钟', `plmn` string COMMENT 'UE接入E-utran网络使用的PLMN号', `data_source` int COMMENT '承建方。电信承建：0；联通承建：1', `cellkey` string COMMENT '小区唯一标识', `regionid` int COMMENT '栅格编码', `x_offset_20` int COMMENT '栅格坐标x轴偏移', `y_offset_20` int COMMENT '栅格坐标y轴偏移', `grd_center_lon` double COMMENT '栅格中心经度', `grd_center_lat` double COMMENT '栅格中心纬度', `rsrp_cnt` bigint COMMENT 'RSRP有效数目', `rsrp_cnt_f95_f43` bigint COMMENT 'RSRP在[-95,-43]范围内的MR数目', `rsrp_cnt_f105_f95` bigint COMMENT 'RSRP在[-105,-95)范围内的MR数目', `rsrp_cnt_f110_f105` bigint COMMENT 'RSRP在[-110,-105)范围内的MR数目', `rsrp_cnt_f115_f110` bigint COMMENT 'RSRP在[-115,-110)范围内的MR数目', `rsrp_cnt_f140_f115` bigint COMMENT 'RSRP在[-140,-115)范围内的MR数目', `rsrp_avg` double COMMENT 'RSRP平均值', `usr_cnt` int COMMENT '用户数')
PARTITIONED BY (`p_provincecode` int, `p_date` string, `p_hour` int, `p_quarter` int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION 'viewfs://nsX/vmax_ns4/zxvmax/telecom/lte/aggr/aggr_lte_coverage_index_reduce_celgrd_q'
TBLPROPERTIES (
  'transient_lastDdlTime' = '1773040722',
  'field.delim' = ',',
  'serialization.format' = ',',
  'colelction.delim' = '|',
  'parquet.compression' = 'SNAPPY'
)

CREATE EXTERNAL TABLE `aggr_nr_coverage_index_reduce_celgrd_q`(`day` string COMMENT '日期', `hour` int COMMENT '小时', `quarter` int COMMENT '15分钟', `plmn` string COMMENT 'UE接入E-utran网络使用的PLMN号', `data_source` int COMMENT '承建方。电信承建：0；联通承建：1', `cellkey` string COMMENT '小区唯一标识', `regionid` int COMMENT '栅格编码', `x_offset_20` int COMMENT '栅格坐标x轴偏移', `y_offset_20` int COMMENT '栅格坐标y轴偏移', `grd_center_lon` double COMMENT '栅格中心经度', `grd_center_lat` double COMMENT '栅格中心纬度', `rsrp_cnt` bigint COMMENT 'RSRP有效数目', `rsrp_cnt_f95_f27` bigint COMMENT 'RSRP在[-95,-27]范围内的MR数目', `rsrp_cnt_f105_f95` bigint COMMENT 'RSRP在[-105,-95)范围内的MR数目', `rsrp_cnt_f110_f105` bigint COMMENT 'RSRP在[-110,-105)范围内的MR数目', `rsrp_cnt_f115_f110` bigint COMMENT 'RSRP在[-115,-110)范围内的MR数目', `rsrp_cnt_f156_f115` bigint COMMENT 'RSRP在[-156,-115)范围内的MR数目', `rsrp_avg` double COMMENT 'RSRP平均值', `usr_cnt` int COMMENT '用户数')
PARTITIONED BY (`p_provincecode` int, `p_date` string, `p_hour` int, `p_quarter` int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION 'viewfs://nsX/vmax_ns4/zxvmax/telecom/nr/aggr/aggr_nr_coverage_index_reduce_celgrd_q'
TBLPROPERTIES (
  'transient_lastDdlTime' = '1773040762',
  'field.delim' = ',',
  'serialization.format' = ',',
  'colelction.delim' = '|',
  'parquet.compression' = 'SNAPPY'
)