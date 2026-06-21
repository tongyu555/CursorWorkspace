# 电商 Hive SQL 算法场景大全

> 面向 **Hive / Spark SQL** 面试与实战，覆盖电商常见业务指标与算法题型。  
> 每题包含：**业务场景 → 表结构假设 → 完整 SQL → 考点函数 → 易错点**。

---

## 目录


| 章节  | 场景            | 核心函数                                             |
| --- | ------------- | ------------------------------------------------ |
| 一   | 基础流量指标        | `count`, `count distinct`, `sum`, `if/case when` |
| 二   | 新增用户 & 留存     | `left join`, `date_add`, 集合运算                    |
| 三   | 连续登录 / 连续购买   | `row_number`, `date_sub`, `group by + having`    |
| 四   | 漏斗转化          | `count distinct + case when`, 宽表                 |
| 五   | TopN & 最近 N 条 | `row_number`, `rank`, `dense_rank`               |
| 六   | 累计 & 滑动窗口     | `sum() over`, 滚动 GMV/UV                          |
| 七   | 同环比           | `lag`, `lead`, 日期对齐                              |
| 八   | 用户 RFM 模型     | 窗口聚合 + 分箱                                        |
| 九   | 复购 & 首购       | `min`, `count`, 自关联                              |
| 十   | 会话切割          | `lag`, 时间差, 会话 ID                                |
| 十一  | cohort 队列分析   | 注册 cohort + 留存矩阵                                 |
| 十二  | 商品关联（简易）      | 自关联, `collect_set`                               |
| 十三  | 指标分位 & 分层     | `percentile`, `ntile`                            |
| 十四  | 数据去重 & 拉链取最新  | `row_number`, `max by`                           |
| 十五  | 大表 UV 优化      | 两阶段去重, `approx_count_distinct`                   |
| 十六  | 数据倾斜 Join 改写  | 加盐, `broadcast hint`                             |
| 十七  | 综合实战题         | 多函数组合                                            |


---

## 公共维度表结构（全文复用）

```sql
-- 用户维度表
-- dim_user_df: user_id, register_date, channel, city, gender

-- 用户日活跃明细
-- dwd_user_active_di: user_id, dt, pv

-- 用户行为明细（曝光/点击/加购/下单/支付）
-- dwd_user_behavior_di: user_id, dt, event_time, event_type, page_id, product_id, session_id

-- 订单明细
-- dwd_trade_order_di: order_id, user_id, product_id, order_amt, pay_amt, order_status, order_time, dt
-- order_status: 1-待支付 2-已支付 3-已取消 4-已退款

-- 商品维度
-- dim_product_df: product_id, product_name, category_id, brand_id, price
```

---

## 一、基础流量指标（PV / UV / DAU(日活)）

### 1.1 业务场景

统计某日页面 PV、UV，并按渠道拆分 DAU。

### 1.2 完整 SQL

```sql
SELECT
    dt
    ,channel
    ,sum(pv) AS pv
    ,count(DISTINCT user_id) AS uv
FROM
    (
        SELECT
            a1.user_id
            ,a1.dt
            ,a1.pv
            ,nvl(b1.channel, 'unknown') AS channel
        FROM
            dwd_user_active_di a1
        LEFT JOIN
            dim_user_df b1
        ON
            a1.user_id = b1.user_id
        WHERE
            a1.dt = '2024-06-01'
    ) t1
GROUP BY
    dt
    ,channel
;
```

### 1.3 考点

- `count(1)` vs `count(*)`
- `count(distinct)` 大表性能问题（见第十五章）
- `nvl` / `coalesce` 空值处理
- 维度补全：`left join` 维表

### 1.4 易错点

- UV 用设备 ID 还是 user_id，口径需统一
- 未登录用户 `user_id` 为空是否计入

---

## 二、新增用户 & 留存率

### 2.1 业务场景

- **新增用户**：当日活跃且历史从未活跃
- **次日留存（D1）**：基准日活跃用户中，次日仍活跃的比例

