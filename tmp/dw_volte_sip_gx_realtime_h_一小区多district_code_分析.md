# dw_volte_sip_gx_realtime_h 一小区对应两个 district_code 问题分析

## 现象

```sql
select distinct city_code, district_code
from dw_volte_sip_gx_realtime_h
where p_provincecode = 230000 and p_date='2026-03-12' and p_hour=10
  and city_code = 232700 and enodebid='46001_10285129' and cellid=314;
```

结果中出现同一小区两条记录：
- 232700, 232722
- 232700, 232761

即同一 (enodebid, cellid) 在同一 (p_date, p_hour) 下对应两个不同的 district_code。  
city_code / district_code 由工参表、纠偏表回填，且生产上这四张源表内该小区无重复/异常。

**补充排查结果**：该小区（enodebid='46001_10285129', cellid=314）**仅在 `fact_nr_cm_projdata_roughrealtime` 中能查到**，在 `fact_nr_cm_projdata_corrected` 及 4G 工参/纠偏表中均无此 cell。即回填来源唯一，只有 5G 粗工参一张表。

---

## 代码逻辑简要

- **输出表**：`dw_volte_sip_gx_realtime_h` 由 Flink 任务写入，数据来自 Kafka 的 volte 信令 + 工参/纠偏回填。
- **回填来源**（4G）：  
  - `lte_cm_projdata_roughrealtime` → CmDim（优先）  
  - `lte_cm_projdata_corrected` → CmCorDim（其次）  
  - `lte_cucc_cm_projdata_rough` → CuDim（再次）  
  按 cellkey 只选一个来源，不存在“同一事件同时用两个表”的情况。
- **回填来源**（5G）：  
  - `fact_nr_cm_projdata_roughrealtime` → NrCmDim（优先）  
  - `fact_nr_cm_projdata_corrected` → NrCmCorDim（其次）  
  同样按 cellkey 只选一个来源。
- **工参加载**：`SetHdfsCmCu` 将上述表读入**静态** `ConcurrentHashMap`（如 `cmDimMap`、`cmCorDimMap` 等），由 `ConnectLetMapFunction` / `ConnectNrMapFunction` 定时（如每 `intervalGetFile` 一次）重新调用 `setCmDim` / `setCmCorDimMap` 等**覆盖式**写回同一 Map，**不先清空 Map**。
- **写入分区**：按 `currentProcessingTime()` 生成 `p_date`、`p_hour`，即按**处理时间**落分区，而非按信令事件时间。

---

## 可能原因（按可能性排序）

### 1. 工参定时刷新 + 处理时间分区导致“同一小时分区内看到两种回填结果”（最可能）

- 工参 Map 每隔一段时间（如 6 小时）用最新 HDFS 数据**整体覆盖**（put 进同一 Map，未先 clear）。
- 若在两次刷新之间，**上游工参/纠偏表对同一 cellkey 的 district_code 做了变更**（如 232722 → 232761）：
  - 刷新前处理的信令：用旧 Map → 回填 232722 → 写入当时对应的 p_date/p_hour（按处理时间）。
  - 刷新后处理的信令：用新 Map → 回填 232761 → 同样可能写入**同一** p_date/p_hour（例如 10 点这一小时持续有数据到达，先处理的用旧工参，后处理的用新工参）。
- 因此**同一 (enodebid, cellid) 在同一 (p_date, p_hour) 下会出现两条记录**：一条 232722，一条 232761。  
- 你查的“生产数据”若是当前最新分区或当前时刻的工参快照，只会看到**当前**的 district_code（例如 232761），看不到历史上曾出现过的 232722，所以源表“无异常”与“同一小时分区内存在两种回填结果”不矛盾。

**结论**：同一小区、同一小时分区内出现两个 district_code，很大概率是**工参在运行过程中发生过变更 + 按处理时间分区**导致的。  
结合“该 cell 仅存在于 `fact_nr_cm_projdata_roughrealtime`”可进一步确认：**两个 district_code 都来自同一张表在不同时刻的版本**——例如当天该表在 T1 时刻为 232722，T2 时刻（如日更或重跑后）变为 232761，Flink 在 T1 前、T2 后各做了一次工参 reload，导致同一 p_hour 内先处理的信令用 232722、后处理的用 232761。

---

### 2. 同一 cellkey 在源表多分区/多文件中存在不同 district_code（未固定“最新账期”）

