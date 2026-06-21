-- 提示词：
-- 请先检查location 是不是以 /test/名字/开头，中文有没有替换 ， 如果有请替换，如果没有请不要修改 location 路径，请不要自动生成建表语句执行，避免使用重复的 HDFS 路径。
-- 然后不要自己用电脑的名字当用户名，询问用户的名字，然后进行替换

CREATE EXTERNAL TABLE `姓名`.`dm_questionnaire_datatable_useapp_stat_m`(`year` int, `month` int, `area_id` int, `area_name` string, `region_id` int, `region_name` string, `province_id` int, `province_name` string, `city_id` int, `city_name` string, `barangay_id` int, `barangay_name` string, `data_level` int, `service_type` string, `questionnaire_feedback_cnt` bigint, `questionnaire_feedback_cnt_qoq` double, `good_ovsat_cnt` bigint, `ovsat_cnt` bigint, `ovsat_ratio` double, `ovsat_ratio_qoq` double, `good_ces_cnt` bigint, `ces_cnt` bigint, `ces_ratio` double, `ces_ratio_qoq` double, `good_easy_signin_cnt` bigint, `easy_signin_cnt` bigint, `easy_signin_ratio` double, `easy_signin_ratio_qoq` double, `good_overall_look_ditoapp_cnt` bigint, `overall_look_ditoapp_cnt` bigint, `overall_look_ditoapp_ratio` double, `overall_look_ditoapp_ratio_qoq` double, `good_fast_download_ditoapp_cnt` bigint, `fast_download_ditoapp_cnt` bigint, `fast_download_ditoapp_ratio` double, `fast_download_ditoapp_ratio_qoq` double, `good_user_friendly_content_inditoapp_cnt` bigint, `user_friendly_content_inditoapp_cnt` bigint, `user_friendly_content_inditoapp_ratio` double, `user_friendly_content_inditoapp_ratio_qoq` double, `justenough_opinion_on_access_permissions_cnt` bigint, `opinion_on_access_permissions_cnt` bigint, `opinion_on_access_permissions_ratio` double, `opinion_on_access_permissions_ratio_qoq` double)
PARTITIONED BY (`p_year` int, `p_month` int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '/test/姓名/jwy_dito_dtsw/dm/cxm_questionnaire/dm_questionnaire_datatable_useapp_stat_m'
TBLPROPERTIES (
  'bucketing_version' = '2',
  'transient_lastDdlTime' = '1779192399',
  'field.delim' = ',',
  'serialization.format' = ','
)
