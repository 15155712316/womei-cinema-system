#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试刷新验证服务
检查定时验证是否正常工作
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton, QLabel
from PyQt5.QtCore import QTimer, pyqtSlot
from services.refresh_timer_service import refresh_timer_service


class RefreshServiceDebugWindow(QMainWindow):
    """刷新服务调试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("刷新验证服务调试工具")
        self.setFixedSize(800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 状态标签
        self.status_label = QLabel("服务状态: 未启动")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.status_label)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 控制按钮
        self.start_btn = QPushButton("启动验证服务")
        self.start_btn.clicked.connect(self.start_service)
        layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止验证服务")
        self.stop_btn.clicked.connect(self.stop_service)
        layout.addWidget(self.stop_btn)
        
        self.status_btn = QPushButton("检查服务状态")
        self.status_btn.clicked.connect(self.check_status)
        layout.addWidget(self.status_btn)
        
        # 连接刷新服务信号
        refresh_timer_service.auth_success.connect(self.on_auth_success)
        refresh_timer_service.auth_failed.connect(self.on_auth_failed)
        
        # 状态更新定时器
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)  # 每秒更新一次状态
        
        self.log("调试工具启动完成")
        
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def start_service(self):
        """启动验证服务"""
        try:
            # 模拟用户信息
            test_user = {
                'phone': '13800138000',
                'username': '测试用户',
                'machine_code': 'TEST123456'
            }
            
            self.log("尝试启动刷新验证服务...")
            
            # 设置较短的检查间隔用于测试（1分钟）
            refresh_timer_service.set_check_interval(1)
            self.log("设置检查间隔为1分钟")
            
            # 启动监控
            success = refresh_timer_service.start_monitoring(test_user)
            
            if success:
                self.log("✅ 刷新验证服务启动成功")
                self.start_btn.setEnabled(False)
                self.stop_btn.setEnabled(True)
            else:
                self.log("❌ 刷新验证服务启动失败")
                
        except Exception as e:
            self.log(f"❌ 启动服务异常: {e}")
            import traceback
            traceback.print_exc()
    
    def stop_service(self):
        """停止验证服务"""
        try:
            self.log("停止刷新验证服务...")
            refresh_timer_service.stop_monitoring()
            self.log("✅ 刷新验证服务已停止")
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
        except Exception as e:
            self.log(f"❌ 停止服务异常: {e}")
    
    def check_status(self):
        """检查服务状态"""
        try:
            status = refresh_timer_service.get_status()
            self.log("=== 服务状态详情 ===")
            self.log(f"运行状态: {'运行中' if status['is_running'] else '已停止'}")
            self.log(f"当前用户: {status['current_user'] or '无'}")
            self.log(f"检查间隔: {status['check_interval_minutes']} 分钟")
            self.log(f"定时器状态: {'活跃' if status['timer_active'] else '非活跃'}")
            self.log("==================")
        except Exception as e:
            self.log(f"❌ 检查状态异常: {e}")
    
    def update_status_display(self):
        """更新状态显示"""
        try:
            status = refresh_timer_service.get_status()
            if status['is_running']:
                self.status_label.setText(f"服务状态: 运行中 - 用户: {status['current_user']}")
                self.status_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.status_label.setText("服务状态: 已停止")
                self.status_label.setStyleSheet("font-weight: bold; color: red;")
        except Exception as e:
            self.status_label.setText(f"服务状态: 错误 - {e}")
            self.status_label.setStyleSheet("font-weight: bold; color: orange;")
    
    @pyqtSlot(dict)
    def on_auth_success(self, user_info):
        """认证成功处理"""
        phone = user_info.get('phone', 'N/A')
        self.log(f"🎉 认证成功: {phone}")
    
    @pyqtSlot(str)
    def on_auth_failed(self, error_msg):
        """认证失败处理"""
        self.log(f"💥 认证失败: {error_msg}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = RefreshServiceDebugWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
