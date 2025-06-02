#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度诊断qrcode模块导入问题
分析主程序运行环境与直接运行脚本的差异
"""

import sys
import os
import subprocess
import importlib.util

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*80)
    print(f"🔍 {title}")
    print("="*80)

def diagnose_python_environment():
    """诊断Python运行环境"""
    print_separator("Python运行环境诊断")
    
    print(f"📋 Python版本: {sys.version}")
    print(f"📋 Python可执行文件: {sys.executable}")
    print(f"📋 当前工作目录: {os.getcwd()}")
    print(f"📋 脚本文件路径: {__file__}")
    print(f"📋 脚本所在目录: {os.path.dirname(os.path.abspath(__file__))}")
    
    # 检查是否在虚拟环境中
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"📋 虚拟环境: 是")
        print(f"📋 虚拟环境路径: {sys.prefix}")
        if hasattr(sys, 'base_prefix'):
            print(f"📋 基础Python路径: {sys.base_prefix}")
    else:
        print(f"📋 虚拟环境: 否")

def diagnose_sys_path():
    """诊断Python模块搜索路径"""
    print_separator("Python模块搜索路径")
    
    print(f"📋 sys.path包含 {len(sys.path)} 个路径:")
    for i, path in enumerate(sys.path):
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"   {i:2d}: {exists} {path}")

def diagnose_qrcode_installation():
    """诊断qrcode模块安装状态"""
    print_separator("qrcode模块安装诊断")
    
    # 方法1: 尝试直接导入
    try:
        import qrcode
        print(f"✅ 方法1 - 直接导入: 成功")
        print(f"📋 qrcode模块位置: {qrcode.__file__}")
        print(f"📋 qrcode模块目录: {os.path.dirname(qrcode.__file__)}")
        
        # 检查版本
        try:
            version = qrcode.__version__
            print(f"📋 qrcode版本: {version}")
        except AttributeError:
            print(f"📋 qrcode版本: 无法获取")
        
        # 检查关键组件
        try:
            qr = qrcode.QRCode()
            print(f"✅ QRCode类创建: 成功")
        except Exception as e:
            print(f"❌ QRCode类创建: 失败 - {e}")
            
    except ImportError as e:
        print(f"❌ 方法1 - 直接导入: 失败 - {e}")
    
    # 方法2: 使用importlib检查
    try:
        spec = importlib.util.find_spec("qrcode")
        if spec is not None:
            print(f"✅ 方法2 - importlib查找: 成功")
            print(f"📋 模块规格: {spec}")
            print(f"📋 模块文件: {spec.origin}")
        else:
            print(f"❌ 方法2 - importlib查找: 失败 - 模块未找到")
    except Exception as e:
        print(f"❌ 方法2 - importlib查找: 异常 - {e}")
    
    # 方法3: 使用pip检查安装
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "qrcode"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ 方法3 - pip show: 成功")
            print("📋 pip show qrcode 输出:")
            for line in result.stdout.strip().split('\n'):
                print(f"     {line}")
        else:
            print(f"❌ 方法3 - pip show: 失败")
            print(f"📋 错误输出: {result.stderr}")
    except Exception as e:
        print(f"❌ 方法3 - pip show: 异常 - {e}")

def diagnose_file_conflicts():
    """诊断文件名冲突"""
    print_separator("文件名冲突诊断")
    
    current_dir = os.getcwd()
    potential_conflicts = [
        'qrcode.py', 'qrcode.pyc', 'qrcode.pyo',
        '__pycache__/qrcode.cpython-*.pyc',
        'PIL.py', 'PIL.pyc', 'PIL.pyo'
    ]
    
    conflicts_found = False
    
    for pattern in potential_conflicts:
        if '*' in pattern:
            # 处理通配符模式
            import glob
            matches = glob.glob(os.path.join(current_dir, pattern))
            for match in matches:
                print(f"⚠️ 发现潜在冲突文件: {match}")
                conflicts_found = True
        else:
            filepath = os.path.join(current_dir, pattern)
            if os.path.exists(filepath):
                print(f"⚠️ 发现潜在冲突文件: {filepath}")
                conflicts_found = True
    
    if not conflicts_found:
        print(f"✅ 未发现文件名冲突")
    
    # 检查utils目录
    utils_dir = os.path.join(current_dir, 'utils')
    if os.path.exists(utils_dir):
        print(f"📋 检查utils目录: {utils_dir}")
        for filename in os.listdir(utils_dir):
            if filename.startswith('qrcode') and filename.endswith('.py'):
                filepath = os.path.join(utils_dir, filename)
                print(f"📋 发现相关文件: {filepath}")

def diagnose_import_from_utils():
    """诊断从utils导入的情况"""
    print_separator("utils模块导入诊断")
    
    try:
        # 尝试导入utils.qrcode_generator
        from utils.qrcode_generator import generate_ticket_qrcode
        print(f"✅ 从utils.qrcode_generator导入: 成功")
    except ImportError as e:
        print(f"❌ 从utils.qrcode_generator导入: 失败 - {e}")
        import traceback
        print("📋 详细错误信息:")
        traceback.print_exc()

def compare_environments():
    """对比不同运行环境"""
    print_separator("环境对比分析")
    
    print("📋 当前运行方式: 直接运行诊断脚本")
    print(f"📋 Python解释器: {sys.executable}")
    print(f"📋 工作目录: {os.getcwd()}")
    
    # 模拟主程序运行环境
    print("\n📋 模拟主程序运行环境检查:")
    main_script = "main_modular.py"
    if os.path.exists(main_script):
        print(f"✅ 找到主程序: {main_script}")
        
        # 检查主程序中的导入
        try:
            with open(main_script, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'qrcode' in content:
                    print(f"📋 主程序中包含qrcode相关代码")
                else:
                    print(f"📋 主程序中未直接包含qrcode导入")
        except Exception as e:
            print(f"❌ 读取主程序失败: {e}")
    else:
        print(f"❌ 未找到主程序: {main_script}")

def main():
    """主诊断函数"""
    print("🔍 开始深度诊断qrcode模块导入问题")
    print(f"⏰ 诊断时间: {__import__('datetime').datetime.now()}")
    
    diagnose_python_environment()
    diagnose_sys_path()
    diagnose_qrcode_installation()
    diagnose_file_conflicts()
    diagnose_import_from_utils()
    compare_environments()
    
    print_separator("诊断完成")
    print("📋 诊断报告已生成，请查看上述输出以确定问题根源")

if __name__ == "__main__":
    main()
