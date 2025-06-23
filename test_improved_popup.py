#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试改进后的Token失效弹窗
验证直接显示详细信息，无需用户点击查看详情
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class ImprovedPopupTestWindow(QMainWindow):
    """改进弹窗测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.last_token_popup_time = 0
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("改进Token失效弹窗测试")
        self.setGeometry(300, 200, 800, 600)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标题
        title_label = QLabel("Token失效弹窗改进测试")
        title_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加说明
        info_label = QLabel("改进内容：\n• 直接显示详细信息，无需点击查看详情\n• 使用警告图标更醒目\n• 提供明确的解决方案")
        info_label.setFont(QFont("微软雅黑", 10))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 创建测试按钮
        test_btn = QPushButton("测试改进后的Token失效弹窗")
        test_btn.setFont(QFont("微软雅黑", 12))
        test_btn.clicked.connect(self.test_improved_popup)
        layout.addWidget(test_btn)
        
        # 对比测试按钮
        compare_btn = QPushButton("对比：原版弹窗（有详情按钮）")
        compare_btn.setFont(QFont("微软雅黑", 12))
        compare_btn.clicked.connect(self.test_original_popup)
        layout.addWidget(compare_btn)
        
        print(f"[测试窗口] 改进弹窗测试窗口初始化完成")
    
    def test_improved_popup(self):
        """测试改进后的弹窗"""
        error_msg = "获取TOKEN超时 [5105A]"
        self.show_improved_token_popup(error_msg)
    
    def test_original_popup(self):
        """测试原版弹窗（对比用）"""
        error_msg = "获取TOKEN超时 [5105A]"
        self.show_original_token_popup(error_msg)
    
    def show_improved_token_popup(self, error_msg: str):
        """
        显示改进后的token失效弹窗
        
        Args:
            error_msg: 错误信息
        """
        try:
            import time
            current_time = time.time()
            
            # 防重复弹窗：1分钟内只显示一次
            if current_time - self.last_token_popup_time < 60:
                print(f"[Token失效] ⚠️ 1分钟内已显示过弹窗，跳过重复显示")
                return
            
            self.last_token_popup_time = current_time
            
            print(f"[Token失效] 📢 显示改进后的弹窗")
            
            # 🎯 创建信息弹窗
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("系统提醒")
            
            # 🔧 直接显示详细信息，不需要用户点击查看详情
            main_text = "Token已失效，请及时更新"
            detail_text = f"\n错误详情：{error_msg}"

            # 🎯 将主要信息和详细信息合并显示
            full_message = main_text + detail_text
            msg_box.setText(full_message)
            
            msg_box.setIcon(QMessageBox.Warning)  # 使用警告图标更醒目
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # 🔧 设置弹窗为模态，但不阻塞
            msg_box.setModal(False)
            msg_box.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
            
            # 🎯 先显示弹窗以获取正确的尺寸
            msg_box.show()
            
            # 🎯 等待弹窗完全显示后再计算位置
            def center_popup():
                try:
                    # 使用客户区域计算居中位置
                    main_client = self.geometry()
                    client_x = main_client.x()
                    client_y = main_client.y()
                    client_width = main_client.width()
                    client_height = main_client.height()
                    
                    # 获取弹窗的几何信息
                    popup_geometry = msg_box.geometry()
                    popup_width = popup_geometry.width()
                    popup_height = popup_geometry.height()
                    
                    # 计算居中位置
                    center_x = client_x + (client_width - popup_width) // 2
                    center_y = client_y + (client_height - popup_height) // 2
                    
                    print(f"[Token失效] 📋 改进弹窗位置计算:")
                    print(f"[Token失效] 📋 主窗口: x={client_x}, y={client_y}, w={client_width}, h={client_height}")
                    print(f"[Token失效] 📋 弹窗: w={popup_width}, h={popup_height}")
                    print(f"[Token失效] 📋 居中位置: x={center_x}, y={center_y}")
                    
                    # 移动弹窗到居中位置
                    msg_box.move(center_x, center_y)
                    
                    print(f"[Token失效] ✅ 改进弹窗已居中显示")
                    
                except Exception as e:
                    print(f"[Token失效] ❌ 居中计算异常: {e}")
            
            # 延迟50ms后执行居中
            QTimer.singleShot(50, center_popup)
            
            # 🎯 2秒后自动关闭（比原来稍长，因为内容更多）
            QTimer.singleShot(2000, msg_box.close)
            
            print(f"[Token失效] ✅ 改进弹窗显示完成，2秒后自动关闭")
            
        except Exception as e:
            print(f"[Token失效] ❌ 显示改进弹窗异常: {e}")
            import traceback
            traceback.print_exc()
    
    def show_original_token_popup(self, error_msg: str):
        """
        显示原版token失效弹窗（对比用）
        
        Args:
            error_msg: 错误信息
        """
        try:
            print(f"[Token失效] 📢 显示原版弹窗（对比）")
            
            # 原版弹窗
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("系统提醒")
            msg_box.setText("Token已失效，请重新登录或更新Token")
            msg_box.setDetailedText(f"详细错误信息：{error_msg}")  # 需要点击查看详情
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            msg_box.setModal(False)
            msg_box.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
            msg_box.show()
            
            # 居中显示
            def center_popup():
                main_client = self.geometry()
                popup_geometry = msg_box.geometry()
                center_x = main_client.x() + (main_client.width() - popup_geometry.width()) // 2
                center_y = main_client.y() + (main_client.height() - popup_geometry.height()) // 2
                msg_box.move(center_x, center_y)
                print(f"[Token失效] ✅ 原版弹窗已居中显示")
            
            QTimer.singleShot(50, center_popup)
            QTimer.singleShot(2000, msg_box.close)
            
            print(f"[Token失效] ✅ 原版弹窗显示完成，2秒后自动关闭")
            
        except Exception as e:
            print(f"[Token失效] ❌ 显示原版弹窗异常: {e}")

def test_popup_comparison():
    """测试弹窗对比"""
    print("🎬 沃美电影票务系统 - Token失效弹窗改进测试")
    print("=" * 60)
    print("📋 改进内容：")
    print("  ✅ 直接显示详细信息，无需点击查看详情")
    print("  ✅ 使用警告图标更醒目")
    print("  ✅ 提供明确的解决方案")
    print("  ✅ 自动关闭时间调整为2秒（内容更多）")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = ImprovedPopupTestWindow()
    window.show()
    
    # 自动测试改进弹窗
    def auto_test_improved():
        print(f"\n🔄 自动测试改进后的弹窗...")
        window.test_improved_popup()
    
    # 自动测试原版弹窗
    def auto_test_original():
        print(f"\n🔄 自动测试原版弹窗（对比）...")
        window.test_original_popup()
    
    # 3秒后测试改进版，6秒后测试原版
    QTimer.singleShot(3000, auto_test_improved)
    QTimer.singleShot(6000, auto_test_original)
    
    print(f"✅ 测试窗口已显示")
    print(f"📋 3秒后自动测试改进弹窗")
    print(f"📋 6秒后自动测试原版弹窗（对比）")
    print(f"📋 您也可以手动点击按钮测试")
    
    # 运行应用
    sys.exit(app.exec_())

def test_message_content():
    """测试消息内容格式"""
    print("\n🧪 测试消息内容格式")
    print("=" * 60)
    
    # 模拟不同的错误信息
    error_messages = [
        "获取TOKEN超时 [5105A]",
        "TOKEN已过期 [5105B]", 
        "TOKEN验证失败 [5105C]",
        "网络连接超时，TOKEN无法验证"
    ]
    
    for i, error_msg in enumerate(error_messages, 1):
        print(f"\n📋 测试场景 {i}:")
        print(f"原始错误: {error_msg}")
        
        # 格式化消息
        main_text = "Token已失效，请及时更新"
        detail_text = f"\n错误详情：{error_msg}"
        full_message = main_text + detail_text
        
        print(f"完整消息:")
        print(f"{'='*40}")
        print(full_message)
        print(f"{'='*40}")
    
    print(f"\n✅ 消息内容格式测试完成")

def main():
    print("🎬 沃美电影票务系统 - Token失效弹窗改进测试")
    print("=" * 60)
    print("📋 测试目标：验证改进后的弹窗用户体验")
    print("🔍 测试内容：")
    print("  1. 弹窗对比测试")
    print("  2. 消息内容格式测试")
    print("=" * 60)
    
    # 先测试消息内容格式
    test_message_content()
    
    # 再进行弹窗对比测试
    print(f"\n🚀 开始弹窗对比测试...")
    test_popup_comparison()

if __name__ == "__main__":
    main()
