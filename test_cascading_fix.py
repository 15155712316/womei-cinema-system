#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
四级联动修复验证脚本
直接测试修复后的四级联动功能
"""

def main():
    """启动系统并验证四级联动"""
    print("🔧 四级联动修复验证")
    print("=" * 50)
    
    # 启动主程序
    import sys
    import os
    
    # 添加项目路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        print("🚀 启动模块化系统...")
        from main_modular import main
        main()
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 