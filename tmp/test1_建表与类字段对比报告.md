# 建表语句与 NrCmDim 类字段对比报告

## 1. 数据源说明

- **建表**：`fact_nr_cm_projdata_roughrealtime`，分隔符 `|`，与类中 `SEPARATOR = "\\|"` 一致。
- **类**：`NrCmDim(String line)` 通过 `line.split(SEPARATOR, -1)` 按列下标取值，下标与表列顺序一一对应（从 0 开始）。

---

## 2. 建表列顺序（0-based 下标）与类字段映射

| 下标 | 建表列名 | 类字段 | 是否一致 |
|------|----------|--------|----------|
| 0 | date | （未使用） | — |
| 1 | vendor | （未使用） | — |
| 2 | province | provinceName | 含义一致，命名不同 |
| 3 | city | cityName | 含义一致，命名不同 |
| 4 | district | districtName | 含义一致，命名不同 |
| 5 | provincecode | provinceCode | 一致（仅大小写） |
| 6 | citycode | cityCode | 一致（仅大小写） |
| 7 | districtcode | districtCode | 一致（仅大小写） |
| 8 | plmnnum | （仅用于过滤 plmn=46011） | — |
| 9 | master_operators | （未使用） | — |
| 10 | ne_belong | （未使用） | — |
| 11 | master_gnbname | （未使用） | — |
| 12 | master_cellname | （未使用） | — |
| 13 | master_gnbid | （未使用） | — |
| 14 | master_cellid | plmn（取 split("-")[0]） | 列名与含义不一致：表为 master_cellid，类用作 plmn 来源 |
| 15 | gnbname | enodebname | 含义一致（5G gnb / 4G 命名 enodeb） |
| 16 | cellname | cellname | 一致 |
| 17 | gnbid | enodebid | 含义一致，命名不同 |
| 18 | cellid | cellid | 一致 |
| 19 | cellkey | cellkey | 一致 |
| 20 | celdu_id_local | （未使用） | — |
| 21 | tac | tac | 一致 |
| 22～62 | pci … bound_type | （未使用） | — |
| 63 | cell_longitude | cellLon | 含义一致，命名不同 |
| 64 | cell_latitude | cellLat | 含义一致，命名不同 |
| 65～69 | cell_height … cell_downtilt | （未使用） | — |
| 70 | end_prov | oppositeProvince | 含义一致，命名不同 |
| 71 | end_net_title | oppositeCity | 含义一致，命名不同 |
| 72 | end_county | （未使用） | — |
| 73 | stand_province_id | standProvinceId | 一致（仅大小写/下划线） |
| 74 | stand_province | standProvince | 一致 |
| 75 | stand_city_id | standCityId | 一致 |
| 76 | stand_city | standCity | 一致 |
| 77 | stand_county_id | standCountyId | 一致 |
| 78 | stand_county | standCounty | 一致 |
| 79 | tjj_town_id | standTownId | 含义一致，命名不同（stand vs tjj） |
| 80 | tjj_town | standTown | 含义一致，命名不同 |

---

## 3. 结论摘要

### 3.1 顺序与含义

- **列顺序一致**：类中使用的所有 `split[i]` 与建表列从左到右的下标一一对应，无错位。
- **所用列含义一致**：除下表所列外，类字段与对应建表列在业务含义上一致（仅命名风格不同：类 camelCase，表 lowercase_underscore）。

### 3.2 需注意的不一致

| 类型 | 说明 |
|------|------|
| **plmn 来源列** | 类中 `plmn` 来自 `split[14]`（建表列为 `master_cellid`），并对该值做 `split("-", -1)[0]`。若业务上 plmn 应来自 `plmnnum`（下标 8），则当前用 14 可能与表设计意图不符，需业务确认。 |
| **命名差异** | 表为 `tjj_town_id`/`tjj_town`，类为 `standTownId`/`standTown`，仅为命名不同，映射关系正确。 |

### 3.3 建表有但类未使用的列

以下建表列在 `NrCmDim(String line)` 中未使用（类只取部分列，属正常）：  
date, vendor, master_operators, ne_belong, master_gnbname, master_cellname, master_gnbid, celdu_id_local, pci, ssbfrequency, ssbsubcarrierspacing, cover_lerver, indoor_flag, radio_flag, freq, freq_ul, freq_dl, freq_pointno_ul, freq_pointno_dl, bandwidth_ul, bandwidth_dl, sfsysid, ant_code, towns, site_addr_code, rattypeid, gnb_model, gnb_serialid, gnb_type, gnb_deployment_mode, freq_mode, ant_extend, cel_num, rru_type, rru_model, rru_serialid, ant_vendor, ant_gain, ant_hbwd, ant_vbwd, ant_mechanicaldowntilt, ele_down_dis_21, ele_down_dis_18, ele_down_dis_26, ele_down_dis_800, ant_preset_electangle, cover_road_type, cover_hotspot_type, bound_type, cell_height, cell_cover_type, citycharacter, cell_azimuth, cell_downtilt, end_county。

### 3.4 类有但建表无的字段

- **time**：类中 `this.time = System.currentTimeMillis()`，为运行时生成，非表字段，合理。

---

## 4. 总体结论

- **建表列顺序与类按下标解析一致**，无错位。
- **类使用的表列与类字段对应关系正确**，仅存在命名风格差异（camelCase vs snake_case）以及 `stand*` 与 `tjj_town*` 的命名不同。
- **唯一需业务确认点**：`plmn` 使用 `split[14]`（表列 `master_cellid`）而非 `split[8]`（`plmnnum`），是否为预期逻辑。
