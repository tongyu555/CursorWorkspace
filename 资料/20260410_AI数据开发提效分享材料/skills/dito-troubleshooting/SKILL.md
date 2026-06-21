# DITO 问题排查技能

## 触发条件
当用户提出以下类型的请求时触发：
- 问题排查 / 核查 / 验证 / 数据对不上
- 指标异常 / 数据缺失 / 数据不一致
- bug排查 / 数据质量问题
- 涉及DITO项目的PM/DPI/MR/覆盖/高负荷/场景等数据异常

## 执行流程

### 1. 问题定位与分类
根据用户描述的现象，匹配问题类型：

| 问题大类 | 典型现象 | 排查方向 |
|---------|---------|---------|
| 数据缺失 | 某分区无数据/表为空/查不出 | 任务依赖→HDFS路径→分区存在性→上游数据 |
| 数据不一致 | 两张表同指标值不同/汇总≠明细和 | 口径对齐→聚合粒度→过滤条件→时间窗口 |
| 指标偏差 | 值偏大/偏小/突变 | 公式验证→单小区下钻→源数据抽样→维表变更 |
| 逻辑错误 | 业务规则不符合预期 | 规则定义→边界条件→CASE WHEN逻辑→阈值参数 |
| 性能问题 | 查询慢/资源爆/分区裁剪失效 | 分区条件→谓词下推→like/函数破坏裁剪 |
| 字段解析 | 厂商PM结构差异/数组字段 | 厂商分表→regexp_extract→CU/DU分离 |
| 跨系统 | PG/ClickHouse/HBase同步异常 | 同步配置→库名→引号→任务调度 |

### 2. 排查方法论（通用六步法）

```
第一步：固化现象
  ↓ 明确：哪张表、哪个分区、哪个维度、什么值、预期是什么
第二步：确认分区与数据存在性
  ↓ show partitions / select max(p_date) / dfs -ls
第三步：选定锚点对象
  ↓ 选1-3个具体的 cell_key / msisdn / barangay_id 作为排查样本
第四步：纵向血缘追溯
  ↓ DM → AGGR → FACT → ODS，同一指标逐层对比
第五步：横向一致性比对
  ↓ 同粒度 FULL/LEFT JOIN，找差集和差值
第六步：定位根因 → 验证修复
  ↓ 单对象复跑确认；必要时 desc formatted + HDFS核对
```

### 3. 按领域的排查策略

#### 3.1 DPI数据排查
**常见问题**：用户数/流量对不上、应用层与底层差异

**排查路径**：
```
aggr_45g_dpi_ip_host_d (天级汇总)
  ↑
aggr_lte_{http,https,other,dns,video,game}_base_q (15分钟级)
  ↑
fact_5gdpi_*_e2e / fact_psup_*_e2e (E2E明细)
  ↑
ods_5gdpi_*_e2e_q (ODS原始)
```

**排查SQL模板**：
```sql
-- 1. 对比应用层与底层用户数
select '底层UNION' as source, count(distinct msisdn) as user_cnt
from (
    select msisdn from aggr_lte_http_base_q where p_date = '${p_date}'
    union all
    select msisdn from aggr_lte_https_base_q where p_date = '${p_date}'
    union all
    select msisdn from aggr_lte_other_base_q where p_date = '${p_date}'
) t
union all
select '汇聚表' as source, count(distinct msisdn) as user_cnt
from aggr_lte_dpi_usrimeicelapp_q where p_date = '${p_date}';

-- 2. 找差集（在A不在B）
select A1.msisdn
from (select distinct msisdn from aggr_lte_http_base_q where p_date = '${p_date}') A1
left join (select distinct msisdn from aggr_45g_dpi_ip_host_d where p_date = '${p_date}') B1
    on A1.msisdn = B1.msisdn
where B1.msisdn is null
limit 20;
```

#### 3.2 PM无线指标排查
**常见问题**：KPI值不一致、QCI分册与合计不符

