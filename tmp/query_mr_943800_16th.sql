-- 基站 943800 在 16 号全天上报的 MR 条数，按使用方（plmn）区分
-- 使用前请将 p_date 改为实际日期，如 '2025-03-16'

-- 方式一：按使用方汇总（推荐）
SELECT
    plmn AS 使用方,
    COUNT(1) AS mr条数
FROM fact_lte_mro_location_q
WHERE enodebid = 943800
  AND p_date = '2025-03-16'
GROUP BY plmn
ORDER BY mr条数 DESC;

-- 方式二：先看总量，再看各使用方占比
SELECT
    COUNT(1) AS 当日mr总量,
    COUNT(DISTINCT plmn) AS 使用方数量
FROM fact_lte_mro_location_q
WHERE enodebid = 943800
  AND p_date = '2025-03-16';

SELECT
    plmn AS 使用方,
    COUNT(1) AS mr条数,
    ROUND(COUNT(1) * 100.0 / SUM(COUNT(1)) OVER (), 2) AS 占比pct
FROM fact_lte_mro_location_q
WHERE enodebid = 943800
  AND p_date = '2025-03-16'
GROUP BY plmn
ORDER BY mr条数 DESC;
