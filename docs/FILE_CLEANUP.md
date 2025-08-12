# TagUI Web管理系统 - 文件说明

## 📁 核心文件（7个）

### 🚀 启动文件
- **`start_web_system.bat`** - 一键启动Web系统的批处理文件

### 🏗️ 系统核心
- **`auto_run.py`** - 后端服务器（智能执行引擎）
- **`index.html`** - 前端Web界面（证书管理系统）

### 🤖 自动化脚本
- **`test3.tag`** - TagUI自动化脚本（主要业务逻辑）
- **`test3.cmd`** - 备用的CMD执行脚本

### 📖 文档资源
- **`README.md`** - 系统使用说明文档
- **`火炬logo.png`** - 界面Logo图片

## 🗑️ 已清理的冗余文件（15个）

以下文件已被删除，因为功能已集成到新系统中：

### 旧版服务器文件
- `server.py` - 旧版HTTP服务器
- `start_server.bat` - 旧版启动脚本

### 旧版Python执行脚本
- `test.py` - 基础Python执行器
- `test_admin.py` - 管理员权限执行器
- `test_fast.py` - 快速执行脚本
- `test_with_timeout.py` - 超时处理脚本

### 旧版批处理文件
- `run_as_admin.bat` - 管理员权限批处理
- `run_simple.bat` - 简单执行批处理
- `run_elevated.bat` - 权限提升批处理
- `run_safe.bat` - 安全执行批处理
- `run_tagui_fixed.bat` - 修复版批处理
- `smart_run.bat` - 智能运行批处理

### 测试文件
- `test_simple.tag` - 简单测试脚本
- `test_basic.tag` - 基础测试脚本
- `test_basic.tag.js` - TagUI生成的JS文件
- `test_basic.tag.log` - TagUI生成的日志文件
- `test_basic.tag.raw` - TagUI原始文件

## ✨ 清理效果

- **文件数量**：从 22个 → 7个
- **结构清晰**：只保留必要的核心文件
- **功能完整**：所有功能都保留在新系统中
- **维护简单**：减少了68%的文件数量

## 🎯 使用建议

现在只需要关注这几个文件：
1. **启动系统**：双击 `start_web_system.bat`
2. **修改脚本**：编辑 `test3.tag`
3. **查看文档**：阅读 `README.md`
4. **高级用户**：直接运行 `auto_run.py`
