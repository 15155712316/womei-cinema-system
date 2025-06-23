#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试Token输入框问题
检查Token输入框是否真的无法输入
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TokenInputDebugWindow(QMainWindow):
    """Token输入调试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Token输入框调试")
        self.setGeometry(300, 200, 600, 500)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("Token输入框调试测试")
        title_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 测试1：标准QLineEdit
        layout.addWidget(QLabel("测试1：标准QLineEdit"))
        self.standard_input = QLineEdit()
        self.standard_input.setPlaceholderText("标准QLineEdit - 请输入Token")
        layout.addWidget(self.standard_input)
        
        # 测试2：ClassicLineEdit
        layout.addWidget(QLabel("测试2：ClassicLineEdit"))
        try:
            from ui.widgets.classic_components import ClassicLineEdit
            self.classic_input = ClassicLineEdit("ClassicLineEdit - 请输入Token")
            layout.addWidget(self.classic_input)
            print(f"[调试] ✅ ClassicLineEdit加载成功")
        except Exception as e:
            error_label = QLabel(f"❌ ClassicLineEdit加载失败: {e}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)
            self.classic_input = None
            print(f"[调试] ❌ ClassicLineEdit加载失败: {e}")
        
        # 测试3：AccountWidget中的Token输入框
        layout.addWidget(QLabel("测试3：AccountWidget中的Token输入框"))
        try:
            from ui.widgets.account_widget import AccountWidget
            self.account_widget = AccountWidget()
            
            # 只显示Token输入框部分
            token_widget = QWidget()
            token_layout = QVBoxLayout(token_widget)
            token_layout.addWidget(QLabel("从AccountWidget提取的Token输入框:"))
            token_layout.addWidget(self.account_widget.token_input)
            layout.addWidget(token_widget)
            
            print(f"[调试] ✅ AccountWidget加载成功")
        except Exception as e:
            error_label = QLabel(f"❌ AccountWidget加载失败: {e}")
            error_label.setStyleSheet("color: red;")
            layout.addWidget(error_label)
            self.account_widget = None
            print(f"[调试] ❌ AccountWidget加载失败: {e}")
        
        # 测试按钮
        test_layout = QVBoxLayout()
        
        # 检查输入状态按钮
        check_btn = QPushButton("检查所有输入框状态")
        check_btn.clicked.connect(self.check_input_status)
        test_layout.addWidget(check_btn)
        
        # 填充测试数据按钮
        fill_btn = QPushButton("填充测试Token")
        fill_btn.clicked.connect(self.fill_test_data)
        test_layout.addWidget(fill_btn)
        
        # 清空所有输入按钮
        clear_btn = QPushButton("清空所有输入")
        clear_btn.clicked.connect(self.clear_all_inputs)
        test_layout.addWidget(clear_btn)
        
        layout.addLayout(test_layout)
        
        # 结果显示
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
        print(f"[调试] 调试窗口初始化完成")
    
    def check_input_status(self):
        """检查所有输入框状态"""
        try:
            results = []
            
            # 检查标准QLineEdit
            standard_text = self.standard_input.text()
            standard_enabled = self.standard_input.isEnabled()
            standard_readonly = self.standard_input.isReadOnly()
            results.append(f"标准QLineEdit:")
            results.append(f"  文本: '{standard_text}' ({len(standard_text)}字符)")
            results.append(f"  启用: {standard_enabled}")
            results.append(f"  只读: {standard_readonly}")
            
            # 检查ClassicLineEdit
            if self.classic_input:
                classic_text = self.classic_input.text()
                classic_enabled = self.classic_input.isEnabled()
                classic_readonly = self.classic_input.isReadOnly()
                classic_echo = self.classic_input.echoMode()
                results.append(f"\nClassicLineEdit:")
                results.append(f"  文本: '{classic_text}' ({len(classic_text)}字符)")
                results.append(f"  启用: {classic_enabled}")
                results.append(f"  只读: {classic_readonly}")
                results.append(f"  回显模式: {classic_echo} ({'Normal' if classic_echo == 0 else 'Other'})")
            
            # 检查AccountWidget中的Token输入框
            if self.account_widget:
                token_text = self.account_widget.token_input.text()
                token_enabled = self.account_widget.token_input.isEnabled()
                token_readonly = self.account_widget.token_input.isReadOnly()
                token_echo = self.account_widget.token_input.echoMode()
                token_maxlength = self.account_widget.token_input.maxLength()
                results.append(f"\nAccountWidget Token输入框:")
                results.append(f"  文本: '{token_text}' ({len(token_text)}字符)")
                results.append(f"  启用: {token_enabled}")
                results.append(f"  只读: {token_readonly}")
                results.append(f"  回显模式: {token_echo} ({'Normal' if token_echo == 0 else 'Other'})")
                results.append(f"  最大长度: {token_maxlength} ({'无限制' if token_maxlength == 0 else '有限制'})")
            
            result_text = "\n".join(results)
            self.result_label.setText(result_text)
            
            print(f"[调试] 📋 输入框状态检查:")
            for line in results:
                print(f"[调试] {line}")
                
        except Exception as e:
            error_msg = f"❌ 检查输入框状态失败: {e}"
            print(f"[调试] {error_msg}")
            self.result_label.setText(error_msg)
    
    def fill_test_data(self):
        """填充测试数据"""
        try:
            test_token = "dc028617920fcca58086940d7b6b76c3"
            
            # 填充标准QLineEdit
            self.standard_input.setText(test_token)
            print(f"[调试] ✅ 标准QLineEdit已填充")
            
            # 填充ClassicLineEdit
            if self.classic_input:
                self.classic_input.setText(test_token)
                print(f"[调试] ✅ ClassicLineEdit已填充")
            
            # 填充AccountWidget中的Token输入框
            if self.account_widget:
                self.account_widget.token_input.setText(test_token)
                print(f"[调试] ✅ AccountWidget Token输入框已填充")
            
            self.result_label.setText(f"✅ 已填充测试Token: {test_token}")
            
        except Exception as e:
            error_msg = f"❌ 填充测试数据失败: {e}"
            print(f"[调试] {error_msg}")
            self.result_label.setText(error_msg)
    
    def clear_all_inputs(self):
        """清空所有输入"""
        try:
            # 清空标准QLineEdit
            self.standard_input.clear()
            
            # 清空ClassicLineEdit
            if self.classic_input:
                self.classic_input.clear()
            
            # 清空AccountWidget中的Token输入框
            if self.account_widget:
                self.account_widget.token_input.clear()
            
            self.result_label.setText("✅ 所有输入框已清空")
            print(f"[调试] ✅ 所有输入框已清空")
            
        except Exception as e:
            error_msg = f"❌ 清空输入失败: {e}"
            print(f"[调试] {error_msg}")
            self.result_label.setText(error_msg)

def main():
    print("🔍 Token输入框调试测试")
    print("=" * 60)
    print("📋 测试目标：调试Token输入框无法输入的问题")
    print("🔍 测试内容：")
    print("  1. 标准QLineEdit输入测试")
    print("  2. ClassicLineEdit输入测试")
    print("  3. AccountWidget Token输入框测试")
    print("  4. 输入框状态检查")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建调试窗口
    window = TokenInputDebugWindow()
    window.show()
    
    # 自动检查输入框状态
    def auto_check():
        print(f"\n🔄 自动检查输入框状态...")
        window.check_input_status()
    
    # 3秒后自动检查
    QTimer.singleShot(3000, auto_check)
    
    print(f"✅ 调试窗口已显示，3秒后自动检查输入框状态")
    print(f"📋 您可以手动测试以下功能:")
    print(f"  1. 尝试在各个输入框中输入文字")
    print(f"  2. 点击'检查所有输入框状态'查看详细信息")
    print(f"  3. 点击'填充测试Token'自动填充")
    print(f"  4. 观察哪个输入框无法正常工作")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
