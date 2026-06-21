@echo off
REM Hive AES 解密工具 - 编译脚本
REM 请确保 hive-exec-2.3.9-core.jar 在当前目录

echo ========================================
echo Hive AES 解密工具 - 编译脚本
echo ========================================
echo.

REM 检查 jar 包是否存在
if not exist "hive-exec-2.3.9-core.jar" (
    echo [错误] 找不到 hive-exec-2.3.9-core.jar
    echo 请将 hive-exec-2.3.9-core.jar 复制到当前目录
    echo 当前目录: %CD%
    pause
    exit /b 1
)

REM 检查 Java 源文件是否存在
if not exist "HiveAesDecrypt.java" (
    echo [错误] 找不到 HiveAesDecrypt.java
    pause
    exit /b 1
)

echo [1/2] 正在编译 HiveAesDecrypt.java...
javac -encoding UTF-8 -cp "hive-exec-2.3.9-core.jar" HiveAesDecrypt.java

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] 编译失败!
    echo 请检查:
    echo   1. 是否安装了 JDK
    echo   2. javac 是否在系统 PATH 中
    echo   3. hive-exec-2.3.9-core.jar 是否正确
    pause
    exit /b 1
)

echo [2/2] 编译成功!
echo.
echo ========================================
echo 编译完成! 已生成 HiveAesDecrypt.class
echo ========================================
echo.
echo 使用方法:
echo   批量解密: run_decrypt.bat ^<密钥^> data_jiami.txt [输出文件]
echo   交互模式: run_decrypt.bat ^<密钥^>
echo.
echo 示例:
echo   run_decrypt.bat mykey123 data_jiami.txt result.txt
echo ========================================
echo.
pause

