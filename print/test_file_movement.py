"""
文件移动功能测试工具
用于调试和验证文件检查移动功能
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backed.auto_run import TagUIRunner

def test_file_movement():
    """测试文件移动功能"""
    print("🧪 文件移动功能测试")
    print("="*60)
    
    # 创建TagUI运行器实例
    runner = TagUIRunner()
    
    # 显示配置信息
    print("📋 当前配置:")
    print(f"   下载目录: {runner.downloads_dir}")
    print(f"   目标目录: {runner.target_zip_dir}")
    print()
    
    # 询问用户是否要创建测试文件
    response = input("是否要在下载目录创建测试文件？(y/n): ")
    if response.lower() == 'y':
        create_test_files(runner.downloads_dir)
    
    # 执行文件检查和移动
    print("\n🚀 开始执行文件检查和移动:")
    result = runner.check_and_move_downloaded_files()
    
    print(f"\n📊 测试结果: {'✅ 成功' if result else '❌ 失败'}")

def create_test_files(downloads_dir):
    """在下载目录创建测试文件"""
    print("\n📝 创建测试文件:")
    
    try:
        # 确保下载目录存在
        downloads_dir.mkdir(parents=True, exist_ok=True)
        
        test_files = [
            "测试证照.zip",
            "测试文档.pdf",
            "测试表格.xlsx"
        ]
        
        for filename in test_files:
            test_file = downloads_dir / filename
            
            # 创建测试文件
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(f"这是测试文件: {filename}\n")
                f.write(f"创建时间: {os.path.getctime}\n")
                f.write("内容仅用于测试文件移动功能\n")
            
            print(f"   ✅ 创建: {filename}")
        
        print(f"   📁 测试文件已创建在: {downloads_dir}")
        
    except Exception as e:
        print(f"   ❌ 创建测试文件失败: {e}")

def show_directory_status():
    """显示目录状态"""
    runner = TagUIRunner()
    
    print("📁 目录状态检查:")
    print("="*60)
    
    # 检查下载目录
    print(f"📥 下载目录: {runner.downloads_dir}")
    if runner.downloads_dir.exists():
        print("   ✅ 目录存在")
        try:
            files = list(runner.downloads_dir.iterdir())
            print(f"   📊 文件数量: {len(files)}")
            for f in files[:10]:  # 显示前10个
                size = f.stat().st_size if f.is_file() else 0
                file_type = "文件夹" if f.is_dir() else "文件"
                print(f"      - {f.name} ({file_type}, {size} bytes)")
            if len(files) > 10:
                print(f"      ... 还有 {len(files) - 10} 个项目")
        except Exception as e:
            print(f"   ❌ 无法列出文件: {e}")
    else:
        print("   ❌ 目录不存在")
    
    print()
    
    # 检查目标目录
    print(f"📦 目标目录: {runner.target_zip_dir}")
    if runner.target_zip_dir.exists():
        print("   ✅ 目录存在")
        try:
            files = list(runner.target_zip_dir.iterdir())
            print(f"   📊 文件数量: {len(files)}")
            for f in files:
                size = f.stat().st_size if f.is_file() else 0
                file_type = "文件夹" if f.is_dir() else "文件"
                print(f"      - {f.name} ({file_type}, {size} bytes)")
        except Exception as e:
            print(f"   ❌ 无法列出文件: {e}")
    else:
        print("   ❌ 目录不存在")

if __name__ == "__main__":
    print("🔧 TagUI 文件移动测试工具")
    print("="*60)
    
    while True:
        print("\n请选择操作:")
        print("1. 显示目录状态")
        print("2. 测试文件移动功能")
        print("3. 退出")
        
        choice = input("\n请输入选项 (1-3): ").strip()
        
        if choice == "1":
            show_directory_status()
        elif choice == "2":
            test_file_movement()
        elif choice == "3":
            print("👋 再见！")
            break
        else:
            print("❌ 无效选项，请重试")
