-- 提示词：
-- 请先检查location 是不是以 /test/名字/开头，中文有没有替换 ， 如果有请替换，如果没有请不要修改 location 路径，请不要自动生成建表语句执行，避免使用重复的 HDFS 路径。
-- 然后不要自己用电脑的名字当用户名，询问用户的名字，然后进行替换

CREATE EXTERNAL TABLE `姓名`.`dm_questionnaire_datatable_pay_stat_y`(`year` int, `area_id` int, `area_name` string, `region_id` int, `region_name` string, `province_id` int, `province_name` string, `city_id` int, `city_name` string, `barangay_id` int, `barangay_name` string, `data_level` int, `service_type` string, `questionnaire_feedback_cnt` bigint, `questionnaire_feedback_cnt_qoq` double, `good_ovsat_cnt` bigint, `ovsat_cnt` bigint, `ovsat_ratio` double, `ovsat_ratio_qoq` double, `good_ces_cnt` bigint, `ces_cnt` bigint, `ces_ratio` double, `ces_ratio_qoq` double, `good_clear_topup_cnt` bigint, `clear_topup_cnt` bigint, `clear_topup_ratio` double, `clear_topup_ratio_qoq` double, `good_complete_instructions_provided_cnt` bigint, `complete_instructions_provided_cnt` bigint, `complete_instructions_provided_ratio` double, `complete_instructions_provided_ratio_qoq` double, `good_fast_topup_cnt` bigint, `fast_topup_cnt` bigint, `fast_topup_ratio` double, `fast_topup_ratio_qoq` double, `good_correct_amount_topup_cnt` bigint, `correct_amount_topup_cnt` bigint, `correct_amount_topup_ratio` double, `correct_amount_topup_ratio_qoq` double, `good_complete_transaction_details_received_via_sms_cnt` bigint, `complete_transaction_details_received_via_sms_cnt` bigint, `complete_transaction_details_received_via_sms_ratio` double, `complete_transaction_details_received_via_sms_ratio_qoq` double, `good_transaction_his_show_ditoapp_cnt` bigint, `transaction_his_show_ditoapp_cnt` bigint, `transaction_his_show_ditoapp_ratio` double, `transaction_his_show_ditoapp_ratio_qoq` double, `good_realtime_balance_update_cnt` bigint, `realtime_balance_update_cnt` bigint, `realtime_balance_update_ratio` double, `realtime_balance_update_ratio_qoq` double, `good_payment_options_can_conveniently_use_cnt` bigint, `payment_options_can_conveniently_use_cnt` bigint, `payment_options_can_conveniently_use_ratio` double, `payment_options_can_conveniently_use_ratio_qoq` double, `good_promo_inclusions_fit_my_needs_cnt` bigint, `promo_inclusions_fit_my_needs_cnt` bigint, `promo_inclusions_fit_my_needs_ratio` double, `promo_inclusions_fit_my_needs_ratio_qoq` double)
PARTITIONED BY (`p_year` int)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '/test/姓名/jwy_dito_dtsw/dm/cxm_questionnaire/dm_questionnaire_datatable_pay_stat_y'
TBLPROPERTIES (
  'bucketing_version' = '2',
  'transient_lastDdlTime' = '1779192400',
  'field.delim' = ',',
  'serialization.format' = ','
)
