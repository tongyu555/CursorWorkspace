@echo off
REM Hive AES 解密工具 - 运行脚本
REM 用法: run_decrypt.bat <密钥> [输入文件] [输出文件]

REM 设置字符编码为 UTF-8
chcp 65001 > nul

REM 检查是否已编译
if not exist "HiveAesDecrypt.class" (
    echo [错误] 找不到 HiveAesDecrypt.class
    echo 请先运行 compile_decrypt.bat 编译程序
    pause
    exit /b 1
)

REM 检查 jar 包是否存在
if not exist "hive-exec-2.3.9-core.jar" (
    echo [错误] 找不到 hive-exec-2.3.9-core.jar
    echo 请将 hive-exec-2.3.9-core.jar 复制到当前目录
    pause
    exit /b 1
)

REM 运行程序
java -Dfile.encoding=UTF-8 -cp ".;hive-exec-2.3.9-core.jar" HiveAesDecrypt %*








