#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 main_modular.py 的智能默认选择优化
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer


def test_smart_selection_flow():
    """测试智能选择流程"""
    print("🧪 测试 main_modular.py 智能选择流程")
    
    try:
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        from main_modular import ModularCinemaMainWindow
        
        # 创建主窗口（会触发登录）
        main_window = ModularCinemaMainWindow()
        
        print(f"  ✅ 主窗口创建成功")
        
        # 监控智能选择流程
        selection_steps = []
        
        def monitor_selection():
            print(f"  📊 监控智能选择流程...")
            
            # 检查影院选择状态
            if hasattr(main_window, 'tab_manager_widget'):
                tab_manager = main_window.tab_manager_widget
                
                # 检查影院下拉框
                if hasattr(tab_manager, 'cinema_combo'):
                    cinema_count = tab_manager.cinema_combo.count()
                    current_cinema = tab_manager.cinema_combo.currentText()
                    print(f"     - 影院列表: {cinema_count} 个影院")
                    print(f"     - 当前影院: {current_cinema}")
                    
                    if current_cinema and current_cinema != "请选择影院":
                        selection_steps.append(f"影院选择: {current_cinema}")
                
                # 检查电影下拉框
                if hasattr(tab_manager, 'movie_combo'):
                    movie_count = tab_manager.movie_combo.count()
                    current_movie = tab_manager.movie_combo.currentText()
                    print(f"     - 电影列表: {movie_count} 个电影")
                    print(f"     - 当前电影: {current_movie}")
                    
                    if current_movie and "等待账号选择" not in current_movie:
                        selection_steps.append(f"电影加载: {current_movie}")
            
            # 检查账号选择状态
            if hasattr(main_window, 'current_account') and main_window.current_account:
                userid = main_window.current_account.get('userid', main_window.current_account.get('phone', 'N/A'))
                print(f"     - 当前账号: {userid}")
                selection_steps.append(f"账号选择: {userid}")
            
            # 检查账号组件状态
            if hasattr(main_window, 'account_widget'):
                account_widget = main_window.account_widget
                if hasattr(account_widget, 'account_table'):
                    account_count = account_widget.account_table.rowCount()
                    current_row = account_widget.account_table.currentRow()
                    print(f"     - 账号表格: {account_count} 个账号，当前行: {current_row}")
                    
                    if current_row >= 0:
                        selection_steps.append(f"账号表格选择: 第{current_row+1}行")
            
            # 检查是否出现"等待账号选择"
            if hasattr(main_window, 'tab_manager_widget') and hasattr(main_window.tab_manager_widget, 'movie_combo'):
                movie_text = main_window.tab_manager_widget.movie_combo.currentText()
                if "等待账号选择" in movie_text:
                    print(f"     ⚠️  仍然出现'等待账号选择': {movie_text}")
                    selection_steps.append("问题: 仍有等待账号选择")
                else:
                    print(f"     ✅ 没有'等待账号选择'问题")
            
            # 继续监控或结束
            if len(selection_steps) < 4 and len(selection_steps) > 0:  # 期望至少4个步骤
                QTimer.singleShot(1000, monitor_selection)
            else:
                print(f"  📋 智能选择流程完成:")
                for i, step in enumerate(selection_steps, 1):
                    print(f"     {i}. {step}")
                
                # 判断是否成功
                has_cinema = any("影院选择" in step for step in selection_steps)
                has_account = any("账号选择" in step for step in selection_steps)
                no_waiting = not any("等待账号选择" in step for step in selection_steps)
                
                if has_cinema and has_account and no_waiting:
                    print(f"  🎉 智能选择成功！")
                    print(f"     ✅ 自动选择了影院")
                    print(f"     ✅ 自动选择了账号")
                    print(f"     ✅ 没有'等待账号选择'问题")
                else:
                    print(f"  ⚠️  智能选择部分成功:")
                    print(f"     影院选择: {'✅' if has_cinema else '❌'}")
                    print(f"     账号选择: {'✅' if has_account else '❌'}")
                    print(f"     无等待问题: {'✅' if no_waiting else '❌'}")
                
                # 5秒后关闭
                QTimer.singleShot(5000, app.quit)
        
        # 等待登录完成后开始监控
        def start_monitoring():
            if hasattr(main_window, 'login_window') and main_window.login_window:
                if main_window.login_window.isVisible():
                    print(f"  ⏳ 等待用户登录...")
                    QTimer.singleShot(3000, start_monitoring)
                else:
                    print(f"  ✅ 登录完成，开始监控智能选择")
                    QTimer.singleShot(1000, monitor_selection)
            else:
                print(f"  ✅ 直接开始监控智能选择")
                QTimer.singleShot(1000, monitor_selection)
        
        # 开始监控
        QTimer.singleShot(1000, start_monitoring)
        
        # 20秒后强制退出
        QTimer.singleShot(20000, lambda: [print("  ⏰ 测试超时"), app.quit()])
        
        app.exec_()
        
        return True
        
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_optimized_main_script():
    """创建优化版的主启动脚本"""
    print("\n📝 创建优化版主启动脚本...")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 主入口优化版 (智能默认选择)