### 2.2 新增用户 SQL

```sql
SELECT
    a1.dt
    ,count(DISTINCT a1.user_id) AS new_user_cnt
FROM
    dwd_user_active_di a1
LEFT JOIN
    (
        SELECT DISTINCT user_id
        FROM dwd_user_active_di
        WHERE
            dt < '2024-06-01'
    ) b1
ON
    a1.user_id = b1.user_id
WHERE
    a1.dt = '2024-06-01'
    AND b1.user_id IS NULL
GROUP BY
    a1.dt
;
```

**替代写法（用注册日）**：

```sql
SELECT
    register_date AS dt
    ,count(DISTINCT user_id) AS new_user_cnt
FROM
    dim_user_df
WHERE
    register_date = '2024-06-01'
GROUP BY
    register_date
;
```

> 两种口径不同：活跃新增 vs 注册新增，面试需主动说明。

### 2.3 次日 / 7 日留存 SQL

```sql
SELECT
    a1.dt AS base_dt
    ,count(DISTINCT a1.user_id) AS base_uv
    ,count(DISTINCT b1.user_id) AS d1_retain_uv
    ,count(DISTINCT b1.user_id) / count(DISTINCT a1.user_id) AS d1_retain_rate
FROM
    dwd_user_active_di a1
LEFT JOIN
    dwd_user_active_di b1
ON
    a1.user_id = b1.user_id
    AND b1.dt = date_add(a1.dt, 1)
WHERE
    a1.dt = '2024-06-01'
GROUP BY
    a1.dt
;
```

**7 日留存**：`date_add(a1.dt, 7)` 替换即可。

### 2.4 批量计算近 30 天 D1 留存趋势

```sql
SELECT
    a1.dt AS base_dt
    ,count(DISTINCT a1.user_id) AS base_uv
    ,count(DISTINCT b1.user_id) AS d1_retain_uv
    ,round(count(DISTINCT b1.user_id) / count(DISTINCT a1.user_id), 4) AS d1_retain_rate
FROM
    dwd_user_active_di a1
LEFT JOIN
    dwd_user_active_di b1
ON
    a1.user_id = b1.user_id
    AND b1.dt = date_add(a1.dt, 1)
WHERE
    a1.dt >= date_sub('2024-06-30', 29)
    AND a1.dt <= '2024-06-30'
GROUP BY
    a1.dt
ORDER BY
    a1.dt
;
```

### 2.5 考点

- `left join` + `is null` 反查新增
- `date_add` 日期偏移
- 留存分母是**基准日 UV**，不是次日 UV

---

## 三、连续登录 N 天（经典算法题）

### 3.1 业务场景

找出 2024 年 6 月内**至少连续登录 7 天**的用户。

### 3.2 核心原理

同一用户连续日期，满足：`login_date - row_number()` 分组标识相同。

### 3.3 完整 SQL

```sql
SELECT
    user_id
    ,min(start_date) AS streak_start
    ,max(end_date) AS streak_end
    ,max(streak_days) AS streak_days
FROM
    (
        SELECT
            user_id
            ,min(login_date) AS start_date
            ,max(login_date) AS end_date
            ,count(1) AS streak_days
        FROM
            (
                SELECT
                    user_id
                    ,login_date
                    ,date_sub(login_date, rn) AS grp_flag
                FROM
                    (
                        SELECT
                            user_id
                            ,login_date
                            ,row_number() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
                        FROM
                            (
                                SELECT DISTINCT
                                    user_id
                                    ,dt AS login_date
                                FROM
                                    dwd_user_active_di
                                WHERE
                                    dt >= '2024-06-01'
                                    AND dt <= '2024-06-30'
                            ) c1
                    ) b1
            ) a1
        GROUP BY
            user_id
            ,grp_flag
        HAVING
            count(1) >= 7
    ) t1
GROUP BY
    user_id
;
```

### 3.4 考点

