# HBase建表语句导出工具使用说明

## 概述

本工具提供了两个版本的Shell脚本,用于从HBase中导出指定命名空间下所有表的建表语句。

## 脚本文件

### 1. get_hbase_ddl.sh (基础版本)
- 功能完整的基础版本
- 使用Shell命令解析HBase输出
- 适合大多数场景

### 2. get_hbase_ddl_v2.sh (优化版本)
- 使用Python辅助解析,更准确
- 支持参数自定义
- 推荐使用

## 使用方法

### 基础版本使用

```bash
# 1. 添加执行权限
chmod +x get_hbase_ddl.sh

# 2. 执行脚本(默认获取nifi_cache命名空间)
./get_hbase_ddl.sh
```

### 优化版本使用

```bash
# 1. 添加执行权限
chmod +x get_hbase_ddl_v2.sh

# 2. 使用默认参数(nifi_cache命名空间)
./get_hbase_ddl_v2.sh

# 3. 指定命名空间
./get_hbase_ddl_v2.sh your_namespace

# 4. 指定命名空间和输出文件
./get_hbase_ddl_v2.sh nifi_cache output.rb
```

## 前置条件

### 必须条件
1. **HBase环境**: 确保HBase已安装并配置好环境变量
2. **HBase Shell**: 确保可以执行`hbase shell`命令
3. **权限**: 需要有读取HBase表的权限

### 可选条件(优化版本)
- **Python3**: 优化版本需要Python3支持
- 如果没有Python3,请使用基础版本

## 输出文件

### 文件命名
- 默认: `hbase_ddl_YYYYMMDD_HHMMSS.rb`
- 自定义: 通过参数指定

### 文件格式
生成的文件为HBase Shell可执行的Ruby脚本格式,例如:

```ruby
create 'nifi_cache:cache_4gdpi',{NAME => 'f', BLOOMFILTER => 'ROW', VERSIONS => '1', IN_MEMORY => 'true', KEEP_DELETED_CELLS => 'FALSE', DATA_BLOCK_ENCODING => 'NONE', TTL => '2592000', COMPRESSION => 'NONE', MIN_VERSIONS => '1', BLOCKCACHE => 'true', BLOCKSIZE => '65536', REPLICATION_SCOPE => '0'}
```

## 使用生成的建表语句

### 方法1: 直接在HBase Shell中执行

```bash
hbase shell < hbase_ddl_20250101_120000.rb
```

### 方法2: 在HBase Shell中逐条执行

```bash
hbase shell
hbase> create 'nifi_cache:cache_4gdpi',{NAME => 'f', ...}
```

### 方法3: 作为备份保存

将生成的文件保存为HBase表结构备份,用于:
- 文档记录
- 灾难恢复
- 环境迁移

## 常见问题

### Q1: 提示"未找到hbase命令"
**解决方法**: 
```bash
# 配置HBase环境变量
export HBASE_HOME=/path/to/hbase
export PATH=$PATH:$HBASE_HOME/bin
```

### Q2: 无法获取表列表
**可能原因**:
1. 命名空间不存在
2. 没有权限访问该命名空间
3. HBase服务未启动

**检查方法**:
```bash
# 在HBase Shell中检查
hbase shell
hbase> list_namespace
hbase> list_namespace_tables 'nifi_cache'
```

### Q3: 生成的语句格式不正确
**解决方法**: 
- 使用优化版本 `get_hbase_ddl_v2.sh`
- 检查Python3是否安装

### Q4: 部分表无法导出
**可能原因**:
- 表结构特殊(包含多个列族)
- 权限不足

**解决方法**:
- 手动检查该表: `describe 'namespace:table'`
- 使用HBase管理员权限

## 脚本特点

### 优点
✓ 自动化批量导出  
✓ 保留完整的表配置信息  
✓ 生成可直接执行的脚本  
✓ 支持多列族表  
✓ 带进度提示  

### 限制
✗ 不包含表数据,仅包含表结构  
✗ 不包含表的分区(Region)信息  
✗ 不包含协处理器配置  

## 高级用法

### 导出多个命名空间

```bash
#!/bin/bash
namespaces=("nifi_cache" "default" "test")
for ns in "${namespaces[@]}"
do
    ./get_hbase_ddl_v2.sh ${ns} "ddl_${ns}.rb"
done
```

### 定时备份

添加到crontab定时任务:
```bash
# 每天凌晨2点备份
0 2 * * * /path/to/get_hbase_ddl_v2.sh nifi_cache /backup/hbase_ddl_$(date +\%Y\%m\%d).rb
```

### 比对表结构变化

```bash
# 导出当前结构
./get_hbase_ddl_v2.sh nifi_cache current.rb

# 与历史备份比较
diff backup_20250101.rb current.rb
```

## 技术说明

### 脚本工作原理

1. **获取表列表**: 使用`list_namespace_tables`命令
2. **逐表描述**: 使用`describe`命令获取表详细配置
3. **解析配置**: 提取列族及各项参数
4. **生成语句**: 构造HBase create命令格式
5. **输出文件**: 保存为.rb格式的可执行脚本

### 主要配置参数说明

| 参数 | 说明 | 示例值 |
|------|------|--------|
| NAME | 列族名称 | 'f' |
| BLOOMFILTER | 布隆过滤器类型 | 'ROW' |
| VERSIONS | 保留版本数 | '1' |
| IN_MEMORY | 是否加载到内存 | 'true' |
| TTL | 数据过期时间(秒) | '2592000' (30天) |
| COMPRESSION | 压缩算法 | 'NONE' |
| BLOCKSIZE | 块大小 | '65536' |

## 更新日志

- **v2.0** (2025-10-29): 添加Python解析支持,提高准确性
- **v1.0** (2025-10-29): 初始版本,支持基础导出功能

## 联系支持

如有问题或建议,请通过以下方式联系:
- 提交Issue
- 发送邮件
- 查看HBase官方文档


