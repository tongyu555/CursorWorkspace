# 数据资产知识库总索引

> 本目录用于存放各项目的 Hive 数据资产知识库。每个项目拥有独立的子目录，包含该项目完整的表结构、ETL逻辑、数据血缘等知识。

---

## 目录结构

```
000_doc/
├── README.md                    -- 本文件（总索引）
├── 通用知识库整理提示词.md        -- 新项目知识库构建的通用模板
├── DITO/                        -- DITO项目知识库
│   ├── DDL/                     -- DDL源文件
│   ├── sql_code/                -- ETL SQL代码（265个任务组）
│   ├── 模型_excel/              -- 原始模型Excel文件（5个）
│   ├── 模型_toon/               -- 模型TOON格式文件（2463个，按Excel分目录）
│   ├── 知识库_表资产目录.json     -- 2036张表的元数据
│   ├── 知识库_ETL任务索引.json    -- 2231个ETL任务索引
│   ├── 知识库_数据血缘.json       -- 表级血缘关系
│   ├── 知识库_数据资产全景.md     -- 数据资产总览
│   ├── 知识库_表结构速查手册.md   -- 字段级速查手册
│   └── 知识库构建提示词.md        -- DITO项目构建提示词
├── _archive/                    -- 归档的早期方法论文档
│   ├── Hive 资产"AI 化"整理标准（技术实施版）.md
│   ├── Cursor 核心配置模板（.cursorrules）.md
│   ├── 项目总体实施方案（管理决策版）.md
│   └── 开发者取数操作 SOP（员工手册版）.md
├── 开发规则/                    -- 开发规则文档
└── 模板/                        -- 模板文件
```

---

## 项目索引

| 项目 | 状态 | 表数量 | ETL任务数 | 规则文件 | 知识库路径 |
|------|------|--------|----------|---------|-----------|
| DITO | 已完成 | 2036 | 2231 | `10-dito-project.mdc` | `000_doc/DITO/` |

### DITO项目技能（Skills）

| 技能 | 路径 | 用途 |
|------|------|------|
| SQL审查 | `.cursor/skills/sql-review/SKILL.md` | SQL代码审查与格式优化 |
| 知识库构建 | `.cursor/skills/knowledge-base-builder/SKILL.md` | 新项目知识库构建 |
| 临时取数 | `.cursor/skills/dito-adhoc-query/SKILL.md` | 按需数据提取与导出（基于50个历史BRT经验），含问卷关联/工单管理版本验证等场景 |
| 问题排查 | `.cursor/skills/dito-troubleshooting/SKILL.md` | 数据异常排查与定位（基于107个历史排查案例），含autoorder版本迭代验证 |

### DITO项目经验材料

| 材料 | 路径 | 说明 |
|------|------|------|
| 临时取数经验 | `07_linshiqushu/` | 50个历史取数SQL，覆盖DPI/画像/台风/高负荷/MR/问卷关联/工单管理版本验证等场景 |
| 问题排查历史 | `05_bug/` | 107个排查SQL，覆盖PM/DPI/覆盖/场景/负荷/用户/配置表空跑/autoorder版本迭代等领域 |

---

## 如何添加新项目

1. 在 `000_doc/` 下创建 `<项目名>/` 目录，包含 `DDL/` 和 `sql_code/` 子目录
2. 参考 `通用知识库整理提示词.md` 中的模板，引导 AI 构建知识库
3. 在 `.cursor/rules/` 下创建 `1x-<项目名>-project.mdc` 项目专属规则
4. 更新本文件的项目索引表

### 项目规则编号约定
- `10-dito-project.mdc` — DITO
- `11-<项目名>-project.mdc` — 第二个项目
- `12-<项目名>-project.mdc` — 第三个项目
- 以此类推...

---

## 通用规则（所有项目共享）

| 规则文件 | 说明 | 加载方式 |
|---------|------|---------|
| `01-sql-coding-standard.mdc` | 通用SQL编码规范 | alwaysApply |
| `02-sql-review-rules.mdc` | 36条审查规则（R001-R036） | 按需加载 |
| `03-ai-code-marker.mdc` | AI代码标记规则 | alwaysApply |
| `04-review-report-format.mdc` | 审查报告输出格式 | alwaysApply |
| `05-json-to-sql.mdc` | JSON转SQL转换规范 | alwaysApply |
