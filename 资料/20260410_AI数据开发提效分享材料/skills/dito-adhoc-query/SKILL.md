# DITO 临时取数技能

## 触发条件
当用户提出以下类型的请求时触发：
- 临时取数 / 取数 / 抽数 / 提数
- BRT需求 / 数据提取 / 数据导出
- 按需查询 / ad-hoc query
- 涉及DITO项目的用户画像、DPI流量、覆盖指标、高负荷、台风影响等业务取数

## 执行流程

### 1. 需求分析与场景识别
根据用户描述识别取数场景，匹配下表：

| 场景 | 关键词 | 推荐源表 |
|------|--------|---------|
| DPI应用感知 | app/host/流量/时延/重传/TCP/UDP/游戏/视频/博彩 | `aggr_45g_dpi_ip_host_d`, `aggr_lte_*_base_q`, `aggr_ct_xdr_lte_4g_s1u_n3_*_h` |
| 用户画像关联 | 年龄/性别/付费类型/FWA/常驻地/barangay | `dwm.W2_PRD_USR_INFO_D`, `dm_lte_user_45g_resident_area_d`, `cfg_oss_barangay_7area` |
| 问卷/CRM关联 | token/问卷/limesurvey/手机号 | `dwa.a_limesurvey_answer_info_d`, `dm_lte_user_45g_resident_area_d`, `fact_45g_userterminal_change_d` |
| 业务流量聚合 | 业务/子类/Grab/inDrive/微信 | `aggr_45g_user_business_d` |
| NAT公网IP | 公网IP/publicip/NAT/IMEI溯源 | `aggr_nat_join_dpi_h` |
| 台风/故障影响 | 台风/断站/离线/故障用户/影响用户 | `aggr_cell_fault_affectusers_d` |
| MR/MRO导出 | MR/MRO/测量报告/按小区导出 | `ods_lte_mro_q`, `aggr_mr_cellgrid_kpi_d` |
| 扩容小区 | 扩容/新增站/开站日期 | `dm_wirelesskpi_sector_index_d`, `dm_base_cell_info_d` |
| 高负荷 | 高负荷/PRB利用率/忙时 | `aggr_lte_pm_cel_q`, `dm_wirelesskpi_sector_index_h`, `dm_wirelesskpi_5gcell_index_h` |
| 栅格覆盖 | 栅格/RSRP/覆盖率/弱覆盖 | `aggr_mr_cellgrid_kpi_d`, `aggr_nr_mr_cellgrid_kpi_temp_d` |
| 防火墙日志 | 防火墙/firewall/源IP/目的IP | `fact_cloudpool_firewall_h` |
| 5G/4G E2E | E2E/端到端/丢包/抖动 | `fact_5gdpi_*_e2e*`, `fact_psup_*_e2e*` |
| PRB趋势 | PRB/城市级/月趋势/忙时 | `dm_wirelesskpi_sector_index_h`, `dm_wirelesskpi_5gcell_index_h` |
| 终端信息 | 终端/TAC/品牌/型号 | `fact_45g_userterminal_change_d` |
| 工单管理版本验证 | autoorder/工单/版本迭代/质差打标/下行速率/频谱效率 | `dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d`, `dm_autoorder_cell_lte_wirelesskpi_d`, `dm_autoorder_cell_lte_owner_wirelesskpi_d`, `dm_autoorder_cell_lte_ownbusy_wirelesskpi_d` |

### 2. 加载项目知识
- 加载 `.cursor/rules/10-dito-project.mdc` 获取DITO项目分区惯例和数仓架构
- 必要时查阅 `D:\000_zhaoxc\01_zhaoxc\04_project\000_doc\DITO\知识库_表资产目录.json` 确认表结构
- 必要时查阅 `D:\000_zhaoxc\01_zhaoxc\04_project\000_doc\DITO\知识库_表结构速查手册.md` 确认字段名

### 3. 构建SQL

#### 3.1 SQL骨架模式
根据需求选择合适的模式：

