#!/bin/bash
# Hive AES 解密工具 - 运行脚本 (Linux/Mac)
# 用法: ./run_decrypt.sh <密钥> [输入文件] [输出文件]

# 检查是否已编译
if [ ! -f "HiveAesDecrypt.class" ]; then
    echo "[错误] 找不到 HiveAesDecrypt.class"
    echo "请先运行 ./compile_decrypt.sh 编译程序"
    exit 1
fi

# 检查 jar 包是否存在
if [ ! -f "hive-exec-2.3.9-core.jar" ]; then
    echo "[错误] 找不到 hive-exec-2.3.9-core.jar"
    echo "请将 hive-exec-2.3.9-core.jar 复制到当前目录"
    exit 1
fi

# 运行程序
java -Dfile.encoding=UTF-8 -cp ".:hive-exec-2.3.9-core.jar" HiveAesDecrypt "$@"

