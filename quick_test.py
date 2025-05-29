#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试模块化系统
"""

def test_main_window_display():
    """测试主窗口显示"""
    print("🔧 测试主窗口显示修复...")
    
    try:
        from main_modular import ModularCinemaMainWindow
        from PyQt5.QtWidgets import QApplication
        import sys
        
        app = QApplication(sys.argv)
        
        # 创建主窗口
        window = ModularCinemaMainWindow()
        
        print("✅ 主窗口创建成功")
        print("✅ 登录窗口应该会自动显示")
        print("✅ 登录成功后主窗口将会显示")
        
        # 模拟登录成功
        def simulate_login():
            user_info = {
                "phone": "15155712316",
                "machineCode": "91F16A48D96494E3",
                "points": 888,
                "status": 1
            }
            print("🎯 模拟登录成功，主窗口应该显示...")
            window._on_user_login_success(user_info)
        
        # 5秒后模拟登录成功
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(5000, simulate_login)
        
        # 启动应用
        app.exec_()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 柴犬影院模块化系统快速测试")
    print("=" * 50)
    
    test_main_window_display() 