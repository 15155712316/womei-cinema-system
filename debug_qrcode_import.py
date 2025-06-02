#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断qrcode模块导入问题
"""

import sys
import os

def diagnose_qrcode_import():
    """诊断qrcode模块导入问题"""
    print("=" * 80)
    print("🔍 诊断qrcode模块导入问题")
    print("=" * 80)
    
    # 1. 检查Python版本和路径
    print(f"📋 Python版本: {sys.version}")
    print(f"📋 Python可执行文件: {sys.executable}")
    print(f"📋 当前工作目录: {os.getcwd()}")
    print()
    
    # 2. 检查Python路径
    print(f"📋 Python模块搜索路径:")
    for i, path in enumerate(sys.path):
        print(f"   {i}: {path}")
    print()
    
    # 3. 尝试导入qrcode模块
    print(f"🔍 尝试导入qrcode模块...")
    try:
        import qrcode
        print(f"✅ qrcode模块导入成功")
        print(f"📋 qrcode模块位置: {qrcode.__file__}")
        
        # 检查qrcode模块的属性
        print(f"📋 qrcode模块属性:")
        for attr in dir(qrcode):
            if not attr.startswith('_'):
                print(f"   - {attr}")
        
        # 尝试创建QRCode对象
        try:
            qr = qrcode.QRCode()
            print(f"✅ QRCode对象创建成功")
        except Exception as e:
            print(f"❌ QRCode对象创建失败: {e}")
            
    except ImportError as e:
        print(f"❌ qrcode模块导入失败: {e}")
        
        # 检查是否安装了qrcode
        try:
            import subprocess
            result = subprocess.run([sys.executable, "-m", "pip", "show", "qrcode"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"📋 qrcode包信息:")
                print(result.stdout)
            else:
                print(f"❌ qrcode包未安装")
        except Exception as e2:
            print(f"❌ 检查qrcode包失败: {e2}")
    
    # 4. 尝试导入PIL
    print(f"\n🔍 尝试导入PIL...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        print(f"✅ PIL模块导入成功")
        print(f"📋 PIL版本: {Image.__version__ if hasattr(Image, '__version__') else 'Unknown'}")
    except ImportError as e:
        print(f"❌ PIL模块导入失败: {e}")
    
    # 5. 检查当前目录中是否有冲突文件
    print(f"\n🔍 检查当前目录中的潜在冲突文件...")
    current_dir = os.getcwd()
    potential_conflicts = ['qrcode.py', 'qrcode.pyc', 'PIL.py', 'PIL.pyc']
    
    for filename in potential_conflicts:
        filepath = os.path.join(current_dir, filename)
        if os.path.exists(filepath):
            print(f"⚠️ 发现潜在冲突文件: {filepath}")
        else:
            print(f"✅ 无冲突文件: {filename}")
    
    # 6. 尝试在utils目录中导入
    print(f"\n🔍 尝试从utils目录导入...")
    try:
        # 添加当前目录到Python路径
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        from utils.qrcode_generator import generate_ticket_qrcode
        print(f"✅ utils.qrcode_generator导入成功")
    except ImportError as e:
        print(f"❌ utils.qrcode_generator导入失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_qrcode_import()