- `row_number()` 窗口排序
- `date_sub` 构造连续分组键
- 两层 `group by`：先找连续段，再汇总用户

### 3.5 变体：连续购买 N 天

将 `dwd_user_active_di` 换为支付成功订单按日去重即可。

---

## 四、漏斗转化分析

### 4.1 业务场景

统计某日：**首页 → 商品详情 → 加购 → 下单 → 支付** 各环节 UV 及转化率。

### 4.2 方案 A：用户日粒度宽表（常用）

```sql
SELECT
    dt
    ,count(DISTINCT CASE WHEN is_home = 1 THEN user_id END) AS home_uv
    ,count(DISTINCT CASE WHEN is_detail = 1 THEN user_id END) AS detail_uv
    ,count(DISTINCT CASE WHEN is_cart = 1 THEN user_id END) AS cart_uv
    ,count(DISTINCT CASE WHEN is_order = 1 THEN user_id END) AS order_uv
    ,count(DISTINCT CASE WHEN is_pay = 1 THEN user_id END) AS pay_uv
FROM
    (
        SELECT
            user_id
            ,dt
            ,max(CASE WHEN event_type = 'home_view' THEN 1 ELSE 0 END) AS is_home
            ,max(CASE WHEN event_type = 'detail_view' THEN 1 ELSE 0 END) AS is_detail
            ,max(CASE WHEN event_type = 'add_cart' THEN 1 ELSE 0 END) AS is_cart
            ,max(CASE WHEN event_type = 'create_order' THEN 1 ELSE 0 END) AS is_order
            ,max(CASE WHEN event_type = 'pay_success' THEN 1 ELSE 0 END) AS is_pay
        FROM
            dwd_user_behavior_di
        WHERE
            dt = '2024-06-01'
        GROUP BY
            user_id
            ,dt
    ) a1
GROUP BY
    dt
;
```

**转化率计算（外层或 BI 层）**：

```sql
-- detail / home, cart / detail, ...
```

### 4.3 方案 B：严格有序漏斗（同一 session 内按时间有序）

```sql
SELECT
    count(DISTINCT user_id) AS funnel_uv
FROM
    (
        SELECT
            user_id
            ,session_id
            ,max(CASE WHEN step = 1 THEN 1 ELSE 0 END) AS s1
            ,max(CASE WHEN step = 2 THEN 1 ELSE 0 END) AS s2
            ,max(CASE WHEN step = 3 THEN 1 ELSE 0 END) AS s3
            ,max(CASE WHEN step = 4 THEN 1 ELSE 0 END) AS s4
            ,max(CASE WHEN step = 5 THEN 1 ELSE 0 END) AS s5
        FROM
            (
                SELECT
                    user_id
                    ,session_id
                    ,event_type
                    ,event_time
                    ,CASE event_type
                        WHEN 'home_view' THEN 1
                        WHEN 'detail_view' THEN 2
                        WHEN 'add_cart' THEN 3
                        WHEN 'create_order' THEN 4
                        WHEN 'pay_success' THEN 5
                    END AS step
                FROM
                    dwd_user_behavior_di
                WHERE
                    dt = '2024-06-01'
            ) b1
        GROUP BY
            user_id
            ,session_id
    ) a1
WHERE
    s1 = 1
    AND s2 = 1
    AND s3 = 1
    AND s4 = 1
    AND s5 = 1
;
```

### 4.4 考点

- `case when` + `max` 打宽
- 宽松漏斗 vs 严格漏斗口径差异
- `count(distinct case when ...)` 条件计数

---

## 五、TopN & 最近 N 条

### 5.1 每用户最近 3 笔订单

```sql
SELECT
    user_id
    ,order_id
    ,order_amt
    ,order_time
FROM
    (
        SELECT
            user_id
            ,order_id
            ,order_amt
            ,order_time
            ,row_number() OVER (
                PARTITION BY user_id
                ORDER BY order_time DESC
            ) AS rn
        FROM
            dwd_trade_order_di
        WHERE
            dt = '2024-06-01'
            AND order_status = 2
    ) a1
WHERE
    a1.rn <= 3
;
```

