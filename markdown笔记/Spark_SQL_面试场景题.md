# Spark SQL 大数据开发面试场景题（进阶版）

> 涵盖窗口函数、聚合、JOIN、日期/字符串、空值处理、去重、行列转换、复杂业务逻辑等，建议先自己写 SQL 再对照思路/答案。

---

## 一、窗口函数类

### 1.1 连续登录/连续达标

**表**：`user_login(user_id, login_date)`，每天每用户最多一条。

**题**：求每个用户**最长连续登录天数**（断一天即重新计）。

```sql
-- 思路：按 user_id 分区、login_date 排序，用 date_sub 做“日期 - 行号”得到连续段标识，再按段聚合求 max(cnt)
WITH t1 AS (
  SELECT user_id, login_date,
         date_sub(login_date, row_number() OVER (PARTITION BY user_id ORDER BY login_date)) AS grp
  FROM user_login
),
t2 AS (
  SELECT user_id, grp, count(*) AS cnt
  FROM t1
  GROUP BY user_id, grp
)
SELECT user_id, max(cnt) AS max_consecutive_days
FROM t2
GROUP BY user_id;
```

---

### 1.2 同组内 TopN，且 N 不固定

**表**：`orders(dt, city, amount)`。

**题**：每个 `dt` 下，按 `amount` 降序取每个 city 的**前 3 名**，若不足 3 条则全部保留。

```sql
SELECT dt, city, amount, rn
FROM (
  SELECT dt, city, amount,
         row_number() OVER (PARTITION BY dt, city ORDER BY amount DESC) AS rn
  FROM orders
) t
WHERE rn <= 3;
```

**变式**：用 `rank()` 或 `dense_rank()` 时，同分同名、是否跳号的区别要能说清。

---

### 1.3 同比/环比（lag/lead）

**表**：`sales(dt, amount)`，dt 为日期，按天一条。

**题**：求每日销售额，以及**昨日销售额**、**去年同期销售额**（假设有完整一年数据）。

```sql
SELECT dt, amount,
       lag(amount, 1)  OVER (ORDER BY dt) AS last_day_amount,
       lag(amount, 365) OVER (ORDER BY dt) AS same_day_last_year
FROM sales;
```

**进阶**：用 `date_format(dt,'MM-dd')` 做“同月日”的同比，需先按 (year, month-day) 分组或再用一次窗口。

---

### 1.4 累计求和（窗口 frame）

**表**：`daily_sales(dt, amount)`。

**题**：求每日的**当日销售额**与**截至当日的累计销售额**。

```sql
SELECT dt, amount,
       sum(amount) OVER (ORDER BY dt ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_sum
FROM daily_sales;
-- 或：sum(amount) OVER (ORDER BY dt RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
-- 可以简化成 : sum(amount) OVER (ORDER BY dt)
```

区分 `ROWS` 与 `RANGE` 在相同 `dt` 多行时的行为。

---

### 1.5 组内占比与组内排名

**表**：`orders(region, product_id, amount)`。

**题**：每个 region 内，每个 product_id 的**销售额占比**，以及**在 region 内的金额排名**。

```sql
SELECT region, product_id, amount,
       amount * 1.0 / sum(amount) OVER (PARTITION BY region) AS pct,
       rank() OVER (PARTITION BY region ORDER BY amount DESC) AS rn
FROM orders;
```

---

## 二、聚合与分组类

### 2.1 多维度聚合（GROUPING SETS / CUBE / ROLLUP）

**表**：`sales(dt, region, product, amount)`。

**题**：一次查询得到：(1) 按 dt；(2) 按 dt+region；(3) 按 dt+region+product；(4) 总合计。

```sql
SELECT dt, region, product,
       sum(amount) AS total,
       grouping_id(dt, region, product) AS gid
FROM sales
GROUP BY dt, region, product
GROUPING SETS (
  (dt),
  (dt, region),
  (dt, region, product),
  ()
);
-- 或用 CUBE(dt, region, product) / ROLLUP(dt, region, product) 根据需求选
```

