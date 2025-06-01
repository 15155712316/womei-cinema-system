#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复原版本的账号自动选择功能
"""

import sys
import os


def add_auto_account_selection():
    """为Tab管理器添加自动账号选择功能"""
    
    print("🔧 修复Tab管理器的账号自动选择...")
    
    # 读取Tab管理器文件
    tab_manager_file = "ui/widgets/tab_manager_widget.py"
    
    if not os.path.exists(tab_manager_file):
        print(f"❌ 文件不存在: {tab_manager_file}")
        return False
    
    try:
        with open(tab_manager_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已经有自动选择功能
        if "_auto_select_first_account" in content:
            print("✅ 自动账号选择功能已存在")
            return True
        
        # 添加自动账号选择方法
        auto_select_method = '''
    def _auto_select_first_account(self):
        """自动选择第一个可用账号"""
        try:
            from services.account_manager import account_manager
            
            # 获取账号列表
            accounts = account_manager.load_account_list()
            
            if accounts:
                first_account = accounts[0]
                self.current_account = first_account
                
                print(f"[Tab管理器] 自动选择账号: {first_account.get('userid', 'N/A')}")
                
                # 发布账号选择事件
                from utils.signals import event_bus
                event_bus.account_changed.emit(first_account)
                
                return True
            else:
                print("[Tab管理器] 没有可用账号")
                return False
                
        except Exception as e:
            print(f"[Tab管理器] 自动选择账号失败: {e}")
            return False
'''
        
        # 在类定义中添加方法
        class_pattern = "class TabManagerWidget"
        if class_pattern in content:
            # 找到类定义的位置，在适当位置插入方法
            lines = content.split('\n')
            new_lines = []
            
            for i, line in enumerate(lines):
                new_lines.append(line)
                
                # 在 __init__ 方法后添加自动选择方法
                if "def __init__(self" in line and "TabManagerWidget" in lines[max(0, i-10):i+1]:
                    # 找到 __init__ 方法的结束位置
                    indent_level = len(line) - len(line.lstrip())
                    j = i + 1
                    while j < len(lines):
                        if lines[j].strip() and not lines[j].startswith(' ' * (indent_level + 4)):
                            break
                        j += 1
                    
                    # 在这里插入自动选择方法
                    new_lines.extend(auto_select_method.split('\n'))
                    break
            
            # 修改 _check_and_load_movies 方法
            modified_content = '\n'.join(new_lines)
            
            # 替换等待账号选择的逻辑
            old_check_logic = '''if not self.current_account:
                print("[Tab管理器] 等待账号选择...")
                self.movie_combo.clear()
                self.movie_combo.addItem("等待账号选择...")
                
                # 🆕 只延迟检查一次，避免无限循环
                QTimer.singleShot(1000, lambda: self._final_check_and_load_movies(selected_cinema))
                return'''
            
            new_check_logic = '''if not self.current_account:
                print("[Tab管理器] 尝试自动选择账号...")
                if self._auto_select_first_account():
                    # 账号选择成功，继续加载影片
                    print(f"[Tab管理器] 账号已自动选择: {self.current_account.get('userid', 'N/A')}")
                else:
                    # 没有可用账号
                    print("[Tab管理器] 没有可用账号，等待手动选择...")
                    self.movie_combo.clear()
                    self.movie_combo.addItem("请先添加账号")
                    return'''
            
            modified_content = modified_content.replace(old_check_logic, new_check_logic)
            
            # 写回文件
            with open(tab_manager_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print("✅ Tab管理器自动账号选择功能已添加")
            return True
        else:
            print("❌ 未找到TabManagerWidget类定义")
            return False
            
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False


def create_enhanced_startup_script():
    """创建增强版启动脚本"""
    
    print("📝 创建增强版启动脚本...")
    
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
柴犬影院下单系统 - 原版本增强版 (自动账号选择)
"""

import sys
import os

def main():
    """主程序入口 - 原版本增强版"""
    print("=" * 60)
    print("🎬 柴犬影院下单系统 - 原版本增强版")
    print("=" * 60)
    print("🏗️  架构: 单体架构 + Tab管理器")
    print("🎨  界面: 传统PyQt5界面")
    print("🔧  特性: 完整功能 + 自动账号选择")
    print("✨  增强: 解决\"等待账号选择\"问题")
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
        app.setApplicationName("柴犬影院下单系统-增强版")
        app.setApplicationVersion("1.5.0")
        app.setOrganizationName("柴犬影院")
        
        # 设置默认字体
        default_font = QFont("Microsoft YaHei", 10)
        app.setFont(default_font)
        
        print("✅ 应用程序初始化完成")
        
        # 导入原版本主窗口
        from main_modular import MainWindow
        print("✅ 原版本主窗口模块加载完成")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        print("✅ 原版本主窗口创建完成")
        
        # 启动应用程序
        print("🚀 启动增强版应用程序...")
        print("✨ 现在会自动选择第一个可用账号")
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
        with open('main_original_enhanced.py', 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print("✅ 创建增强版启动脚本: main_original_enhanced.py")
        return True
        
    except Exception as e:
        print(f"❌ 创建脚本失败: {e}")
        return False


def main():
    """主修复函数"""
    print("=" * 60)
    print("🔧 修复原版本的账号自动选择功能")
    print("=" * 60)
    
    print("💡 修复目标:")
    print("   - 消除\"等待账号选择\"日志")
    print("   - 自动选择第一个可用账号")
    print("   - 保持原版本的完整功能")
    print()
    
    # 1. 添加自动账号选择功能
    auto_select_added = add_auto_account_selection()
    
    # 2. 创建增强版启动脚本
    script_created = create_enhanced_startup_script()
    
    print("\n" + "=" * 60)
    print("📊 修复结果:")
    print(f"   自动选择功能: {'✅ 已添加' if auto_select_added else '❌ 添加失败'}")
    print(f"   增强版脚本: {'✅ 已创建' if script_created else '❌ 创建失败'}")
    
    if auto_select_added and script_created:
        print("\n🎉 修复完成！现在有两个选择:")
        print()
        print("📋 选择1: 重构版本 (推荐新用户)")
        print("   启动: python main_refactored_clean.py")
        print("   特点: 简洁、稳定、现代化界面")
        print()
        print("📋 选择2: 原版本增强版 (推荐老用户)")
        print("   启动: python main_original_enhanced.py")
        print("   特点: 完整功能、自动账号选择、Tab管理器")
        print()
        print("💡 两个版本都解决了\"等待账号选择\"问题")
    else:
        print("\n❌ 修复未完全成功，建议使用重构版本:")
        print("   python main_refactored_clean.py")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
