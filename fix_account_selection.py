#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复账号选择问题 - 确保重构版本独立运行
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def check_running_processes():
    """检查是否有其他相关进程在运行"""
    print("🔍 检查运行中的进程...")
    
    try:
        import psutil
        
        current_pid = os.getpid()
        python_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    if proc.info['pid'] != current_pid:
                        cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                        if '电影go' in cmdline or 'main' in cmdline:
                            python_processes.append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline
                            })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if python_processes:
            print("  ⚠️  发现其他相关Python进程:")
            for proc in python_processes:
                print(f"     PID {proc['pid']}: {proc['cmdline']}")
            print("  💡 建议关闭其他进程后重新运行")
            return False
        else:
            print("  ✅ 没有发现其他相关进程")
            return True
            
    except ImportError:
        print("  ⚠️  psutil未安装，无法检查进程")
        return True
    except Exception as e:
        print(f"  ❌ 检查进程失败: {e}")
        return True


def test_clean_startup():
    """测试干净的重构版本启动"""
    print("\n🧪 测试干净的重构版本启动")
    
    try:
        # 确保没有其他QApplication实例
        app = QApplication.instance()
        if app:
            print("  ⚠️  发现已存在的QApplication实例")
            app.quit()
        
        app = QApplication(sys.argv)
        print("  ✅ 创建新的QApplication实例")
        
        # 导入重构版本的主窗口
        from views.main_window import MainWindow
        
        # 创建主窗口
        main_window = MainWindow()
        print("  ✅ 重构版本主窗口创建成功")
        
        # 检查是否有Tab管理器相关的导入
        import sys
        tab_manager_modules = [name for name in sys.modules.keys() if 'tab_manager' in name.lower()]
        
        if tab_manager_modules:
            print(f"  ⚠️  发现Tab管理器模块已导入: {tab_manager_modules}")
            print("  💡 这可能是\"等待账号选择\"日志的来源")
        else:
            print("  ✅ 没有发现Tab管理器模块导入")
        
        # 检查登录窗口状态
        def check_login_status():
            if hasattr(main_window, 'login_window') and main_window.login_window:
                login_window = main_window.login_window
                print(f"  📊 登录窗口状态:")
                print(f"     - 可见: {login_window.isVisible()}")
                print(f"     - 登录按钮启用: {login_window.login_button.isEnabled()}")
                print(f"     - 防自动登录: {login_window.auto_login_prevented}")
                
                if login_window.isVisible():
                    print("  ✅ 重构版本登录窗口正常显示")
                    print("  🎉 重构版本运行正常，没有Tab管理器干扰")
                else:
                    print("  ❌ 登录窗口不可见")
            else:
                print("  ❌ 登录窗口不存在")
            
            app.quit()
        
        # 延迟检查
        QTimer.singleShot(2000, check_login_status)
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_clean_startup_script():
    """创建干净的启动脚本"""
    print("\n📝 创建干净的启动脚本...")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 重构版本 (干净启动)
确保只运行重构版本，避免Tab管理器干扰
"""

import sys
import os

def clean_imports():
    """清理可能冲突的导入"""
    # 移除可能导致冲突的模块
    modules_to_remove = []
    for module_name in sys.modules.keys():
        if any(keyword in module_name.lower() for keyword in ['tab_manager', 'main_modular']):
            modules_to_remove.append(module_name)
    
    for module_name in modules_to_remove:
        print(f"清理模块: {module_name}")
        del sys.modules[module_name]

def main():
    """主程序入口 - 重构版本专用"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 重构版本 v2.0.0 (干净启动)")
    print("=" * 60)
    print("🏗️  架构: MVC + 事件总线")
    print("🎨  界面: PyQt5")
    print("🔧  特性: 模块化、解耦、可扩展")
    print("🧹  模式: 干净启动，避免Tab管理器干扰")
    print("=" * 60)
    print()
    
    try:
        # 清理可能冲突的导入
        clean_imports()
        
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QCoreApplication
        from PyQt5.QtGui import QFont
        
        # 高DPI支持
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("柴犬影院下单系统-重构版")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("柴犬影院")
        
        # 设置默认字体
        default_font = QFont("Microsoft YaHei", 10)
        app.setFont(default_font)
        
        print("✅ 应用程序初始化完成")
        
        # 导入重构版本主窗口
        from views.main_window import MainWindow
        print("✅ 重构版本主窗口模块加载完成")
        
        # 创建主窗口
        MainWindow()
        print("✅ 重构版本主窗口创建完成")
        
        # 启动应用程序
        print("🚀 启动重构版本应用程序...")
        print("💡 如果看到\"等待账号选择\"日志，说明有其他进程在运行")
        sys.exit(app.exec_())
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有依赖已正确安装:")
        print("  pip install -r requirements.txt")
        input("\\n按回车键退出...")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 启动错误: {e}")
        print("\\n错误详情:")
        import traceback
        traceback.print_exc()
        input("\\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''
    
    try:
        with open('main_refactored_clean.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("  ✅ 创建干净启动脚本: main_refactored_clean.py")
        return True
        
    except Exception as e:
        print(f"  ❌ 创建脚本失败: {e}")
        return False


def main():
    """主诊断函数"""
    print("=" * 60)
    print("🔧 账号选择问题修复 - 重构版本独立运行")
    print("=" * 60)
    
    # 1. 检查运行进程
    clean_processes = check_running_processes()
    
    # 2. 测试干净启动
    clean_startup = test_clean_startup()
    
    # 3. 创建干净启动脚本
    script_created = create_clean_startup_script()
    
    print("\n" + "=" * 60)
    print("📊 诊断结果:")
    print(f"   进程检查: {'✅ 干净' if clean_processes else '⚠️  有其他进程'}")
    print(f"   重构版本: {'✅ 正常' if clean_startup else '❌ 异常'}")
    print(f"   启动脚本: {'✅ 已创建' if script_created else '❌ 创建失败'}")
    
    print("\n💡 解决方案:")
    
    if not clean_processes:
        print("   1. 关闭所有Python进程")
        print("   2. 重新启动系统")
    
    if script_created:
        print("   3. 使用干净启动脚本:")
        print("      python main_refactored_clean.py")
    
    print("\n🎯 \"等待账号选择\"的原因:")
    print("   - Tab管理器是原版本(main_modular.py)的组件")
    print("   - 重构版本(views/main_window.py)不包含Tab管理器")
    print("   - 如果看到此日志，说明有原版本组件在运行")
    print("   - 使用干净启动脚本可以避免这个问题")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