---

### 2.2 条件聚合（count/sum + case when）

**表**：`user_events(user_id, event_type, event_time)`。

**题**：每个用户：总事件数、点击次数、曝光次数、最后点击时间。

```sql
SELECT user_id,
       count(*) AS total_events,
       sum(case when event_type = 'click' then 1 else 0 end) AS clicks,
       sum(case when event_type = 'exposure' then 1 else 0 end) AS exposures,
       max(case when event_type = 'click' then event_time end) AS last_click_time
FROM user_events
GROUP BY user_id;
```

---

### 2.3 collect_list / collect_set 与拼接

**表**：`orders(user_id, order_id, dt)`。

**题**：每个用户最近 3 笔订单的 **order_id 列表**（按 dt 降序，用逗号拼接）。

```sql
SELECT user_id,
       concat_ws(',', collect_list(cast(order_id AS string))) AS order_list
FROM (
  SELECT user_id, order_id,
         row_number() OVER (PARTITION BY user_id ORDER BY dt DESC) AS rn
  FROM orders
) t
WHERE rn <= 3
GROUP BY user_id;
```

注意：`collect_list` 顺序依赖上游数据顺序，子查询里已用 `row_number` 限定了“最近 3 笔”。

---

## 三、JOIN 与去重类

### 3.1 保留“最新一条”的去重（row_number）

**表**：`user_profile(user_id, name, city, etl_time)`，同一 user_id 有多条（多次上报），按 `etl_time` 取最新。

**题**：每个 user_id 只保留 **etl_time 最大** 的一条。

```sql
SELECT user_id, name, city, etl_time
FROM (
  SELECT user_id, name, city, etl_time,
         row_number() OVER (PARTITION BY user_id ORDER BY etl_time DESC) AS rn
  FROM user_profile
) t
WHERE rn = 1;
```

---

### 3.2 不等值 JOIN（区间匹配）

**表**：`events(user_id, event_time)`；`dim_interval(level, start_sec, end_sec)`，表示等级与时间区间（秒）。

**题**：每个事件的 **event_time（秒）** 落在哪个 level 的区间内。

```sql
SELECT e.user_id, e.event_time, d.level
FROM events e
JOIN dim_interval d
  ON e.event_time >= d.start_sec AND e.event_time < d.end_sec;
```

注意：区间不重叠时可得到唯一 level；若重叠需业务约定或再用聚合/窗口定序。

---

### 3.3 存在性判断（LEFT SEMI JOIN / IN / EXISTS）

**表**：`users(user_id)`，`orders(user_id, order_id)`。

**题**：有订单的用户列表（只保留 user 维度，不扩列）。

```sql
-- 写法1
SELECT u.user_id FROM users u
WHERE u.user_id IN (SELECT user_id FROM orders);

-- 写法2（Spark 常用，可避免 shuffle 过大）
SELECT u.user_id FROM users u
LEFT SEMI JOIN orders o ON u.user_id = o.user_id;
```

---

## 四、日期与字符串类

### 4.1 自然周/自然月（date_format、trunc）

**表**：`logs(dt, amount)`，dt 为 'yyyy-MM-dd'。

**题**：按**自然周**、**自然月**分别汇总 amount。

```sql
SELECT date_format(trunc(dt, 'WW'), 'yyyy-MM-dd') AS week_start,
       sum(amount) AS total
FROM logs
GROUP BY trunc(dt, 'WW');

SELECT date_format(trunc(dt, 'MM'), 'yyyy-MM') AS month_key,
       sum(amount) AS total
FROM logs
GROUP BY trunc(dt, 'MM');
```

`trunc(dt, 'WW')` 周一为起始；`trunc(dt, 'MM')` 为当月 1 日。

---

### 4.2 工作日/节假日（date_add、datediff、条件判断）

**表**：`orders(dt, order_id)`。

**题**：求每个订单日期**往后第 3 个工作日**的日期（简化：周末为周六日，先不考虑法定节假日）。

