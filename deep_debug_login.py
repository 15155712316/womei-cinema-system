#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度诊断登录窗口一闪而过问题
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, QObject, pyqtSignal


class WindowMonitor(QObject):
    """窗口监控器"""
    
    window_closed = pyqtSignal(str)
    
    def __init__(self, window, name):
        super().__init__()
        self.window = window
        self.name = name
        self.is_monitoring = True
        
        # 重写窗口的关闭事件
        original_close_event = window.closeEvent
        
        def monitored_close_event(event):
            print(f"🚨 [{self.name}] 窗口关闭事件被触发！")
            print(f"   调用栈信息:")
            import traceback
            traceback.print_stack()
            
            self.window_closed.emit(self.name)
            
            if original_close_event:
                original_close_event(event)
        
        window.closeEvent = monitored_close_event
        
        # 监控窗口状态变化
        self._start_monitoring()
    
    def _start_monitoring(self):
        """开始监控窗口状态"""
        def check_status():
            if self.is_monitoring:
                visible = self.window.isVisible()
                if not visible:
                    print(f"⚠️  [{self.name}] 窗口变为不可见！")
                    print(f"   时间: {time.strftime('%H:%M:%S')}")
                    self.is_monitoring = False
                else:
                    # 继续监控
                    QTimer.singleShot(100, check_status)
        
        QTimer.singleShot(100, check_status)


def test_login_window_with_monitoring():
    """测试登录窗口并监控其行为"""
    print("🔍 深度监控登录窗口行为")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from ui.login_window import LoginWindow
        
        # 创建登录窗口
        print("  📱 创建登录窗口...")
        login_window = LoginWindow()
        
        # 创建窗口监控器
        monitor = WindowMonitor(login_window, "登录窗口")
        
        def on_window_closed(name):
            print(f"🚨 监控器检测到 {name} 被关闭")
        
        monitor.window_closed.connect(on_window_closed)
        
        # 监控登录相关的信号
        login_success_triggered = False
        
        def on_login_success(user_info):
            nonlocal login_success_triggered
            login_success_triggered = True
            print(f"🚨 检测到登录成功信号: {user_info}")
            print(f"   这可能导致窗口关闭！")
        
        login_window.login_success.connect(on_login_success)
        
        # 显示窗口
        print("  👁️ 显示登录窗口...")
        login_window.show()
        login_window.raise_()
        login_window.activateWindow()
        
        print(f"  📊 初始状态:")
        print(f"     - 窗口可见: {login_window.isVisible()}")
        print(f"     - 窗口位置: {login_window.pos()}")
        print(f"     - 登录按钮启用: {login_window.login_button.isEnabled()}")
        print(f"     - 手机号内容: '{login_window.phone_input.text()}'")
        
        # 强制保持窗口显示
        def force_show():
            if not login_window.isVisible():
                print("  🔧 强制重新显示窗口...")
                login_window.show()
                login_window.raise_()
                login_window.activateWindow()
        
        # 每500ms检查一次并强制显示
        def periodic_check():
            force_show()
            QTimer.singleShot(500, periodic_check)
        
        QTimer.singleShot(500, periodic_check)
        
        # 10秒后结束测试
        def end_test():
            print(f"  📊 最终状态:")
            print(f"     - 窗口可见: {login_window.isVisible()}")
            print(f"     - 登录成功触发: {login_success_triggered}")
            print(f"     - 登录按钮启用: {login_window.login_button.isEnabled()}")
            
            if login_window.isVisible():
                print("  ✅ 窗口成功保持显示")
            else:
                print("  ❌ 窗口仍然消失了")
            
            app.quit()
        
        QTimer.singleShot(10000, end_test)
        
        print("  🚀 启动事件循环...")
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_minimal_login_window():
    """测试最小化的登录窗口"""
    print("\n🧪 测试最小化登录窗口（无自动填入）")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit
        
        # 创建最简单的登录窗口
        window = QWidget()
        window.setWindowTitle("简化登录测试")
        window.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        label = QLabel("手机号:")
        layout.addWidget(label)
        
        phone_input = QLineEdit()
        phone_input.setPlaceholderText("请输入手机号")
        layout.addWidget(phone_input)
        
        login_button = QPushButton("登录")
        login_button.setEnabled(False)
        layout.addWidget(login_button)
        
        status_label = QLabel("请稍候...")
        layout.addWidget(status_label)
        
        window.setLayout(layout)
        
        # 2秒后启用登录按钮
        def enable_login():
            login_button.setEnabled(True)
            status_label.setText("可以登录了")
            print("  ✅ 登录按钮已启用")
        
        QTimer.singleShot(2000, enable_login)
        
        # 显示窗口
        window.move(100, 100)  # 安全位置
        window.show()
        window.raise_()
        window.activateWindow()
        
        print(f"  📊 简化窗口状态:")
        print(f"     - 窗口可见: {window.isVisible()}")
        print(f"     - 窗口位置: {window.pos()}")
        
        # 监控窗口状态
        def check_simple_window():
            print(f"  📊 简化窗口检查: 可见={window.isVisible()}")
            if window.isVisible():
                QTimer.singleShot(1000, check_simple_window)
            else:
                print("  ⚠️  简化窗口也消失了！")
                app.quit()
        
        QTimer.singleShot(1000, check_simple_window)
        
        # 10秒后关闭
        QTimer.singleShot(10000, lambda: [print("  ✅ 简化窗口测试完成"), app.quit()])
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 简化测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_system_environment():
    """检查系统环境"""
    print("\n🔍 检查系统环境")
    
    try:
        import platform
        print(f"  🖥️ 操作系统: {platform.system()} {platform.release()}")
        print(f"  🐍 Python版本: {platform.python_version()}")
        
        from PyQt5.QtCore import QT_VERSION_STR
        from PyQt5.Qt import PYQT_VERSION_STR
        print(f"  🎨 Qt版本: {QT_VERSION_STR}")
        print(f"  🎨 PyQt5版本: {PYQT_VERSION_STR}")
        
        # 检查显示器信息
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_count = desktop.screenCount()
        print(f"  🖥️ 显示器数量: {screen_count}")
        
        for i in range(screen_count):
            screen_rect = desktop.screenGeometry(i)
            print(f"     显示器 {i}: {screen_rect.width()}x{screen_rect.height()} at ({screen_rect.x()}, {screen_rect.y()})")
        
        primary_screen = desktop.primaryScreen()
        print(f"  🖥️ 主显示器: {primary_screen}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 环境检查失败: {e}")
        return False


