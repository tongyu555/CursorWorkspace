-- 提示词：
-- 请先检查location 是不是以 /test/名字/开头，中文有没有替换 ， 如果有请替换，如果没有请不要修改 location 路径，请不要自动生成建表语句执行，避免使用重复的 HDFS 路径。
-- 然后不要自己用电脑的名字当用户名，询问用户的名字，然后进行替换

CREATE EXTERNAL TABLE `姓名`.`dm_questionnaire_pay_stat_qt_d`(`areacode` int, `year` int, `quarter` int, `day` string, `area_name` string, `regioncode` int, `region_name` string, `provincecode` int, `province_name` string, `citycode` string, `city_name` string, `barangay_id` string, `barangay_name` string, `support_type` int, `pay_type` string, `good_ovsat_nums` bigint, `ovsat_nums` bigint, `good_ces_nums` bigint, `ces_nums` bigint, `promoter_nps_nums` bigint, `detractor_nps_nums` bigint, `nps_nums` bigint, `good_clear_topup_nums` bigint, `clear_topup_nums` bigint, `good_complete_instructions_provided_nums` bigint, `complete_instructions_provided_nums` bigint, `good_fast_topup_nums` bigint, `fast_topup_nums` bigint, `good_correct_amount_topup_nums` bigint, `correct_amount_topup_nums` bigint, `good_complete_transaction_details_received_via_sms_nums` bigint, `complete_transaction_details_received_via_sms_nums` bigint, `good_transaction_his_show_ditoapp_nums` bigint, `transaction_his_show_ditoapp_nums` bigint, `good_realtime_balance_update_nums` bigint, `realtime_balance_update_nums` bigint, `good_payment_options_can_conveniently_use_nums` bigint, `payment_options_can_conveniently_use_nums` bigint, `good_promo_inclusions_fit_my_needs_nums` bigint, `promo_inclusions_fit_my_needs_nums` bigint, `price_just_right_nums` bigint, `worth_slightly_morethan_price_nums` bigint, `bottom_3_box_nums` bigint, `yes_charged_correctly_dito_loadorpromo_nums` bigint, `no_charged_correctly_dito_loadorpromo_nums` bigint, `charged_correctly_dito_loadorpromo_nums` bigint, `buy_type` string, `purchase_channel_level2` string, `purchase_channel_level3` string, `payment_method` string, `pay_user_nums` bigint, `service_type` string, `porpuse_type` string, `subs_tenure_month` string, `satisfaction_degree` string)
PARTITIONED BY (`p_date` string)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = '1'
)
STORED AS
  INPUTFORMAT 'org.apache.hadoop.mapred.TextInputFormat'
  OUTPUTFORMAT 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
LOCATION '/test/姓名/jwy_dito_dtsw/dm/cxm_questionnaire/dm_questionnaire_pay_stat_qt_d'
TBLPROPERTIES (
  'bucketing_version' = '2',
  'transient_lastDdlTime' = '1779192192',
  'field.delim' = ',',
  'serialization.format' = ','
)