**排查路径**：
```
dm_wirelesskpi_sector_index_{d,h} / dm_wirelesskpi_5gcell_index_{d,h}
  ↑
aggr_lte_pm_cel_q / aggr_nr_pm_cell_sa_h
  ↑
fact_nr_pm_lceldu_h / fact_lte_pm_cel_h
  ↑
ite_nr_pm_lceldu_{zx,hw,nsn}_q (厂商原始)
  ↑
ods_lte_pm_cel_q / ods_nr_pm_*
```

**排查SQL模板**：
```sql
-- 单小区按小时逐层对比
-- DM层
select p_date, p_hour, cell_key, puschprbtotmeandl, prb_dl_avail
from dm_wirelesskpi_sector_index_h
where p_date = '${p_date}' and cell_key = '${cell_key}'
order by p_hour;

-- AGGR层
select p_date, p_hour,
    concat(related_enb_id, '_', cel_id) as cell_key,
    puschprbtotmeandl, prb_dl_avail
from aggr_lte_pm_cel_q
where p_date = '${p_date}'
    and concat(related_enb_id, '_', cel_id) = '${cell_key}'
order by p_hour;
```

**5G注意事项**：
- CU/DU分表：`ite_nr_pm_lceldu_*`（DU）vs `ite_nr_pm_lcelcu_*`（CU）
- 5QI数组字段需 `regexp_extract(col, '5QI9:([0-9.]+)', 1)` 拆解
- 厂商差异：ZTE/HW/NSN 的 `cel_id`、`gnb_cell` 映射规则不同

#### 3.3 MR/覆盖分析排查
**常见问题**：覆盖率跳变、分级和≠1、弱覆盖判定异常

**排查路径**：
```
dm_wirelesscover_{area_stat,stat}_{d,w} (区域汇总)
  ↑
dm_wirelesscover_cell_detail_{d,w} / dm_wirelesscover_5ggrid_index_d (小区/栅格)
  ↑
aggr_mr_cellgrid_kpi_d / aggr_nr_mr_cellgrid_kpi_temp_d (栅格聚合)
  ↑
fact_nr_mr_temp (MR明细)
```

**排查SQL模板**：
```sql
-- 1. 清单 vs 区域汇总对比
select A1.area_id,
    A1.mr_nums as detail_sum,
    B1.mr_nums as stat_val,
    A1.mr_nums - B1.mr_nums as diff
from (
    select area_id, sum(mr_nums) as mr_nums
    from dm_wirelesscover_cell_detail_d
    where p_date = '${p_date}'
    group by area_id
) A1
left join dm_wirelesscover_area_stat_d B1
    on A1.area_id = B1.area_id and B1.p_date = '${p_date}'
where A1.mr_nums != B1.mr_nums;

-- 2. 两日栅格FULL JOIN（定位覆盖率跳变）
select
    nvl(A1.regionid, B1.regionid) as regionid,
    nvl(A1.x_offset_20, B1.x_offset_20) as x,
    nvl(A1.y_offset_20, B1.y_offset_20) as y,
    A1.mr_nums as day1_mr,
    B1.mr_nums as day2_mr
from (select * from aggr_nr_mr_cellgrid_kpi_temp_d where p_date = '${date1}') A1
full outer join (select * from aggr_nr_mr_cellgrid_kpi_temp_d where p_date = '${date2}') B1
    on A1.regionid = B1.regionid
    and A1.x_offset_20 = B1.x_offset_20
    and A1.y_offset_20 = B1.y_offset_20
where A1.mr_nums is null or B1.mr_nums is null
limit 50;
```

**关键注意**：
- `goodcover` 统计必须带 `mr_nums > 0`，否则分子可能大于分母
- `locationtype` 过滤（200/1000/1001）会改变栅格结果
- 4G回填5G时注意 `int` 截断（比例<1 被截为0）

#### 3.4 高负荷/负荷分析排查
**常见问题**：高负荷小区数不一致、判定规则差异

**排查路径**：
```
dm_loadanalysis_4g_resource_indicator_d (负荷分析应用)
  ↑
dm_wirelesskpi_sector_night_busytime_index_d (忙时统计)
  ↑
dm_wirelesskpi_sector_index_h (PM小时)
  ↑
aggr_lte_pm_cel_q (PM聚合)
```