### 5.2 商品销量 Top10（三种排名函数对比）

```sql
SELECT
    product_id
    ,sale_cnt
    ,rn
    ,rk
    ,dr
FROM
    (
        SELECT
            product_id
            ,sale_cnt
            ,row_number() OVER (ORDER BY sale_cnt DESC) AS rn
            ,rank() OVER (ORDER BY sale_cnt DESC) AS rk
            ,dense_rank() OVER (ORDER BY sale_cnt DESC) AS dr
        FROM
            (
                SELECT
                    product_id
                    ,count(1) AS sale_cnt
                FROM
                    dwd_trade_order_di
                WHERE
                    dt = '2024-06-01'
                    AND order_status = 2
                GROUP BY
                    product_id
            ) b1
    ) a1
WHERE
    a1.rn <= 10
;
```


| 函数             | 并列处理     | 典型用途         |
| -------------- | -------- | ------------ |
| `row_number()` | 不并列，强制排序 | 取 TopN、去重取最新 |
| `rank()`       | 并列跳号     | 排行榜展示        |
| `dense_rank()` | 并列不跳号    | 分段排名         |


### 5.3 每个类目销量 Top3 商品

```sql
SELECT
    category_id
    ,product_id
    ,sale_cnt
FROM
    (
        SELECT
            category_id
            ,product_id
            ,sale_cnt
            ,row_number() OVER (
                PARTITION BY category_id
                ORDER BY sale_cnt DESC
            ) AS rn
        FROM
            (
                SELECT
                    b1.category_id
                    ,a1.product_id
                    ,sum(a1.pay_amt) AS sale_cnt
                FROM
                    dwd_trade_order_di a1
                INNER JOIN
                    dim_product_df b1
                ON
                    a1.product_id = b1.product_id
                WHERE
                    a1.dt >= '2024-06-01'
                    AND a1.dt <= '2024-06-30'
                    AND a1.order_status = 2
                GROUP BY
                    b1.category_id
                    ,a1.product_id
            ) c1
    ) t1
WHERE
    rn <= 3
;
```

---

## 六、累计 & 滑动窗口

### 6.1 累计 GMV（按日）

```sql
SELECT
    dt
    ,day_gmv
    ,sum(day_gmv) OVER (
        ORDER BY dt
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cum_gmv
FROM
    (
        SELECT
            dt
            ,sum(pay_amt) AS day_gmv
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            dt
    ) a1
ORDER BY
    dt
;
```

### 6.2 近 7 日滚动 GMV

```sql
SELECT
    dt
    ,sum(day_gmv) OVER (
        ORDER BY dt
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7d_gmv
FROM
    (
        SELECT
            dt
            ,sum(pay_amt) AS day_gmv
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            dt
    ) a1
ORDER BY
    dt
;
```

### 6.3 用户生命周期累计消费

```sql
SELECT
    user_id
    ,order_time
    ,pay_amt
    ,sum(pay_amt) OVER (
        PARTITION BY user_id
        ORDER BY order_time
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cum_pay_amt
FROM
    dwd_trade_order_di
WHERE
    dt >= '2024-01-01'
    AND order_status = 2
;
```

### 6.4 考点

- `sum() over(partition by ... order by ...)`
- `ROWS BETWEEN` 帧边界
- 累计 vs 滑动窗口区别

---

## 七、同环比（lag / lead）

### 7.1 业务场景

计算每日 GMV 的**日环比**、**周同比**。

### 7.2 日环比 SQL

```sql
SELECT
    dt
    ,day_gmv
    ,lag(day_gmv, 1) OVER (ORDER BY dt) AS prev_day_gmv
    ,round(
        (day_gmv - lag(day_gmv, 1) OVER (ORDER BY dt))
        / lag(day_gmv, 1) OVER (ORDER BY dt)
        , 4
    ) AS dod_rate
FROM
    (
        SELECT
            dt
            ,sum(pay_amt) AS day_gmv
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            dt
    ) a1
ORDER BY
    dt
;
```

