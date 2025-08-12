import subprocess
import os
import json
import http.server
import socketserver
import threading
import shutil
import time
from pathlib import Path

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self):
        self.db_config = {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'root',
            'password': '123456',
            'database': 'fzdz_system',
            'charset': 'utf8mb4'
        }
    
    def get_print_logs(self, limit=100):
        """获取打印日志数据"""
        try:
            import mysql.connector
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM print_log ORDER BY print_time DESC LIMIT %s", (limit,))
            logs = cursor.fetchall()
            cursor.close()
            conn.close()
            
            # 转换datetime对象为字符串以便JSON序列化
            for log in logs:
                if 'print_time' in log and log['print_time']:
                    log['print_time'] = log['print_time'].isoformat()
            
            return logs
            
        except ImportError:
            print("⚠️ mysql-connector-python 未安装")
            
        except Exception as e:
            print(f"获取打印日志时出错: {e}")
            return self._get_error_logs(str(e))
    
    def add_print_log(self, cert_no, operator, status='SUCCESS', err_type=None, err_msg=None):
        """添加打印日志记录"""
        try:
            import mysql.connector
            from datetime import datetime
            
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO print_log (cert_no, operator, sys_version, status, err_type, err_msg)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            values = (cert_no, operator, 'v1.0.0', status, err_type, err_msg)
            cursor.execute(insert_query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"📝 打印日志已记录到数据库: {cert_no} | {operator} | {status}")
            return True
            
        except ImportError:
            print("⚠️ mysql-connector-python 未安装")
            self._print_log_fallback(cert_no, operator, status, err_msg)
            return False
            
        except Exception as e:
            print(f"添加打印日志到数据库时出错: {e}")
            self._print_log_fallback(cert_no, operator, status, err_msg)
            return False
  
    def _get_error_logs(self, error_msg):
        """获取错误日志数据"""
        from datetime import datetime, timedelta
        
        error_logs = []
        for i in range(5):
            log = {
                'id': i + 1,
                'cert_no': f'ERROR_{str(i+1).zfill(3)}',
                'print_time': (datetime.now() - timedelta(hours=i)).isoformat(),
                'operator': '系统测试',
                'sys_version': 'v1.0.0',
                'status': 'FAIL',
                'err_type': 'DB_ERROR',
                'err_msg': f'数据库连接失败: {error_msg}'
            }
            error_logs.append(log)
        
        return error_logs
    
    def _print_log_fallback(self, cert_no, operator, status, err_msg):
        """打印日志备用方案"""
        from datetime import datetime
        print(f"📝 打印日志记录(备用): {cert_no} | {operator} | {status} | {datetime.now()}")
        if err_msg:
            print(f"   错误信息: {err_msg}")

# 创建全局数据库管理器实例
db_manager = DatabaseManager()

