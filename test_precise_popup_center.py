#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试精确的弹窗居中显示
验证修复后的弹窗居中逻辑
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox, QLabel
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class PreciseTestWindow(QMainWindow):
    """精确测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.last_token_popup_time = 0
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("精确弹窗居中测试 - 修复后版本")
        self.setGeometry(200, 150, 900, 700)  # 设置窗口大小和位置
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标题
        title_label = QLabel("Token失效弹窗居中测试 - 修复后版本")
        title_label.setFont(QFont("微软雅黑", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 添加说明
        info_label = QLabel("此测试验证修复后的弹窗居中逻辑\n使用frameGeometry()和客户区域计算")
        info_label.setFont(QFont("微软雅黑", 10))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 创建测试按钮
        test_btn = QPushButton("测试Token失效弹窗（修复后）")
        test_btn.setFont(QFont("微软雅黑", 12))
        test_btn.clicked.connect(self.test_token_popup)
        layout.addWidget(test_btn)
        
        # 添加窗口信息显示
        self.window_info_label = QLabel()
        self.window_info_label.setFont(QFont("Consolas", 9))
        self.window_info_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(self.window_info_label)
        
        # 更新窗口信息
        self.update_window_info()
        
        print(f"[测试窗口] 精确测试窗口初始化完成")
    
    def update_window_info(self):
        """更新窗口信息显示"""
        frame_geo = self.frameGeometry()
        client_geo = self.geometry()
        
        info_text = f"""窗口几何信息:
