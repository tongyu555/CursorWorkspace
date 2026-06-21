# IDEA 直接运行 - 快速使用指南

## 🚀 三步搞定

### 第1步：添加jar包依赖

在IDEA中：

1. 右键点击项目 → `Open Module Settings` (或按 `F4`)
2. 选择 `Libraries` → 点击 `+` → `Java`
3. 选择你的 `hive-exec-2.3.9-core.jar` 文件
4. 点击 `OK`

**或者更简单的方法：**
- 直接将 `hive-exec-2.3.9-core.jar` 拖到项目中
- 右键 → `Add as Library`

---

### 第2步：修改密钥

打开 `SimpleHiveDecrypt.java`，修改第20行的密钥：

```java
// 修改这里的密钥为你的实际密钥
private static final String SECRET_KEY = "你的密钥";
```

**可选：** 如果 `data_jiami.txt` 不在 `E:\cursor_test\` 目录，也修改第23行的文件路径。

---

### 第3步：运行

在 `SimpleHiveDecrypt.java` 文件中：
- 右键点击代码 → `Run 'SimpleHiveDecrypt.main()'`
- 或者点击行号旁边的绿色运行按钮 ▶️

完成！查看控制台输出的解密结果。

---

## 📋 输出示例

```
========================================
Hive AES 解密工具
========================================
密钥: mykey123
文件: E:\cursor_test\data_jiami.txt
========================================

第 1 行:
  密文: qXxnUp3Pg3zV1cr/ralBog==
  明文: 解密结果1

第 2 行:
  密文: lNVK8rLo9O2kSgdC7XyJYQ==
  明文: 解密结果2

...

========================================
解密完成! 成功: 10/10 条
========================================
```

---

## ❓ 常见问题

### 问题1: 找不到类 GenericUDFAesDecrypt

**原因**: 没有添加jar包依赖

**解决**: 按第1步添加 `hive-exec-2.3.9-core.jar` 到项目依赖

---

### 问题2: 找不到文件

**错误信息**: `FileNotFoundException`

**解决**: 修改代码中的 `INPUT_FILE` 路径为正确的绝对路径

---

### 问题3: 解密失败

**输出**: `[解密失败 - 密钥可能不正确]`

**解决**: 检查 `SECRET_KEY` 是否与加密时使用的密钥完全一致

---

## 💡 小技巧

### 技巧1: 测试单个密文

在main方法中添加：

```java
public static void main(String[] args) {
    try {
        SimpleHiveDecrypt decryptor = new SimpleHiveDecrypt();
        
        // 直接测试单个密文
        String result = decryptor.decrypt("qXxnUp3Pg3zV1cr/ralBog==", "mykey123");
        System.out.println("解密结果: " + result);
        
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

### 技巧2: 测试多个密钥

如果不确定密钥，可以尝试多个：

```java
String[] possibleKeys = {"key1", "key2", "key3"};
String ciphertext = "qXxnUp3Pg3zV1cr/ralBog==";

for (String key : possibleKeys) {
    String result = decryptor.decrypt(ciphertext, key);
    System.out.println("密钥 [" + key + "] 结果: " + result);
}
```

### 技巧3: 保存结果到文件

```java
import java.io.FileWriter;
import java.io.BufferedWriter;

// 在main方法中
BufferedWriter writer = new BufferedWriter(new FileWriter("result.txt"));
writer.write(plaintext);
writer.newLine();
writer.close();
```

---

## 📝 完整的测试代码示例

如果你想快速测试，可以把main方法改成这样：

```java
public static void main(String[] args) {
    String[] testData = {
        "qXxnUp3Pg3zV1cr/ralBog==",
        "lNVK8rLo9O2kSgdC7XyJYQ==",
        "ywDPFxAcJmSrmtpK57yLPQ=="
    };
    
    String key = "mykey123";  // 你的密钥
    
    try {
        SimpleHiveDecrypt decryptor = new SimpleHiveDecrypt();
        
        for (int i = 0; i < testData.length; i++) {
            String result = decryptor.decrypt(testData[i], key);
            System.out.println((i+1) + ". " + result);
        }
        
    } catch (Exception e) {
        e.printStackTrace();
    }
}
```

---

**就这么简单！不需要命令行，不需要编译脚本，在IDEA中直接运行即可。**







