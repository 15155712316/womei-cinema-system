#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复沃美影院系统账号选择和分发问题
"""

def analyze_account_flow():
    """分析账号信息流转问题"""
    print("🔍 分析沃美影院系统账号信息流转问题")
    print("=" * 60)
    
    print("📋 当前账号信息流转路径:")
    print("1. AccountWidget 自动选择第一个账号")
    print("2. AccountWidget 发出 account_selected 信号")
    print("3. 主窗口接收信号 → _on_account_selected → set_current_account")
    print("4. 主窗口发布全局事件 → event_bus.account_changed.emit")
    print("5. Tab管理器接收事件 → _on_account_changed → 更新 current_account")
    
    print("\n❌ 发现的问题:")
    print("1. 座位提交时显示'选择账号'对话框 → current_account 为空")
    print("2. 影院选择区域显示'当前账号未选择' → UI状态未更新")
    print("3. 账号信息在各组件间同步失败")
    
    print("\n🔧 需要修复的地方:")
    print("1. 确保AccountWidget正确发出账号选择信号")
    print("2. 确保主窗口正确接收并处理账号信号")
    print("3. 确保Tab管理器正确接收全局账号事件")
    print("4. 确保UI状态正确更新")
    print("5. 添加账号信息验证和调试日志")

def create_account_debug_test():
    """创建账号调试测试"""
    print("\n🧪 创建账号调试测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号信息流转调试测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QTimer
from ui.widgets.account_widget import AccountWidget
from ui.widgets.tab_manager_widget import TabManagerWidget
from utils.signals import event_bus

class AccountDebugWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("账号信息流转调试")
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中央组件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 创建账号组件
        print("🚀 创建账号组件...")
        self.account_widget = AccountWidget()
        layout.addWidget(self.account_widget)
        
        # 创建Tab管理器
        print("🚀 创建Tab管理器...")
        self.tab_manager = TabManagerWidget()
        layout.addWidget(self.tab_manager)
        
        # 创建调试按钮
        self.debug_button = QPushButton("检查账号状态")
        self.debug_button.clicked.connect(self.check_account_status)
        layout.addWidget(self.debug_button)
        
        # 连接信号
        self.account_widget.account_selected.connect(self.on_account_selected)
        
        # 延迟检查
        QTimer.singleShot(2000, self.initial_check)
        QTimer.singleShot(5000, self.final_check)
    
    def on_account_selected(self, account_data):
        """账号选择处理"""
        print(f"\\n📱 主窗口接收到账号选择信号:")
        print(f"  - 账号: {account_data.get('phone', 'N/A')}")
        print(f"  - Token: {account_data.get('token', '')[:20]}...")
        
        # 发布全局事件
        event_bus.account_changed.emit(account_data)
        print(f"✅ 已发布全局账号变更事件")
    
    def check_account_status(self):
        """检查账号状态"""
        print(f"\\n🔍 检查账号状态:")
        
        # 检查账号组件
        if hasattr(self.account_widget, 'current_account'):
            account = self.account_widget.current_account
            print(f"  - 账号组件: {account.get('phone') if account else 'None'}")
        else:
            print(f"  - 账号组件: 无current_account属性")
        
        # 检查Tab管理器
        if hasattr(self.tab_manager, 'current_account'):
            account = self.tab_manager.current_account
            print(f"  - Tab管理器: {account.get('phone') if account else 'None'}")
        else:
            print(f"  - Tab管理器: 无current_account属性")
        
        # 检查UI显示
        if hasattr(self.tab_manager, 'current_account_label'):
            label_text = self.tab_manager.current_account_label.text()
            print(f"  - UI显示: {label_text}")
        else:
            print(f"  - UI显示: 无current_account_label")
    
    def initial_check(self):
        """初始检查"""
        print(f"\\n⏰ 初始检查（2秒后）:")
        self.check_account_status()
    
    def final_check(self):
        """最终检查"""
        print(f"\\n⏰ 最终检查（5秒后）:")
        self.check_account_status()

def main():
    app = QApplication(sys.argv)
    window = AccountDebugWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
'''
    
    with open("test_account_debug.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("✅ 账号调试测试脚本已创建: test_account_debug.py")

def create_fix_plan():
    """创建修复计划"""
    print("\n📋 账号分发问题修复计划:")
    print("=" * 60)
    
    fixes = [
        {
            "问题": "座位提交时显示'选择账号'对话框",
            "原因": "Tab管理器的current_account为空",
            "修复": "确保账号信息正确传递到Tab管理器",
            "文件": "ui/widgets/tab_manager_widget.py",
            "方法": "_on_submit_order"
        },
        {
            "问题": "影院选择区域显示'当前账号未选择'",
            "原因": "UI状态未正确更新",
            "修复": "确保_on_account_changed方法正确更新UI",
            "文件": "ui/widgets/tab_manager_widget.py", 
            "方法": "_on_account_changed"
        },
        {
            "问题": "账号信息在组件间同步失败",
            "原因": "事件总线连接或时序问题",
            "修复": "增强事件连接和错误处理",
            "文件": "main_modular.py",
            "方法": "set_current_account"
        },
        {
            "问题": "调试模式下账号加载时序问题",
            "原因": "组件初始化顺序导致信号丢失",
            "修复": "添加延迟重试和状态检查",
            "文件": "main_modular.py",
            "方法": "_send_debug_account_info"
        }
    ]
    
    for i, fix in enumerate(fixes, 1):
        print(f"修复 {i}: {fix['问题']}")
        print(f"  原因: {fix['原因']}")
        print(f"  修复: {fix['修复']}")
        print(f"  文件: {fix['文件']}")
        print(f"  方法: {fix['方法']}")
        print()

def main():
    """主函数"""
    print("🔧 沃美影院系统账号选择和分发问题修复工具")
    print("=" * 60)
    
    # 分析问题
    analyze_account_flow()
    
    # 创建调试测试
    create_account_debug_test()
    
    # 创建修复计划
    create_fix_plan()
    
    print("🎯 下一步操作:")
    print("1. 运行调试测试: python test_account_debug.py")
    print("2. 观察账号信息流转过程")
    print("3. 根据测试结果实施具体修复")
    print("4. 验证修复效果")

if __name__ == "__main__":
    main()
