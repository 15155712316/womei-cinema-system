#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户登录窗口
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QMessageBox, 
                             QFrame, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QClipboard

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import auth_service

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
        self.init_ui()
    
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
        
        # 回车键登录
        self.phone_input.returnPressed.connect(self.login)
        
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
        machine_code_label = QLabel("当前设备机器码")
        machine_code_label.setFont(QFont("微软雅黑", 12, QFont.Bold))
        machine_code_label.setStyleSheet("""
            QLabel {
                color: #1a1a1a; 
                background-color: transparent;
                margin: 15px 0px 8px 0px;
                padding: 0px;
            }
        """)
        machine_code_label.setAlignment(Qt.AlignCenter)
        
        # 机器码显示文本框（只读，可选中复制）
        self.machine_code_display = QTextEdit()
        self.machine_code_display.setPlainText(self.machine_code)
        self.machine_code_display.setFont(QFont("Consolas", 10))
        self.machine_code_display.setStyleSheet("""
            QTextEdit {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 6px;
                padding: 8px;
                color: #333;
                line-height: 1.2;
            }
        """)
        self.machine_code_display.setReadOnly(True)
        self.machine_code_display.setFixedHeight(60)  # 固定高度
        self.machine_code_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.machine_code_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 复制按钮
        copy_button = QPushButton("复制机器码")
        copy_button.setFont(QFont("微软雅黑", 10))
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 6px;
                font-size: 10px;
                min-height: 18px;
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
        main_layout.addWidget(machine_code_label)  # 直接添加，不要空白
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
    
    def center_window(self):
        """窗口居中显示"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)
    
    def copy_machine_code(self):
        """复制机器码到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.machine_code)
        
        # 临时改变按钮文本提示复制成功
        copy_button = self.sender()
        original_text = copy_button.text()
        copy_button.setText("已复制!")
        copy_button.setStyleSheet(copy_button.styleSheet().replace("#6c757d", "#28a745"))
        
        # 2秒后恢复原样
        QTimer.singleShot(2000, lambda: [
            copy_button.setText(original_text),
            copy_button.setStyleSheet(copy_button.styleSheet().replace("#28a745", "#6c757d"))
        ])
    
    def login(self):
        """执行登录"""
        phone = self.phone_input.text().strip()
        
        if not phone:
            QMessageBox.warning(self, "输入错误", "请输入手机号")
            self.phone_input.setFocus()
            return
        
        if len(phone) != 11 or not phone.isdigit():
            QMessageBox.warning(self, "输入错误", "请输入正确的11位手机号")
            self.phone_input.setFocus()
            return
        
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
            # 登录成功
            user_name = user_info.get('username', '用户')
            phone = user_info.get('phone', '')
            points = user_info.get('points', 0)
            
            QMessageBox.information(
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
            QMessageBox.critical(self, "登录失败", f"{message}\n\n请检查手机号或联系管理员")
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