思路：**日历表 + 窗口** 或 **UDF 循环 + 日期加减**。面试时可说明“生成日历维表标记 is_workday，再 JOIN 后取第 3 个 is_workday=1 的日期”。

---

### 4.3 字符串解析与拼接（split、regexp、concat）

**表**：`raw(log_line)`，如 `"2025-01-01 10:00:00 | uid=123 | city=beijing"`。

**题**：解析出 **ts**、**uid**、**city** 三列。

```sql
SELECT to_timestamp(split(log_line, ' \\| ')[0]) AS ts,
       regexp_extract(log_line, 'uid=([0-9]+)', 1) AS uid,
       regexp_extract(log_line, 'city=([a-z]+)', 1) AS city
FROM raw;
```

---

### 4.4 JSON 解析（get_json_object / from_json）

**表**：`events(line)`，line 为 JSON 字符串，如 `{"user_id":1,"tags":["a","b"]}`。

**题**：解析出 **user_id** 与 **tags 数组**，并展开为一行一个 tag。

```sql
SELECT get_json_object(line, '$.user_id') AS user_id,
       get_json_object(line, '$.tags[0]') AS tag1,
       get_json_object(line, '$.tags[1]') AS tag2
FROM events;

-- 或用 from_json + explode（Spark 支持）
SELECT e.user_id, t.tag
FROM (
  SELECT get_json_object(line, '$.user_id') AS user_id,
         split(regexp_replace(get_json_object(line, '$.tags'), '[\\[\\]"]', ''), ',') AS tag_arr
  FROM events
) e
LATERAL VIEW explode(e.tag_arr) t AS tag;
```

---

## 五、空值与类型类

### 5.1 空值替换与默认值（coalesce / nvl）

**表**：`t(a, b, c)`，部分为 NULL。

**题**：计算 `a/b`，若 b 为 NULL 则按 0 算；若 a 为 NULL 则按 0 算；且分母为 0 时结果为 0。

```sql
SELECT coalesce(a, 0) * 1.0 / nullif(coalesce(b, 0), 0) AS ratio
FROM t;
-- 或：case when coalesce(b, 0) = 0 then 0 else coalesce(a, 0) * 1.0 / b end
```

`nullif(b, 0)` 在 b=0 时返回 NULL，从而整个除法为 NULL，再外层可 coalesce 为 0。

---

### 5.2 类型转换（cast、安全转换）

**表**：`t(amount_str)`，如 "123.45" 或 "invalid"。

**题**：转为 double，非法则置为 NULL。

说明：`cast(amount_str AS double)` 非法可能 NULL 或报错；更稳妥用 regexp 先判断或 `try_cast`（若引擎支持）。

---

## 六、行列转换类

### 6.1 行转列（多列聚合 + CASE WHEN）

**表**：`scores(student, subject, score)`。

**题**：转为 (student, math, english, chinese) 一行一个学生。

```sql
SELECT student,
       max(case when subject = 'math'    then score end) AS math,
       max(case when subject = 'english' then score end) AS english,
       max(case when subject = 'chinese' then score end) AS chinese
FROM scores
GROUP BY student;
```

---

### 6.2 列转行（explode + union）

**表**：`wide(id, c1, c2, c3)`。

**题**：转为 (id, col_name, col_value) 长表。

```sql
SELECT id, 'c1' AS col_name, c1 AS col_value FROM wide
UNION ALL
SELECT id, 'c2', c2 FROM wide
UNION ALL
SELECT id, 'c3', c3 FROM wide;
```

Spark 也可用 `stack(3, 'c1', c1, 'c2', c2, 'c3', c3)` 再 LATERAL VIEW 展开。

---

## 七、复杂业务逻辑类

### 7.1 会话划分（sessionize）

**表**：`clicks(user_id, event_time)`。

**题**：若两次点击间隔超过 30 分钟则视为新会话；为每个事件打上 **session_id**（同一会话相同）。

