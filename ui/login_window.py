#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户登录窗口
"""

import sys
import os
import json
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFrame, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QClipboard

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import auth_service
from services.ui_utils import MessageManager, UIConstants

class LoginThread(QThread):
    """登录验证线程"""
    login_result = pyqtSignal(bool, str, object)  # 是否成功, 消息, 用户信息
    
    def __init__(self, phone: str):
        super().__init__()
        self.phone = phone
    
    def run(self):
        """执行登录验证"""
        try:
            success, message, user_info = auth_service.login(self.phone)
            self.login_result.emit(success, message, user_info)
        except Exception as e:
            self.login_result.emit(False, f"登录异常: {str(e)}", None)

class LoginWindow(QWidget):
    """用户登录窗口"""
    
    # 信号定义
    login_success = pyqtSignal(dict)  # 登录成功信号，传递用户信息
    
    def __init__(self):
        super().__init__()
        self.login_thread = None
        self.machine_code = auth_service.get_machine_code()  # 预先获取机器码
        self.login_history_file = "data/login_history.json"  # 登录历史文件
        self.auto_login_prevented = False  # 防止自动登录标志

        # 输出机器码信息，方便用户确认
        print(f"[机器码生成] 当前设备机器码: {self.machine_code}")
        print(f"[登录窗口] 机器码已显示在界面上，可点击复制按钮复制")

        self.init_ui()
        self.load_login_history()  # 加载登录历史

        # 直接启用登录功能
        self.auto_login_prevented = True
        print("[登录窗口] 登录功能已启用")

    def _safe_login(self):
        """安全登录方法 - 防止意外触发"""
        print("[登录窗口] _safe_login() 被调用")

        # 额外的安全检查
        if not self.auto_login_prevented:
            print("[登录窗口] 安全检查：登录功能尚未启用，忽略回车键")
            return

        if not self.login_button.isEnabled():
            print("[登录窗口] 安全检查：登录按钮未启用，忽略回车键")
            return

        print("[登录窗口] 安全检查通过，执行登录")
        self.login()

    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("乐影票务系统 - 用户登录")
        self.setFixedSize(380, 480)  # 再次减少高度
        self.setWindowFlags(Qt.WindowCloseButtonHint)  # 只显示关闭按钮
        
        # 设置窗口居中
        self.center_window()
        
        # 创建主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(18)  # 进一步减少间距
        main_layout.setContentsMargins(35, 30, 35, 30)
        
        # 标题
        title_label = QLabel("乐影票务系统")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("微软雅黑", 22, QFont.Bold))  # 稍微减小字体
        title_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a; 
                background-color: transparent;
                margin: 0px;
                padding: 10px 0px;
            }
        """)
        title_label.setFixedHeight(50)  # 固定高度确保完整显示
        
        # 手机号输入框
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入11位手机号")
        self.phone_input.setStyleSheet("""
            QLineEdit {
                padding: 16px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 15px;
                background-color: white;
                min-height: 20px;
                color: #333;
            }
            QLineEdit:focus {
                border-color: #3498db;
                outline: none;
            }
            QLineEdit:hover {
                border-color: #bbb;
            }
        """)
        self.phone_input.setFont(QFont("微软雅黑", 13))
        self.phone_input.setMaxLength(11)
        
        # 回车键登录 - 延迟连接，防止自动触发
        # self.phone_input.returnPressed.connect(self.login)  # 暂时禁用
        self.phone_input.returnPressed.connect(self._safe_login)
        
        # 登录按钮
        self.login_button = QPushButton("登 录")
        self.login_button.setFont(QFont("微软雅黑", 15, QFont.Bold))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 18px;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.login_button.clicked.connect(self.login)
        
        # 进度条（登录时显示）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-size: 11px;
                max-height: 22px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 5px;
            }
        """)
        
        # 机器码显示区域 - 直接添加，不要空白间隔
        machine_code_label = QLabel("设备机器码验证")
        machine_code_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
        machine_code_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a; 
                background-color: transparent;
                margin: 15px 0px 5px 0px;
                padding: 0px;
            }
        """)
        machine_code_label.setAlignment(Qt.AlignCenter)
        
        # 机器码说明
        machine_code_info = QLabel("当前设备机器码如下，管理员需将此码录入系统后方可登录")
        machine_code_info.setFont(QFont("微软雅黑", 9))
        machine_code_info.setStyleSheet("""
            QLabel {
                color: #666; 
                background-color: transparent;
                margin: 0px 5px 8px 5px;
                padding: 0px;
            }
        """)
        machine_code_info.setAlignment(Qt.AlignCenter)
        machine_code_info.setWordWrap(True)
        
        # 机器码显示文本框（只读，可选中复制）
        self.machine_code_display = QTextEdit()
        self.machine_code_display.setPlainText(self.machine_code)
        self.machine_code_display.setFont(QFont("Consolas", 11))
        self.machine_code_display.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 12px;
                color: #333;
                line-height: 1.2;
                font-weight: bold;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        self.machine_code_display.setReadOnly(True)
        self.machine_code_display.setFixedHeight(65)  # 稍微增加高度
        self.machine_code_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.machine_code_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 复制按钮
        copy_button = QPushButton("📋 复制机器码")
        copy_button.setFont(QFont("微软雅黑", 10))
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 11px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #495057;
            }
        """)
        copy_button.clicked.connect(self.copy_machine_code)
        
        # 布局组装 - 去掉空白间隔
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.phone_input)
        main_layout.addWidget(self.login_button)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(machine_code_label)  # 标题
        main_layout.addWidget(machine_code_info)   # 说明文字
        main_layout.addWidget(self.machine_code_display)
        main_layout.addWidget(copy_button)
        main_layout.addStretch()  # 底部留少量空白
        
        self.setLayout(main_layout)
        
        # 设置默认焦点到手机号输入框
        QTimer.singleShot(100, lambda: self.phone_input.setFocus())
        
        # 设置窗口样式
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
            }
        """)
    
    def load_login_history(self):
        """加载登录历史，自动填入上次登录的手机号"""
        try:
            # 确保data目录存在
            os.makedirs("data", exist_ok=True)
            
            if os.path.exists(self.login_history_file):
                with open(self.login_history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    last_phone = history.get('last_phone', '')
                    if last_phone and len(last_phone) == 11:
                        self.phone_input.setText(last_phone)
                        print(f"[登录历史] 已自动填入上次登录手机号: {last_phone}")
        except Exception as e:
            print(f"[登录历史] 加载登录历史失败: {e}")
    
    def save_login_history(self, phone: str):
        """保存登录历史"""
        try:
            # 确保data目录存在
            os.makedirs("data", exist_ok=True)
            
            # 修复：使用datetime模块获取当前时间
            import datetime
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            history = {
                'last_phone': phone,
                'last_login_time': current_time
            }
            
            with open(self.login_history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
            
            print(f"[登录历史] 已保存登录历史: {phone} at {current_time}")
        except Exception as e:
            print(f"[登录历史] 保存登录历史失败: {e}")
    
    def center_window(self):
        """窗口居中显示 - 确保在主屏幕"""
        try:
            # 获取主屏幕的几何信息
            desktop = QApplication.desktop()
            screen_rect = desktop.availableGeometry(desktop.primaryScreen())

            # 获取窗口大小
            window_size = self.size()

            # 计算中央位置
            x = screen_rect.x() + (screen_rect.width() - window_size.width()) // 2
            y = screen_rect.y() + (screen_rect.height() - window_size.height()) // 2

            # 确保窗口完全在屏幕内
            x = max(screen_rect.x(), min(x, screen_rect.x() + screen_rect.width() - window_size.width()))
            y = max(screen_rect.y(), min(y, screen_rect.y() + screen_rect.height() - window_size.height()))

            self.move(x, y)
            print(f"[登录窗口] 窗口已居中到主屏幕: ({x}, {y})")
            print(f"[登录窗口] 主屏幕范围: {screen_rect}")

        except Exception as e:
            print(f"[登录窗口] 居中窗口失败: {e}")
            # 备用方案：移动到安全位置
            self.move(100, 100)
    
    def copy_machine_code(self):
        """复制机器码到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_code)
        
        # 临时改变按钮文本提示复制成功
        copy_button = self.sender()
        original_text = copy_button.text()
        original_style = copy_button.styleSheet()
        
        # 设置成功状态
        copy_button.setText("✅ 已复制!")
        success_style = original_style.replace("#6c757d", "#28a745")
        copy_button.setStyleSheet(success_style)
        
        print(f"[复制机器码] 机器码已复制到剪贴板: {self.machine_code}")
        
        # 2.5秒后恢复原样
        QTimer.singleShot(2500, lambda: [
            copy_button.setText(original_text),
            copy_button.setStyleSheet(original_style)
        ])
    
    def login(self):
        """执行登录"""
        # 防止自动登录检查
        if not self.auto_login_prevented:
            print("[登录窗口] 阻止自动登录，登录功能尚未启用")
            return

        phone = self.phone_input.text().strip()

        if not phone:
            MessageManager.show_warning(self, "输入错误", "请输入手机号")
            self.phone_input.setFocus()
            return

        if len(phone) != 11 or not phone.isdigit():
            MessageManager.show_warning(self, "输入错误", "请输入正确的11位手机号")
            self.phone_input.setFocus()
            return

        print(f"[登录窗口] 用户手动触发登录: {phone}")

        # 显示登录进度
        self.set_login_state(True)

        # 启动登录线程
        self.login_thread = LoginThread(phone)
        self.login_thread.login_result.connect(self.on_login_result)
        self.login_thread.start()
    
    @pyqtSlot(bool, str, object)
    def on_login_result(self, success: bool, message: str, user_info: dict):
        """处理登录结果"""
        self.set_login_state(False)
        
        if success:
            # 登录成功 - 保存登录历史
            phone = self.phone_input.text().strip()
            self.save_login_history(phone)
            
            # 只有登录成功需要弹窗提示
            if UIConstants.should_show_success_popup("login_success"):
                user_name = user_info.get('username', '用户')
                phone = user_info.get('phone', '')
                points = user_info.get('points', 0)
                
                MessageManager.show_info(
                    self, 
                    "登录成功", 
                    f"欢迎回来，{user_name}！\n\n"
                    f"手机号: {phone}\n"
                    f"当前积分: {points}\n"
                    f"账号状态: 正常"
                )
            
            # 发送登录成功信号
            self.login_success.emit(user_info)
            
            # 关闭登录窗口
            self.close()
        else:
            # 登录失败
            MessageManager.show_error(self, "登录失败", f"{message}\n\n请检查手机号或联系管理员")
            self.phone_input.clear()
            self.phone_input.setFocus()
    
    def set_login_state(self, is_logging: bool):
        """设置登录状态"""
        self.login_button.setEnabled(not is_logging)
        self.phone_input.setEnabled(not is_logging)
        
        if is_logging:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            self.login_button.setText("登录中...")
        else:
            self.progress_bar.setVisible(False)
            self.login_button.setText("登 录")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果正在登录，先停止线程
        if self.login_thread and self.login_thread.isRunning():
            self.login_thread.terminate()
            self.login_thread.wait()
        
        event.accept()

def main():
    """测试登录窗口"""
    app = QApplication(sys.argv)
    
    # 设置应用程序图标和样式
    app.setApplicationName("乐影票务系统")
    app.setApplicationVersion("1.0.0")
    
    login_window = LoginWindow()
    
    def on_login_success(user_info):
        print(f"登录成功: {user_info}")
        app.quit()
    
    login_window.login_success.connect(on_login_success)
    login_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 