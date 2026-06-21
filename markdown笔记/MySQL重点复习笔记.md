# MySQL重点复习笔记 - 面试必备

## 📚 目录

- [1. MySQL基础概念](#1-mysql基础概念)
- [2. 索引机制](#2-索引机制)
- [3. 事务ACID](#3-事务acid)
- [4. 锁机制](#4-锁机制)
- [5. 存储引擎](#5-存储引擎)
- [6. 查询优化](#6-查询优化)
- [7. 主从复制](#7-主从复制)
- [8. 分库分表](#8-分库分表)
- [9. 面试高频问题](#9-面试高频问题)

---

## 1. MySQL基础概念

### 1.1 架构层次
```
连接层 (Connection Layer)
  ↓
SQL层 (SQL Layer) - 解析器、优化器、执行器
  ↓  
存储引擎层 (Storage Engine Layer) - InnoDB、MyISAM等
  ↓
文件系统层 (File System Layer)
```

### 1.2 数据类型选择
- **整数类型**: `TINYINT(1字节)` < `SMALLINT(2字节)` < `INT(4字节)` < `BIGINT(8字节)`
- **字符串类型**: `VARCHAR`(变长) vs `CHAR`(定长)
- **时间类型**: `DATETIME`(8字节) vs `TIMESTAMP`(4字节，有时区)
- **JSON类型**: MySQL 5.7+支持原生JSON

### 1.3 字符集和排序规则
```sql
-- 查看字符集
SHOW VARIABLES LIKE 'character%';

-- 设置字符集
ALTER TABLE table_name CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 2. 索引机制 ⭐⭐⭐

### 2.1 索引类型
| 索引类型     | 特点               | 使用场景         |
| ------------ | ------------------ | ---------------- |
| **B+树索引** | 默认索引，有序存储 | 范围查询、排序   |
| **哈希索引** | 等值查询快，无序   | 精确匹配         |
| **全文索引** | 文本搜索           | LIKE '%keyword%' |
| **空间索引** | 地理位置           | GIS应用          |

### 2.2 索引分类
```sql
-- 主键索引 (聚簇索引)
ALTER TABLE users ADD PRIMARY KEY (id);

-- 唯一索引
CREATE UNIQUE INDEX idx_email ON users(email);

-- 普通索引 (二级索引/非聚簇索引)
CREATE INDEX idx_name ON users(name);

-- 联合索引
CREATE INDEX idx_name_age ON users(name, age);

-- 前缀索引
CREATE INDEX idx_email_prefix ON users(email(10));
```

### 2.3 聚簇索引 vs 非聚簇索引
**聚簇索引 (主键索引)**:
- 叶子节点存储完整行数据
- 一个表只能有一个聚簇索引
- 数据页按主键顺序物理存储

**非聚簇索引 (二级索引)**:
- 叶子节点存储主键值
- 需要回表查询完整数据
- 覆盖索引可避免回表

### 2.4 索引优化原则
1. **最左前缀匹配原则**
   ```sql
   -- 索引: (a,b,c)
   ✅ WHERE a=1
   ✅ WHERE a=1 AND b=2  
   ✅ WHERE a=1 AND b=2 AND c=3
   ❌ WHERE b=2 AND c=3
   ```

2. **避免索引失效**
   ```sql
   -- 索引失效情况
   ❌ WHERE name LIKE '%张'        -- 前导模糊匹配
   ❌ WHERE age + 1 = 25           -- 计算字段
   ❌ WHERE UPPER(name) = 'ZHANG'  -- 函数调用
   ❌ WHERE age != 18              -- 不等于
   ❌ WHERE age IS NULL            -- NULL值判断
   ```

3. **覆盖索引**
   ```sql
   -- 创建覆盖索引避免回表
   CREATE INDEX idx_cover ON users(name, age, email);
   SELECT name, age, email FROM users WHERE name = '张三';
   ```

---

## 3. 事务ACID ⭐⭐⭐

### 3.1 ACID特性
- **原子性 (Atomicity)**: 事务不可分割，要么全部成功，要么全部失败
- **一致性 (Consistency)**: 事务执行前后，数据保持一致性约束
- **隔离性 (Isolation)**: 并发事务之间相互隔离
- **持久性 (Durability)**: 事务提交后，修改永久保存

### 3.2 事务隔离级别

| 隔离级别                        | 脏读 | 不可重复读 | 幻读 | 实现方式   |
| ------------------------------- | ---- | ---------- | ---- | ---------- |
| **读未提交** (READ UNCOMMITTED) | ✅    | ✅          | ✅    | 无锁       |
| **读已提交** (READ COMMITTED)   | ❌    | ✅          | ✅    | 读锁       |
| **可重复读** (REPEATABLE READ)  | ❌    | ❌          | ✅    | MVCC+Gap锁 |
| **串行化** (SERIALIZABLE)       | ❌    | ❌          | ❌    | 表锁       |

```sql
-- 查看和设置隔离级别
SELECT @@transaction_isolation;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

### 3.3 MVCC (多版本并发控制)
**核心组件**:
- **隐藏列**: `DB_TRX_ID`(事务ID)、`DB_ROLL_PTR`(回滚指针)
- **Undo Log**: 存储历史版本数据
- **Read View**: 判断版本可见性

**Read View判断逻辑**:
```
if (DB_TRX_ID < min_trx_id) return 可见;
if (DB_TRX_ID > max_trx_id) return 不可见;  
if (DB_TRX_ID in trx_ids) return 不可见;
return 可见;
```

---

## 4. 锁机制 ⭐⭐⭐

### 4.1 锁的分类
**按锁粒度**:
- **表级锁**: 开销小，并发度低
- **页级锁**: 中等开销，中等并发
- **行级锁**: 开销大，并发度高

**按锁模式**:
- **共享锁 (S锁)**: `SELECT ... LOCK IN SHARE MODE`
- **排他锁 (X锁)**: `SELECT ... FOR UPDATE`

**按锁算法**:
- **Record Lock**: 锁定单个行记录
- **Gap Lock**: 锁定间隙，防止幻读
- **Next-Key Lock**: Record Lock + Gap Lock

### 4.2 死锁分析
```sql
-- 查看死锁信息
SHOW ENGINE INNODB STATUS;

-- 死锁示例
-- 事务1: UPDATE t1 SET col=1 WHERE id=1; UPDATE t2 SET col=1 WHERE id=2;
-- 事务2: UPDATE t2 SET col=2 WHERE id=2; UPDATE t1 SET col=2 WHERE id=1;
```

**死锁预防**:
1. 按相同顺序访问资源
2. 缩短事务执行时间
3. 降低事务隔离级别
4. 使用`SELECT ... FOR UPDATE NOWAIT`

---

## 5. 存储引擎 ⭐⭐

### 5.1 InnoDB vs MyISAM

| 特性         | InnoDB     | MyISAM     |
| ------------ | ---------- | ---------- |
| **事务支持** | ✅ 支持ACID | ❌ 不支持   |
| **锁粒度**   | 行级锁     | 表级锁     |
| **外键约束** | ✅ 支持     | ❌ 不支持   |
| **崩溃恢复** | ✅ 自动恢复 | ❌ 手动修复 |
| **MVCC**     | ✅ 支持     | ❌ 不支持   |
| **全文索引** | ✅ 5.6+     | ✅ 支持     |
| **存储结构** | 聚簇索引   | 堆表结构   |

### 5.2 InnoDB架构
```
Buffer Pool (缓冲池)
├── Data Pages (数据页)
├── Index Pages (索引页)  
├── Undo Pages (撤销页)
└── Insert Buffer (插入缓冲)

Log Buffer (日志缓冲)
├── Redo Log (重做日志)
└── Binlog (二进制日志)
```

---

## 6. 查询优化 ⭐⭐⭐

### 6.1 执行计划分析
```sql
EXPLAIN SELECT * FROM users WHERE age > 18;
```

**关键字段**:
- **type**: `system` > `const` > `eq_ref` > `ref` > `range` > `index` > `ALL`
- **key**: 实际使用的索引
- **rows**: 预估扫描行数
- **Extra**: 
  - `Using index` - 覆盖索引
  - `Using filesort` - 文件排序
  - `Using temporary` - 临时表

### 6.2 SQL优化技巧

1. **SELECT优化**
   ```sql
   -- ✅ 指定需要的列
   SELECT id, name FROM users WHERE age > 18;
   
   -- ❌ 避免SELECT *
   SELECT * FROM users WHERE age > 18;
   ```

2. **WHERE优化**
   ```sql
   -- ✅ 利用索引
   SELECT * FROM orders WHERE status = 'paid' AND created_at > '2023-01-01';
   
   -- ❌ 避免函数调用
   SELECT * FROM orders WHERE DATE(created_at) = '2023-01-01';
   ```

3. **JOIN优化**
   ```sql
   -- ✅ 小表驱动大表
   SELECT * FROM small_table s 
   INNER JOIN big_table b ON s.id = b.small_id;
   
   -- ✅ 使用EXISTS替代IN (大数据量)
   SELECT * FROM users u 
   WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
   ```

4. **分页优化**
   ```sql
   -- ❌ 深分页问题
   SELECT * FROM users ORDER BY id LIMIT 1000000, 10;
   
   -- ✅ 游标分页
   SELECT * FROM users WHERE id > 1000000 ORDER BY id LIMIT 10;
   
   -- ✅ 延迟关联
   SELECT u.* FROM users u 
   INNER JOIN (SELECT id FROM users ORDER BY created_at LIMIT 1000000, 10) t 
   ON u.id = t.id;
   ```

### 6.3 慢查询优化
```sql
-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 2;

-- 分析慢查询
mysqldumpslow -s t -t 10 /var/log/mysql/mysql-slow.log
```

---

## 7. 主从复制 ⭐⭐

### 7.1 复制原理
```
Master                    Slave
  ↓                        ↑
Binary Log    →    I/O Thread (接收)
                      ↓
                  Relay Log
                      ↓  
                 SQL Thread (重放)
```

### 7.2 复制模式
- **异步复制**: 默认模式，性能好但可能丢数据
- **半同步复制**: 至少一个从库确认才返回
- **并行复制**: MySQL 5.6+ 支持多线程复制

### 7.3 主从延迟解决
1. **硬件优化**: SSD、增加内存
2. **参数优化**: 
   ```sql
   # 并行复制线程数
   slave_parallel_workers = 4
   # 并行复制模式  
   slave_parallel_type = LOGICAL_CLOCK
   ```
3. **架构优化**: 读写分离、分库分表

---

## 8. 分库分表 ⭐⭐

### 8.1 垂直拆分 vs 水平拆分

**垂直拆分**:
- 按业务模块拆分表
- 按字段拆分表 (冷热分离)

**水平拆分**:
- 按范围分片: `user_2023_01`, `user_2023_02`
- 按哈希分片: `user_0`, `user_1`, `user_2`

### 8.2 分片策略
```sql
-- 范围分片
SELECT * FROM user_2023_01 WHERE id BETWEEN 1 AND 100000;

-- 哈希分片  
-- 路由逻辑: table_name = "user_" + (user_id % 4)
SELECT * FROM user_1 WHERE id = 12345;
```

### 8.3 分库分表问题
- **跨库JOIN**: 应用层解决或冗余数据
- **分布式事务**: 两阶段提交、最终一致性
- **全局ID**: 雪花算法、UUID、数据库序列

---

## 9. 面试高频问题 ⭐⭐⭐

### Q1: InnoDB的B+树索引为什么要用B+树而不用B树？
**答案**:
1. **B+树非叶子节点不存储数据**，可以存储更多索引，减少IO
2. **叶子节点通过指针连接**，范围查询效率高
3. **所有数据在叶子节点**，查询性能稳定
4. **更适合磁盘存储**，减少随机IO

### Q2: MySQL如何解决幻读问题？
**答案**:
1. **MVCC** (多版本并发控制) - 快照读
2. **Next-Key Lock** (Record Lock + Gap Lock) - 当前读
3. **可重复读隔离级别**下，通过锁定记录和间隙防止新增数据

### Q3: 什么情况下索引会失效？
**答案**:
1. 违反最左前缀匹配原则
2. 使用函数或表达式计算
3. 使用`!=`、`<>`、`NOT IN`
4. `LIKE`以通配符开头
5. 字符串不加引号导致隐式转换
6. `OR`连接的条件中有未建索引的列

### Q4: 如何优化千万级数据的分页查询？
**答案**:
1. **游标分页**: 使用上次查询的最大ID作为起点
2. **延迟关联**: 先分页查ID，再关联查完整数据  
3. **搜索引擎**: 使用ES等搜索引擎
4. **缓存**: 缓存热点页数据

### Q5: MySQL主从延迟如何解决？
**答案**:
1. **硬件升级**: 使用SSD，增加内存
2. **并行复制**: 开启多线程复制
3. **网络优化**: 使用更快的网络连接
4. **读写分离**: 重要查询走主库
5. **业务优化**: 异步处理，最终一致性

### Q6: 如何设计一个全局ID生成器？
**答案**:
1. **雪花算法**: 时间戳+机器ID+序列号 (64位)
2. **数据库序列**: 单独的序列表
3. **Redis自增**: 利用Redis的INCR命令
4. **UUID**: 全球唯一，但无序且较长

---

## 🎯 面试准备建议

### 必须掌握的核心知识
1. **索引原理和优化** - 必考
2. **事务和隔离级别** - 必考  
3. **锁机制和死锁** - 高频
4. **主从复制原理** - 高频
5. **SQL优化技巧** - 必考

### 实际项目经验准备
- 分享过SQL优化的具体案例
- 解决过慢查询的经历
- 处理过数据库高并发的方案
- 设计过分库分表的架构

### 深入学习资源
- 《MySQL技术内幕：InnoDB存储引擎》
- 《高性能MySQL》
- MySQL官方文档
- 极客时间《MySQL实战45讲》

---

## ⚡ 速记口诀

**索引优化**: 左前缀，避函数，范围后，覆盖好  
**事务ACID**: 原一隔持 (原子性、一致性、隔离性、持久性)  
**隔离级别**: 读未读已可重复串行化  
**锁的类型**: 表页行，共排意向  
**B+树优势**: 范围好，IO少，性能稳

记住这份笔记，MySQL面试无忧！ 🚀
