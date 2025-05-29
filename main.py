#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 主入口文件
模块化架构版本
"""

import sys
import os

def main():
    """主程序入口"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 模块化版本")
    print("=" * 60)
    print()
    
    try:
        # 导入并启动模块化主程序
        from main_modular import main as modular_main
        print("✅ 启动模块化系统...")
        modular_main()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装: pip install -r requirements.txt")
        input("按回车键退出...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        input("按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main() 