#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试弹窗居中显示修复
验证token失效弹窗能正确显示在主窗口正中央
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestMainWindow(QMainWindow):
    """测试主窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.last_token_popup_time = 0
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("Token失效弹窗居中测试")
        self.setGeometry(100, 100, 800, 600)  # 设置窗口大小和位置
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 创建测试按钮
        test_btn = QPushButton("测试Token失效弹窗")
        test_btn.setFont(QFont("微软雅黑", 12))
        test_btn.clicked.connect(self.test_token_popup)
        layout.addWidget(test_btn)
        
        # 添加说明文字
        info_btn = QPushButton("点击按钮测试弹窗是否在窗口正中央显示")
        info_btn.setEnabled(False)
        info_btn.setFont(QFont("微软雅黑", 10))
        layout.addWidget(info_btn)
        
        print(f"[测试窗口] 主窗口初始化完成")
        print(f"[测试窗口] 窗口位置: x={self.x()}, y={self.y()}")
        print(f"[测试窗口] 窗口大小: w={self.width()}, h={self.height()}")
    
    def test_token_popup(self):
        """测试token失效弹窗"""
        error_msg = "获取TOKEN超时 [5105A]"
        self.show_token_expired_popup(error_msg)
    
    def show_token_expired_popup(self, error_msg: str):
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
            
            print(f"[Token失效] 📢 显示弹窗提醒")
            
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
                    # 获取主窗口的几何信息
                    main_geometry = self.geometry()
                    main_x = main_geometry.x()
                    main_y = main_geometry.y()
                    main_width = main_geometry.width()
                    main_height = main_geometry.height()
                    
                    # 获取弹窗的几何信息
                    popup_geometry = msg_box.geometry()
                    popup_width = popup_geometry.width()
                    popup_height = popup_geometry.height()
                    
                    # 🎯 计算居中位置
                    center_x = main_x + (main_width - popup_width) // 2
                    center_y = main_y + (main_height - popup_height) // 2
                    
                    print(f"[Token失效] 📋 位置计算:")
                    print(f"[Token失效] 📋 主窗口: x={main_x}, y={main_y}, w={main_width}, h={main_height}")
                    print(f"[Token失效] 📋 弹窗: w={popup_width}, h={popup_height}")
                    print(f"[Token失效] 📋 居中位置: x={center_x}, y={center_y}")
                    
                    # 🎯 移动弹窗到居中位置
                    msg_box.move(center_x, center_y)
                    
                    print(f"[Token失效] ✅ 弹窗已居中显示")
                    
                    # 验证最终位置
                    final_geometry = msg_box.geometry()
                    final_x = final_geometry.x()
                    final_y = final_geometry.y()
                    print(f"[Token失效] 📋 最终位置: x={final_x}, y={final_y}")
                    
                    # 计算是否真正居中
                    expected_center_x = main_x + main_width // 2
                    expected_center_y = main_y + main_height // 2
                    actual_center_x = final_x + popup_width // 2
                    actual_center_y = final_y + popup_height // 2
                    
                    print(f"[Token失效] 📋 中心点验证:")
                    print(f"[Token失效] 📋 期望中心: x={expected_center_x}, y={expected_center_y}")
                    print(f"[Token失效] 📋 实际中心: x={actual_center_x}, y={actual_center_y}")
                    
                    # 计算偏差
                    offset_x = abs(actual_center_x - expected_center_x)
                    offset_y = abs(actual_center_y - expected_center_y)
                    
                    if offset_x <= 5 and offset_y <= 5:
                        print(f"[Token失效] ✅ 弹窗居中成功！偏差: x={offset_x}px, y={offset_y}px")
                    else:
                        print(f"[Token失效] ❌ 弹窗居中失败！偏差: x={offset_x}px, y={offset_y}px")
                    
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

def test_popup_positioning():
    """测试弹窗定位"""
    print("🧪 测试Token失效弹窗居中显示")
    print("=" * 60)
    print("📋 测试说明:")
    print("  1. 将显示一个测试窗口")
    print("  2. 点击按钮测试弹窗显示")
    print("  3. 观察弹窗是否在窗口正中央")
    print("  4. 查看控制台输出的位置计算信息")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = TestMainWindow()
    window.show()
    
    # 自动测试弹窗（可选）
    def auto_test():
        print(f"\n🔄 自动测试弹窗显示...")
        window.test_token_popup()
    
    # 3秒后自动测试
    QTimer.singleShot(3000, auto_test)
    
    print(f"✅ 测试窗口已显示，3秒后自动测试弹窗")
    print(f"📋 您也可以手动点击按钮测试")
    
    # 运行应用
    sys.exit(app.exec_())

def test_different_window_sizes():
    """测试不同窗口大小下的弹窗居中"""
    print("\n🧪 测试不同窗口大小下的弹窗居中")
    print("=" * 60)
    
    # 模拟不同的窗口配置
    window_configs = [
        {"name": "小窗口", "x": 100, "y": 100, "w": 600, "h": 400},
        {"name": "中等窗口", "x": 200, "y": 150, "w": 800, "h": 600},
        {"name": "大窗口", "x": 50, "y": 50, "w": 1200, "h": 800},
        {"name": "偏移窗口", "x": 300, "y": 200, "w": 900, "h": 700},
    ]
    
    for config in window_configs:
        print(f"\n📋 测试配置: {config['name']}")
        
        # 模拟主窗口几何信息
        main_x, main_y = config['x'], config['y']
        main_w, main_h = config['w'], config['h']
        
        # 模拟弹窗尺寸（QMessageBox的典型尺寸）
        popup_w, popup_h = 350, 150
        
        # 计算居中位置
        center_x = main_x + (main_w - popup_w) // 2
        center_y = main_y + (main_h - popup_h) // 2
        
        # 验证中心点
        main_center_x = main_x + main_w // 2
        main_center_y = main_y + main_h // 2
        popup_center_x = center_x + popup_w // 2
        popup_center_y = center_y + popup_h // 2
        
        print(f"  主窗口: x={main_x}, y={main_y}, w={main_w}, h={main_h}")
        print(f"  弹窗位置: x={center_x}, y={center_y}")
        print(f"  主窗口中心: ({main_center_x}, {main_center_y})")
        print(f"  弹窗中心: ({popup_center_x}, {popup_center_y})")
        
        # 检查是否居中
        if popup_center_x == main_center_x and popup_center_y == main_center_y:
            print(f"  ✅ 居中计算正确")
        else:
            print(f"  ❌ 居中计算错误")
    
    print(f"\n✅ 不同窗口大小测试完成")

def main():
    print("🎬 沃美电影票务系统 - 弹窗居中显示测试")
    print("=" * 60)
    print("📋 测试目标：验证token失效弹窗能正确显示在主窗口正中央")
    print("🔍 测试内容：")
    print("  1. 弹窗定位测试")
    print("  2. 不同窗口大小测试")
    print("=" * 60)
    
    # 先进行理论计算测试
    test_different_window_sizes()
    
    # 再进行实际显示测试
    print(f"\n🚀 开始实际弹窗显示测试...")
    test_popup_positioning()

if __name__ == "__main__":
    main()