**常见根因**：
- **14天≥8天** vs **周内≥3天**：两种高负荷定义会导致计数差异
- **band_width_dl变更**：带宽变更导致多行，JOIN时可能挂错行
- **扇区合并**：多小区扇区需要把PRB使用量先合并后再算利用率

#### 3.5 场景分析排查
**常见问题**：覆盖小区标记异常、cell_scene_mrcnt_rate>1

**排查SQL模板**：
```sql
-- 检查场景小区是否重复
select cell_key, count(*) as cnt
from dm_scene_45g_covercell_d
where p_date = '${p_date}'
group by cell_key
having count(*) > 1;

-- 比率求和校验
select scene_id,
    sum(cell_scene_mrcnt_rate) as total_rate
from dm_scene_45g_area_stat_d
where p_date = '${p_date}'
group by scene_id
having sum(cell_scene_mrcnt_rate) > 1.01;
```

#### 3.6 用户/投诉排查
**常见问题**：常驻位置不一致、用户数差异

**排查路径**：
```
dm_lte_user_45g_resident_area_d (常驻地)
  ↑
aggr_45g_user_last7day_* (近7天行为)
  ↑
aggr_user_*resident* (常驻中间)
```

**排查要点**：
- 同一 `imsi` 在 `temp_*` 中间表逐步对齐
- `hour_list` 与 HBase rowkey 的时段字段可能不一致
- `order_nums = 1` 取第一常驻地

#### 3.7 工单管理/AutoOrder版本迭代验证
**常见问题**：新版规则上线后指标或打标结果与预期不一致、质差小区数异常增减

**涉及表**：
```
dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d (下行/上行速率 - 任意小时打标)
dm_autoorder_cell_lte_wirelesskpi_d (频谱效率 - 全天)
dm_autoorder_cell_lte_owner_wirelesskpi_d (频谱效率 - 自选忙时)
dm_autoorder_cell_lte_ownbusy_wirelesskpi_d (频谱效率 - 指标自忙时)
dm_autoorder_abnormal_cell_threshold_d (阈值配置表)
```

**版本迭代验证排查路径**：
```
版本迭代验证
  ↓ 明确版本变更内容（规则变更/阈值变更/数据源变更）
  ↓ 确认测试库（dtsw_test）与生产库（dtsw）的表是否一致
  ↓ 按天按小区全量输出新旧版本指标和打标结果
  ↓ 对比差异：
      ├─ 指标值一致但打标不同 → 检查阈值配置表变更
      ├─ 指标值不同 → 检查数据源或聚合逻辑变更
      └─ 打标全部一致 → 确认新规则配置尚未生效（如流量阈值未配置）
  ↓ 输出对比结论
```

**排查SQL模板**：
```sql
-- 1. 新旧版本下行速率打标对比（按天汇总质差小区数）
select
    A1.p_date
    ,sum(A1.is_abn_dlscdthr_exclud_qci689) as new_abn_cnt
    ,sum(A2.is_abn_dlscdthr_exclud_qci689) as old_abn_cnt
    ,sum(A1.is_abn_dlscdthr_exclud_qci689) - sum(A2.is_abn_dlscdthr_exclud_qci689) as diff
from dtsw_test.dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d A1
inner join dtsw.dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d A2
    on A1.cell_key = A2.cell_key
    and A1.p_date = A2.p_date
where A1.p_date between '2026-03-01' and '2026-03-31'
group by A1.p_date
order by A1.p_date;

-- 2. 检查阈值配置表是否有变更
select p_date, freq, threshold_name, threshold_value
from dm_autoorder_abnormal_cell_threshold_d
where p_date in ('${old_date}', '${new_date}')
    and threshold_name like '%spectrum%'
order by p_date, freq;

-- 3. 频谱效率三种类型质差小区数对比
select spectrum_type, count(*) as total_cells,
    sum(is_abn_dl_spectrum_rate) as dl_abn_cnt,
    sum(is_abn_ul_spectrum_rate) as ul_abn_cnt
from (
    select 'allday' as spectrum_type, is_abn_dl_spectrum_rate, is_abn_ul_spectrum_rate
    from dm_autoorder_cell_lte_wirelesskpi_d where p_date = '${p_date}'
    union all
    select 'owner', is_abn_dl_spectrum_rate, is_abn_ul_spectrum_rate
    from dm_autoorder_cell_lte_owner_wirelesskpi_d where p_date = '${p_date}'
    union all
    select concat('ownbusy_', ownbusy_type), is_abn_dl_spectrum_rate, is_abn_ul_spectrum_rate
    from dm_autoorder_cell_lte_ownbusy_wirelesskpi_d where p_date = '${p_date}'
) t
group by spectrum_type;
```