### 7.3 周同比（7 天前同一天）

```sql
SELECT
    dt
    ,day_gmv
    ,lag(day_gmv, 7) OVER (ORDER BY dt) AS wow_base_gmv
    ,round(
        (day_gmv - lag(day_gmv, 7) OVER (ORDER BY dt))
        / lag(day_gmv, 7) OVER (ORDER BY dt)
        , 4
    ) AS wow_rate
FROM
    (
        SELECT
            dt
            ,sum(pay_amt) AS day_gmv
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            dt
    ) a1
ORDER BY
    dt
;
```

### 7.4 考点

- `lag(col, n)` 向前取 n 行
- `lead(col, n)` 向后取 n 行
- 除法需处理分母为 0：`nullif(prev, 0)`

---

## 八、RFM 用户价值模型

### 8.1 业务场景

按 **R（最近一次消费距今天数）/ F（消费频次）/ M（消费金额）** 对用户分层。

### 8.2 完整 SQL

```sql
SELECT
    user_id
    ,recency_days
    ,frequency
    ,monetary
    ,ntile(5) OVER (ORDER BY recency_days DESC) AS r_score
    ,ntile(5) OVER (ORDER BY frequency ASC) AS f_score
    ,ntile(5) OVER (ORDER BY monetary ASC) AS m_score
FROM
    (
        SELECT
            user_id
            ,datediff('2024-06-30', max(dt)) AS recency_days
            ,count(DISTINCT order_id) AS frequency
            ,sum(pay_amt) AS monetary
        FROM
            dwd_trade_order_di
        WHERE
            dt >= date_sub('2024-06-30', 89)
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            user_id
    ) a1
;
```

**R 分数说明**：`recency_days` 越大表示越久未消费，按降序 `ntile` 后需结合业务反转解读，面试中应说明打分规则。

**RFM 组合标签示例**：

```sql
SELECT
    user_id
    ,concat('R', r_score, 'F', f_score, 'M', m_score) AS rfm_tag
    ,CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN '重要价值用户'
        WHEN r_score <= 2 AND f_score >= 4 THEN '重要挽留用户'
        WHEN r_score >= 4 AND f_score <= 2 THEN '新客户'
        ELSE '一般客户'
    END AS user_segment
FROM
    rfm_score_table
;
```

### 8.3 考点

- `datediff` 计算间隔
- `ntile(n)` 等频分箱
- 业务规则 + SQL 分层的结合

---

## 九、复购率 & 首购用户

### 9.1 月复购率

**口径**：当月购买 ≥2 次的用户 / 当月购买用户。

```sql
SELECT
    month_id
    ,count(DISTINCT user_id) AS buy_uv
    ,count(DISTINCT CASE WHEN order_cnt >= 2 THEN user_id END) AS repurchase_uv
    ,count(DISTINCT CASE WHEN order_cnt >= 2 THEN user_id END)
        / count(DISTINCT user_id) AS repurchase_rate
FROM
    (
        SELECT
            substr(dt, 1, 7) AS month_id
            ,user_id
            ,count(DISTINCT order_id) AS order_cnt
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            substr(dt, 1, 7)
            ,user_id
    ) a1
GROUP BY
    month_id
;
```

### 9.2 首购用户 GMV 贡献

```sql
SELECT
    a1.dt
    ,sum(a1.pay_amt) AS first_order_gmv
    ,count(DISTINCT a1.user_id) AS first_buy_uv
FROM
    dwd_trade_order_di a1
INNER JOIN
    (
        SELECT
            user_id
            ,min(dt) AS first_buy_dt
        FROM
            dwd_trade_order_di
        WHERE
            order_status = 2
        GROUP BY
            user_id
    ) b1
ON
    a1.user_id = b1.user_id
    AND a1.dt = b1.first_buy_dt
WHERE
    a1.order_status = 2
    AND a1.dt >= '2024-06-01'
    AND a1.dt <= '2024-06-30'
GROUP BY
    a1.dt
;
```

