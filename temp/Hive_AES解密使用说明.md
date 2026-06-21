# Hive AES 解密工具使用说明

## 概述

这个Python脚本用于解密使用Hive的`aes_encrypt`函数加密的数据。支持Hive 2.3.9版本的`GenericUDFAesEncrypt`实现。

## 安装依赖

```bash
pip install -r hive_aes_requirements.txt
```

或者直接安装:

```bash
pip install cryptography
```

## Hive中的加密示例

### 1. ECB模式加密(默认)

```sql
-- 创建临时函数
CREATE TEMPORARY FUNCTION aes_encrypt AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesEncrypt';
CREATE TEMPORARY FUNCTION aes_decrypt AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesDecrypt';

-- 加密数据
SELECT aes_encrypt('敏感数据', 'mySecretKey123');
-- 返回Base64编码的密文

-- 解密数据
SELECT aes_decrypt(encrypted_column, 'mySecretKey123') FROM table_name;
```

### 2. CBC模式加密

```sql
-- 使用CBC模式(需要提供IV)
SELECT aes_encrypt('敏感数据', 'mySecretKey123', 'CBC', 'myInitVector16b');
```

## Python脚本使用方法

### 方法1: 交互式模式(推荐)

直接运行脚本,按照提示输入:

```bash
python hive_aes_decrypt.py
```

交互式步骤:
1. 选择加密模式(ECB/CBC)
2. 选择密钥长度(128/192/256位)
3. 输入密钥
4. 如果是CBC模式,输入IV
5. 选择单条或批量解密
6. 输入密文,查看解密结果

### 方法2: 在代码中调用

```python
from hive_aes_decrypt import aes_decrypt_ecb, aes_decrypt_cbc, batch_decrypt

# ECB模式解密(最常用)
key = "mySecretKey123"
ciphertext = "YourBase64EncodedCiphertext"
plaintext = aes_decrypt_ecb(ciphertext, key)
print(f"解密结果: {plaintext}")

# CBC模式解密
iv = "myInitVector16b"
plaintext_cbc = aes_decrypt_cbc(ciphertext, key, iv)
print(f"解密结果: {plaintext_cbc}")

# 批量解密
ciphertext_list = [
    "ciphertext1",
    "ciphertext2",
    "ciphertext3"
]
results = batch_decrypt(ciphertext_list, key, mode='ECB')
for idx, result in enumerate(results, 1):
    print(f"{idx}. {result}")
```

## 密钥处理说明

### Hive的密钥处理规则

1. **密钥长度不足时**: 使用SHA-256哈希后截取所需长度
2. **密钥长度过长时**: 直接截取所需长度
3. **支持的密钥长度**:
   - 128位(16字节) - 默认,推荐
   - 192位(24字节)
   - 256位(32字节)

### 密钥示例

```python
# 示例1: 短密钥(会被SHA-256哈希处理)
key = "123456"

# 示例2: 标准长度密钥(16字节 = 128位)
key = "1234567890123456"

# 示例3: 长密钥(会被截取)
key = "this_is_a_very_long_key_that_will_be_truncated"
```

## 常见问题

### 1. 解密失败 - "ValueError: Unable to unpad data"

**原因**: 
- 密钥不正确
- 加密模式不匹配(ECB vs CBC)
- 密文已损坏或格式不正确

**解决方法**:
- 确认使用的密钥与加密时完全一致
- 确认加密模式(ECB或CBC)
- 检查密文是否完整

### 2. Base64解码错误

**原因**: 密文不是有效的Base64编码

**解决方法**:
- 检查密文是否完整复制
- 确认密文没有多余的空格或换行符

### 3. UTF-8解码失败

**原因**: 解密结果不是有效的UTF-8文本

**解决方法**:
- 确认原始数据确实是文本数据
- 检查密钥和加密参数是否正确

## 与Hive UDF的兼容性

本脚本严格遵循Hive 2.3.9的`GenericUDFAesEncrypt`/`GenericUDFAesDecrypt`实现:

| 特性 | Hive实现 | Python脚本 |
|------|---------|-----------|
| 加密算法 | AES | ✓ AES |
| 默认模式 | ECB | ✓ ECB |
| 填充方式 | PKCS5Padding | ✓ PKCS7 (兼容) |
| 输出编码 | Base64 | ✓ Base64 |
| 密钥处理 | SHA-256截取 | ✓ SHA-256截取 |
| 支持模式 | ECB, CBC | ✓ ECB, CBC |

## 性能建议

### 批量解密大量数据

如果需要解密大量数据,建议:

1. **使用批量解密函数**:
```python
results = batch_decrypt(ciphertext_list, key, mode='ECB')
```

2. **或者直接在Hive中解密**:
```sql
SELECT 
    id,
    aes_decrypt(encrypted_column, 'mySecretKey123') as decrypted_data
FROM table_name;
```

3. **使用Hive导出时解密**:
```sql
INSERT OVERWRITE LOCAL DIRECTORY '/path/to/output'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT 
    id,
    aes_decrypt(encrypted_column, 'mySecretKey123') as decrypted_data
FROM table_name;
```

## 安全提示

⚠️ **重要安全建议**:

1. **不要在代码中硬编码密钥** - 使用环境变量或配置文件
2. **保护密钥文件** - 设置适当的文件权限
3. **使用强密钥** - 至少16个随机字符
4. **定期轮换密钥** - 建议定期更换加密密钥
5. **ECB模式安全性** - ECB模式安全性较低,生产环境建议使用CBC或更安全的模式

## 环境变量配置示例

```python
import os
from hive_aes_decrypt import aes_decrypt_ecb

# 从环境变量读取密钥
key = os.getenv('HIVE_AES_KEY', 'default_key')
ciphertext = "YourCiphertext"

plaintext = aes_decrypt_ecb(ciphertext, key)
```

在命令行设置环境变量:

```bash
# Linux/Mac
export HIVE_AES_KEY="mySecretKey123"
python your_script.py

# Windows
set HIVE_AES_KEY=mySecretKey123
python your_script.py
```

## 完整示例: 从Hive导出并解密

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从CSV文件批量解密Hive加密数据"""

import csv
from hive_aes_decrypt import aes_decrypt_ecb

# 配置
KEY = "mySecretKey123"
INPUT_FILE = "encrypted_data.csv"
OUTPUT_FILE = "decrypted_data.csv"

# 读取加密数据
with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    
    # 准备输出
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as outfile:
        fieldnames = reader.fieldnames + ['decrypted_column']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # 逐行解密
        for row in reader:
            encrypted_value = row['encrypted_column']
            decrypted_value = aes_decrypt_ecb(encrypted_value, KEY)
            
            row['decrypted_column'] = decrypted_value
            writer.writerow(row)

print(f"解密完成! 结果已保存到: {OUTPUT_FILE}")
```

## 技术细节

### AES加密参数

- **算法**: AES (Advanced Encryption Standard)
- **密钥长度**: 128/192/256位
- **分组大小**: 128位(16字节)
- **填充方式**: PKCS5/PKCS7
- **模式**: ECB(默认) 或 CBC

### Hive UDF源码参考

Hive的AES加密实现位于:
```
org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesEncrypt
org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesDecrypt
```

## 联系与支持

如有问题或建议,请联系开发团队。








