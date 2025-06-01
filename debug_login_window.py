#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录窗口问题诊断脚本
"""

import sys
import os
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def check_login_history():
    """检查登录历史文件"""
    print("🔍 检查登录历史文件...")
    
    history_file = "data/login_history.json"
    
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            print(f"  📄 登录历史文件存在")
            print(f"  📱 上次登录手机号: {history.get('last_phone', '无')}")
            print(f"  🕐 上次登录时间: {history.get('last_login_time', '无')}")
            
            return history
            
        except Exception as e:
            print(f"  ❌ 读取登录历史失败: {e}")
            return None
    else:
        print(f"  📄 登录历史文件不存在")
        return None


def test_login_window_behavior():
    """测试登录窗口行为"""
    print("\n🧪 测试登录窗口行为...")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from ui.login_window import LoginWindow
        
        # 创建登录窗口
        login_window = LoginWindow()
        
        print(f"  ✅ 登录窗口创建成功")
        print(f"  📱 手机号输入框内容: '{login_window.phone_input.text()}'")
        print(f"  👁️ 窗口可见性: {login_window.isVisible()}")
        
        # 监控登录窗口的信号
        login_triggered = False
        login_success_triggered = False
        
        def on_login_triggered():
            nonlocal login_triggered
            login_triggered = True
            print(f"  🚨 检测到登录被触发！")
        
        def on_login_success(user_info):
            nonlocal login_success_triggered
            login_success_triggered = True
            print(f"  ✅ 检测到登录成功信号: {user_info}")
        
        # 连接信号监控
        login_window.login_success.connect(on_login_success)
        
        # 显示窗口
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        print(f"  👁️ 窗口显示后可见性: {login_window.isVisible()}")
        
        # 设置定时器检查窗口状态
        check_count = 0
        
        def check_window_status():
            nonlocal check_count
            check_count += 1
            
            print(f"  📊 检查 #{check_count}:")
            print(f"     - 窗口可见: {login_window.isVisible()}")
            print(f"     - 登录按钮启用: {login_window.login_button.isEnabled()}")
            print(f"     - 进度条可见: {login_window.progress_bar.isVisible()}")
            print(f"     - 登录线程运行: {login_window.login_thread.isRunning() if login_window.login_thread else False}")
            
            if not login_window.isVisible() and check_count < 5:
                print(f"  ⚠️  窗口在第 {check_count} 次检查时已不可见！")
            
            if check_count < 10:
                QTimer.singleShot(500, check_window_status)
            else:
                print(f"  📊 最终状态:")
                print(f"     - 登录被触发: {login_triggered}")
                print(f"     - 登录成功: {login_success_triggered}")
                print(f"     - 窗口最终可见: {login_window.isVisible()}")
                
                app.quit()
        
        # 开始检查
        QTimer.singleShot(100, check_window_status)
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def backup_login_history():
    """备份登录历史文件"""
    print("\n💾 备份登录历史文件...")
    
    history_file = "data/login_history.json"
    backup_file = "data/login_history_backup.json"
    
    if os.path.exists(history_file):
        try:
            import shutil
            shutil.copy2(history_file, backup_file)
            print(f"  ✅ 登录历史已备份到: {backup_file}")
            return True
        except Exception as e:
            print(f"  ❌ 备份失败: {e}")
            return False
    else:
        print(f"  📄 没有登录历史文件需要备份")
        return True


def clear_login_history():
    """清空登录历史"""
    print("\n🗑️ 清空登录历史...")
    
    history_file = "data/login_history.json"
    
    if os.path.exists(history_file):
        try:
            os.remove(history_file)
            print(f"  ✅ 登录历史文件已删除")
            return True
        except Exception as e:
            print(f"  ❌ 删除失败: {e}")
            return False
    else:
        print(f"  📄 登录历史文件不存在")
        return True


def main():
    """主诊断函数"""
    print("=" * 60)
    print("🔍 登录窗口一闪而过问题诊断")
    print("=" * 60)
    
    # 1. 检查登录历史
    history = check_login_history()
    
    # 2. 备份登录历史
    backup_login_history()
    
    # 3. 测试当前行为
    print("\n" + "="*30 + " 当前行为测试 " + "="*30)
    test_login_window_behavior()
    
    print("\n" + "=" * 60)
    print("🔧 问题分析和解决方案:")
    
    if history and history.get('last_phone'):
        print("📱 发现问题：登录历史中有手机号，可能触发自动登录")
        print(f"   上次登录手机号: {history.get('last_phone')}")
        print("\n💡 解决方案:")
        print("   1. 清空登录历史，避免自动填入")
        print("   2. 修改登录窗口，禁用自动登录")
        print("   3. 添加用户确认机制")
        
        reply = input("\n是否清空登录历史？(y/n): ").lower().strip()
        if reply == 'y':
            if clear_login_history():
                print("✅ 登录历史已清空，请重新运行系统测试")
            else:
                print("❌ 清空失败")
    else:
        print("📱 登录历史正常，问题可能在其他地方")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