class TagUIRunner:
    """TagUI执行器类"""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.execution_status = {
            "running": False, 
            "message": "", 
            "method": "",
            "status": "idle",
            "pdf_files": []
        }
        self.downloads_dir = Path("D:/辅助打证/test/downloads")
        self.extracted_files_dir = Path("D:/辅助打证/test/extracted_files")
        
        # 启动时加载现有的PDF文件
        self.load_existing_pdf_files()

    def load_existing_pdf_files(self):   # 加载现有PDF文件，打印路径下pdf文档的数量

        """启动时加载现有的PDF文件"""
        try:
            pdf_files = self.find_extracted_pdf_files()
            if pdf_files:
                self.execution_status["pdf_files"] = pdf_files
                self.execution_status["status"] = "completed"
                self.execution_status["message"] = f"发现 {len(pdf_files)} 个PDF文件"
                print(f"🎯 启动时发现 {len(pdf_files)} 个现有PDF文件")
            else:
                print("📭 启动时未发现PDF文件")
        except Exception as e:
            print(f"⚠️  加载现有PDF文件时出错: {e}")

    def find_extracted_pdf_files(self):  # 查找路径下的文档，打印文档列表
        """查找解压后的PDF文件"""
        pdf_files = []
        extracted_dir = Path("D:/辅助打证/test/extracted_files")
        
        if extracted_dir.exists():
            # 查找所有PDF文件
            for pdf_file in extracted_dir.rglob("*.pdf"):
                try:
                    relative_path = pdf_file.relative_to(extracted_dir)
                    # 将Windows路径分隔符转换为URL兼容的正斜杠
                    relative_path_str = str(relative_path).replace('\\', '/')
                    
                    # 创建文件信息对象
                    file_info = {
                        'name': pdf_file.name,
                        'path': relative_path_str,
                        'size': pdf_file.stat().st_size
                    }
                    
                    pdf_files.append(file_info)
                    print(f"📄 找到PDF文件: {relative_path_str}")
                except Exception as e:
                    print(f"处理PDF文件路径时出错: {e}")
        
        return pdf_files
    
    def list_all_cmd_processes(self):
        """列出所有cmd.exe进程的信息（包括进程号）"""
        print("📋 当前所有cmd.exe进程:")
        
        try:
            # 直接使用tasklist命令（更可靠）
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FO', 'CSV'], 
                                  capture_output=True, text=True, encoding='gbk')
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                cmd_count = 0
                
                for line in lines[1:]:  # 跳过标题行
                    if 'cmd.exe' in line:
                        # 解析CSV格式
                        fields = [field.strip('"') for field in line.split('","')]
                        if len(fields) >= 2:
                            process_name = fields[0]
                            pid = fields[1]
                            
                            if pid.isdigit():
                                cmd_count += 1
                                print(f"   进程{cmd_count}: {process_name}, PID={pid}")
                                
                                # 尝试获取详细命令行信息
                                try:
                                    # 使用PowerShell获取命令行
                                    ps_cmd = f'Get-WmiObject Win32_Process -Filter "ProcessId={pid}" | Select-Object CommandLine'
                                    ps_result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                                             capture_output=True, text=True, 
                                                             encoding='utf-8', errors='ignore')
                                    if ps_result.returncode == 0 and ps_result.stdout:
                                        cmdline = ps_result.stdout.strip()
                                        if 'tagui' in cmdline.lower():
                                            print(f"      🎯 这是TagUI相关进程!")
                                            print(f"      命令行: {cmdline[:100]}...")
                                        else:
                                            print(f"      命令行: {cmdline[:100]}...")
                                except:
                                    print(f"      命令行: (无法获取详细信息)")
                                print()
                
                if cmd_count == 0:
                    print("   没有找到cmd.exe进程")
                else:
                    print(f"   总共找到{cmd_count}个cmd.exe进程")
            else:
                print(f"   tasklist命令执行失败: {result.stderr}")
                
        except Exception as e:
            print(f"   获取cmd进程信息失败: {e}")
            # 最简单的备用方法
            try:
                print("   尝试最简单方法...")
                result = subprocess.run(['tasklist'], capture_output=True, text=True, encoding='gbk')
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    cmd_lines = [line for line in lines if 'cmd.exe' in line]
                    if cmd_lines:
                        print(f"   找到{len(cmd_lines)}个cmd.exe进程:")
                        for i, line in enumerate(cmd_lines, 1):
                            print(f"   进程{i}: {line.strip()}")
                    else:
                        print("   没有找到cmd.exe进程")
            except Exception as e2:
                print(f"   所有方法都失败: {e2}")

    def get_current_cmd_pids(self):
        """获取当前所有cmd进程的PID列表"""
        cmd_pids = set()
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FO', 'CSV'], 
                                  capture_output=True, text=True, encoding='gbk', errors='ignore')
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # 跳过标题行
                    if 'cmd.exe' in line:
                        fields = [field.strip('"') for field in line.split('","')]
                        if len(fields) >= 2 and fields[1].isdigit():
                            cmd_pids.add(fields[1])
        except Exception as e:
            print(f"   获取cmd进程PID失败: {e}")
        return cmd_pids
    
    def find_new_tagui_cmd_process(self, initial_cmd_pids):
        """查找新启动的TagUI cmd进程"""
        try:
            # 获取当前cmd进程
            current_cmd_pids = self.get_current_cmd_pids()
            new_cmd_pids = current_cmd_pids - initial_cmd_pids
            
            print(f"   初始cmd进程数: {len(initial_cmd_pids)}")
            print(f"   当前cmd进程数: {len(current_cmd_pids)}")
            print(f"   新增cmd进程数: {len(new_cmd_pids)}")
            
            if new_cmd_pids:
                print(f"   新增的cmd进程PID: {list(new_cmd_pids)}")
                
                # 检查每个新进程，找到真正的TagUI主进程
                tagui_candidates = []
                
                for pid in new_cmd_pids:
                    try:
                        # 使用PowerShell获取命令行信息
                        ps_cmd = f'Get-WmiObject Win32_Process -Filter "ProcessId={pid}" | Select-Object -ExpandProperty CommandLine'
                        ps_result = subprocess.run(['powershell', '-Command', ps_cmd], 
                                                 capture_output=True, text=True, 
                                                 encoding='utf-8', errors='ignore')
                        
                        if ps_result.returncode == 0 and ps_result.stdout:
                            command_line = ps_result.stdout.strip()
                            print(f"   PID {pid} 命令行: {command_line[:100]}...")
                            
                            # 检查是否包含TagUI关键字
                            if 'tagui' in command_line.lower():
                                print(f"   🎯 PID {pid} 确认是TagUI相关进程")
                                tagui_candidates.append({
                                    'pid': pid,
                                    'command': command_line,
                                    'priority': 1  # 直接包含tagui的进程优先级最高
                                })
                            elif any(keyword in command_line.lower() for keyword in ['cmd.exe', 'cmd /c', 'cmd /k']):
                                print(f"   📝 PID {pid} 可能是TagUI启动的cmd进程")
                                tagui_candidates.append({
                                    'pid': pid,
                                    'command': command_line,
                                    'priority': 2  # cmd进程优先级次之
                                })
                            else:
                                print(f"   ❓ PID {pid} 进程性质不明确")
                                tagui_candidates.append({
                                    'pid': pid,
                                    'command': command_line,
                                    'priority': 3  # 其他进程优先级最低
                                })
                        else:
                            print(f"   ⚠️ 无法获取PID {pid} 的命令行信息")
                            # 即使无法获取命令行，也作为候选
                            tagui_candidates.append({
                                'pid': pid,
                                'command': '(无法获取)',
                                'priority': 3
                            })
                    except Exception as e:
                        print(f"   ❌ 检查PID {pid} 时出错: {e}")
                
                if tagui_candidates:
                    # 按优先级排序，选择最有可能的TagUI进程
                    tagui_candidates.sort(key=lambda x: x['priority'])
                    selected_process = tagui_candidates[0]
                    
                    print(f"   ✅ 选择监控进程: PID={selected_process['pid']} (优先级={selected_process['priority']})")
                    print(f"   📝 选择原因: {selected_process['command'][:100]}...")
                    
                    return selected_process['pid']
                else:
                    print(f"   ❌ 没有找到合适的TagUI候选进程")
                    return None
            else:
                print(f"   ❌ 未发现新的cmd进程")
                return None
                
        except Exception as e:
            print(f"   查找新TagUI进程失败: {e}")
            return None
    
    def monitor_specific_cmd_process(self, cmd_pid, check_interval=3):
        """监控特定的cmd进程，等待它结束"""
        print(f"👀 开始监控特定cmd进程: PID={cmd_pid}")
        print(f"   检查间隔: {check_interval}秒")
        
        start_time = time.time()
        
        while True:
            try:
                elapsed_time = time.time() - start_time
                
                # 检查指定的cmd进程是否还在运行
                try:
                    result = subprocess.run(['tasklist', '/FI', f'PID eq {cmd_pid}', '/FO', 'CSV'], 
                                          capture_output=True, text=True, encoding='gbk', errors='ignore')
                    
                    process_running = False
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # 跳过标题行
                            if cmd_pid in line and 'cmd.exe' in line:
                                process_running = True
                                break
                    
                    if process_running:
                        print(f"   ⏳ TagUI cmd进程运行中... PID={cmd_pid}, 已运行: {elapsed_time:.1f}秒")
                    else:
                        # TagUI cmd进程已经结束
                        print(f"   ✅ TagUI cmd进程已结束! PID={cmd_pid}")
                        print(f"   📊 执行统计:")
                        print(f"      总执行时间: {elapsed_time:.2f}秒")
                        print(f"   🎯 TagUI脚本执行完毕，开始后续操作...")
                        return True
                    
                except Exception as e:
                    print(f"   ⚠️  检查进程状态失败: {e}")
                    # 如果检查失败，可能进程已经结束了
                    return True
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"   ⚠️  进程监控异常: {e}")
                time.sleep(check_interval)

    def monitor_tagui_processes(self, check_interval=3):
        """监控TagUI启动的cmd进程，等待它结束"""
        print("👀 开始监控TagUI启动的cmd进程...")
        print(f"   检查间隔: {check_interval}秒")
        
        start_time = time.time()
        tagui_cmd_found = False
        tagui_cmd_pid = None
        initial_wait_time = 5  # 给TagUI 5秒时间启动
        
        # 记录执行前的cmd进程
        initial_cmd_pids = set()
        try:
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FO', 'CSV'], 
                                  capture_output=True, text=True, encoding='gbk', errors='ignore')
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:  # 跳过标题行
                    if 'cmd.exe' in line:
                        fields = [field.strip('"') for field in line.split('","')]
                        if len(fields) >= 2 and fields[1].isdigit():
                            initial_cmd_pids.add(fields[1])
            print(f"   📋 记录执行前的cmd进程: {len(initial_cmd_pids)} 个")
        except Exception as e:
            print(f"   ⚠️  无法获取初始cmd进程: {e}")
        
        print(f"   ⏳ 等待TagUI cmd进程启动... ({initial_wait_time}秒)")
        time.sleep(initial_wait_time)
        
        while True:
            try:
                elapsed_time = time.time() - start_time
                
                # 获取当前所有cmd进程
                current_cmd_pids = set()
                try:
                    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq cmd.exe', '/FO', 'CSV'], 
                                          capture_output=True, text=True, encoding='gbk', errors='ignore')
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines[1:]:  # 跳过标题行
                            if 'cmd.exe' in line:
                                fields = [field.strip('"') for field in line.split('","')]
                                if len(fields) >= 2 and fields[1].isdigit():
                                    current_cmd_pids.add(fields[1])
                except Exception as e:
                    print(f"   ⚠️  获取cmd进程失败: {e}")
                    time.sleep(check_interval)
                    continue
                
                # 查找新的cmd进程（TagUI启动的）
                new_cmd_pids = current_cmd_pids - initial_cmd_pids
                
                if not tagui_cmd_found:
                    if new_cmd_pids:
                        # 发现新的cmd进程，应该是TagUI启动的
                        tagui_cmd_pid = list(new_cmd_pids)[0]  # 取第一个新进程
                        print(f"   ✅ 发现TagUI cmd进程: PID={tagui_cmd_pid}")
                        
                        # 尝试获取该进程的命令行信息确认
                        try:
                            wmic_result = subprocess.run([
                                'wmic', 'process', 'where', f'ProcessId={tagui_cmd_pid}',
                                'get', 'CommandLine', '/format:list'
                            ], capture_output=True, text=True, encoding='gbk', errors='ignore')
                            
                            if 'tagui' in wmic_result.stdout.lower():
                                print(f"   🎯 确认这是TagUI相关的cmd进程")
                            else:
                                print(f"   📝 cmd进程命令行: {wmic_result.stdout.strip()[:100]}...")
                        except:
                            print(f"   📝 无法获取cmd进程详细信息")
                        
                        tagui_cmd_found = True
                    else:
                        print(f"   ⏳ 等待TagUI cmd进程启动... 已等待: {elapsed_time:.1f}秒")
                        if elapsed_time > 60:  # 60秒还没启动就报错
                            print("   ❌ TagUI cmd进程启动超时 (60秒)")
                            return False
                else:
                    # 已经找到TagUI cmd进程，检查它是否还在运行
                    if tagui_cmd_pid in current_cmd_pids:
                        print(f"   ⏳ TagUI cmd进程运行中... PID={tagui_cmd_pid}, 已运行: {elapsed_time:.1f}秒")
                    else:
                        # TagUI cmd进程已经结束
                        print(f"   ✅ TagUI cmd进程已结束! PID={tagui_cmd_pid}")
                        print(f"   📊 执行统计:")
                        print(f"      总执行时间: {elapsed_time:.2f}秒")
                        print(f"   🎯 TagUI脚本执行完毕，开始后续操作...")
                        return True
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"   ⚠️  进程检查异常: {e}")
                time.sleep(check_interval)
    
    def run_with_powershell_elevation(self):
        """使用PowerShell尝试提升权限"""
        # PowerShell命令，尝试以管理员身份运行
        ps_command = f'''
        $currentDir = "{self.script_dir}"
        Set-Location $currentDir
        
        # 设置环境变量
        $env:JAVA_TOOL_OPTIONS = "-Dfile.encoding=UTF-8 -Duser.language=zh -Duser.country=CN"
        
        # 执行TagUI (使用Edge浏览器)
        & "C:\\tagui\\src\\tagui" "tag\\test3.tag" -edge
        '''
        
        try:
            # 执行前列出当前cmd进程并记录
            print("🔍 执行前的cmd进程状态:")
            initial_cmd_pids = self.get_current_cmd_pids()
            self.list_all_cmd_processes()
            
            # 启动PowerShell进程（非阻塞）
            print("🚀 启动PowerShell进程执行TagUI脚本...")
            process = subprocess.Popen([
                "powershell", 
                "-ExecutionPolicy", "Bypass",
                "-WindowStyle", "Normal",
                "-Command", ps_command
            ], cwd=str(self.script_dir))
            
            print(f"📋 PowerShell进程已启动，PID: {process.pid}")
            
            # 不再监控PowerShell进程，而是监控TagUI进程
            print("⏳ 等待PowerShell启动TagUI...")
            time.sleep(3)  # 给PowerShell时间启动TagUI
            
            # 列出启动后的cmd进程，并获取新启动的TagUI cmd进程
            print("🔍 启动后的cmd进程状态:")
            self.list_all_cmd_processes()  # 详细列出所有cmd进程
            
            tagui_cmd_pid = self.find_new_tagui_cmd_process(initial_cmd_pids)
            
            if tagui_cmd_pid:
                print(f"✅ 找到TagUI cmd进程: PID={tagui_cmd_pid}")
                # 监控这个特定的TagUI cmd进程
                self.monitor_specific_cmd_process(tagui_cmd_pid)
            else:
                print("⚠️ 未找到特定TagUI cmd进程，使用通用监控")
                # 如果找不到特定进程，使用原来的方法
                self.monitor_tagui_processes()
            
            # TagUI进程已退出，脚本执行完成
            print("✅ TagUI cmd.exe进程已全部退出 - 脚本执行完毕")
            
            # 执行完成后再次列出cmd进程
            print("🔍 执行完成后的cmd进程状态:")
            self.list_all_cmd_processes()
            
            # 现在开始检查下载的文件
            print("🔍 开始检查下载文件...")
            file_processed = self.check_and_extract_downloaded_files()
            if file_processed:
                print("📁 文件处理完成")
            else:
                print("⚠️  文件处理未成功")
            
            return True
            
        except Exception as e:
            print(f"❌ PowerShell执行失败: {e}")
            return False
    
    def check_and_extract_downloaded_files(self):
        """直接检查下载目录中的压缩包文件并解压"""
        print("="*60)
        print("🔍 开始检查下载目录中的压缩包文件")
        print("="*60)
        
        try:
            # 步骤1: 检查下载目录
            print(f"📁 步骤1: 检查下载目录")
            print(f"   下载目录: {self.downloads_dir}")
            
            if not self.downloads_dir.exists():
                print(f"   ❌ 下载目录不存在！")
                return False
            else:
                print(f"   ✅ 下载目录存在")
            
            # 步骤2: 扫描压缩包文件
            print(f"\n🔎 步骤2: 扫描压缩包文件")
            archive_patterns = ["*.zip", "*.rar", "*.7z"]
            print(f"   搜索模式: {archive_patterns}")
            
            found_archives = []
            for pattern in archive_patterns:
                files = list(self.downloads_dir.glob(pattern))
                if files:
                    print(f"   找到 {len(files)} 个 {pattern} 文件")
                    for f in files:
                        print(f"      - {f.name} (修改时间: {time.ctime(f.stat().st_mtime)})")
                found_archives.extend(files)
            
            if not found_archives:
                print(f"   ❌ 下载目录中没有找到任何压缩包文件")
                print(f"   💡 下载目录内容:")
                try:
                    all_files = list(self.downloads_dir.iterdir())
                    if all_files:
                        for f in all_files[:10]:  # 只显示前10个文件
                            print(f"      - {f.name} ({'文件夹' if f.is_dir() else '文件'})")
                        if len(all_files) > 10:
                            print(f"      ... 还有 {len(all_files) - 10} 个文件/文件夹")
                    else:
                        print(f"      (目录为空)")
                except Exception as e:
                    print(f"      无法列出目录内容: {e}")
                return False
            
            print(f"   ✅ 总共找到 {len(found_archives)} 个压缩包文件")
            
            # 步骤3: 检查文件时间
            print(f"\n⏰ 步骤3: 检查文件时间")
            current_time = time.time()
            print(f"   当前时间: {time.ctime(current_time)}")
            print(f"   时间窗口: 2分钟 (120秒)")
            
            recent_archives = []
            for file_path in found_archives:
                file_time = file_path.stat().st_mtime
                time_diff = current_time - file_time
                
                print(f"   文件: {file_path.name}")
                print(f"      修改时间: {time.ctime(file_time)}")
                print(f"      时间差: {time_diff:.2f} 秒")

                if time_diff <= 120:  # 2分钟 = 120秒
                    print(f"      ✅ 符合时间条件 (≤120秒)")
                    recent_archives.append(file_path)
                else:
                    print(f"      ❌ 超出时间窗口 (>120秒)")
            
            if not recent_archives:
                print(f"   ❌ 没有找到最近2分钟内的压缩包文件")
                return False
            
            print(f"   ✅ 找到 {len(recent_archives)} 个符合时间条件的压缩包文件")
            
            # 步骤4: 直接解压压缩包文件
            print(f"\n📦 步骤4: 解压压缩包文件")
            extracted_count = 0
            
            for i, archive_path in enumerate(recent_archives, 1):
                print(f"   处理压缩包 {i}/{len(recent_archives)}: {archive_path.name}")
                
                try:
                    # 获取文件大小
                    file_size = archive_path.stat().st_size
                    print(f"      文件大小: {file_size / 1024:.2f} KB")
                    
                    # 直接解压到extracted_files目录
                    print(f"      开始解压...")
                    extract_success = self.extract_archive_file(archive_path)
                    
                    if extract_success:
                        print(f"      ✅ 解压成功")
                        extracted_count += 1
                        
                        # 解压成功后删除原压缩包
                        try:
                            archive_path.unlink()
                            print(f"      ✅ 原压缩包已删除")
                        except Exception as e:
                            print(f"      ⚠️  删除原压缩包失败: {e}")
                    else:
                        print(f"      ❌ 解压失败")
                    
                except Exception as e:
                    print(f"      ❌ 处理压缩包失败: {e}")
                    print(f"         错误类型: {type(e).__name__}")
            
            # 步骤5: 总结
            print(f"\n📊 步骤5: 处理总结")
            print(f"   总压缩包数: {len(recent_archives)}")
            print(f"   成功解压: {extracted_count}")
            print(f"   失败数量: {len(recent_archives) - extracted_count}")
            
            if extracted_count > 0:
                print(f"   🎉 压缩包解压完成！")
                
                # 显示解压目录内容
                print(f"   📁 解压目录内容:")
                try:
                    if self.extracted_files_dir.exists():
                        extracted_files = list(self.extracted_files_dir.iterdir())
                        for f in extracted_files[-5:]:  # 显示最新的5个文件
                            if f.is_file():
                                size = f.stat().st_size / 1024
                                print(f"      - {f.name} ({size:.2f} KB)")
                            else:
                                print(f"      - {f.name} (文件夹)")
                except Exception as e:
                    print(f"      无法列出解压目录: {e}")
                
                return True
            else:
                print(f"   ❌ 没有成功解压任何文件")
                return False
            
        except Exception as e:
            print(f"❌ 检查和解压过程失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

    def extract_archive_file(self, archive_path):
        """解压单个压缩包文件"""
        try:
            # 确保解压目录存在
            if not self.extracted_files_dir.exists():
                self.extracted_files_dir.mkdir(parents=True, exist_ok=True)
            
            # 根据文件扩展名选择解压方法
            if archive_path.suffix.lower() == '.zip':
                return self.extract_zip_file(archive_path)
            elif archive_path.suffix.lower() == '.rar':
                print(f"      ⚠️  RAR文件需要特殊处理，暂时跳过")
                return False
            elif archive_path.suffix.lower() == '.7z':
                print(f"      ⚠️  7z文件需要特殊处理，暂时跳过")
                return False
            else:
                print(f"      ❌ 不支持的压缩格式: {archive_path.suffix}")
                return False
                
        except Exception as e:
            print(f"      ❌ 解压文件失败: {e}")
            return False

    def extract_zip_file(self, zip_path):
        """解压ZIP文件"""
        try:
            import zipfile
            
            print(f"      正在解压ZIP文件: {zip_path.name}")
            
            # 生成带时间戳的文件夹名
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            extract_folder_name = f"{zip_path.stem}_{timestamp}"
            extract_folder = self.extracted_files_dir / extract_folder_name
            
            # 创建解压目录
            extract_folder.mkdir(parents=True, exist_ok=True)
            print(f"      解压到: {extract_folder}")
            
            # 解压文件
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 使用CP936编码处理中文文件名
                for file_info in zip_ref.filelist:
                    try:
                        # 尝试用CP936解码文件名
                        filename = file_info.filename.encode('cp437').decode('cp936')
                    except:
                        # 如果失败，使用原始文件名
                        filename = file_info.filename
                    
                    # 提取文件
                    file_info.filename = filename
                    zip_ref.extract(file_info, extract_folder)
            
            print(f"      ✅ ZIP文件解压完成")
            
            # 列出解压的文件
            extracted_files = list(extract_folder.rglob('*'))
            file_count = len([f for f in extracted_files if f.is_file()])
            print(f"      解压出 {file_count} 个文件")
            
            # 更新执行状态中的PDF文件列表
            pdf_files = [f for f in extracted_files if f.is_file() and f.suffix.lower() == '.pdf']
            if pdf_files:
                print(f"      发现 {len(pdf_files)} 个PDF文件")
                # 添加到执行状态
                if not hasattr(self, 'execution_status'):
                    self.execution_status = {}
                if 'pdf_files' not in self.execution_status:
                    self.execution_status['pdf_files'] = []
                
                for pdf_file in pdf_files:
                    relative_path = pdf_file.relative_to(self.extracted_files_dir)
                    # 将Windows路径分隔符转换为URL兼容的正斜杠
                    relative_path_str = str(relative_path).replace('\\', '/')
                    self.execution_status['pdf_files'].append({
                        'name': pdf_file.name,
                        'path': relative_path_str,
                        'size': pdf_file.stat().st_size
                    })
                    print(f"         - {pdf_file.name}")
            
            return True
            
        except Exception as e:
            print(f"      ❌ ZIP解压失败: {e}")
            return False

    def run_normal(self):
        """普通权限执行"""
        try:
            # 设置环境变量
            env = os.environ.copy()
            env['JAVA_TOOL_OPTIONS'] = '-Dfile.encoding=UTF-8 -Duser.language=zh -Duser.country=CN'
            
            # 启动TagUI进程（非阻塞）
            print("🚀 启动TagUI进程（普通权限）...")
            process = subprocess.Popen([
                "C:\\tagui\\src\\tagui", 
                "tag\\test3.tag",
                "-edge"
            ], cwd=str(self.script_dir), env=env)
            
            print(f"📋 TagUI进程已启动，PID: {process.pid}")
            
            # 监控TagUI进程
            self.monitor_tagui_processes()
            
            # TagUI进程已退出，脚本执行完成
            print("✅ TagUI进程已全部退出 - 脚本执行完毕")
            
            # 现在开始检查下载的文件
            print("🔍 开始检查下载文件...")
            file_processed = self.check_and_extract_downloaded_files()
            if file_processed:
                print("📁 文件处理完成")
            else:
                print("⚠️  文件处理未成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 普通权限执行失败: {e}")
            return False
    
    def execute_async(self):
        """异步执行TagUI脚本"""
        self.execution_status["running"] = True
        self.execution_status["message"] = "正在尝试执行..."
        self.execution_status["status"] = "running"
        self.execution_status["pdf_files"] = []
        
        methods = [
            ("PowerShell方式", self.run_with_powershell_elevation),
            ("普通权限方式", self.run_normal),
        ]
        
        for method_name, method_func in methods:
            print(f"\n📝 尝试: {method_name}")
            self.execution_status["method"] = method_name
            self.execution_status["message"] = f"正在使用{method_name}执行..."
            
            try:
                if method_func():
                    print(f"✅ {method_name} 成功")
                    
                    # 查找生成的PDF文件
                    pdf_files = self.find_extracted_pdf_files()
                    
                    self.execution_status["message"] = f"{method_name}执行成功，文件已处理"
                    self.execution_status["status"] = "completed"
                    self.execution_status["running"] = False
                    self.execution_status["pdf_files"] = pdf_files
                    
                    # 记录成功的打印日志
                    from datetime import datetime
                    cert_no = f"AUTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    db_manager.add_print_log(cert_no, "系统自动", "SUCCESS")
                    
                    return True
                else:
                    print(f"❌ {method_name} 失败，尝试下一种方式...")
            except Exception as e:
                print(f"💥 {method_name} 异常: {e}")
        
        self.execution_status["message"] = "所有执行方式都失败了"
        self.execution_status["status"] = "failed"
        self.execution_status["running"] = False
        
        # 记录失败的打印日志
        from datetime import datetime
        cert_no = f"AUTO_{datetime.now().strftime('%Y%m%d_%H%M%S')}_FAILED"
        db_manager.add_print_log(cert_no, "系统自动", "FAIL", "EXEC_ERROR", "所有执行方式都失败了")
        
        return False



# 全局TagUI执行器实例
tagui_runner = TagUIRunner()

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # 设置静态文件服务目录为frontend
        super().__init__(*args, directory="frontend", **kwargs)
    
    def clear_extracted_files(self):
        """清空解压文件目录"""
        try:
            import shutil
            extracted_dir = Path("D:/辅助打证/test/extracted_files")
            
            if extracted_dir.exists():
                # 删除目录中的所有内容
                for item in extracted_dir.iterdir():
                    if item.is_file():
                        item.unlink()
                        print(f"   删除文件: {item.name}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        print(f"   删除文件夹: {item.name}")
                
                print(f"✅ 解压文件目录已清空: {extracted_dir}")
                
                # 清空执行状态中的PDF文件列表
                tagui_runner.execution_status["pdf_files"] = []
                tagui_runner.execution_status["status"] = "idle"
                tagui_runner.execution_status["message"] = ""
                
                return True
            else:
                print(f"⚠️  解压文件目录不存在: {extracted_dir}")
                return True  # 目录不存在也算成功
                
        except Exception as e:
            print(f"❌ 清空解压文件目录失败: {e}")
            return False
    
    def get_print_logs(self):
        """获取打印日志数据"""
        return db_manager.get_print_logs()
    
    def add_print_log(self, cert_no, operator, status='SUCCESS', err_type=None, err_msg=None):
        """添加打印日志记录"""
        return db_manager.add_print_log(cert_no, operator, status, err_type, err_msg)
    
    def do_GET(self):
        # 处理状态查询
        if self.path == '/status':
            try:
                status_data = tagui_runner.execution_status.copy()
                
                # 确保状态数据完整
                if "status" not in status_data:
                    if status_data.get("running", False):
                        status_data["status"] = "running"
                    else:
                        status_data["status"] = "idle"
                
                response = {
                    'status': status_data.get("status", "idle"),
                    'message': status_data.get("message", ""),
                    'method': status_data.get("method", ""),
                    'pdf_files': status_data.get("pdf_files", [])
                }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                try:
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except ConnectionAbortedError:
                    print("状态查询响应时连接中断")
                return
            except ConnectionAbortedError as e:
                print(f"状态查询连接中断: {e}")
                return
            except Exception as e:
                print(f"状态查询错误: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    error_response = {
                        'status': 'error',
                        'message': f'状态查询失败: {str(e)}',
                        'method': '',
                        'pdf_files': []
                    }
                    
                    self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                except:
                    # 如果发送错误响应也失败，说明连接已断开，静默处理
                    pass
                return
        
        # 处理PDF预览
        elif self.path.startswith('/preview-pdf'):
            try:
                # 解析PDF文件路径参数
                from urllib.parse import urlparse, parse_qs, unquote
                parsed_url = urlparse(self.path)
                query_params = parse_qs(parsed_url.query)
                
                if 'path' in query_params:
                    # 对URL编码的路径进行解码
                    pdf_relative_path = unquote(query_params['path'][0])
                    pdf_full_path = Path("D:/辅助打证/test/extracted_files") / pdf_relative_path
                    
                    if pdf_full_path.exists() and pdf_full_path.suffix.lower() == '.pdf':
                        # 直接返回PDF文件
                        with open(pdf_full_path, 'rb') as pdf_file:
                            pdf_content = pdf_file.read()
                        
                        # 对中文文件名进行正确的编码处理
                        filename = pdf_full_path.name
                        try:
                            # 尝试ASCII编码（适用于英文文件名）
                            filename.encode('ascii')
                            disposition = f'inline; filename="{filename}"'
                        except UnicodeEncodeError:
                            # 中文文件名使用RFC6266标准
                            from urllib.parse import quote
                            encoded_filename = quote(filename)
                            disposition = f'inline; filename*=UTF-8\'\'{encoded_filename}'
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/pdf')
                        self.send_header('Content-Disposition', disposition)
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        
                        try:
                            self.wfile.write(pdf_content)
                        except ConnectionAbortedError:
                            print("PDF传输时连接中断")
                            return
                        return
                    else:
                        self.send_response(404)
                        self.send_header('Content-type', 'text/plain')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(b'PDF file not found')
                        return
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/plain')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(b'Missing path parameter')
                    return
            except ConnectionAbortedError as e:
                print(f"PDF预览连接中断: {e}")
                # 连接已断开，不尝试发送响应
                return
            except Exception as e:
                print(f"PDF预览错误: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/plain')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(f'Preview error: {str(e)}'.encode('utf-8'))
                except:
                    # 如果发送错误响应也失败，说明连接已断开，静默处理
                    pass
                return
        
        # 处理清空解压文件目录
        elif self.path == '/clear-extracted-files':
            try:
                success = self.clear_extracted_files()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'success': success,
                    'message': '解压文件目录已清空' if success else '清空解压文件目录失败'
                }
                
                try:
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except ConnectionAbortedError:
                    print("清空文件响应时连接中断")
                return
            except ConnectionAbortedError as e:
                print(f"清空文件连接中断: {e}")
                return
            except Exception as e:
                print(f"清空解压文件目录错误: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    error_response = {
                        'success': False,
                        'message': f'清空失败: {str(e)}'
                    }
                    
                    self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                except:
                    # 如果发送错误响应也失败，说明连接已断开，静默处理
                    pass
                return
                error_response = {'success': False, 'message': str(e)}
                self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                return
        
        # 处理打印日志查询
        elif self.path == '/print-log':
            try:
                logs = self.get_print_logs()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'success': True,
                    'logs': logs
                }
                
                try:
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except ConnectionAbortedError:
                    print("打印日志响应时连接中断")
                return
            except ConnectionAbortedError as e:
                print(f"打印日志连接中断: {e}")
                return
            except Exception as e:
                print(f"获取打印日志错误: {e}")
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    
                    error_response = {
                        'success': False,
                        'message': f'获取打印日志失败: {str(e)}'
                    }
                    
                    self.wfile.write(json.dumps(error_response, ensure_ascii=False).encode('utf-8'))
                except:
                    # 如果发送错误响应也失败，说明连接已断开，静默处理
                    pass
                return
        
        # 如果请求根路径，重定向到index.html
        elif self.path == '/':
            self.path = '/index.html'
        
        # 处理其他静态文件请求
        try:
            return super().do_GET()
        except ConnectionAbortedError:
            print(f"静态文件传输时连接中断: {self.path}")
            return
        except Exception as e:
            print(f"静态文件服务错误: {e} (路径: {self.path})")
            try:
                self.send_response(500)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'Internal Server Error')
            except:
                # 如果发送错误响应也失败，静默处理
                pass
            return
    
    def do_POST(self):
        if self.path == '/execute-tagui':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            print(f"收到执行TagUI的请求")
            
            try:
                # 解析请求数据
                try:
                    request_data = json.loads(post_data.decode('utf-8'))
                    action = request_data.get('action', 'execute')
                except:
                    action = 'execute'
                
                if action == 'execute':
                    if tagui_runner.execution_status["running"]:
                        response = {
                            'status': 'running',
                            'message': '脚本正在执行中，请稍等...',
                            'current_method': tagui_runner.execution_status["method"]
                        }
                    else:
                        # 启动异步执行
                        thread = threading.Thread(target=tagui_runner.execute_async)
                        thread.daemon = True
                        thread.start()
                        
                        response = {
                            'status': 'started',
                            'message': 'TagUI脚本已开始执行（异步）',
                            'note': '脚本正在后台运行，请等待完成'
                        }
                
                elif action == 'status':
                    response = {
                        'status': 'running' if tagui_runner.execution_status["running"] else 'idle',
                        'message': tagui_runner.execution_status["message"],
                        'method': tagui_runner.execution_status["method"]
                    }
                
                else:
                    response = {
                        'status': 'error',
                        'message': f'未知操作: {action}'
                    }
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                try:
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except ConnectionAbortedError:
                    print("POST响应时连接中断")
                    return
                
            except ConnectionAbortedError:
                print("POST请求处理时连接中断")
                return
            except Exception as e:
                print(f"处理请求时发生错误: {str(e)}")
                response = {
                    'status': 'error',
                    'message': f'服务器错误: {str(e)}'
                }
                
                try:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
                except:
                    # 如果发送错误响应也失败，静默处理
                    pass
        else:
            super().do_POST()
    
    def do_OPTIONS(self):
        try:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
        except ConnectionAbortedError:
            print("OPTIONS响应时连接中断")
            return
        except Exception as e:
            print(f"OPTIONS请求处理错误: {e}")
            return

if __name__ == "__main__":
    PORT = 8000
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 TagUI后端服务器启动在 http://localhost:{PORT}")
        print("� 请在浏览器中访问 http://localhost:8000/index.html")
        print("⭐ 支持的API端点:")
        print("   POST /execute-tagui - 执行TagUI脚本")
        print("   GET  /             - 访问前端页面")
        print("📝 按 Ctrl+C 停止服务器")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务器已停止")