### 9.3 考点

- `min(dt)` 找首次行为
- 条件聚合 `count(distinct case when ...)`

---

## 十、会话切割（Sessionization）

### 10.1 业务场景

用户 30 分钟无行为则开启新会话，统计每用户会话数、会话时长。

### 10.2 完整 SQL

```sql
SELECT
    user_id
    ,session_id
    ,min(event_time) AS session_start
    ,max(event_time) AS session_end
    ,unix_timestamp(max(event_time)) - unix_timestamp(min(event_time)) AS session_seconds
    ,count(1) AS event_cnt
FROM
    (
        SELECT
            user_id
            ,event_time
            ,event_type
            ,sum(is_new_session) OVER (
                PARTITION BY user_id
                ORDER BY event_time
                ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
            ) AS session_id
        FROM
            (
                SELECT
                    user_id
                    ,event_time
                    ,event_type
                    ,CASE
                        WHEN lag(event_time, 1) OVER (
                            PARTITION BY user_id
                            ORDER BY event_time
                        ) IS NULL THEN 1
                        WHEN unix_timestamp(event_time)
                            - unix_timestamp(lag(event_time, 1) OVER (
                                PARTITION BY user_id
                                ORDER BY event_time
                            )) > 1800 THEN 1
                        ELSE 0
                    END AS is_new_session
                FROM
                    dwd_user_behavior_di
                WHERE
                    dt = '2024-06-01'
            ) b1
    ) a1
GROUP BY
    user_id
    ,session_id
;
```

### 10.3 考点

- `lag()` 取上一条事件时间
- `unix_timestamp` 时间差
- 累计 `sum() over()` 生成会话 ID

---

## 十一、Cohort 队列留存矩阵

### 11.1 业务场景

按**注册月份** cohort，观察第 0/1/2/… 月的留存率。

### 11.2 完整 SQL

```sql
SELECT
    cohort_month
    ,month_diff
    ,count(DISTINCT user_id) AS retain_uv
    ,max(cohort_uv) AS cohort_uv
    ,count(DISTINCT user_id) / max(cohort_uv) AS retain_rate
FROM
    (
        SELECT
            a1.user_id
            ,a1.cohort_month
            ,months_between(a1.active_month, a1.cohort_month) AS month_diff
            ,b1.cohort_uv
        FROM
            (
                SELECT
                    u1.user_id
                    ,substr(u1.register_date, 1, 7) AS cohort_month
                    ,substr(a2.dt, 1, 7) AS active_month
                FROM
                    dim_user_df u1
                INNER JOIN
                    dwd_user_active_di a2
                ON
                    u1.user_id = a2.user_id
                WHERE
                    u1.register_date >= '2024-01-01'
                    AND a2.dt >= '2024-01-01'
            ) a1
        INNER JOIN
            (
                SELECT
                    substr(register_date, 1, 7) AS cohort_month
                    ,count(DISTINCT user_id) AS cohort_uv
                FROM
                    dim_user_df
                WHERE
                    register_date >= '2024-01-01'
                GROUP BY
                    substr(register_date, 1, 7)
            ) b1
        ON
            a1.cohort_month = b1.cohort_month
    ) t1
GROUP BY
    cohort_month
    ,month_diff
ORDER BY
    cohort_month
    ,month_diff
;
```

### 11.3 考点

- cohort 分析思维
- `months_between` 计算月份差
- 留存矩阵是面试高频综合题

---

## 十二、商品关联分析（简易购物篮）

### 12.1 业务场景

同一订单内共现的商品对，找 Top 关联组合。

### 12.2 完整 SQL