**模式A：cache链 → 建表 → 导出（最常用）**
```sql
-- 需求说明注释
-- 步骤1：缩小扫描范围
cache table cache_step1 as
select ...
from table_d
where p_date = '${p_date}';

-- 步骤2：关联维度
cache table cache_step2 as
select A1.*, B1.dim_col
from cache_step1 A1
left join dim_table B1 on A1.key = B1.key;

-- 步骤3：落盘
create table dtsw.data_extraction_xxx as
select ...
from cache_step2;
```

**模式B：insert overwrite 持久化（大数据量）**
```sql
insert overwrite table dtsw_test.target_table
partition(
    p_date = '${p_date}'
)
select ...
from source_table
where p_date = '${p_date}'
distribute by rand();
```

**模式C：多协议/多事实表 union all（DPI场景）**
```sql
cache table cache_union as
select 'http' as protocol, col1, col2, null as game_col
from aggr_lte_http_base_q where p_date between '...' and '...'
union all
select 'https' as protocol, col1, col2, null as game_col
from aggr_lte_https_base_q where p_date between '...' and '...'
union all
select 'game' as protocol, col1, col2, game_col
from aggr_lte_game_base_q where p_date between '...' and '...';
```

**模式E：版本迭代验证取数（autoorder场景）**
```sql
-- 从autoorder DM层直取指标+质差打标，按天按小区输出
-- 适用于版本迭代前后对比验证
cache table cache_indicator as
select
    A1.p_date
    ,A1.cell_key
    ,A1.cell_name
    ,A1.freq
    ,A1.target_indicator --目标指标值
    ,A1.is_abn_target_indicator --是否质差打标
from
    dtsw.dm_autoorder_cell_lte_xxx_d A1
where
    A1.p_date between '${start_date}' and '${end_date}'
;
-- 多种类型（如频谱效率的allday/owner/ownbusy）用union all合并
-- 落盘到 self_zxc_autoorder_<指标>_<月份>
create table dtsw.self_zxc_autoorder_xxx_yyyymm as
select * from cache_indicator;
```

**模式D：按月造表 → union all（长周期趋势）**
```sql
create table temp_indicator_202501 as
select '2025-01' as month_id, ...
from dm_wirelesskpi_sector_index_h
where p_date between '2025-01-01' and '2025-01-31'
    and p_hour between 20 and 20
group by ...;
-- 重复每月...
-- 最后 union all 所有月
```

#### 3.2 关键规范
- **分区必写**：`_d` → `p_date`; `_h` → `p_date + p_hour`; `_q` → `p_date`; `_w` → `p_year + p_week`
- **servicetype编码**：先查 `dim_dpi_ff_servicetype` 的 `concat(apptype_id, app_id, app_segment_id)`，再用于 IN 过滤
- **加权平均**：时延类指标用 `sum(delay * cnt) / sum(cnt)`，禁止对预聚合字段直接 `avg()`
- **空值与除零**：比率计算用 `case when sum(den) > 0 then sum(num) / sum(den) end`
- **去重取最新**：终端等变化维度用 `row_number() over (partition by msisdn order by change_time desc) rn` 取 `rn = 1`
- **跨库表注意**：`dwm.W2_PRD_USR_INFO_D` 用 `p_day_id`（int型如 20260208），不带引号
- **区域表已升级**：使用 `cfg_oss_barangay_7area` 替代旧版 `cfg_oss_barangay`

### 4. 生成导出命令

#### Spark SQL CLI导出（最常用）
```bash
spark-sql \
  --master yarn \
  --num-executors 100 \
  --executor-memory 4g \
  --executor-cores 8 \
  --driver-memory 5g \
  --silent \
  --database dtsw \
  --hiveconf hive.cli.print.header=true \
  --conf spark.debug.maxToStringFields=100 \
  --conf spark.driver.maxResultSize=5g \
  --conf spark.kryoserializer.buffer.max=2047m \
  -e "select * from dtsw.data_extraction_xxx" > /tmp/BRTxxxxxxxx.csv

sed -i 's/\t/\,/g' /tmp/BRTxxxxxxxx.csv
```

#### Beeline导出（JDBC方式）
```bash
beeline -u "jdbc:hive2://zk_host:port/;serviceDiscoveryMode=zooKeeper;zooKeeperNamespace=..." \
  --outputformat=txt \
  -e "use dtsw; select * from data_extraction_xxx" > /tmp/output.csv
```