**关键注意**：
- 下行速率打标规则从"忙时判断"升级为"全天任意小时满足即打标"，对比时注意anyhour表和原表的差异
- 频谱效率新增下行流量判断，但若阈值未配置则预期与旧版一致
- 指标自忙时表(ownbusy)每小区有5条记录(flux/prb/rrc/pdcp_sduoctul/pdcp_sduoctdl)
- 版本验证通常从dtsw_test库取数，对比dtsw生产库

**历史案例**：
- **2026-04-08 autoorder版本迭代验证**：工单管理V3.0.26.12_V3.0.5版本，下行速率改为任意小时打标，频谱效率新增流量判断（但阈值未配置）。验证取3月全月数据，按天按小区输出指标值和打标结果用于前后对比。详见 `05_bug/20260408_autoorder_dlrate_spectrum_validation.sql`

#### 3.8 配置表/维表空跑排查
**常见问题**：配置表因调度依赖配置错误导致空跑，下游大面积表数据异常

**典型现象**：
- 多张不相关业务域的表同时出现数据量减少或为空
- 下游ETL任务执行成功（无报错），但产出数据量骤降
- 异常仅限于特定区域（p_provincecode），其他区域正常

**高危配置表及影响范围**：

| 配置表 | 直接下游数 | 影响业务域 |
|--------|-----------|-----------|
| `cfg_grid_tag` | **81张** | 覆盖分析/用户常驻/网络洞察/GIS规划/FWA/干扰/投诉 |
| `cfg_oss_barangay` | 大量 | 几乎所有涉及区域维度的表 |
| `dm_base_cell_info_d` | 大量 | 几乎所有涉及小区维度的表 |
| `cfg_region` | 中等 | 区域汇总类表 |

**排查路径**：
```
大面积数据异常
  ↓ 梳理异常表清单，找共同上游
  ↓ 通过知识库ETL任务索引反查 source_tables
  ↓ 识别出共同的配置表/维表
  ↓ 检查配置表当日数据量（与前几天对比）
  ↓ 检查调度系统任务执行日志和依赖配置
  ↓ 确认根因：依赖配置错误 / 上游空跑 / 分区缺失
```

**排查SQL模板**：
```sql
-- 1. 快速检查核心配置表数据量（多日对比）
select 'cfg_grid_tag' as table_name, p_provincecode, count(*) as row_cnt
from cfg_grid_tag
where p_provincecode = ${p_provincecode}
group by p_provincecode
union all
select 'cfg_oss_barangay' as table_name, cast(area_id as int), count(*)
from cfg_oss_barangay
where area_id = ${p_provincecode}
group by area_id;

-- 2. 配置表空跑检测（数据量为0的分区）
select p_provincecode, count(*) as row_cnt
from cfg_grid_tag
group by p_provincecode
order by row_cnt;

-- 3. 受影响的下游表一站式数据量对比
-- 通过知识库ETL任务索引获取受影响表清单后，
-- 使用UNION ALL对比所有下游表当日vs前一天数据量
```

**历史案例**：
- **2026-04-06 cfg_grid_tag NLZ空跑事件**：调度系统依赖配置错误导致 `cfg_grid_tag` 在 p_provincecode=2 空跑，直接影响81张下游表，涉及覆盖/用户/洞察/规划等所有业务域。排查通过逐层血缘追溯定位，最终确认根因为调度依赖配置问题。

### 4. 通用排查SQL模板库

