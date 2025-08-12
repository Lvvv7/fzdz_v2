import zipfile
import os
import datetime

def fix_filename_encoding(filename):
    """修复zip文件中的中文文件名编码问题"""
    try:
        # 方法1: CP437 -> GBK (Windows最常见的情况)
        if filename.encode('cp437'):
            return filename.encode('cp437').decode('gbk')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    try:
        # 方法2: ISO-8859-1 -> UTF-8
        return filename.encode('iso-8859-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    try:
        # 方法3: 尝试其他常见编码
        return filename.encode('latin1').decode('gbk')
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    
    # 如果都失败了，返回原文件名
    return filename

def decode_zip_file(zip_filename, base_extract_path="extracted_files"):
    """解压指定的zip文件，支持中文文件名"""
    
    # 获取zip文件名（不含路径和扩展名）
    zip_name = os.path.splitext(os.path.basename(zip_filename))[0]
    
    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 创建以zip文件名+时间戳命名的文件夹
    extract_folder_name = f"{zip_name}_{timestamp}"
    extract_to = os.path.join(base_extract_path, extract_folder_name)
    
    # 确保解压目录存在
    os.makedirs(extract_to, exist_ok=True)
    
    print(f"[INFO] 解压zip文件: {zip_filename}")
    print(f"[INFO] 目标文件夹: {extract_to}")
    
    try:
        # 尝试使用UTF-8编码打开
        with zipfile.ZipFile(zip_filename, 'r') as zipf:
            # 获取所有文件名
            file_list = zipf.namelist()
            print(f"[INFO] 发现 {len(file_list)} 个文件")
            
            for file_info in zipf.infolist():
                # 获取原始文件名
                raw_filename = file_info.filename
                
                # 修复文件名编码
                fixed_filename = fix_filename_encoding(raw_filename)
                
                if fixed_filename != raw_filename:
                    print(f"[FIX] 修复文件名: {raw_filename} -> {fixed_filename}")
                else:
                    print(f"[FILE] 文件名: {fixed_filename}")
                
                # 创建正确的文件路径
                target_path = os.path.join(extract_to, fixed_filename)
                target_dir = os.path.dirname(target_path)
                
                # 确保目标目录存在
                if target_dir:
                    os.makedirs(target_dir, exist_ok=True)
                
                # 提取文件
                with zipf.open(file_info) as source, open(target_path, 'wb') as target:
                    target.write(source.read())
                
                print(f"[SUCCESS] 解压: {fixed_filename}")
        
        print(f"[SUCCESS] 解压zip文件成功: {zip_filename}")
        print(f"[INFO] 解压到目录: {extract_to}")
        print(f"[INFO] 文件夹名称: {os.path.basename(extract_to)}")
        return extract_to
        
    except Exception as e:
        print(f"[ERROR] 解压失败: {e}")
        # 如果上面的方法失败，尝试简单解压
        try:
            print("[INFO] 尝试简单解压模式...")
            with zipfile.ZipFile(zip_filename, 'r') as zipf:
                zipf.extractall(extract_to)
            print(f"[SUCCESS] 简单解压成功: {zip_filename}")
            return extract_to
        except Exception as e2:
            print(f"[ERROR] 简单解压也失败: {e2}")
            return None

def batch_extract_zip_files(zip_files_list, base_extract_path="extracted_files"):
    """批量解压多个zip文件"""
    results = []
    
    for zip_file in zip_files_list:
        if os.path.exists(zip_file):
            print(f"\n[PROCESS] 正在处理: {zip_file}")
            result = decode_zip_file(zip_file, base_extract_path)
            results.append({
                'zip_file': zip_file,
                'extract_path': result,
                'success': result is not None
            })
        else:
            print(f"[ERROR] 文件不存在: {zip_file}")
            results.append({
                'zip_file': zip_file,
                'extract_path': None,
                'success': False
            })
    
    
    return results

if __name__ == "__main__":
    # 自动检测zip目录中的所有zip文件
    
    zip_directory = "../zip"  # 从print目录向上一级找到zip目录
    
    # 检查zip目录是否存在
    if not os.path.exists(zip_directory):
        print(f"[ERROR] zip目录不存在: {zip_directory}")
        print("[INFO] 请确保zip目录存在并包含要解压的zip文件")
        
        # 尝试绝对路径
        absolute_zip_dir = os.path.abspath("../zip")
        print(f"[INFO] 尝试绝对路径: {absolute_zip_dir}")
        if os.path.exists(absolute_zip_dir):
            zip_directory = absolute_zip_dir
            print(f"[SUCCESS] 找到zip目录: {zip_directory}")
        else:
            print(f"[ERROR] 绝对路径也不存在")
            # 显示当前目录内容帮助调试
            current_dir = os.getcwd()
            parent_dir = os.path.dirname(current_dir)
            print(f"[INFO] 当前目录: {current_dir}")
            print(f"[INFO] 上级目录: {parent_dir}")
            if os.path.exists(parent_dir):
                print(f"[INFO] 上级目录内容:")
                for item in os.listdir(parent_dir):
                    print(f"   - {item}")
            exit(1)  # 退出程序
    
    if os.path.exists(zip_directory):
        # 自动发现所有zip文件
        print(f"[INFO] 扫描zip目录: {zip_directory}")
        
        # 获取所有zip文件
        zip_files = []
        for file in os.listdir(zip_directory):
            if file.lower().endswith('.zip'):
                zip_path = os.path.join(zip_directory, file)
                zip_files.append(zip_path)
        
        if zip_files:
            print(f"[INFO] 发现 {len(zip_files)} 个zip文件:")
            for i, zip_file in enumerate(zip_files, 1):
                file_size = os.path.getsize(zip_file) / 1024  # KB
                print(f"   {i}. {os.path.basename(zip_file)} ({file_size:.1f} KB)")
            
            print(f"\n[INFO] 开始批量解压...")
            batch_results = batch_extract_zip_files(zip_files)
            
            # 统计结果
            success_count = sum(1 for result in batch_results if result['success'])
            total_count = len(batch_results)
            
            print(f"\n[RESULT] 解压结果统计:")
            print(f"   总文件数: {total_count}")
            print(f"   成功解压: {success_count}")
            print(f"   失败数量: {total_count - success_count}")
            
            if success_count > 0:
                print(f"\n[SUCCESS] 解压完成！解压文件保存在 extracted_files 目录中")
                
                # 解压完成后清空zip文件夹
                print(f"\n[INFO] 开始清空zip文件夹...")
                try:
                    deleted_count = 0
                    failed_count = 0
                    
                    for zip_file in zip_files:
                        try:
                            if os.path.exists(zip_file):
                                os.remove(zip_file)
                                print(f"   [DELETE] 已删除: {os.path.basename(zip_file)}")
                                deleted_count += 1
                            else:
                                print(f"   [WARN] 文件不存在: {os.path.basename(zip_file)}")
                        except Exception as e:
                            print(f"   [ERROR] 删除失败: {os.path.basename(zip_file)} - {e}")
                            failed_count += 1
                    
                    print(f"\n[RESULT] 清理结果:")
                    print(f"   成功删除: {deleted_count} 个文件")
                    print(f"   删除失败: {failed_count} 个文件")
                    
                    # 检查zip目录是否为空
                    remaining_files = []
                    try:
                        for file in os.listdir(zip_directory):
                            file_path = os.path.join(zip_directory, file)
                            if os.path.isfile(file_path):
                                remaining_files.append(file)
                        
                        if remaining_files:
                            print(f"   [INFO] zip目录剩余文件: {len(remaining_files)} 个")
                            for file in remaining_files[:5]:  # 显示前5个
                                print(f"      - {file}")
                            if len(remaining_files) > 5:
                                print(f"      ... 还有 {len(remaining_files) - 5} 个文件")
                        else:
                            print(f"   [SUCCESS] zip目录已清空")
                            
                    except Exception as e:
                        print(f"   [WARN] 无法检查zip目录状态: {e}")
                    
                except Exception as e:
                    print(f"   [ERROR] 清空zip文件夹时发生异常: {e}")
                    
            else:
                print(f"\n[ERROR] 所有文件解压都失败了")
                print(f"[INFO] zip文件将保留，请检查文件是否损坏")
        else:
            print(f"[INFO] zip目录中没有找到任何zip文件")
            print(f"   目录内容:")
            try:
                files = os.listdir(zip_directory)
                if files:
                    for file in files[:10]:  # 只显示前10个文件
                        print(f"      - {file}")
                    if len(files) > 10:
                        print(f"      ... 还有 {len(files) - 10} 个文件")
                else:
                    print(f"      (目录为空)")
            except Exception as e:
                print(f"      无法读取目录内容: {e}")