#### 按小区循环导出（MR/大体量场景）
```bash
for cell_id in cell1 cell2 cell3; do
  spark-sql --master yarn --num-executors 50 --executor-memory 2g \
    --executor-cores 4 --driver-memory 5g --silent --database dtsw \
    --hiveconf hive.cli.print.header=true \
    -e "select * from temp_table where cell_key='${cell_id}'" > /tmp/mr_${cell_id}.csv
  sed -i 's/\t/\,/g' /tmp/mr_${cell_id}.csv
done
```

### 5. Spark配置参数模板

#### 防小文件配置（建表/insert场景必加）
```sql
set spark.sql.adaptive.enabled = true;
set spark.sql.adaptive.coalescePartitions.enabled = true;
set spark.sql.adaptive.coalescePartitions.maxPartitionSize = 256m;
set spark.sql.adaptive.coalescePartitions.minPartitionSize = 128m;
set mapreduce.fileoutputcommitter.marksuccessfuljobs = false;
set spark.sql.hive.convertMetastoreOrc = false;
set spark.sql.hive.convertInsertingPartitionedTable = false;
set spark.sql.hive.convertMetastoreParquet = false;
```

## 核心数据源表速查

### DPI / 应用感知
| 表 | 粒度 | 关联键 | 核心字段 |
|----|------|--------|---------|
| `aggr_45g_dpi_ip_host_d` | 天 | `p_date`, `msisdn`, `service_type`, `host`, `server_ip` | `dl_dpi_flux`, `up_dpi_flux`, `tcpsetupresponsedelay`, `tcpsetupackdelay`, `*_cnt`, `poor_quality_cnt`, `xdr_cnt` |
| `aggr_lte_{http,https,other,dns,video,game}_base_q` | 15分钟 | `p_date`, `servicetype`, `cell_key`, `msisdn` | `data_ulflux_byte`, `data_dlflux_byte`, `tcp_setup_response_delay`, `tcp_setup_ack_delay` |
| `aggr_ct_xdr_lte_4g_s1u_n3_game_h` | 小时 | `p_date`, `p_hour`, `cell_key` | TCP/UDP时延、重传、流量 |
| `dim_dpi_ff_servicetype` | 维表 | `concat(apptype_id, app_id, app_segment_id)` | `app_name` |
| `aggr_45g_user_business_d` | 天 | `p_date`, `msisdn`, `business_subtype` | `dl_flux`, `up_flux`, `online_dur` |

### 用户 / CRM
| 表 | 粒度 | 关联键 | 核心字段 |
|----|------|--------|---------|
| `dwm.W2_PRD_USR_INFO_D` | 天 | `p_day_id`(int), `acc_nbr` | `PROD_INST_TYPE`, `cust_age`, `cust_gender`, `payment_mode` |
| `dm_lte_user_45g_resident_area_d` | 天 | `p_date`, `msisdn`, `order_nums=1` | `barangay_name`, `barangay_id`, `city_name` |
| `dwa.a_limesurvey_answer_info_d` | 天 | `p_day_id`, `token` | `acc_nbr`, `payment_mode` |
| `fact_45g_userterminal_change_d` | 天 | `p_date`, `msisdn` | `terminal_brand`, `terminal_model`, `terminal_tac` |

### 网络 / PM
| 表 | 粒度 | 关联键 | 核心字段 |
|----|------|--------|---------|
| `dm_base_cell_info_d` | 天 | `p_date`, `cell_key`, `enodeb_id` | `freq`, `band_width_dl`, `cell_name`, `enodeb_type` |
| `dm_wirelesskpi_sector_index_{d,h}` | 天/时 | `p_date`, `cell_key` | PRB使用/可用、RRC用户数、吞吐 |
| `dm_wirelesskpi_5gcell_index_h` | 小时 | `p_date`, `p_hour`, `cell_key` | `prb_usedul`, `prb_availul`, `prb_useddl`, `prb_availdl` |
| `aggr_lte_pm_cel_q` | 15分钟 | `p_date`, `p_hour`, `concat(related_enb_id,'_',cel_id)` | PRB、RRC、PDCP QCI字段 |
| `aggr_nat_join_dpi_h` | 小时 | `p_date`, `p_hour`, `publicip` | `msisdn`, `imei` |