#### 4.1 分区存在性检查
```sql
select max(p_date) as latest_date from target_table;
-- 或
show partitions target_table;
```

#### 4.2 行数总量对齐
```sql
select 'table_A' as src, count(*) as cnt
from table_A where p_date = '${p_date}'
union all
select 'table_B' as src, count(*) as cnt
from table_B where p_date = '${p_date}';
```

#### 4.3 维度分层求和
```sql
select area_id,
    sum(metric) as agg_val
from detail_table
where p_date = '${p_date}'
group by area_id
order by agg_val desc;
```

#### 4.4 差集查找
```sql
select A1.key_col
from (select distinct key_col from table_A where p_date = '${p_date}') A1
left join (select distinct key_col from table_B where p_date = '${p_date}') B1
    on A1.key_col = B1.key_col
where B1.key_col is null
limit 20;
```

#### 4.5 字段一致性检查
```sql
select A1.cell_key,
    A1.metric_a as dm_val,
    B1.metric_a as aggr_val,
    A1.metric_a - B1.metric_a as diff
from dm_table A1
inner join aggr_table B1
    on A1.cell_key = B1.cell_key
    and A1.p_date = B1.p_date
where abs(A1.metric_a - B1.metric_a) > 0.01
limit 20;
```

#### 4.6 滚动窗口计数
```sql
select cell_key,
    count(distinct if(is_highload = 1, p_date, null)) as highload_days
from daily_table
where p_date between date_sub('${p_date}', 13) and '${p_date}'
group by cell_key
having count(distinct if(is_highload = 1, p_date, null)) >= 8;
```

#### 4.7 厂商PM结构解析
```sql
-- ZTE 5QI字段解析
select cell_key,
    regexp_extract(qci_field, '5QI9:([0-9.]+)', 1) as qci9_val
from ite_nr_pm_lceldu_zx_q
where p_date = '${p_date}'
limit 10;
```

## 排查决策树

```
问题现象
├─ "查不出/超慢/OOM"
│   ├─ 检查分区条件是否完整（_d→p_date, _h→p_date+p_hour）
│   ├─ 检查WHERE中是否有like/函数破坏分区裁剪
│   └─ 检查是否需要子查询先过滤再JOIN
├─ "某分区/表无数据"
│   ├─ show partitions / dfs -ls 确认路径
│   ├─ 检查上游ETL任务是否成功
│   ├─ 检查依赖任务的执行顺序
│   ├─ 检查同步配置（PG/CK/FTP）
│   └─ 【新增】检查配置表/维表是否空跑（调度依赖问题）
├─ "大面积多表数据同时异常"
│   ├─ 优先排查共同上游的配置表/维表（cfg_grid_tag/cfg_oss_barangay/dm_base_cell_info_d）
│   ├─ 通过知识库ETL任务索引反查共同来源表
│   ├─ 检查调度系统中配置表任务的依赖配置和执行日志
│   └─ 确认配置表数据量是否正常（与前一天对比）
├─ "两张表总数对不上"
│   ├─ 确认是否同粒度（天/时/季）
│   ├─ 确认是否同过滤条件
│   ├─ 确认sum vs avg口径
│   ├─ 按area/cell/grid分层定位差异层级
│   └─ FULL JOIN找差集
├─ 按领域细分
│   ├─ DPI → 多base表UNION vs 汇聚表差集
│   ├─ PM → ODS→AGGR→DM单小区按小时逐层对比
│   ├─ MR/覆盖 → 栅格FULL JOIN多日；mr_nums与弱覆盖规则
│   ├─ 场景 → 图层/距离/cache计数与dm_scene对照
│   ├─ 负荷 → 14d/7d规则；band_width历史；cell差集
│   ├─ 用户 → imsi贯穿temp与aggr逐步对齐
│   ├─ 参数 → dm_paramcheck与ods分布/regexp
│   └─ AutoOrder → 新旧版本按天按小区全量对比；阈值配置表变更；anyhour vs 忙时规则差异
└─ 输出：根因类别 + 修复建议（SQL/任务/配置/维表）
```

## 经验教训与防范要点