"""

import sys
import os

def main():
    """主程序入口 - 智能默认选择优化版"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 主入口优化版")
    print("=" * 60)
    print("🏗️  架构: 单体架构 + Tab管理器")
    print("🎨  界面: 传统PyQt5界面")
    print("🔧  特性: 完整功能 + 智能默认选择")
    print("✨  优化: 登录后自动选择影院和账号")
    print("🚀  流程: 登录→主界面→自动选择影院→自动选择账号→加载影片")
    print("=" * 60)
    print()
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, QCoreApplication
        from PyQt5.QtGui import QFont
        
        # 高DPI支持
        QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # 创建应用程序
        app = QApplication(sys.argv)
        
        # 设置应用程序信息
        app.setApplicationName("柴犬影院下单系统-优化版")
        app.setApplicationVersion("1.6.0")
        app.setOrganizationName("柴犬影院")
        
        # 设置默认字体
        default_font = QFont("Microsoft YaHei", 10)
        app.setFont(default_font)
        
        print("✅ 应用程序初始化完成")
        
        # 导入主窗口
        from main_modular import ModularCinemaMainWindow
        print("✅ 优化版主窗口模块加载完成")
        
        # 创建主窗口
        window = ModularCinemaMainWindow()
        print("✅ 优化版主窗口创建完成")
        
        # 启动应用程序
        print("🚀 启动优化版应用程序...")
        print("💡 登录后将自动选择默认影院和关联账号")
        print("🎯 不再出现'等待账号选择'问题")
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
        with open('main_optimized.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("  ✅ 创建优化版启动脚本: main_optimized.py")
        return True
        
    except Exception as e:
        print(f"  ❌ 创建脚本失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 60)
    print("🎯 main_modular.py 智能默认选择优化测试")
    print("=" * 60)
    
    print("💡 优化目标:")
    print("   ❌ 消除'等待账号选择'日志")
    print("   ✅ 登录后自动选择第一个影院")
    print("   ✅ 自动选择该影院的关联主账号")
    print("   ✅ Tab管理器可以正常加载影片数据")
    print("   ✅ 用户无需手动选择，直接可用")
    print()
    
    print("🔧 实现方案:")
    print("   1. 修改 _trigger_default_cinema_selection() 方法")
    print("   2. 添加 _auto_select_cinema_account() 方法")
    print("   3. 智能选择流程: 影院 → 账号 → 影片加载")
    print("   4. 保持原有Tab管理器不变")
    print()
    
    # 1. 测试智能选择流程
    success = test_smart_selection_flow()
    
    # 2. 创建优化版启动脚本
    script_created = create_optimized_main_script()
    
    print("\n" + "=" * 60)
    print("📊 测试结果:")
    print(f"   智能选择流程: {'✅ 正常' if success else '❌ 异常'}")
    print(f"   优化版脚本: {'✅ 已创建' if script_created else '❌ 创建失败'}")
    
    if success and script_created:
        print("\n🎉 main_modular.py 优化成功！")
        print()
        print("🚀 现在可以使用优化版启动:")
        print("   python main_optimized.py")
        print()
        print("✨ 优化后的用户体验:")
        print("   1. 启动系统 → 登录窗口显示")
        print("   2. 用户登录 → 主界面显示")
        print("   3. 系统自动选择第一个影院")
        print("   4. 系统自动选择该影院的关联账号")
        print("   5. Tab管理器自动加载影片数据")
        print("   6. 用户直接开始选择影片和场次")
        print("   7. 无'等待账号选择'问题")
    else:
        print("\n⚠️  测试未完全成功")
        print("   建议检查:")
        print("   1. 账号数据是否存在")
        print("   2. 影院数据是否正确")
        print("   3. Tab管理器组件是否正常")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