- `SetHdfsCmCu` 中 **getLatestDate() 未被使用**，传入的 path 为 `.../p_provincecode=230000` 这类**不含 p_date** 的路径。
- 若 `HdfsFileReadUtils.readParquet/readCsv` 只读当前 path 下**一层**文件（不递归子目录），则：
  - 若表结构是 `p_provincecode=230000/p_date=yyyy-MM-dd/` 下再存文件，可能实际读不到任何文件，或只读到未分区的一层文件；
  - 若会递归或读到多个分区/多个文件，则同一 cellkey 在不同文件/分区中若 district_code 不同，后写入 Map 的会覆盖先写入的，**单次加载**内每个 cellkey 仍只对应一个 district_code。
- 因此“多文件/多分区”更可能影响的是**不同时刻加载到的“版本”不同**（结合原因 1），而不是在一次加载内产生两个值。但若未来修改为递归或读多分区，建议**只读最新一个 p_date**（例如用 getLatestDate），避免同一次加载中混入多账期。

---

### 3. 4G/5G 两路都写同一张表，且同一逻辑小区在 4G/5G 工参中 district 不一致（已排除）

- 主链路 4G 与侧路 5G 最终 `union` 后写同一张 HDFS 表；enodebid 在 5G 侧会被改为 `plmn_enodebid`（如 46001_10285129）。
- **本案已排除**：该小区仅在 `fact_nr_cm_projdata_roughrealtime` 存在，4G 工参/纠偏及 5G 纠偏表均无此 cell，故不存在“4G 回填 232722、5G 回填 232761”的多源混用。

---

### 4. 并行与静态 Map 的可见性

- 多个 subtask 共享同一静态 Map（如 `SetHdfsCmCu.cmDimMap`）。定时刷新在**某一个** subtask 的线程中执行，刷新时对 Map 的 put 对所有 subtask 立即可见。
- 因此不会出现“同一时刻同一 cellkey 在不同 subtask 看到不同值”的稳定分叉，但会出现“**不同时刻**（刷新前后）看到不同值”，与原因 1 一致。

---

## 建议排查与改造

1. **确认工参刷新与分区逻辑**
   - 查任务参数 `intervalGetFile`（刷新间隔）。
   - 确认 HDFS sink 的 bucket 是否按 `currentProcessingTime()` 生成 p_date/p_hour；若是，结合原因 1 解释“同一小时分区内两种 district_code”是符合当前实现的。

2. **确认 4G/5G 工参是否一致**（本案已做：该 cell 仅存在于 `fact_nr_cm_projdata_roughrealtime`，故原因 3 已排除）

3. **工参加载建议**
   - 刷新前**先清空对应 Map**（如 `cmDimMap.clear()`）再执行 `setCmDim`，避免旧账期数据长期残留；若 path 含多分区，应**只读最新一个 p_date**（可使用现有 getLatestDate 拼 path），避免同一次加载混入多账期。
   - 若业务要求“同一事件时间、同一小区在同一分区内 district_code 唯一”，可考虑：
     - 按**事件时间**生成 p_date/p_hour，或  
     - 在写入前对 (cellkey, p_date, p_hour) 做一次去重/取最新工参（需评估状态与性能）。

4. **历史数据校验**
   - 对已出现 232722/232761 的 p_date，查当日 **fact_nr_cm_projdata_roughrealtime** 在该 cellkey 上的变更记录或历史快照（若有），可验证是否在当日发生过 district 从 232722 调整为 232761。

---

## 小结

| 原因 | 说明 |
|------|------|
| **工参定时刷新 + 按处理时间分区**（最可能，且与排查结果一致） | 该 cell 仅存在于 **fact_nr_cm_projdata_roughrealtime**，两个 district_code 均来自此表在不同时刻的版本。同一小时内先处理的用旧工参（232722），后处理的用新工参（232761），都落在同一 p_date/p_hour。 |
| **4G/5G 工参不一致** | **已排除**：该 cell 只在 5G 粗工参表中存在，无 4G/5G 多源混用。 |
| **多分区/多文件未固定账期** | getLatestDate 未用，若将来读多分区，可能加载到不同账期混合数据，建议只读最新 p_date 并刷新前清空 Map。 |

**结论**：结合“仅在一张表 fact_nr_cm_projdata_roughrealtime 中能查到该小区”，可认定为一表在不同时刻的工参版本差异（含日更/重跑）经定时 reload 带入，导致同一 p_hour 内出现两个 district_code。建议按“工参加载建议”做 clear + 必要时按事件时间分区或去重，并核查当日该表是否有该 cell 的 district 变更记录。
