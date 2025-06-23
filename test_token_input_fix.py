#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Token输入框修复
验证Token输入框改为普通文本模式后的用户体验
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TokenInputTestWindow(QMainWindow):
    """Token输入测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Token输入框修复测试")
        self.setGeometry(300, 200, 500, 800)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 添加标题
        title_label = QLabel("Token输入框修复测试")
        title_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 添加说明
        info_label = QLabel("修复内容：\n• 移除密码模式，改为普通文本模式\n• 移除显示/隐藏Token切换按钮\n• 用户可以正常查看、复制粘贴Token")
        info_label.setFont(QFont("微软雅黑", 10))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 导入并创建账号组件
        try:
            from ui.widgets.account_widget import AccountWidget
            
            # 创建账号组件
            self.account_widget = AccountWidget()
            layout.addWidget(self.account_widget)
            
            # 连接信号进行测试
            self.account_widget.account_selected.connect(self.on_account_selected)
            self.account_widget.account_login_requested.connect(self.on_account_login_requested)
            self.account_widget.accounts_refreshed.connect(self.on_accounts_refreshed)
            
            print(f"[测试] ✅ 账号组件加载成功")
            
        except Exception as e:
            error_label = QLabel(f"❌ 加载账号组件失败: {e}")
            error_label.setStyleSheet("color: red; padding: 10px;")
            layout.addWidget(error_label)
            print(f"[测试] ❌ 账号组件加载失败: {e}")
        
        # 添加测试按钮
        test_layout = QVBoxLayout()
        
        # 自动填充测试Token按钮
        fill_test_btn = QPushButton("填充测试Token")
        fill_test_btn.setFont(QFont("微软雅黑", 10))
        fill_test_btn.clicked.connect(self.fill_test_token)
        test_layout.addWidget(fill_test_btn)
        
        # 清空输入按钮
        clear_btn = QPushButton("清空输入")
        clear_btn.setFont(QFont("微软雅黑", 10))
        clear_btn.clicked.connect(self.clear_inputs)
        test_layout.addWidget(clear_btn)
        
        # 检查Token可见性按钮
        check_visibility_btn = QPushButton("检查Token可见性")
        check_visibility_btn.setFont(QFont("微软雅黑", 10))
        check_visibility_btn.clicked.connect(self.check_token_visibility)
        test_layout.addWidget(check_visibility_btn)
        
        layout.addLayout(test_layout)
        
        # 测试结果显示
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
        print(f"[测试] 测试窗口初始化完成")
    
    def fill_test_token(self):
        """填充测试Token"""
        try:
            if hasattr(self, 'account_widget'):
                # 填充测试数据
                test_phone = "15155712316"
                test_token = "dc028617920fcca58086940d7b6b76c3"
                
                self.account_widget.phone_input.setText(test_phone)
                self.account_widget.token_input.setText(test_token)
                
                print(f"[测试] ✅ 已填充测试数据")
                print(f"[测试] 📋 手机号: {test_phone}")
                print(f"[测试] 📋 Token: {test_token}")
                
                self.result_label.setText(f"✅ 已填充测试数据\n手机号: {test_phone}\nToken: {test_token}")
            else:
                self.result_label.setText("❌ 账号组件未加载")
                
        except Exception as e:
            error_msg = f"❌ 填充测试数据失败: {e}"
            print(f"[测试] {error_msg}")
            self.result_label.setText(error_msg)
    
    def clear_inputs(self):
        """清空输入"""
        try:
            if hasattr(self, 'account_widget'):
                self.account_widget.phone_input.clear()
                self.account_widget.token_input.clear()
                
                print(f"[测试] ✅ 输入已清空")
                self.result_label.setText("✅ 输入已清空")
            else:
                self.result_label.setText("❌ 账号组件未加载")
                
        except Exception as e:
            error_msg = f"❌ 清空输入失败: {e}"
            print(f"[测试] {error_msg}")
            self.result_label.setText(error_msg)
    
    def check_token_visibility(self):
        """检查Token可见性"""
        try:
            if hasattr(self, 'account_widget'):
                token_input = self.account_widget.token_input
                
                # 检查回显模式
                echo_mode = token_input.echoMode()
                echo_mode_name = {
                    0: "Normal (普通文本)",
                    1: "NoEcho (无回显)",
                    2: "Password (密码模式)",
                    3: "PasswordEchoOnEdit (编辑时显示密码)"
                }.get(echo_mode, f"Unknown ({echo_mode})")
                
                # 获取当前文本
                current_text = token_input.text()
                text_length = len(current_text)
                
                # 检查是否有显示/隐藏按钮
                has_toggle_btn = hasattr(self.account_widget, 'token_toggle_btn')
                
                result_text = f"""Token输入框状态检查:
✅ 回显模式: {echo_mode_name}
✅ 当前文本长度: {text_length}字符
✅ 文本内容可见: {'是' if echo_mode == 0 else '否'}
✅ 显示/隐藏按钮: {'存在' if has_toggle_btn else '已移除'}

当前Token内容预览:
{current_text[:50]}{'...' if text_length > 50 else ''}"""
                
                print(f"[测试] 📋 Token可见性检查:")
                print(f"[测试] 📋 回显模式: {echo_mode_name}")
                print(f"[测试] 📋 文本长度: {text_length}")
                print(f"[测试] 📋 显示/隐藏按钮: {'存在' if has_toggle_btn else '已移除'}")
                
                self.result_label.setText(result_text)
                
                # 验证修复是否成功
                if echo_mode == 0 and not has_toggle_btn:
                    print(f"[测试] ✅ Token输入框修复成功！")
                else:
                    print(f"[测试] ❌ Token输入框修复不完整")
                    
            else:
                self.result_label.setText("❌ 账号组件未加载")
                
        except Exception as e:
            error_msg = f"❌ 检查Token可见性失败: {e}"
            print(f"[测试] {error_msg}")
            self.result_label.setText(error_msg)
    
    def on_account_selected(self, account_data):
        """账号选择信号处理"""
        print(f"[测试] 📋 账号选择信号: {account_data}")
    
    def on_account_login_requested(self, login_data):
        """登录请求信号处理"""
        print(f"[测试] 📋 登录请求信号: {login_data}")
    
    def on_accounts_refreshed(self, accounts_list):
        """账号刷新信号处理"""
        print(f"[测试] 📋 账号刷新信号: {len(accounts_list)} 个账号")

def test_token_input_functionality():
    """测试Token输入功能"""
    print("🧪 测试Token输入框修复")
    print("=" * 60)
    print("📋 修复内容:")
    print("  1. 移除密码模式，改为普通文本模式")
    print("  2. 移除显示/隐藏Token切换按钮")
    print("  3. 用户可以正常查看、复制粘贴Token")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TokenInputTestWindow()
    window.show()
    
    # 自动测试Token可见性
    def auto_check():
        print(f"\n🔄 自动检查Token输入框状态...")
        window.check_token_visibility()
    
    # 3秒后自动检查
    QTimer.singleShot(3000, auto_check)
    
    print(f"✅ 测试窗口已显示，3秒后自动检查Token输入框状态")
    print(f"📋 您可以手动测试以下功能:")
    print(f"  1. 点击'填充测试Token'按钮")
    print(f"  2. 观察Token是否可见")
    print(f"  3. 尝试复制粘贴Token内容")
    print(f"  4. 点击'检查Token可见性'查看详细状态")
    
    # 运行应用
    sys.exit(app.exec_())

def test_echo_mode_comparison():
    """测试回显模式对比"""
    print("\n🧪 测试回显模式对比")
    print("=" * 60)
    
    echo_modes = {
        0: "Normal - 普通文本模式（推荐用于Token）",
        1: "NoEcho - 无回显模式",
        2: "Password - 密码模式（修复前的问题模式）",
        3: "PasswordEchoOnEdit - 编辑时显示密码模式"
    }
    
    print(f"📋 QLineEdit回显模式说明:")
    for mode, desc in echo_modes.items():
        print(f"  {mode}: {desc}")
    
    print(f"\n📋 Token输入的最佳实践:")
    print(f"  ✅ 使用Normal模式 - 用户可以看到完整Token内容")
    print(f"  ✅ 支持复制粘贴操作")
    print(f"  ✅ 便于用户验证Token正确性")
    print(f"  ✅ 调试时可以查看Token内容")
    
    print(f"\n📋 密码模式的问题:")
    print(f"  ❌ 用户无法确认Token是否输入正确")
    print(f"  ❌ 复制粘贴操作无法可视化确认")
    print(f"  ❌ 调试困难")
    print(f"  ❌ Token不需要像密码那样严格隐藏")
    
    print(f"\n✅ 回显模式对比测试完成")

def main():
    print("🎬 沃美电影票务系统 - Token输入框修复测试")
    print("=" * 60)
    print("📋 测试目标：验证Token输入框修复后的用户体验")
    print("🔍 测试内容：")
    print("  1. 回显模式对比测试")
    print("  2. Token输入功能测试")
    print("=" * 60)
    
    # 先进行理论对比
    test_echo_mode_comparison()
    
    # 再进行实际功能测试
    print(f"\n🚀 开始Token输入功能测试...")
    test_token_input_functionality()

if __name__ == "__main__":
    main()
