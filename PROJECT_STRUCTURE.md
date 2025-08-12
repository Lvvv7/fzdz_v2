# 项目结构说明

## 目录结构

```
test/
├── auto_run.py                    # 主程序：TagUI自动运行服务器
├── start_web_system.bat          # 启动脚本
├── README.md                      # 项目说明
├── PROJECT_STRUCTURE.md          # 项目结构说明（本文件）
├── system_flowchart.md           # 系统流程图
├── 火炬logo.png                   # 项目图标
│
├── frontend/                      # 前端文件
│   └── index.html                # Web界面
│
├── tag/                          # TagUI脚本
│   ├── test3.tag                 # TagUI自动化脚本
│   └── test3.cmd                 # 备用命令脚本
│
├── print/                        # 文件处理模块
│   ├── print_test.py             # ZIP文件解压脚本
│   ├── test_file_movement.py     # 文件移动测试
│   └── extracted_files/          # 解压文件存放目录
│
├── zip/                          # ZIP文件存放目录
│   └── (下载的ZIP文件)
│
├── extracted_files/              # 全局解压文件目录
│
├── backed/                       # 备份文件
│   └── auto_run.py               # auto_run.py的备份版本
│
├── __pycache__/                  # Python缓存文件
│
└── 文档目录/
    ├── EXECUTION_FLOW_IMPROVEMENT.md      # 执行流程改进说明
    ├── EXTRACT_NAMING_GUIDE.md           # 解压命名指南
    ├── FILE_CLEANUP.md                   # 文件清理说明
    ├── FILE_MANAGEMENT_GUIDE.md          # 文件管理指南
    ├── PROCESS_MONITORING_GUIDE.md       # 进程监控指南
    └── TAGUI_PROCESS_MONITORING_FIX.md   # TagUI进程监控修复说明
```

## 文件功能说明

### 核心文件

- **auto_run.py**: 主程序，包含HTTP服务器、TagUI执行器、文件管理等功能
- **start_web_system.bat**: 一键启动脚本
- **frontend/index.html**: Web用户界面

### TagUI脚本

- **tag/test3.tag**: 主要的TagUI自动化脚本，执行证照下载任务
- **tag/test3.cmd**: 备用的命令行脚本

### 文件处理

- **print/print_test.py**: ZIP文件解压工具，支持中文文件名编码修复
- **print/test_file_movement.py**: 文件移动测试工具

### 目录结构

- **zip/**: 存放从下载目录移动过来的ZIP文件
- **extracted_files/**: 存放解压后的文件
- **print/extracted_files/**: print模块的解压目录
- **backed/**: 备份文件目录

## 工作流程

1. 用户通过Web界面触发TagUI脚本执行
2. TagUI脚本在Edge浏览器中执行自动化任务
3. 下载的文件自动移动到zip目录
4. ZIP文件自动解压到extracted_files目录
5. 原ZIP文件被清理删除

## 启动方法

### 方法1：使用批处理文件
```batch
start_web_system.bat
```

### 方法2：直接运行Python
```bash
python auto_run.py
```

然后访问：http://localhost:8000

## 配置要求

- Python 3.7+
- TagUI v6.110+
- Microsoft Edge浏览器
- Windows 10/11

## 注意事项

1. 确保TagUI已正确安装在C:\tagui\目录
2. 确保下载目录权限正确设置
3. 第一次运行可能需要管理员权限
4. 建议定期清理extracted_files目录
