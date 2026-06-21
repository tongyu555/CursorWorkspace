# Hive AES Java解密工具使用说明

## 📋 文件清单

- **HiveAesDecrypt.java** - Java解密主程序源码
- **compile_decrypt.bat** - Windows编译脚本
- **run_decrypt.bat** - Windows运行脚本
- **compile_decrypt.sh** - Linux/Mac编译脚本
- **run_decrypt.sh** - Linux/Mac运行脚本
- **data_jiami.txt** - 加密数据文件（示例）

## 🚀 快速开始

### 前置要求

1. ✅ 已安装 **JDK 8** 或更高版本
2. ✅ 已有 **hive-exec-2.3.9-core.jar** 文件
3. ✅ `javac` 和 `java` 命令在系统 PATH 中

检查Java环境：
```bash
java -version
javac -version
```

### Windows 系统

#### 步骤1: 准备jar包
将 `hive-exec-2.3.9-core.jar` 复制到当前目录（`E:\cursor_test`）

#### 步骤2: 编译程序
```cmd
compile_decrypt.bat
```

#### 步骤3: 运行解密

**方式1: 批量解密 data_jiami.txt 文件**
```cmd
run_decrypt.bat <你的密钥> data_jiami.txt
```

**方式2: 批量解密并保存结果**
```cmd
run_decrypt.bat <你的密钥> data_jiami.txt result.txt
```

**方式3: 交互式模式（手动输入密文）**
```cmd
run_decrypt.bat <你的密钥>
```

### Linux/Mac 系统

#### 步骤1: 准备jar包
```bash
# 将 hive-exec-2.3.9-core.jar 复制到当前目录
cp /path/to/hive-exec-2.3.9-core.jar ./
```

#### 步骤2: 编译程序
```bash
chmod +x compile_decrypt.sh
./compile_decrypt.sh
```

#### 步骤3: 运行解密

**方式1: 批量解密 data_jiami.txt 文件**
```bash
./run_decrypt.sh <你的密钥> data_jiami.txt
```

**方式2: 批量解密并保存结果**
```bash
./run_decrypt.sh <你的密钥> data_jiami.txt result.txt
```

**方式3: 交互式模式**
```bash
./run_decrypt.sh <你的密钥>
```

## 💡 使用示例

### 示例1: 解密 data_jiami.txt

假设你的密钥是 `mySecretKey123`：

```cmd
run_decrypt.bat mySecretKey123 data_jiami.txt
```

输出示例：
```
========================================
Hive AES 批量解密工具
========================================
输入文件: data_jiami.txt
密钥: mySecretKey123
========================================

第 1 行:
  密文: qXxnUp3Pg3zV1cr/ralBog==
  明文: 用户数据1

第 2 行:
  密文: lNVK8rLo9O2kSgdC7XyJYQ==
  明文: 用户数据2

...

========================================
解密完成!
成功: 10 条
失败: 0 条
========================================
```

### 示例2: 保存解密结果到文件

```cmd
run_decrypt.bat mySecretKey123 data_jiami.txt decrypted_result.txt
```

生成的 `decrypted_result.txt` 文件内容：
```
用户数据1
用户数据2
用户数据3
...
```

### 示例3: 交互式解密

```cmd
run_decrypt.bat mySecretKey123
```

交互过程：
```
========================================
Hive AES 交互式解密工具
========================================
密钥: mySecretKey123
请输入Base64编码的密文 (输入 'exit' 退出):
========================================

密文 > qXxnUp3Pg3zV1cr/ralBog==
明文 > 用户数据1

密文 > lNVK8rLo9O2kSgdC7XyJYQ==
明文 > 用户数据2

密文 > exit
退出程序
```

## 📝 输入文件格式

`data_jiami.txt` 文件格式很简单，每行一个Base64编码的密文：

```
qXxnUp3Pg3zV1cr/ralBog==
lNVK8rLo9O2kSgdC7XyJYQ==
ywDPFxAcJmSrmtpK57yLPQ==
hFWUpExHVz3hbX8kJ4JnMA==
```

**注意事项**：
- 每行一个密文
- 密文必须是Base64编码
- 空行会被自动跳过
- 支持UTF-8编码

## 🔧 高级用法

### 手动编译和运行

如果不使用批处理脚本，可以手动执行：

**Windows:**
```cmd
# 编译
javac -encoding UTF-8 -cp "hive-exec-2.3.9-core.jar" HiveAesDecrypt.java

# 运行
java -Dfile.encoding=UTF-8 -cp ".;hive-exec-2.3.9-core.jar" HiveAesDecrypt <密钥> [参数...]
```

**Linux/Mac:**
```bash
# 编译
javac -encoding UTF-8 -cp "hive-exec-2.3.9-core.jar" HiveAesDecrypt.java

# 运行
java -Dfile.encoding=UTF-8 -cp ".:hive-exec-2.3.9-core.jar" HiveAesDecrypt <密钥> [参数...]
```

### 在Java代码中使用

```java
// 创建解密器实例
HiveAesDecrypt decryptor = new HiveAesDecrypt("mySecretKey123");

// 解密单条数据
String ciphertext = "qXxnUp3Pg3zV1cr/ralBog==";
String plaintext = decryptor.decrypt(ciphertext);
System.out.println("明文: " + plaintext);

// 批量解密文件
decryptor.decryptFromFile("data_jiami.txt", "result.txt");
```

### 在Hive中验证

