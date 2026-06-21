### 文档二：Hive 资产“AI 化”整理标准（技术实施版）

在将资源导入 Cursor 之前，需按此标准组织文件，以最大化 AI 的理解能力。

**1. 目录结构规范**
```text
/hive-ai-brain/
├── ddl/            # 存放所有表的建表语句 (TableName.sql)
├── logic/          # 存放每张表的生产加工 SQL (了解指标计算逻辑的核心)
├── golden_sql/     # 存放高频、复杂的历史临时取数 SQL 范本
├── docs/           # 存放模型设计 Markdown 或业务指标定义文档
└── .cursorrules    # 全局 AI 行为约束文件
```

**2. 资产预处理（AI 预冲刺）**
*   **自动化任务：** 编写一个脚本，将 Hive Metastore 中的信息导出。
*   **AI 增强：** 针对 `logic/` 中的 SQL，利用 AI 批量提取出“表描述”和“核心字段口径”，并以 README.md 形式存入 `docs/`。