```sql
WITH t1 AS (
  SELECT user_id, event_time,
         sum(session_start) OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
  FROM (
    SELECT user_id, event_time,
           case when unix_timestamp(event_time) - lag(unix_timestamp(event_time)) OVER (PARTITION BY user_id ORDER BY event_time) > 30 * 60
                or lag(unix_timestamp(event_time)) OVER (PARTITION BY user_id ORDER BY event_time) IS NULL
                then 1 else 0 end AS session_start
    FROM clicks
  ) t0
)
SELECT user_id, event_time, session_id FROM t1;
```

---

### 7.2 留存（次日/7 日/30 日）

**表**：`user_login(user_id, dt)`。

**题**：某日新增用户（当日首次登录）的**次日留存率**、**7 日留存率**。

思路：先求每个用户 `min(dt)` 作为首登日；再 JOIN `user_login` 判断 `l.dt = date_add(f.first_dt, 1)` 或 7；最后按首登日聚合 count 做比率。

---

### 7.3 中位数 / 分位数（percentile / approx_percentile）

**表**：`orders(amount)`。

**题**：订单金额的 **中位数**、**P90**。

```sql
SELECT percentile(amount, 0.5) AS median,
       percentile(amount, 0.9) AS p90
FROM orders;

-- 大数据量用近似（Spark）
SELECT approx_percentile(amount, 0.5) AS median,
       approx_percentile(amount, 0.9) AS p90
FROM orders;
```

---

### 7.4 拉链表 / 缓慢变化（SCD 简化）

**表**：`user_snap(user_id, name, city, start_dt, end_dt)`，end_dt 为 9999-12-31 表示当前有效。

**题**：给定日期 `dt`，取每个 user_id 在 **dt 当天有效** 的那条记录。

```sql
SELECT user_id, name, city
FROM user_snap
WHERE '2025-06-15' BETWEEN start_dt AND end_dt;
```

---

## 八、性能与进阶

### 8.1 大表 JOIN 小表（broadcast）

**题**：大表 A 与小表 B（维表）JOIN，如何减少 shuffle？

**答**：`SELECT /*+ BROADCAST(B) */ ... FROM A JOIN B ON ...`，或 `broadcast(B)`，让 B 广播到各节点，避免 A 按 JOIN key 大 shuffle。

---

### 8.2 去重并保留指定行（综合）

**表**：`t(id, type, score, etl_time)`，同一 (id, type) 有多条。

**题**：按 (id, type) 去重，保留 **score 最大** 的一条；若 score 相同则保留 **etl_time 最大** 的一条。

```sql
SELECT id, type, score, etl_time
FROM (
  SELECT id, type, score, etl_time,
         row_number() OVER (PARTITION BY id, type ORDER BY score DESC, etl_time DESC) AS rn
  FROM t
) x
WHERE rn = 1;
```

---

### 8.3 多条件排序（order by 多列与 null 顺序）

**题**：按 a 升序、b 降序，且 NULL 在最后。

```sql
SELECT * FROM t
ORDER BY a ASC NULLS LAST, b DESC NULLS LAST;
```

---

## 九、函数速查（面试口述用）


| 类别   | 函数示例                                                                      |
| ---- | ------------------------------------------------------------------------- |
| 窗口   | row_number, rank, dense_rank, lag, lead, sum/avg over, rows/range between |
| 聚合   | sum/count/max/min, count(distinct), collect_list, collect_set, first/last |
| 分组扩展 | group by, grouping sets, cube, rollup                                     |
| 日期   | date_format, date_add, date_sub, datediff, trunc, to_date, unix_timestamp |
| 字符串  | concat, concat_ws, split, substr, regexp_extract, regexp_replace          |
| 空值   | coalesce, nvl, nullif, ifnull                                             |
| 类型   | cast, try_cast（部分引擎）                                                      |
| 复杂类型 | explode, posexplode, lateral view, get_json_object, from_json             |
| 其他   | case when, if, struct, array, map                                         |


---

按上述场景自己写一遍 SQL，再对照本文思路，面试时就能覆盖 Spark SQL 的重点与进阶用法。建议每类至少练 1～2 题，并能解释窗口 frame、分区键选择对数据倾斜的影响。