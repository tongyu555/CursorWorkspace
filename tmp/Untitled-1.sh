ods_nr_pm_lcelcu_dx_q
ods_nr_pm_lcelcu_lt_q
ods_nr_pm_cellcu_lt_q
ods_nr_pm_cellcu_dx_q
ods_nr_pm_celldu_dx_q
ods_nr_pm_celldu_lt_q

ods_nr_pm_lceldu_lt_q
ods_nr_pm_lceldu_dx_q



ALTER TABLE dtsw_db.ods_nr_pm_lcelcu_dx_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_lcelcu_lt_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_cellcu_lt_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_cellcu_dx_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_celldu_dx_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_celldu_lt_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_lceldu_lt_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');
ALTER TABLE dtsw_db.ods_nr_pm_lceldu_dx_q ADD if not exists PARTITION (p_provincecode = '${p_provincecode}', p_date = '${p_date}',p_hour = '${p_hour}',p_quarter = '${p_quarter}');




hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pmz_lcelcu_dx_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_lcelcu_lt_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_cellcu_lt_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_cellcu_dx_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_celldu_dx_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_celldu_lt_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_lceldu_lt_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}
hdfs://tdp-rbf/dtsw_db/telecom/5g/ods/ods_nr_pm_lceldu_dx_q/p_provincecode=${p_provincecode}/p_date=${p_date}/p_hour=${p_hour}/p_quarter=${p_quarter}