```sql
SELECT
    a1.product_id AS product_a
    ,b1.product_id AS product_b
    ,count(DISTINCT a1.order_id) AS co_order_cnt
FROM
    dwd_trade_order_di a1
INNER JOIN
    dwd_trade_order_di b1
ON
    a1.order_id = b1.order_id
    AND a1.product_id < b1.product_id
WHERE
    a1.dt = '2024-06-01'
    AND b1.dt = '2024-06-01'
    AND a1.order_status = 2
    AND b1.order_status = 2
GROUP BY
    a1.product_id
    ,b1.product_id
ORDER BY
    co_order_cnt DESC
LIMIT 20
;
```

### 12.3 考点

- 自关联 `a.product_id < b.product_id` 避免重复组合
- 大数据量下性能问题，需限制日期/采样

---

## 十三、分位数 & 用户分层

### 13.1 订单金额 P50 / P90 / P99

```sql
SELECT
    percentile_approx(pay_amt, 0.5) AS p50_amt
    ,percentile_approx(pay_amt, 0.9) AS p90_amt
    ,percentile_approx(pay_amt, 0.99) AS p99_amt
FROM
    dwd_trade_order_di
WHERE
    dt = '2024-06-01'
    AND order_status = 2
;
```

### 13.2 按消费金额五等分（高价值用户识别）

```sql
SELECT
    user_id
    ,total_amt
    ,ntile(5) OVER (ORDER BY total_amt DESC) AS value_level
FROM
    (
        SELECT
            user_id
            ,sum(pay_amt) AS total_amt
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            user_id
    ) a1
;
```

### 13.3 考点

- `percentile_approx` 近似分位数（大数据友好）
- `ntile` 分层

---

## 十四、去重取最新（拉链 / 快照）

### 14.1 业务场景

同一用户多条地址记录，取最新一条。

### 14.2 SQL

```sql
SELECT
    user_id
    ,address
    ,update_time
FROM
    (
        SELECT
            user_id
            ,address
            ,update_time
            ,row_number() OVER (
                PARTITION BY user_id
                ORDER BY update_time DESC
            ) AS rn
        FROM
            ods_user_address_di
        WHERE
            dt = '2024-06-01'
    ) a1
WHERE
    a1.rn = 1
;
```

### 14.3 考点

- `row_number()` 去重取最新（Spark 3.x 用子查询 + `where rn = 1`）
- 与 `rank()` 并列时取多条的区别

---

## 十五、大表 UV 优化写法

### 15.1 两阶段去重

```sql
SELECT
    count(1) AS uv
FROM
    (
        SELECT
            user_id
        FROM
            dwd_user_active_di
        WHERE
            dt = '2024-06-01'
        GROUP BY
            user_id
    ) a1
;
```

### 15.2 近似 UV

```sql
SELECT
    approx_count_distinct(user_id) AS approx_uv
FROM
    dwd_user_active_di
WHERE
    dt = '2024-06-01'
;
```

### 15.3 考点

- 精确 vs 近似权衡
- 电商大屏 UV 常用近似，报表用精确

---

## 十六、数据倾斜 Join 改写（电商热点 SKU）

### 16.1 业务场景

订单表 Join 商品维表时，爆款 SKU 导致倾斜。

### 16.2 加盐打散思路（口述 + 伪代码）

```sql
-- Step1: 识别热点 key
-- Step2: 热点 key 加随机后缀 0~N 打散
-- Step3: 维表热点 key 膨胀 N 份
-- Step4: Join 后二次聚合

SELECT
    product_id
    ,sum(pay_amt) AS gmv
FROM
    (
        SELECT
            split(product_id_salt, '_')[0] AS product_id
            ,pay_amt
        FROM
            salted_order_table
    ) a1
GROUP BY
    product_id
;
```

### 16.3 小表 Broadcast

```sql
SELECT /*+ BROADCAST(b1) */
    a1.product_id
    ,b1.category_id
    ,sum(a1.pay_amt) AS gmv
FROM
    dwd_trade_order_di a1
INNER JOIN
    dim_product_df b1
ON
    a1.product_id = b1.product_id
WHERE
    a1.dt = '2024-06-01'
GROUP BY
    a1.product_id
    ,b1.category_id
;
```

