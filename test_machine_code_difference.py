#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试机器码差异问题
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_machine_code_sources():
    """测试不同来源的机器码"""
    print("🔍 测试机器码差异问题")
    print("=" * 60)
    
    # 测试1: utils/machine_code.py 中的函数
    print("📱 测试1: utils/machine_code.py 中的 get_machine_code()")
    try:
        from utils.machine_code import get_machine_code as utils_get_machine_code
        utils_code = utils_get_machine_code()
        print(f"   结果: {utils_code}")
        print(f"   长度: {len(utils_code)} 位")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        utils_code = None
    
    # 测试2: services/auth_service.py 中的函数
    print("\n📱 测试2: services/auth_service.py 中的 get_machine_code()")
    try:
        from services.auth_service import auth_service
        auth_code = auth_service.get_machine_code()
        print(f"   结果: {auth_code}")
        print(f"   长度: {len(auth_code)} 位")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        auth_code = None
    
    # 测试3: 登录窗口使用的机器码
    print("\n📱 测试3: 登录窗口使用的机器码")
    try:
        from ui.login_window import LoginWindow
        from PyQt5.QtWidgets import QApplication
        
        # 创建QApplication（如果不存在）
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 创建登录窗口实例
        login_window = LoginWindow()
        login_code = login_window.machine_code
        print(f"   结果: {login_code}")
        print(f"   长度: {len(login_code)} 位")
        
        # 清理
        login_window.close()
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        login_code = None
    
    # 对比分析
    print("\n" + "=" * 60)
    print("📊 对比分析:")
    
    if utils_code and auth_code:
        print(f"   utils/machine_code.py:     {utils_code}")
        print(f"   services/auth_service.py:  {auth_code}")
        
        if login_code:
            print(f"   ui/login_window.py:        {login_code}")
        
        # 检查是否有关系
        if len(utils_code) == 32 and len(auth_code) == 16:
            if utils_code.startswith(auth_code):
                print("\n✅ 发现关系: auth_service返回的是utils机器码的前16位")
            elif utils_code[:16] == auth_code:
                print("\n✅ 发现关系: auth_service返回的是utils机器码的前16位")
            else:
                print("\n❌ 两个机器码完全不同，使用了不同的算法")
        else:
            print(f"\n❓ 长度不同: utils={len(utils_code) if utils_code else 'N/A'}, auth={len(auth_code) if auth_code else 'N/A'}")
    
    # 检查登录窗口使用的是哪个
    print("\n🔍 登录窗口机器码来源分析:")
    if login_code:
        if login_code == utils_code:
            print("   登录窗口使用的是 utils/machine_code.py 的结果")
        elif login_code == auth_code:
            print("   登录窗口使用的是 services/auth_service.py 的结果")
        else:
            print("   登录窗口使用的是其他来源的机器码")
    
    return utils_code, auth_code, login_code

def test_login_vs_api_machine_code():
    """测试登录时使用的机器码与API发送的机器码是否一致"""
    print("\n🔍 测试登录流程中的机器码一致性")
    print("=" * 60)
    
    try:
        from services.auth_service import auth_service
        
        # 获取登录时实际使用的机器码
        print("📞 模拟登录流程...")
        
        # 这是login方法中实际使用的机器码获取方式
        login_machine_code = auth_service.get_machine_code()
        print(f"   登录时使用的机器码: {login_machine_code}")
        
        # 检查是否与登录窗口显示的一致
        from ui.login_window import LoginWindow
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        login_window = LoginWindow()
        display_machine_code = login_window.machine_code
        print(f"   登录窗口显示的机器码: {display_machine_code}")
        
        if login_machine_code == display_machine_code:
            print("✅ 一致: 登录时使用的机器码与显示的机器码相同")
        else:
            print("❌ 不一致: 登录时使用的机器码与显示的机器码不同")
            print("   这就是问题所在！")
        
        login_window.close()
        
        return login_machine_code == display_machine_code
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_machine_code_algorithms():
    """分析两种机器码算法的差异"""
    print("\n🔍 分析机器码算法差异")
    print("=" * 60)
    
    print("📋 utils/machine_code.py 算法:")
    print("   1. 获取CPU序列号")
    print("   2. 获取主板序列号") 
    print("   3. 获取MAC地址")
    print("   4. 获取硬盘序列号")
    print("   5. 组合: cpu|motherboard|mac|disk")
    print("   6. MD5哈希，返回完整32位大写")
    
    print("\n📋 services/auth_service.py 算法:")
    print("   1. 获取计算机名")
    print("   2. 获取处理器信息")
    print("   3. 获取系统信息")
    print("   4. 获取主板序列号(Windows)")
    print("   5. 获取CPU序列号(Windows)")
    print("   6. 获取硬盘序列号(Windows)")
    print("   7. 按键名排序组合")
    print("   8. MD5哈希，返回前16位大写")
    
    print("\n💡 差异总结:")
    print("   1. 获取的硬件信息不同")
    print("   2. 组合方式不同")
    print("   3. 返回长度不同(32位 vs 16位)")
    print("   4. 这导致了机器码不一致的问题")

def main():
    """运行所有测试"""
    print("🚀 开始机器码差异诊断...")
    
    # 测试机器码来源
    utils_code, auth_code, login_code = test_machine_code_sources()
    
    # 测试登录流程一致性
    is_consistent = test_login_vs_api_machine_code()
    
    # 分析算法差异
    analyze_machine_code_algorithms()
    
    print("\n" + "=" * 60)
    print("🎯 诊断结论:")
    
    if not is_consistent:
        print("❌ 问题确认: 登录窗口显示的机器码与实际发送给服务器的机器码不一致")
        print("\n💡 解决方案:")
        print("   1. 统一使用同一个机器码生成函数")
        print("   2. 或者修改登录窗口使用auth_service.get_machine_code()")
        print("   3. 或者修改auth_service使用utils.machine_code.get_machine_code()")
        
        print(f"\n📋 当前状态:")
        print(f"   登录窗口显示: {login_code}")
        print(f"   实际发送API: {auth_code}")
        print(f"   服务器期望: {auth_code} (需要在服务器中更新)")
    else:
        print("✅ 机器码一致性正常")
    
    return is_consistent

if __name__ == "__main__":
    success = main()
    print(f"\n🎯 诊断结果: {'✅ 正常' if success else '❌ 发现问题'}")
