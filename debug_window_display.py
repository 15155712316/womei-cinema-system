#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口显示问题诊断脚本
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer


def test_login_window_only():
    """测试单独的登录窗口"""
    print("🧪 测试1: 单独创建登录窗口")
    
    try:
        from ui.login_window import LoginWindow
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        print("  ✅ 登录窗口类导入成功")
        
        # 创建登录窗口
        login_window = LoginWindow()
        print("  ✅ 登录窗口创建成功")
        
        # 显示窗口
        login_window.show()
        print("  ✅ 登录窗口show()调用成功")
        
        # 检查窗口是否可见
        print(f"  📊 窗口可见性: {login_window.isVisible()}")
        print(f"  📊 窗口位置: {login_window.pos()}")
        print(f"  📊 窗口大小: {login_window.size()}")
        
        # 强制激活窗口
        login_window.raise_()
        login_window.activateWindow()
        print("  ✅ 窗口激活完成")
        
        # 设置定时器自动关闭
        def close_test():
            print("  ✅ 测试完成，关闭窗口")
            login_window.close()
            app.quit()
        
        QTimer.singleShot(3000, close_test)
        
        print("  🚀 启动事件循环...")
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 登录窗口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_window_creation():
    """测试主窗口创建但不启动认证流程"""
    print("\n🧪 测试2: 主窗口创建（跳过认证）")
    
    try:
        from views.main_window import MainWindow
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        print("  ✅ 主窗口类导入成功")
        
        # 临时修改主窗口，跳过认证流程
        class TestMainWindow(MainWindow):
            def _start_auth_flow(self):
                print("  🔄 跳过认证流程，直接显示主窗口")
                self.show()
                self.raise_()
                self.activateWindow()
        
        # 创建测试主窗口
        main_window = TestMainWindow()
        print("  ✅ 主窗口创建成功")
        
        # 检查窗口状态
        print(f"  📊 窗口可见性: {main_window.isVisible()}")
        print(f"  📊 窗口位置: {main_window.pos()}")
        print(f"  📊 窗口大小: {main_window.size()}")
        
        # 设置定时器自动关闭
        def close_test():
            print("  ✅ 测试完成，关闭窗口")
            main_window.close()
            app.quit()
        
        QTimer.singleShot(3000, close_test)
        
        print("  🚀 启动事件循环...")
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 主窗口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simple_window():
    """测试简单的PyQt5窗口"""
    print("\n🧪 测试3: 简单PyQt5窗口")
    
    try:
        from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
        
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # 创建简单窗口
        window = QWidget()
        window.setWindowTitle("测试窗口")
        window.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        label = QLabel("这是一个测试窗口\n如果您能看到这个窗口，说明PyQt5工作正常")
        label.setStyleSheet("font-size: 14px; padding: 20px;")
        layout.addWidget(label)
        window.setLayout(layout)
        
        # 显示窗口
        window.show()
        window.raise_()
        window.activateWindow()
        
        print("  ✅ 简单窗口创建并显示成功")
        print(f"  📊 窗口可见性: {window.isVisible()}")
        
        # 设置定时器自动关闭
        def close_test():
            print("  ✅ 测试完成，关闭窗口")
            window.close()
            app.quit()
        
        QTimer.singleShot(3000, close_test)
        
        print("  🚀 启动事件循环...")
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 简单窗口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auth_service():
    """测试认证服务"""
    print("\n🧪 测试4: 认证服务")
    
    try:
        from services.auth_service import auth_service
        
        # 测试机器码生成
        machine_code = auth_service.get_machine_code()
        print(f"  ✅ 机器码生成成功: {machine_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 认证服务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主诊断函数"""
    print("=" * 60)
    print("🔍 柴犬影院下单系统 - 窗口显示问题诊断")
    print("=" * 60)
    
    # 运行诊断测试
    tests = [
        ("认证服务", test_auth_service),
        ("简单PyQt5窗口", test_simple_window),
        ("登录窗口", test_login_window_only),
        ("主窗口创建", test_main_window_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 诊断结果: {passed}/{total} 通过")
    
    if passed == total:
        print("🎉 所有测试通过！窗口显示功能正常")
        print("\n💡 建议检查:")
        print("   1. 窗口是否被其他程序遮挡")
        print("   2. 多显示器环境下窗口是否在其他屏幕")
        print("   3. 系统DPI设置是否影响窗口显示")
    else:
        print("⚠️  部分测试失败，请检查相关模块")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