1. **分区是第一道闸**：范围扫描时对比是否多扫分区导致重复或性能差异
2. **聚合口径**：全省`sum`再除 ≠ 对小区`avg`再平均
3. **cell_key多种拼法**：`concat(gnb,'_',cell)`、`split(cel_id,'-')`、`master_phy_cell_id` —— 必须确认与事实表一致
4. **覆盖弱覆盖**：`goodcover`统计带 `mr_nums > 0`
5. **4G回填5G**：回填比例 `int` 截断、`locationtype` 过滤会改变栅格结果
6. **高负荷/周统计**：工参带宽变更产生多行，JOIN时可能挂到错误行
7. **跨系统同步**：PG/ClickHouse/HBase同步要核对引号、库名、任务名、HDFS路径
8. **时间窗口边界**：`date_sub` 的天数、`between` 是否包含端点、`data_time_type` 取值
9. **配置表/维表空跑是高危事件**：`cfg_grid_tag`、`cfg_oss_barangay`、`dm_base_cell_info_d` 等核心配置/维表虽然数据量小、变更频率低，但下游依赖极广（如 `cfg_grid_tag` 直接影响81张表），一旦因调度依赖配置问题导致空跑，影响范围远超普通业务表。排查时应**优先检查配置表数据量**。
10. **调度依赖空跑**：当调度系统中上游任务虽然执行成功但实际产出空数据（如依赖配置错误导致空跑），下游任务不会报错但会产出空结果或数据量骤降。排查此类问题需要同时检查**任务执行状态**和**实际数据量**两个维度。

## 常用排查表清单

| 用途 | 核心表 |
|------|--------|
| 4G PM | `ods_lte_pm_cel_q`, `aggr_lte_pm_cel_q`, `dm_wirelesskpi_sector_index_{d,h}` |
| 5G PM | `ite_nr_pm_lceldu_{zx,hw,nsn}_q`, `fact_nr_pm_lceldu_h`, `aggr_nr_pm_cell_sa_h`, `dm_wirelesskpi_5gcell_index_{d,h}` |
| DPI | `aggr_lte_{http,https,dns,video,game,other}_base_q`, `aggr_45g_dpi_ip_host_d`, `fact_5gdpi_*_e2e` |
| MR/覆盖 | `aggr_mr_cellgrid_kpi_d`, `aggr_nr_mr_cellgrid_kpi_temp_{d,h}`, `dm_wirelesscover_*` |
| 场景 | `dm_scene_45g_covercell_d`, `dm_scene_45g_area_stat_d`, `dm_nr_grid_scene_gis_d` |
| 用户常驻 | `dm_lte_user_45g_resident_area_d`, `aggr_45g_user_last7day_*` |
| 高负荷 | `dm_wirelesskpi_sector_night_busytime_index_d`, `dm_loadanalysis_4g_resource_indicator_d` |
| 故障 | `aggr_cell_fault_affectusers_d`, `aggr_site_fault_affectusers_share_d` |
| 维表/工参 | `dm_base_cell_info_d`, `cfg_grid_tag`, `cfg_oss_barangay_7area` |
| 工单管理/AutoOrder | `dm_autoorder_cell_lte_anyhour_busy_wirelesskpi_d`, `dm_autoorder_cell_lte_wirelesskpi_d`, `dm_autoorder_cell_lte_owner_wirelesskpi_d`, `dm_autoorder_cell_lte_ownbusy_wirelesskpi_d`, `dm_autoorder_abnormal_cell_threshold_d` |
| 参数稽核 | `dm_paramcheck_nr_*`, `ods_nr_wx_*` |
| 数据质量 | `fact_share_quaility_check_card_d`, `cfg_hive_to_ftp_task_d` |

## 注意事项
- 排查过程中不修改生产表，仅做查询分析
- 对于单小区排查，优先使用 `limit 10/20` 控制返回量
- 复杂排查建议先 `cache table` 中间结果，避免重复扫描
- 排查结论应记录：根因分类、影响范围、修复方案、验证SQL
- 必须遵循 AI 代码标记规则（`--Generated By AI Start/End (Cursor)`）
