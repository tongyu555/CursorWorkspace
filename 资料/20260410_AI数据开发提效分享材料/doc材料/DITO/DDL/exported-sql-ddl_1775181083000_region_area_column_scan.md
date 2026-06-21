# DDL 扫描：区域相关标准字段

源文件: `exported-sql-ddl_1775181083000.sql`

匹配规则: 列定义中出现以下任一字段（反引号列名）:
region_id, region_name, region_code, province_id, province_name, province_code,
city_id, city_name, city_code, area_id, area_name, area_level, parent_id,
ntc_area_code, ntc_area_psgc

**匹配表数量: 798**

| 表名 | 匹配字段 | 是否分区表 |
| --- | --- | --- |
| `aggr_45g_cell_deficiency_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_45g_cell_ec_elec_bill_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_45g_dpi_ip_host_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_45g_dpi_ip_host_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_45g_enb_utilization_share_d` | area_id, city_id, province_id, region_id | 是 |
| `aggr_45g_phyenb_utilization_share_d` | area_id, city_id, province_id, region_id | 是 |
| `aggr_45g_speedtest_consumerqoe_filetransfer_share_d` | city_code, city_name, province_code, province_name | 是 |
| `aggr_45g_speedtest_consumerqoe_qoelatency_share_d` | city_code, city_name, province_code, province_name | 是 |
| `aggr_45g_speedtest_consumerqoe_qoevideo_share_d` | city_code, city_name, province_code, province_name | 是 |
| `aggr_45g_speedtest_consumerqoe_webbrowsing_share_d` | city_code, city_name, province_code, province_name | 是 |
| `aggr_45g_user_general_ip_houst_list_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_45g_user_resident_barangay_share_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_4g_dpi_usr_cnlist_rt_q` | area_id | 是 |
| `aggr_4g_http_e2e_rt_q` | area_name, city_name, province_name, region_name | 是 |
| `aggr_4g_https_e2e_rt_q` | area_name, city_name, province_name, region_name | 是 |
| `aggr_4g_lowload_cellist_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_4g_lowloadcell_share_d` | area_name, city_code | 是 |
| `aggr_4g_phyenb_utilization_d` | area_id, city_id, province_id, region_id | 是 |
| `aggr_4g_video_e2e_rt_q` | area_name, city_name, province_name, region_name | 是 |
| `aggr_5g_phygnb_utilization_d` | area_id, city_id, province_id, region_id | 是 |
| `aggr_area_highload_index_share_w` | area_id, area_name | 是 |
| `aggr_area_penetration_qual_share_d` | area_name | 是 |
| `aggr_area_site_utilization_share_d` | area_name | 是 |
| `aggr_brg_45G_mr_contrast_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_brg_45gsites_rrcutilization_share_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_brg_city_coverage_grade_m` | city_code, city_id, city_name, province_name | 是 |
| `aggr_brg_city_coveragegrade_share_m` | city_code, city_id, city_name | 是 |
| `aggr_brg_coverage_population_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `aggr_brg_earfcn_test_d` | area_name, city_name, province_name, region_name | 是 |
| `aggr_brg_maxearfcn_test_d` | area_name, city_name, province_name, region_name | 是 |
| `aggr_brg_penetration_qual_share_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `aggr_brg_population_attribute_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `aggr_brg_site_utilization_share_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `aggr_brg_splitearfcn_test_d` | area_name, city_name, province_name, region_name | 是 |
| `aggr_cbhkpi_mr_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_cell_fault_affectusers_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_cell_fluxrrc_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_cell_resdentuser_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_cell_rrc_capacity_connection_7_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_cell_rrc_capacity_connection_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_city_cellindicator_share_d` | area_id, area_name, city_code, city_id, city_name, region_id, region_name | 是 |
| `aggr_city_penetration_qual_share_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `aggr_city_site_utilization_share_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_dns_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_dns_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_game_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_game_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_http_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_http_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_https_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_other_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_other_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_s1mme_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_s1mme_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_video_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_ct_xdr_lte_4g_s1u_n3_video_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_fwa_activebrg_developreport_d` | area_id, area_name, city_id, city_name | 是 |
| `aggr_fwa_city_developreport_d` | area_id, area_name, city_id, city_name | 是 |
| `aggr_fwa_customarea_developreport_d` | area_id, area_name | 是 |
| `aggr_fwa_mesh_developreport_d` | area_id, area_name | 是 |
| `aggr_fwa_residentbrg_developreport_d` | area_id, area_name, city_id, city_name | 是 |
| `aggr_fwa_usr_info_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_fwa_usr_summary_share_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_grid_develop_report_d` | area_id, area_name | 是 |
| `aggr_grid_earfcn_test_d` | area_name, city_name, province_name, region_name | 是 |
| `aggr_heterofreq_measure_monitor_d` | area_name, city_name, province_name, region_name | 是 |
| `aggr_lte_app_usercnt_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_basestation_share_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_coverage_celgrd_api_h` | city_name, province_name | 是 |
| `aggr_lte_coverage_grd_api_d` | city_name, province_name | 是 |
| `aggr_lte_coverage_grd_api_h` | city_name, province_name | 是 |
| `aggr_lte_dpi_area_app_d` | area_id, area_name | 是 |
| `aggr_lte_dpi_area_app_h` | area_id, area_name | 是 |
| `aggr_lte_dpi_area_apptype_d` | area_id, area_name | 是 |
| `aggr_lte_dpi_area_apptype_h` | area_id, area_name | 是 |
| `aggr_lte_dpi_area_perception_d` | area_id, area_name | 是 |
| `aggr_lte_dpi_area_perception_h` | area_id, area_name | 是 |
| `aggr_lte_dpi_cell_app_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_cell_app_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_cell_apptype_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_cell_apptype_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_cell_perception_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_cell_perception_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_city_app_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_city_app_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_city_apptype_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_city_apptype_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_city_perception_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_city_perception_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_province_app_d` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_province_app_h` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_province_apptype_d` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_province_apptype_h` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_province_perception_d` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_province_perception_h` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_dpi_region_app_d` | area_id, area_name, region_id, region_name | 是 |
| `aggr_lte_dpi_region_app_h` | area_id, area_name, region_id, region_name | 是 |
| `aggr_lte_dpi_region_apptype_d` | area_id, area_name, region_id, region_name | 是 |
| `aggr_lte_dpi_region_apptype_h` | area_id, area_name, region_id, region_name | 是 |
| `aggr_lte_dpi_region_perception_d` | area_id, area_name, region_id, region_name | 是 |
| `aggr_lte_dpi_region_perception_h` | area_id, area_name, region_id, region_name | 是 |
| `aggr_lte_fault_alarm_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_fault_breakdown_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_fault_integration_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_fault_nopmmr_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_highload_cell_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_lte_pm_cel_api_d` | city_name, province_name | 是 |
| `aggr_lte_pm_cel_api_h` | city_name, province_name | 是 |
| `aggr_lte_pm_cel_api_q` | city_name, province_name | 是 |
| `aggr_lte_pm_cel_q` | area_name, region_code, region_name | 是 |
| `aggr_lte_pm_cel_rt_q` | area_name, region_code, region_name | 是 |
| `aggr_lte_rrcutilization_rate_d` | area_name, province_id, province_name | 是 |
| `aggr_lte_site_rrcutilization_rate_d` | area_name, city_name | 是 |
| `aggr_lte_wxcell_backfill_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_mall_covercell_index_share_d` | area_id, city_id | 是 |
| `aggr_mccm_share_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_mr_cell_ta_7_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_mr_cell_ta_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_mr_enb_ta_7_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_mr_enb_ta_d` | area_name, city_code, city_name, province_name, region_name | 是 |
| `aggr_nr_basestation_share_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_coverage_celgrd_api_d` | city_name, province_name | 是 |
| `aggr_nr_coverage_celgrd_api_h` | city_name, province_name | 是 |
| `aggr_nr_coverage_grd_api_d` | city_name, province_name | 是 |
| `aggr_nr_fault_alarm_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_fault_breakdown_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_fault_integration_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_fault_nopmmr_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_grid_loalat_stat_7area_share_d` | city_code, province_code, region_code | 是 |
| `aggr_nr_pm_cel_api_d` | city_name, province_name | 是 |
| `aggr_nr_pm_cel_api_h` | city_name, province_name | 是 |
| `aggr_nr_usersector_band_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_usersector_band_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_nr_wxcell_backfill_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_predict_highload_cell_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_province_penetration_qual_share_d` | area_name, province_code, province_name, region_name | 是 |
| `aggr_province_site_utilization_share_d` | area_name, province_code, province_name, region_name | 是 |
| `aggr_region_penetration_qual_share_d` | area_name, region_name | 是 |
| `aggr_region_site_utilization_share_d` | area_name, region_name | 是 |
| `aggr_site_fault_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_site_utilization_brg_d` | city_id | 是 |
| `aggr_stat_index_7area_share_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `aggr_usersector_band_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_usersector_band_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_usr_terminal_detail_d` | city_code, city_name | 是 |
| `aggr_volte_mw_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_volte_mw_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_volte_s1uslice_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_volte_s1uslice_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `aggr_volte_userbrg_d` | area_name, city_code, city_name, province_code, province_name, region_code, region_name | 是 |
| `cfg_4gparm_threshold_list_d` | area_name, region_name | 是 |
| `cfg_barangay` | area_name, region_name | 否 |
| `cfg_base_5gcell_info_d` | area_name, city_name, province_name, region_name | 是 |
| `cfg_base_cell_info_d` | area_name, city_name, province_name, region_name | 是 |
| `cfg_base_enodeb_info_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `cfg_base_gnodeb_info_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `cfg_building_custom_area` | area_name, region_name | 是 |
| `cfg_city` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 否 |
| `cfg_fwa_custom_area_city_rel_d` | area_name, city_id | 是 |
| `cfg_fwa_sale_barangay_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `cfg_opensignal_threshold_list_d` | area_id | 是 |
| `cfg_oss_barangay` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 否 |
| `cfg_param_nr_threshold_list_d` | area_id, area_name | 是 |
| `cfg_param_threshold_list_d` | area_id, area_name | 是 |
| `cfg_plansite_cell_d` | region_name | 是 |
| `cfg_scene_grid20_rel` | city_name, province_name | 否 |
| `cfg_sector_lte_t` | city_id, city_name, province_id, province_name | 是 |
| `dim_exitport_cell_info` | area_id, city_id, province_id, region_id | 否 |
| `dim_questionnaire_region_config` | area_id, area_name, province_code, province_id, province_name, region_code, region_id, region_name | 否 |
| `dm_45g_area_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_45g_complaint_class_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_45g_netinsight_complaint_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_45g_scene_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_4gsitepro_cell_index_d` | area_name, region_name | 是 |
| `dm_5g_netinsight_cell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_5g_netinsight_cell_index_h` | area_name, city_name, province_name, region_name | 是 |
| `dm_5g_netinsight_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_5g_netinsight_stat_h` | area_name, city_name, province_name, region_name | 是 |
| `dm_5g_netinsight_stat_m` | area_name, city_name, province_name, region_name | 是 |
| `dm_5g_netinsight_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_a_city_subs_usage_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_area_cell_index_d` | area_name, region_name | 是 |
| `dm_area_cell_rel_d` | area_name, region_name | 是 |
| `dm_area_cell_stat_d` | area_name, region_name | 是 |
| `dm_area_grid_stat_d` | area_name, region_name | 是 |
| `dm_area_problem_cell_stat_d` | area_name, region_name | 是 |
| `dm_area_problem_grid_stat_d` | area_name, region_name | 是 |
| `dm_autoorder_area_opensignal_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_abnomal_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_cover_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_highload_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_ownbusy_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_owner_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_lte_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_nr_abnomal_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_nr_highload_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_nr_ownbusy_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_nr_owner_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_cell_nr_wirelesskpi_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_autoorder_pt_order_info_d` | area_name, region_code, region_name | 是 |
| `dm_base_5gcell_cdr_mr_pm_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_5gcell_deficiency_d` | area_name, city_code, province_code, region_name | 是 |
| `dm_base_5gcell_grid_rel_d` | area_name, region_name | 是 |
| `dm_base_5gcell_info_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_5gcell_info_label_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_base_5gcell_info_white_list_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_5gcell_kpi_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_5gcell_kpi_statistic_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_5gcell_redundance_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_cell_2webgis_d` | city_code, province_code, region_code | 是 |
| `dm_base_cell_azimuth_deviation_d` | area_name, region_name | 是 |
| `dm_base_cell_cdr_mr_pm_d` | area_name, region_name | 是 |
| `dm_base_cell_deficiency_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_cell_grid_rel_d` | area_name, region_name | 是 |
| `dm_base_cell_info_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_cell_info_label_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_base_cell_info_webgis_d` | region_code | 是 |
| `dm_base_cell_info_white_list` | area_name, region_name | 是 |
| `dm_base_cell_kpi_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_base_cell_kpi_statistic_d` | area_name, region_name | 是 |
| `dm_base_cell_lonlat_deviation_d` | area_name, region_name | 是 |
| `dm_base_cell_overshoot_d` | area_name, region_name | 是 |
| `dm_base_cell_redundance_d` | area_name, region_name | 是 |
| `dm_biznet_4g_drivertest_brg_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_biznet_4g_drivertest_city_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_biznet_4g_drivertest_grid20_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_biznet_5g_drivertest_brg_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_biznet_5g_drivertest_city_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_biznet_5g_drivertest_grid20_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_building_import_data_d` | area_name, region_name | 是 |
| `dm_cbhkpi_mr_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_cell_fluxrrc_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_cell_online_stat_q` | area_name, region_name | 是 |
| `dm_cell_rrc_capacity_connection_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_complaint_cft_add_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_complaint_cft_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_complaint_increment_order_d` | area_id | 是 |
| `dm_complaint_list_d` | area_id, area_name, region_id, region_name | 是 |
| `dm_ct_xdr_lte_5g_s1u_n3_ohvd_usrcity_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_datacube_brg_rsrp_2gis_d` | area_id, city_id, province_id, region_id | 是 |
| `dm_datacube_brg_rsrp_2gis_w` | area_id, city_id, province_id, region_id | 是 |
| `dm_datacube_cell_rsrp_2gis_d` | area_id, city_id, province_id, region_id | 是 |
| `dm_datacube_cell_rsrp_2gis_w` | area_id, city_id, province_id, region_id | 是 |
| `dm_datamonitor_5g_pm_area_stat_h` | area_id, area_name | 是 |
| `dm_datamonitor_5g_pm_stat_h` | area_id, area_name, region_id, region_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_aggr_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_d` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_fact_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_h_d` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_ods_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_time_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5g_stat_tmp_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5gcell_d` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_5gcell_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_nodata_5gcell_d` | area_name | 是 |
| `dm_datamonitor_mrpm_nodata_5gcell_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_nodata_5ggnodeb_d` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_nodata_5ggnodeb_h` | area_id, area_name | 是 |
| `dm_datamonitor_mrpm_nodata_cell_h` | area_name | 是 |
| `dm_datamonitor_mrpm_stat_access_h` | area_name | 是 |
| `dm_datamonitor_mrpm_stat_aggr_h` | area_name | 是 |
| `dm_datamonitor_mrpm_stat_fact_h` | area_name | 是 |
| `dm_datamonitor_mrpm_stat_h` | area_name | 是 |
| `dm_datamonitor_mrpm_stat_time_h` | area_name | 是 |
| `dm_datamonitor_mrpm_stat_tmp_h` | area_name | 是 |
| `dm_datamonitor_pm_area_stat_h_d` | area_name | 是 |
| `dm_datamonitor_pm_stat_h` | area_name, region_name | 是 |
| `dm_enodeb_online_stat_q` | area_name, region_name | 是 |
| `dm_fwa_barangay_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `dm_fwa_grid_barangay_geom_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `dm_fwa_grid_stat_d` | area_id, area_name | 是 |
| `dm_fwa_lte_grid_kpi_wd` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_fwa_nr_grid_kpi_wd` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_fwa_redcap_cm_projdata_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_fwa_redcap_grid_kpi_wd` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_fwa_sale_barangay_geom_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `dm_fwa_user_location_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_gis_assist_optimize_brg_cover_score_m` | area_name, city_id, city_name, province_id, province_name, region_name | 是 |
| `dm_gis_assist_optimize_city_cover_score_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_gis_assist_optimize_dt_data_d` | region_id | 是 |
| `dm_gis_assistant_optimization_construction_cell_sites_d` | area_name, region_name | 是 |
| `dm_gis_assistant_optimization_full_road_test_mark_q` | area_name, region_name | 是 |
| `dm_gis_assistant_optimization_full_road_test_mark_q_2100m_webgis` | region_code | 是 |
| `dm_gis_assistant_optimization_full_road_test_mark_q_2600m_webgis` | region_code | 是 |
| `dm_gis_assistant_optimization_full_road_test_mark_q_700m_webgis` | region_code | 是 |
| `dm_gis_assistant_optimization_full_road_test_mark_q_all_webgis` | region_code | 是 |
| `dm_interf_allcell_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_interf_cell_index_d` | area_id, area_name | 是 |
| `dm_interf_cell_index_d_2gis` | area_id, city_id, province_id, region_id | 是 |
| `dm_interf_cell_index_h` | area_id, area_name | 是 |
| `dm_interf_cell_samesite_index_h_d` | area_id, area_name | 是 |
| `dm_interf_grid_index_d_2gis` | area_id, city_id, province_id, region_id | 是 |
| `dm_interf_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_legal_user_data_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_legal_user_sms_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_legal_user_voice_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_load_layerzoom_cell_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_load_problem_cell_stat_d` | area_id, area_name | 是 |
| `dm_loadanalysis_4g_areatype_indicator_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_4g_enbtype_indicator_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_4g_resource_indicator_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_4g_scenetype_indicator_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_4g_subscenetype_indicator_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_5g_mutiltype_cellnum_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_5g_resource_indicator_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_areabusy_confidence_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_cell_index_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_cover_cqi_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_horizontalcomp_band_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_horizontalcomp_sector_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_areabusy_confidence_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_areabusy_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_areabusy_latest_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_cell_confidence_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_cell_confidence_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_cell_latest_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_loadanalysis_predict_highload_cell_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_cell_scene_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_city_cover_pop_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_site_rrcutilization_rate_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id | 是 |
| `dm_lte_user_45g_resident_area_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_45g_resident_area_index_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_45g_resident_area_time_d` | area_id, region_id | 是 |
| `dm_lte_user_5g_resident_area_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_5g_resident_area_daynight_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_5g_resident_area_index_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_5g_resident_area_time_d` | area_id, region_id | 是 |
| `dm_lte_user_area_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_area_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_area_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_barangay_cell_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_barangay_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_city_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_city_top20_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_city_top20_stat_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_city_top20_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_complaint_add_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_complaint_full_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_department_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_department_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_department_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_escalation_add_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_escalation_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_escalation_h_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_lte_user_nopparty_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_nopparty_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_nopparty_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_prbtype_top10_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_prbtype_top10_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_prbtype_top10_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_problem_area_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_problem_area_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_problem_area_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_resident_area_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_resident_area_daynight_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_resident_area_index_d` | area_id, region_id, region_name | 是 |
| `dm_lte_user_resident_area_time_d` | area_id, region_id | 是 |
| `dm_lte_user_resident_cell_info_d_2gis` | area_id, city_id, province_id, region_id | 是 |
| `dm_lte_user_rootcause_area_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_rootcause_area_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_rootcause_area_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_tag_top20_stat_d` | area_id, area_name | 是 |
| `dm_lte_user_tag_top20_stat_m` | area_id, area_name | 是 |
| `dm_lte_user_tag_top20_stat_w` | area_id, area_name | 是 |
| `dm_lte_user_warncell_14day_d_2dgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_mr_cell_ta_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_mr_enb_ta_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_neighboranalysis_cell_deficiency_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_neighboranalysis_cell_question_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_neighboranalysis_cell_question_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_neighboranalysis_cell_tac_consistency_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_neighboranalysis_lte_north_plancell_result_d` | area_id, area_name | 是 |
| `dm_neighboranalysis_plancell_d` | area_id, area_name | 是 |
| `dm_neighboranalysis_plancell_result_d` | area_id, area_name, province_code, province_name | 是 |
| `dm_netinsight_busytime_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_busytime_stat_m` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_busytime_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_cell_busytime_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_cell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_cell_index_h` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_highload_cell_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_highload_warncell_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_samepci_cell_ncell_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_samepci_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_stat_h` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_stat_m` | area_name, city_name, province_name, region_name | 是 |
| `dm_netinsight_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_nr_cell_scene_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_area_index_30day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_area_index_7day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_area_index_90day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_cell_index_30day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_cell_index_7day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_cell_index_90day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_cell_info_7day_d_2dgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_opensignal_cluster_allarea_index_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_cluster_area_index_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_enodeb_index_7day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_enodeb_info_7day_d_2dgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_opensignal_rsrp_info_7day_d_2dgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_opensignal_user_index_30day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_user_index_7day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_user_index_90day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_opensignal_user_time_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_access_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_access_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_function_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_huawei_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_nokia_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_power_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_reselection_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_time_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_toggle_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_cell_zte_compare_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_function_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_huawei_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nokia_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nr_access_compare_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nr_access_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nr_broadcast_compare_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nr_broadcast_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nr_signal_compare_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_nr_signal_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_power_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_reselection_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_time_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_toggle_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_paramcheck_zte_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_45g_flux_w_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_grid_complaintvalue_stat_m_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_grid_tacpercep_stat_d_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_light_pop_gdp_y_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_nr_rsrpsinr_w_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_othernet_rsrp_w_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_plan_rsrpsinr_w_2gis` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_pqarea_index_d` | area_name, region_name | 是 |
| `dm_pqarea_stat_d` | area_name, region_name | 是 |
| `dm_pquser_list_d` | area_name, region_name | 是 |
| `dm_pquser_stat_d` | area_name, region_name | 是 |
| `dm_proactive_appease_user_event_fault_list_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_proactive_appease_user_fault_integration_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_full_barangay_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_full_barangay_stat_m_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_full_barangay_stat_qt_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_full_barangay_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_survey_barangay_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_survey_barangay_stat_m_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_survey_barangay_stat_qt_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_combo_survey_barangay_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_csat_iengage_w` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_datatable_area_m` | area_name | 是 |
| `dm_questionnaire_engagehelp_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engagehelp_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engagehelp_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engagehelp_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engageomnibus_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engageomnibus_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engageomnibus_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_engageomnibus_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_expend_ipay_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_expend_ipay_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_expend_ipay_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_expend_ipay_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_expend_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_full_barangay_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_full_barangay_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_full_barangay_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_full_barangay_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_full_user_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_group_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_group_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_group_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_group_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_ipay_user_expend_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_joinol_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_joinol_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_joinol_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_joinol_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_pay_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_pay_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_pay_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_pay_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_survey185451_d` | region_id, region_name | 是 |
| `dm_questionnaire_use_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_useapp_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_useapp_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_useapp_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_useapp_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_usenetwork_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_usenetwork_stat_m_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_usenetwork_stat_qt_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_usenetwork_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_conf_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_engagehelp_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_engageomnibus_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_expend_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_issue_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_questionnaire_user_joinol_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_pay_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_use_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_use_index_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_useapp_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_questionnaire_user_usenetwork_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_regionalanalysis_channelnetwork_share_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_rfo_5g_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_rfo_5gcell_7day_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_rfo_5gcell_7day_index_d_2dgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_rfo_5gcell_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_rfo_5gcell_index_d_2dgis` | city_id, province_id, region_id | 是 |
| `dm_rfo_5ggrid_index_d_2dgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_rfo_5goverlapcell_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_rfo_5govershootcell_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_rfo_abcell7_lastday_index_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_cell_abn_azimuth_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_cell_abn_lonlat_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_cell_index_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_mod30_5gcell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_rfo_mod3cell_index_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_overlapcell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_rfo_overshootcell_7day_index_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_overshootcell_index_d` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_rfo_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_roadtest_district_stat_d` | area_name, region_name | 是 |
| `dm_roadtest_file_stat_d` | area_name, region_name | 是 |
| `dm_roadtest_grid_index_webgis_d` | region_code | 是 |
| `dm_roadtest_point_index_d` | region_id | 是 |
| `dm_roadtest_point_index_d_all` | region_id | 是 |
| `dm_roadtest_point_index_d_temp` | region_id | 是 |
| `dm_roadtest_point_undertake_d` | region_id | 是 |
| `dm_roadtest_segment_gird_rel_temp` | region_id | 是 |
| `dm_roadtest_segment_grid_rel_d` | region_id | 是 |
| `dm_roadtest_stat_d` | area_name, region_name | 是 |
| `dm_roadtest_task_stat_d` | area_name, region_name | 是 |
| `dm_scene_45g_area_cell_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_45g_area_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_45g_area_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_45g_covercell_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_45g_mrcover_subscence_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_celllayer_collect_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_celllayer_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_nr_celllayer_collect_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_scene_nr_celllayer_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_sys_area_d` | area_level, parent_id | 是 |
| `dm_terminal_45g_usersector_band_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_terminal_active_user_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_area_terminal_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_brands_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_datatop_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_goodrate_top_ascdsc_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_income_top_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_terminal_terminal_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_userprcv_barangay_user_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_userprcv_e2e_user_app_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_area_d` | area_id, area_name | 是 |
| `dm_userprcv_regionalanalysis_barangay_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_city_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_city_stat_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_city_stat_m` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_city_stat_w` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_clustering_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_clustering_m` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_clustering_w` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_compliant_stat_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_compliant_stat_m` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_compliant_stat_w` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_deepcover_day` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_gisallregion_barangay_d_webgis` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_gisallregion_deepcover_d_webgis` | area_id, city_id, province_id, region_id | 是 |
| `dm_userprcv_regionalanalysis_heatmap_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_heatmap_m` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_heatmap_w` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_launchedcity_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_province_d` | area_id, area_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_region_d` | area_id, area_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_servicetype_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_regionalanalysis_utilization_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_userprcv_user_app_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `dm_userprcv_user_app_index_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 是 |
| `dm_valueoperation_cell_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_cell_index_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_cell_stat_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_cell_stat_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_city_stat_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_city_stat_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_enodeb_d_2gis` | area_id, city_id, province_id, region_id | 是 |
| `dm_valueoperation_enodeb_freq_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_enodeb_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_enodeb_index_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_enodeb_m_2gis` | area_id, city_id, province_id, region_id | 是 |
| `dm_valueoperation_province_stat_d` | area_id, area_name, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_province_stat_m` | area_id, area_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_site_freq_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_valueoperation_site_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_volte_cell_kpi_d` | area_name, region_name | 是 |
| `dm_volte_kpi_statistic_d` | area_name, region_name | 是 |
| `dm_volte_kpi_tac_statistic_d` | area_name, region_name | 是 |
| `dm_volte_user_regist_list_d` | area_name, region_name | 是 |
| `dm_wirelesscover_5g_area_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_area_stat_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_area_stat_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_area_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_cell_detail_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_cell_detail_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_cell_detail_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_5g_cell_detail_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_area_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_area_stat_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_area_stat_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_area_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_cell_7stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_cell_detail_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_cell_detail_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_cell_detail_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_cell_detail_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_cell_index_d` | city_name, province_name | 是 |
| `dm_wirelesscover_cell_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_grid_cell_rel_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_grid_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_gridmr_7day_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_gridmr_rsrp_7day_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_gridmr_rsrp_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_gridmr_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_multi_operator_barangay_compare_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_multi_operator_barangay_compare_d_2webgis` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_multi_operator_barangay_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_multi_operator_brg_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_multi_operator_grid_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesscover_pre_orderwork_d` | area_name, region_name | 是 |
| `dm_wirelesscover_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_stat_m` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_user_cell_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesscover_user_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_45g_abnorcategory_stat_d` | area_id, area_name, region_id, region_name | 是 |
| `dm_wirelesskpi_45g_abnorpara_stat_d` | area_id, area_name, region_id, region_name | 是 |
| `dm_wirelesskpi_45gcell_parameter_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_45gcell_topn_d` | area_id, area_name, city_code, city_id, city_name | 是 |
| `dm_wirelesskpi_4gcell_index_gis_d` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_4gcell_index_gis_dh` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_4gcity_index_gis_d` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_4gcity_index_gis_dh` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_5g_stat_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5g_stat_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5g_stat_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5g_stat_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_dh` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_gis_d` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_gis_dh` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_h` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_m` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcell_index_w` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcell_parameter_stat_d_order` | area_id, area_name, region_id, region_name | 是 |
| `dm_wirelesskpi_5gcity_index_gis_d` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_5gcity_index_gis_dh` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_5gpreparam_orderwork_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_base_cell_info_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_busy_city_index_d` | area_name, city_id, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_busytime_index_area_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_busytime_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_compared_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_highload_area_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_highload_area_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_cell_highload_area_index_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_highload_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_highload_index_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_cell_highload_index_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_index_dh` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_index_h` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_index_m` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_index_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_cell_parameter_check_stat_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_cell_parameter_stat_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_cell_parameter_stat_d_order` | area_name, region_name | 是 |
| `dm_wirelesskpi_cell_parameter_stat_m` | area_name, region_name | 是 |
| `dm_wirelesskpi_cell_parameter_stat_w` | area_name, region_name | 是 |
| `dm_wirelesskpi_city_stat_area_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_city_stat_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_city_stat_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_city_statistic_area_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_city_statistic_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_city_statistic_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_highload_sugg_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_lowload_zeroflux_cell_index_d` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_lowload_zeroflux_cell_index_w` | area_id, area_name, city_code, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dm_wirelesskpi_ncell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_parameter_stat_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_parameter_stat_m` | area_name, region_name | 是 |
| `dm_wirelesskpi_parameter_stat_w` | area_name, region_name | 是 |
| `dm_wirelesskpi_prb_parameter_analyse_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_pre_orderwork_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_preparam_orderwork_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_rrcuser_cell_grid_rel_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_rrcuser_grid_busy_index_d` | city_id, province_id | 是 |
| `dm_wirelesskpi_rrcuser_grid_index_d` | city_id, province_id | 是 |
| `dm_wirelesskpi_rrcuser_grid_nobusy_index_d` | city_id, province_id | 是 |
| `dm_wirelesskpi_rrcuser_grid_ownbusy_index_d` | area_id, city_id, province_id, region_id | 是 |
| `dm_wirelesskpi_sameenb_cell_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_busytime_index_area_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_busytime_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_busytime_index_dh` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_index_d` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_index_m` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_index_w` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_night_busytime_index_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_night_highload_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_sector_night_maxindex_w` | area_name, city_code, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_stat_compared_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_stat_h` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_stat_night_d` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_stat_night_w` | area_name, city_name, province_name, region_name | 是 |
| `dm_wirelesskpi_station_index_d` | area_name, region_name | 是 |
| `dm_wirelesskpi_statistic_d` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_statistic_m` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dm_wirelesskpi_statistic_w` | area_name, city_id, city_name, province_code, province_name, region_name | 是 |
| `dq_kpi_province_d` | province_code | 是 |
| `dq_kpi_province_h` | province_code | 是 |
| `dq_kpi_province_merge_h` | province_code | 是 |
| `dw_cityutilization_share_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dw_complaint_cft_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dw_complaint_escalation_d` | area_id, area_name, city_id, city_name, province_id, province_name | 是 |
| `dw_complaint_escalation_h_d` | area_id, area_name, city_id, city_name, province_id, province_name | 是 |
| `dw_complaint_full_order_d` | area_id | 是 |
| `dw_lte_alarm_d` | area_id, area_name, region_id, region_name | 是 |
| `dw_lte_alarm_q` | area_id, area_name, region_id, region_name | 是 |
| `dw_lte_area_pmkpis_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dw_lte_cell_pmkpis_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dw_lte_cell_site_d` | city_id, province_id, region_id | 是 |
| `dw_lte_cellpm_label_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dw_lte_cm_projdata_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `dw_lte_mr_monitoring_h` | area_id | 是 |
| `dw_lte_plan_d` | region_id | 是 |
| `dw_lte_pmmr_monitoring_d` | area_name, region_name | 是 |
| `dw_lte_subject_pmkpis_d` | region_code, region_name | 是 |
| `dw_lte_subject_pmkpis_h` | region_code, region_name | 是 |
| `dw_lte_wx_cel_d` | area_id, area_name, region_id, region_name | 是 |
| `dw_lte_wx_enb_d` | area_name, region_name | 是 |
| `dw_roadtest_event_bad_point_d` | area_name, region_name | 是 |
| `dw_sentiment_message_info_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dw_user_0304_opensignal_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `dw_user_0304_opensignal_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `fact_enb_barangay` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_code, region_id, region_name | 否 |
| `fact_lte_calltrace` | area_name, region_code, region_name | 是 |
| `fact_lte_locationinfo_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `fact_lte_wx_north_ncell_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `fact_nr_cm_cell_d` | region_id | 是 |
| `fact_nr_locationinfo_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `fact_predict_areabusy_d` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `fact_predict_highload_cell_d` | city_name | 是 |
| `lte_cm_projdata` | area_id, area_name, city_code, city_id, city_name, province_code, province_id, province_name, region_id, region_name | 是 |
| `ods_a_city_subs_usage_m` | city_code, city_id, city_name, province_name | 是 |
| `ods_a_subs_channel_network_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `ods_cell_device_d_t` | city_id, province_id, region_id | 是 |
| `ods_ct_xdr_volte_s1u_session_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `ods_ct_xdr_volte_s1u_session_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `ods_dm_ct_xdr_lte_5g_s1u_n3_ohvd_usrcity_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `ods_ec_elec_bill_d` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `ods_i_cs_csc_case_all_d` | area_id | 是 |
| `ods_int_oss_order_ctt` | city_id, city_name, province_id, province_name | 是 |
| `ods_int_oss_order_ctt_townos` | city_id, city_name, province_name | 是 |
| `ods_lte_cdr_q` | area_name, region_code, region_name | 是 |
| `ods_lte_cell_site_d` | area_id, city_id, province_id, region_id | 是 |
| `ods_lte_complain_case_d` | area_id | 是 |
| `ods_lte_complain_prd_subs_term_d` | region_id | 是 |
| `ods_lte_complain_prd_usr_info_d` | region_id | 是 |
| `ods_lte_complaint_case_q` | area_id | 是 |
| `ods_lte_plan_d` | region_id | 否 |
| `ods_lte_pm_cel_q` | area_name, region_code, region_name | 是 |
| `ods_lte_wx_cc_d` | area_id, area_name, region_id, region_name | 是 |
| `ods_lte_wx_cel_d` | area_id, area_name, region_id, region_name | 是 |
| `ods_lte_wx_enb_d` | area_name, region_name | 是 |
| `ods_m_evt_cdr_data_detail_d` | region_id | 是 |
| `ods_m_prd_prod_inst_d` | region_id | 是 |
| `ods_mcc_sub_extend_001` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `ods_w2_evt_cdr_data_d` | region_id | 是 |
| `ods_w2_evt_cdr_sms_d` | region_id | 是 |
| `ods_w2_evt_cdr_voice_d` | region_id | 是 |
| `ods_w2_prd_usr_info_d` | region_id | 是 |
| `ods_w2_prd_usr_info_mccm_d` | region_id | 是 |
| `pt_order_info` | area_name, region_code, region_name | 是 |
| `temp_aggr_ct_xdr_lte_4g_s1u_n3_dns_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `temp_aggr_ct_xdr_lte_4g_s1u_n3_game_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `temp_aggr_ct_xdr_lte_4g_s1u_n3_http_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `temp_aggr_ct_xdr_lte_4g_s1u_n3_https_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `temp_aggr_ct_xdr_lte_4g_s1u_n3_other_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `temp_aggr_ct_xdr_lte_4g_s1u_n3_video_h` | area_id, area_name, city_id, city_name, province_id, province_name, region_id, region_name | 是 |
| `temp_aggr_lte_dpi_perception_app_d` | area_name | 是 |
| `temp_aggr_lte_dpi_perception_app_h` | area_name | 是 |
| `time_ods_lte_cdr_q` | area_name, region_code, region_name | 是 |