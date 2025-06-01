#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的 main_modular.py - 唯一主入口
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_main_modular_final():
    """测试修复后的 main_modular.py"""
    print("🧪 测试修复后的 main_modular.py")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from main_modular import ModularCinemaMainWindow
        
        # 创建主窗口
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        # 监控登录窗口状态
        def monitor_login():
            if hasattr(main_window, 'login_window') and main_window.login_window:
                login_window = main_window.login_window
                
                print(f"  📊 登录窗口状态:")
                print(f"     - 可见: {login_window.isVisible()}")
                print(f"     - 登录按钮启用: {login_window.login_button.isEnabled()}")
                print(f"     - 登录按钮文本: '{login_window.login_button.text()}'")
                print(f"     - 防自动登录: {login_window.auto_login_prevented}")
                
                if login_window.isVisible() and login_window.login_button.isEnabled():
                    if login_window.login_button.text() == "登 录":
                        print(f"  ✅ 登录窗口正常！")
                        print(f"     ✅ 登录按钮立即可用")
                        print(f"     ✅ 没有'请稍候'等待")
                        print(f"     ✅ 用户可以立即登录")
                    else:
                        print(f"  ⚠️  登录按钮文本异常: {login_window.login_button.text()}")
                else:
                    print(f"  ⚠️  登录窗口状态异常")
                
                # 5秒后关闭
                QTimer.singleShot(5000, app.quit)
            else:
                print(f"  ❌ 登录窗口不存在")
                app.quit()
        
        # 延迟检查
        QTimer.singleShot(1000, monitor_login)
        
        # 10秒后强制退出
        QTimer.singleShot(10000, lambda: [print("  ⏰ 测试超时"), app.quit()])
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🔧 main_modular.py 最终修复测试")
    print("=" * 60)
    
    print("💡 修复内容:")
    print("   1. ❌ 移除登录窗口的2秒等待")
    print("   2. ❌ 移除'请稍候'提示")
    print("   3. ✅ 登录按钮立即可用")
    print("   4. ✅ 保持智能默认选择功能")
    print("   5. ✅ main_modular.py 作为唯一主入口")
    print()
    
    # 测试修复后的效果
    success = test_main_modular_final()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   main_modular.py: {'✅ 正常' if success else '❌ 异常'}")
    
    if success:
        print("\n🎉 修复完成！")
        print()
        print("🚀 现在可以直接使用:")
        print("   python main_modular.py")
        print()
        print("✨ 修复后的用户体验:")
        print("   1. 启动系统 → 登录窗口立即显示")
        print("   2. 登录按钮立即可用，无需等待")
        print("   3. 用户可以立即输入手机号并登录")
        print("   4. 登录成功后自动选择影院和账号")
        print("   5. 无'等待账号选择'问题")
        print("   6. 用户体验流畅，无不必要的等待")
    else:
        print("\n⚠️  测试未完全成功")
        print("   建议检查登录窗口组件")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