在Hive中使用相同的密钥和数据进行验证：

```sql
-- 创建临时函数
CREATE TEMPORARY FUNCTION aes_decrypt AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesDecrypt';

-- 验证解密结果
SELECT aes_decrypt('qXxnUp3Pg3zV1cr/ralBog==', 'mySecretKey123');

-- 批量解密表数据
SELECT 
    id,
    aes_decrypt(encrypted_column, 'mySecretKey123') as decrypted_value
FROM your_table;
```

## ⚠️ 常见问题

### 1. 编译错误：找不到 GenericUDFAesDecrypt

**原因**：hive-exec-2.3.9-core.jar 不在正确位置或不在classpath中

**解决方法**：
- 确认jar包在当前目录
- 检查jar包文件名是否完全一致
- 使用完整路径：`javac -cp "C:\path\to\hive-exec-2.3.9-core.jar" HiveAesDecrypt.java`

### 2. 运行错误：ClassNotFoundException

**原因**：运行时没有指定正确的classpath

**解决方法**：
```cmd
# Windows - 注意使用分号
java -cp ".;hive-exec-2.3.9-core.jar" HiveAesDecrypt <参数>

# Linux/Mac - 注意使用冒号
java -cp ".:hive-exec-2.3.9-core.jar" HiveAesDecrypt <参数>
```

### 3. 解密失败：返回null或异常

**可能原因**：
- ❌ 密钥不正确
- ❌ 密文格式不对（不是Base64）
- ❌ 密文已损坏
- ❌ 加密时使用的不是Hive的UDF

**解决方法**：
- 确认密钥与加密时完全一致
- 检查密文是否完整（没有被截断）
- 在Hive中测试相同的密钥和密文

### 4. 中文乱码

**原因**：字符编码设置不正确

**解决方法**：
```cmd
# Windows
chcp 65001
run_decrypt.bat <参数>

# 或在运行时指定编码
java -Dfile.encoding=UTF-8 -cp ".;hive-exec-2.3.9-core.jar" HiveAesDecrypt <参数>
```

### 5. jar包版本不匹配

如果你的jar包不是 `hive-exec-2.3.9-core.jar`：

**修改编译命令**：
```cmd
# 假设你的jar包是 hive-exec-3.1.2.jar
javac -cp "hive-exec-3.1.2.jar" HiveAesDecrypt.java
java -cp ".;hive-exec-3.1.2.jar" HiveAesDecrypt <参数>
```

**或修改批处理脚本**中的jar包名称。

## 🔐 与Hive UDF的兼容性

本Java程序直接使用Hive的 `GenericUDFAesDecrypt` 类，因此：

✅ **100%兼容** Hive的加密结果  
✅ **相同的密钥处理逻辑**  
✅ **相同的AES算法实现**  
✅ **相同的Base64编解码**  

### Hive中的加密

```sql
-- 在Hive中加密
CREATE TEMPORARY FUNCTION aes_encrypt AS 'org.apache.hadoop.hive.ql.udf.generic.GenericUDFAesEncrypt';

SELECT aes_encrypt('敏感数据', 'mykey123');
-- 结果: qXxnUp3Pg3zV1cr/ralBog==
```

### Java程序解密

```cmd
# 使用本程序解密
run_decrypt.bat mykey123

密文 > qXxnUp3Pg3zV1cr/ralBog==
明文 > 敏感数据
```

## 📊 性能说明

- **单条解密**: 毫秒级
- **批量解密**: 取决于数据量，通常每秒可处理数千条
- **内存占用**: 很小，主要由Hive jar包决定

### 大文件处理建议

如果要处理百万级数据：

1. **分批处理**: 将大文件拆分成多个小文件
2. **直接在Hive中解密**: 利用Hive的分布式能力
3. **调整JVM内存**: `java -Xmx2g -cp ...`

## 🛠️ 故障排查清单

遇到问题时，按以下顺序检查：

- [ ] JDK已正确安装（`java -version`）
- [ ] hive-exec-2.3.9-core.jar在当前目录
- [ ] 已成功编译（存在HiveAesDecrypt.class文件）
- [ ] 密钥正确（与加密时使用的密钥一致）
- [ ] 密文格式正确（Base64编码）
- [ ] 输入文件编码正确（UTF-8）
- [ ] 字符编码设置正确（-Dfile.encoding=UTF-8）

## 📞 技术支持

如果以上方法都无法解决问题，请提供：

1. 完整的错误信息
2. 使用的命令
3. Java版本（`java -version`）
4. jar包版本
5. 密文示例（可脱敏）

## 📝 附录：完整命令参考

### Windows

```cmd
# 编译
compile_decrypt.bat

# 批量解密（显示在控制台）
run_decrypt.bat <密钥> data_jiami.txt

# 批量解密（保存到文件）
run_decrypt.bat <密钥> data_jiami.txt result.txt

# 交互模式
run_decrypt.bat <密钥>

# 查看帮助
run_decrypt.bat
```

### Linux/Mac

```bash
# 编译
./compile_decrypt.sh

# 批量解密（显示在终端）
./run_decrypt.sh <密钥> data_jiami.txt

# 批量解密（保存到文件）
./run_decrypt.sh <密钥> data_jiami.txt result.txt

# 交互模式
./run_decrypt.sh <密钥>

# 查看帮助
./run_decrypt.sh
```

---

**版本**: 1.0  
**更新日期**: 2025-11-13  
**兼容**: Hive 2.3.9+