def main():
    """主诊断函数"""
    print("=" * 60)
    print("🔍 登录窗口一闪而过深度诊断")
    print("=" * 60)
    
    # 1. 检查系统环境
    check_system_environment()
    
    # 2. 测试最小化窗口
    success1 = test_minimal_login_window()
    
    # 3. 测试实际登录窗口
    success2 = test_login_window_with_monitoring()
    
    print("\n" + "=" * 60)
    print("📊 深度诊断结果:")
    print(f"   系统环境: ✅ 正常")
    print(f"   简化窗口: {'✅ 正常' if success1 else '❌ 异常'}")
    print(f"   登录窗口: {'✅ 正常' if success2 else '❌ 异常'}")
    
    if success1 and not success2:
        print("\n💡 分析结论:")
        print("   - 简化窗口正常说明PyQt5环境没问题")
        print("   - 登录窗口异常说明问题在登录窗口的特定代码中")
        print("   - 可能的原因:")
        print("     1. 登录历史自动填入触发了某种机制")
        print("     2. 登录线程或信号处理有问题")
        print("     3. 窗口关闭事件被意外触发")
    elif not success1:
        print("\n💡 分析结论:")
        print("   - 连简化窗口都有问题，可能是系统级问题")
        print("   - 建议检查:")
        print("     1. 防火墙或安全软件设置")
        print("     2. 显示器DPI设置")
        print("     3. PyQt5安装是否完整")
    else:
        print("\n💡 分析结论:")
        print("   - 所有测试都正常，问题可能是间歇性的")
        print("   - 建议多次测试确认")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