### 故障 / 影响
| 表 | 粒度 | 关联键 | 核心字段 |
|----|------|--------|---------|
| `aggr_cell_fault_affectusers_d` | 天 | `p_date`, `phy_enodebid` | `fault_time`, `restored_time`, `msisdn`, `city_code`, `flag` |

### MR / 覆盖
| 表 | 粒度 | 关联键 | 核心字段 |
|----|------|--------|---------|
| `ods_lte_mro_q` | 原始 | `p_date`, `enodebid`, `cellid` | MR测量报告全量字段 |
| `aggr_mr_cellgrid_kpi_d` | 天 | `p_date`, `cell_key`, 栅格坐标 | RSRP分级计数 |
| `aggr_nr_mr_cellgrid_kpi_temp_d` | 天 | 同上 | 5G RSRP/SINR分级计数 |

### 工单管理/AutoOrder
| 表 | 粒度 | 关联键 | 核心字段 |
|----|------|--------|---------|
| `dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d` | 天 | `p_date`, `cell_key` | `dlscdthr_exclud_qci689`(下行速率), `ulscdthr_exclud_qci689`(上行速率), `is_abn_dlscdthr_exclud_qci689`(下行质差打标), `is_abn_ulscdthr_exclud_qci689`(上行质差打标), `rrc_userconnmean_dl/ul`, `puschprbtotmeandl/ul_rate`, `pdcp_sduoctdl/ul` |
| `dm_autoorder_cell_lte_wirelesskpi_d` | 天 | `p_date`, `cell_key` | `dl_spectrum_rate`(下行频谱效率), `ul_spectrum_rate`(上行频谱效率), `is_abn_dl_spectrum_rate`, `is_abn_ul_spectrum_rate` — 全天类型 |
| `dm_autoorder_cell_lte_owner_wirelesskpi_d` | 天 | `p_date`, `cell_key` | 同上 — 自选忙时类型（按owner_hours聚合） |
| `dm_autoorder_cell_lte_ownbusy_wirelesskpi_d` | 天 | `p_date`, `cell_key`, `ownbusy_type` | 同上 + `ownbusy_hour`(忙时时间) — 指标自忙时类型（每小区5条：flux/prb/rrc/pdcp_sduoctul/pdcp_sduoctdl） |
| `dm_autoorder_abnormal_cell_threshold_d` | 天 | `p_date`, `freq` | 各指标阈值配置表，质差打标时关联此表判断 |

## 注意事项
- 临时取数结果表建议命名为 `data_extraction_<业务描述>` 或 `self_zxc_BRT<编号>`
- 大结果集优先 `insert overwrite` 到测试分区表，避免单次 `select` 撑爆 driver
- 博彩/灰产 host 关键字列表应集中维护，避免跨脚本复制导致不一致
- 时间格式对齐：断站 `fault_time` 常需 `substr(...,1,10)` 或 `from_unixtime` 统一
- 工单管理autoorder版本验证取数时，注意区分dtsw（生产库）和dtsw_test（测试库），验证时通常从dtsw_test取数
- autoorder频谱效率涉及三种类型（全天/自选忙时/指标自忙时），建议用`spectrum_type`字段区分后union all合并输出
- autoorder指标自忙时表（ownbusy）每个小区有5条记录，按`ownbusy_type`区分：flux/prb/rrc/pdcp_sduoctul/pdcp_sduoctdl
- 必须遵循 AI 代码标记规则（`--Generated By AI Start/End (Cursor)`）

## 历史案例参考

| 案例编号 | 需求类型 | 关键技术点 | 文件路径 |
|---------|---------|-----------|---------|
| BRT20260401000011 | 问卷token关联用户信息 | token→limesurvey→msisdn→常驻地+终端，cache链模式，row_number取最新 | `07_linshiqushu/BRT20260401000011/BRT20260401000011.sql` |
| autoorder版本验证202503 | 工单管理指标版本迭代验证 | 下行速率(anyhour任意小时打标)+频谱效率(三种类型union all)，按天按小区输出 | `05_bug/20260408_autoorder_dlrate_spectrum_validation.sql` |
