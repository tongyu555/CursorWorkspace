-- 提示词：
-- 请先检查location 是不是以 /test/名字/开头，中文有没有替换 ， 如果有请替换，如果没有请不要修改 location 路径，请不要自动生成建表语句执行，避免使用重复的 HDFS 路径。
-- 然后不要自己用电脑的名字当用户名，询问用户的名字，然后进行替换

CREATE EXTERNAL TABLE `姓名`.`dm_questionnaire_useapp_stat_w`(`areacode` int, `year` int, `week` int, `area_name` string, `regioncode` int, `region_name` string, `provincecode` int, `province_name` string, `citycode` string, `city_name` string, `barangay_id` string, `barangay_name` string, `support_type` int, `good_ovsat_nums` int, `ovsat_nums` int, `good_ces_nums` int, `ces_nums` int, `promoter_nps_nums` int, `detractor_nps_nums` string, `nps_nums` int, `good_easy_signin_nums` int, `easy_signin_nums` int, `good_overall_look_ditoapp_nums` int, `overall_look_ditoapp_nums` int, `good_fast_download_ditoapp_nums` int, `fast_download_ditoapp_nums` int, `good_user_friendly_content_inditoapp_nums` int, `user_friendly_content_inditoapp_nums` int, `justenough_opinion_on_access_permissions_nums` int, `toomuch_opinion_on_access_permissions_nums` int, `opinion_on_access_permissions_nums` int, `subs_tenure_month` string, `tenuretenure_month` int, `service_type` string, `pay_user_nums` bigint)
PARTITIONED BY (`p_year` int, `p_week` int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '/test/姓名/jwy_dito_dtsw/dm/cxm_questionnaire/dm_questionnaire_useapp_stat_w'
TBLPROPERTIES (
  'bucketing_version' = '2',
  'transient_lastDdlTime' = '1779191903',
  'field.delim' = ',',
  'serialization.format' = ','
)
