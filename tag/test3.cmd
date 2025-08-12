@echo off 

REM 检查管理员权限
net session >nul 2>&1
if %errorlevel% == 0 (
    echo 已具有管理员权限，继续执行...
    goto :execute
)

echo 正在尝试获取管理员权限...

REM 尝试通过任务计划程序自动获取权限
schtasks /create /tn "TagUIAuto" /tr "cmd /c \"cd /d \"%~dp0\" && set JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8 -Duser.language=zh -Duser.country=CN && \"C:\tagui\src\tagui\" \"test3.tag\" -edge && pause\"" /sc once /st 23:59 /rl highest /f >nul 2>&1

if %errorlevel__ == 0 (
    echo 通过任务计划程序获取权限...
    schtasks /run /tn "TagUIAuto" >nul 2>&1
    timeout /t 2 /nobreak >nul
    schtasks /delete /tn "TagUIAuto" /f >nul 2>&1
    echo 任务已启动
    exit /b 0
)

echo 自动获取权限失败，使用普通权限执行...

:execute
REM 设置Java环境变量解决字符编码问题，但保持UTF-8
set JAVA_TOOL_OPTIONS=-Dfile.encoding=UTF-8 -Duser.language=zh -Duser.country=CN

REM 使用相对路径避免中文路径问题
cd /d "%~dp0"
"C:\tagui\src\tagui" "test3.tag" -edge         