框架区域 (frameGeometry): x={frame_geo.x()}, y={frame_geo.y()}, w={frame_geo.width()}, h={frame_geo.height()}
客户区域 (geometry): x={client_geo.x()}, y={client_geo.y()}, w={client_geo.width()}, h={client_geo.height()}
标题栏高度: {frame_geo.height() - client_geo.height()}px
边框宽度: {(frame_geo.width() - client_geo.width()) // 2}px"""
        
        self.window_info_label.setText(info_text)
    
    def resizeEvent(self, event):
        """窗口大小改变事件"""
        super().resizeEvent(event)
        QTimer.singleShot(100, self.update_window_info)  # 延迟更新，确保几何信息正确
    
    def moveEvent(self, event):
        """窗口移动事件"""
        super().moveEvent(event)
        QTimer.singleShot(100, self.update_window_info)  # 延迟更新，确保几何信息正确
    
    def test_token_popup(self):
        """测试token失效弹窗"""
        error_msg = "获取TOKEN超时 [5105A]"
        self.show_token_expired_popup_fixed(error_msg)
    
    def show_token_expired_popup_fixed(self, error_msg: str):
        """
        显示token失效弹窗提醒（修复后的版本）
        
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
            
            print(f"[Token失效] 📢 显示弹窗提醒（修复后版本）")
            
            # 🎯 创建信息弹窗
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("系统提醒")
            msg_box.setText("Token已失效，请重新登录或更新Token")
            msg_box.setDetailedText(f"详细错误信息：{error_msg}")
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Ok)
            
            # 🔧 设置弹窗为模态，但不阻塞
            msg_box.setModal(False)
            msg_box.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
            
            # 🎯 先显示弹窗以获取正确的尺寸
            msg_box.show()
            
            # 🎯 等待弹窗完全显示后再计算位置
            def center_popup():
                try:
                    # 🔧 使用frameGeometry()获取包含标题栏的完整窗口区域
                    main_frame = self.frameGeometry()
                    main_x = main_frame.x()
                    main_y = main_frame.y()
                    main_width = main_frame.width()
                    main_height = main_frame.height()
                    
                    # 🔧 使用客户区域计算，排除标题栏影响
                    main_client = self.geometry()
                    client_x = main_client.x()
                    client_y = main_client.y()
                    client_width = main_client.width()
                    client_height = main_client.height()
                    
                    # 获取弹窗的几何信息
                    popup_geometry = msg_box.geometry()
                    popup_width = popup_geometry.width()
                    popup_height = popup_geometry.height()
                    
                    # 🎯 使用客户区域计算居中位置（更精确）
                    center_x = client_x + (client_width - popup_width) // 2
                    center_y = client_y + (client_height - popup_height) // 2
                    
                    print(f"[Token失效] 📋 位置计算:")
                    print(f"[Token失效] 📋 主窗口框架: x={main_x}, y={main_y}, w={main_width}, h={main_height}")
                    print(f"[Token失效] 📋 主窗口客户区: x={client_x}, y={client_y}, w={client_width}, h={client_height}")
                    print(f"[Token失效] 📋 弹窗: w={popup_width}, h={popup_height}")
                    print(f"[Token失效] 📋 居中位置: x={center_x}, y={center_y}")
                    
                    # 🎯 移动弹窗到居中位置
                    msg_box.move(center_x, center_y)
                    
                    # 🔧 验证最终位置
                    QTimer.singleShot(50, lambda: self.verify_popup_position(msg_box, client_x, client_y, client_width, client_height))
                    
                    print(f"[Token失效] ✅ 弹窗已移动到居中位置")
                    
                except Exception as e:
                    print(f"[Token失效] ❌ 居中计算异常: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 🎯 延迟50ms后执行居中，确保弹窗已完全显示
            QTimer.singleShot(50, center_popup)
            
            # 🎯 1.5秒后自动关闭
            QTimer.singleShot(1500, msg_box.close)
            
            print(f"[Token失效] ✅ 弹窗显示完成，1.5秒后自动关闭")
            
        except Exception as e:
            print(f"[Token失效] ❌ 显示弹窗异常: {e}")
            import traceback
            traceback.print_exc()
    
    def verify_popup_position(self, msg_box, client_x, client_y, client_width, client_height):
        """验证弹窗位置"""
        try:
            final_geometry = msg_box.geometry()
            final_x = final_geometry.x()
            final_y = final_geometry.y()
            popup_width = final_geometry.width()
            popup_height = final_geometry.height()
            
            # 计算中心点偏差
            expected_center_x = client_x + client_width // 2
            expected_center_y = client_y + client_height // 2
            actual_center_x = final_x + popup_width // 2
            actual_center_y = final_y + popup_height // 2
            
            offset_x = abs(actual_center_x - expected_center_x)
            offset_y = abs(actual_center_y - expected_center_y)
            
            print(f"[Token失效] 📋 最终位置验证:")
            print(f"[Token失效] 📋 弹窗最终位置: x={final_x}, y={final_y}")
            print(f"[Token失效] 📋 期望中心: x={expected_center_x}, y={expected_center_y}")
            print(f"[Token失效] 📋 实际中心: x={actual_center_x}, y={actual_center_y}")
            print(f"[Token失效] 📋 偏差: x={offset_x}px, y={offset_y}px")
            
            if offset_x <= 3 and offset_y <= 3:
                print(f"[Token失效] ✅ 弹窗居中成功！偏差在可接受范围内")
            elif offset_x <= 10 and offset_y <= 10:
                print(f"[Token失效] ⚠️ 弹窗基本居中，有轻微偏差")
            else:
                print(f"[Token失效] ❌ 弹窗居中失败，偏差较大")
            
        except Exception as e:
            print(f"[Token失效] ❌ 位置验证异常: {e}")

def main():
    print("🎬 沃美电影票务系统 - 精确弹窗居中测试")
    print("=" * 60)
    print("📋 测试目标：验证修复后的弹窗居中逻辑")
    print("🔧 修复内容：")
    print("  - 使用frameGeometry()获取完整窗口区域")
    print("  - 使用客户区域计算，排除标题栏影响")
    print("  - 增加位置验证和偏差计算")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = PreciseTestWindow()
    window.show()
    
    # 自动测试弹窗
    def auto_test():
        print(f"\n🔄 自动测试修复后的弹窗显示...")
        window.test_token_popup()
    
    # 3秒后自动测试
    QTimer.singleShot(3000, auto_test)
    
    print(f"✅ 测试窗口已显示，3秒后自动测试弹窗")
    print(f"📋 您也可以手动点击按钮测试")
    print(f"📋 可以移动或调整窗口大小后再测试")
    
    # 运行应用
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