---

## 十七、综合实战题（面试压轴）

### 17.1 题目

统计 2024 年 6 月每个渠道：

1. DAU、支付 UV、支付 GMV
2. 支付转化率（支付 UV / DAU）
3. 渠道 GMV 日环比
4. 每渠道 Top3 商品

### 17.2 思路拆解


| 子问题       | 方法                              |
| --------- | ------------------------------- |
| DAU       | 活跃表按渠道 `count distinct user_id` |
| 支付 UV/GMV | 订单表 `order_status=2` 汇总         |
| 转化率       | 指标相除，注意分母为 0                    |
| 日环比       | 先按日汇总 GMV，再 `lag()`             |
| Top3 商品   | 分区 `row_number()`               |


### 17.3 支付转化 + GMV 示例

```sql
SELECT
    nvl(b1.channel, 'unknown') AS channel
    ,count(DISTINCT a1.user_id) AS dau
    ,count(DISTINCT c1.user_id) AS pay_uv
    ,nvl(sum(c1.pay_amt), 0) AS gmv
    ,count(DISTINCT c1.user_id) / count(DISTINCT a1.user_id) AS pay_rate
FROM
    dwd_user_active_di a1
LEFT JOIN
    dim_user_df b1
ON
    a1.user_id = b1.user_id
LEFT JOIN
    (
        SELECT
            user_id
            ,sum(pay_amt) AS pay_amt
        FROM
            dwd_trade_order_di
        WHERE
            dt >= '2024-06-01'
            AND dt <= '2024-06-30'
            AND order_status = 2
        GROUP BY
            user_id
    ) c1
ON
    a1.user_id = c1.user_id
WHERE
    a1.dt >= '2024-06-01'
    AND a1.dt <= '2024-06-30'
GROUP BY
    nvl(b1.channel, 'unknown')
;
```

---

## 附录 A：Hive SQL 重点函数速查


| 分类   | 函数                                                | 电商场景      |
| ---- | ------------------------------------------------- | --------- |
| 聚合   | `sum/count/max/min`                               | GMV、订单量   |
| 去重   | `count(distinct)` / 两阶段 / `approx_count_distinct` | UV        |
| 条件   | `if` / `case when`                                | 漏斗、状态过滤   |
| 空值   | `nvl` / `coalesce` / `nullif`                     | 除零、默认值    |
| 字符串  | `substr/concat/split`                             | 日期截断、解析   |
| 日期   | `date_add/sub/diff`, `months_between`             | 留存、cohort |
| 排序窗口 | `row_number/rank/dense_rank`                      | TopN、去重   |
| 偏移窗口 | `lag/lead`                                        | 同环比       |
| 聚合窗口 | `sum/avg count over`                              | 累计、滑动     |
| 分箱   | `ntile`                                           | RFM、用户分层  |
| 分位   | `percentile_approx`                               | 客单价分布     |
| 集合   | `collect_list/set`                                | 用户行为序列    |
| 类型   | `cast`                                            | 类型转换      |
| Join | `left/inner join`                                 | 维表关联      |
| Hint | `BROADCAST`                                       | 小表 Join   |


---

## 附录 B：面试口述 checklist

- [ ] 指标口径先说清楚（GMV 是否含退款、UV 用哪个 ID）
- [ ] 连续 N 天：`date - row_number` 分组
- [ ] 留存：基准日 UV 做分母，`date_add` 对齐
- [ ] TopN：优先 `row_number()`，说明与 `rank` 区别
- [ ] 漏斗：宽松（日宽表）vs 严格（session 有序）
- [ ] 大表 UV：两阶段去重或近似
- [ ] 倾斜：热点 key 加盐 / broadcast 小表
- [ ] 窗口帧：`ROWS BETWEEN` 累计 vs 滑动

---

*文档适用于 Hive / Spark SQL 电商数仓面试与刷题，表名可按实际项目替换。*