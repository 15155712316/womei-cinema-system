#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试二维码显示功能
测试事件总线和主窗口显示
"""

import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# 导入项目模块
from utils.signals import event_bus
from utils.qrcode_generator import generate_ticket_qrcode

class QRCodeDebugWindow(QWidget):
    """二维码调试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_events()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("二维码显示调试")
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("二维码显示功能调试")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        layout.addWidget(title)
        
        # 测试按钮
        self.test_btn1 = QPushButton("🧪 测试1: 发送文本消息")
        self.test_btn1.setMinimumHeight(40)
        self.test_btn1.clicked.connect(self.test_text_message)
        layout.addWidget(self.test_btn1)
        
        self.test_btn2 = QPushButton("🧪 测试2: 发送生成的二维码")
        self.test_btn2.setMinimumHeight(40)
        self.test_btn2.clicked.connect(self.test_generated_qrcode)
        layout.addWidget(self.test_btn2)
        
        self.test_btn3 = QPushButton("🧪 测试3: 发送取票码信息")
        self.test_btn3.setMinimumHeight(40)
        self.test_btn3.clicked.connect(self.test_ticket_code_info)
        layout.addWidget(self.test_btn3)
        
        # 状态显示
        self.status_label = QLabel("点击按钮开始测试...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font: 11px "Microsoft YaHei";
                padding: 10px;
                background-color: #f5f5f5;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.status_label)
        
        # 模拟主窗口的二维码显示区域
        self.qr_display = QLabel("模拟主窗口二维码显示区域")
        self.qr_display.setAlignment(Qt.AlignCenter)
        self.qr_display.setMinimumHeight(250)
        self.qr_display.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 12px "Microsoft YaHei";
                background-color: #ffffff;
                border: 2px dashed #cccccc;
                border-radius: 5px;
                padding: 20px;
            }
        """)
        layout.addWidget(self.qr_display)
        
        # 日志显示
        self.log_label = QLabel("等待事件...")
        self.log_label.setAlignment(Qt.AlignLeft)
        self.log_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font: 10px "Microsoft YaHei";
                padding: 10px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.log_label)
    
    def connect_events(self):
        """连接事件"""
        # 监听二维码显示事件
        event_bus.show_qrcode.connect(self.on_qrcode_received)
        print("[调试] 已连接二维码显示事件")
    
    def test_text_message(self):
        """测试1: 发送文本消息"""
        try:
            self.status_label.setText("🚀 发送文本消息...")
            
            text_message = "测试文本消息 - 订单 123456789"
            
            print(f"[调试] 发送文本消息: {text_message}")
            event_bus.show_qrcode.emit(text_message)
            
            self.status_label.setText("✅ 文本消息已发送")
            
        except Exception as e:
            print(f"[调试] 测试1错误: {e}")
            self.status_label.setText(f"❌ 测试1失败: {e}")
    
    def test_generated_qrcode(self):
        """测试2: 发送生成的二维码"""
        try:
            self.status_label.setText("🚀 生成并发送二维码...")
            
            # 生成测试二维码
            test_ticket_code = "DEBUG123456789"
            test_order_info = {
                'filmName': '调试测试影片',
                'cinemaName': '调试测试影院',
                'showTime': '2025-06-02 20:00',
                'seatInfo': '调试座位',
                'hallName': '调试影厅'
            }
            
            qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
            
            if qr_bytes:
                # 创建二维码数据
                qr_data = {
                    'order_no': 'DEBUG_ORDER_123',
                    'qr_bytes': qr_bytes,
                    'data_size': len(qr_bytes),
                    'data_format': 'PNG',
                    'display_type': 'generated_qrcode',
                    'ticket_code': test_ticket_code,
                    'film_name': test_order_info['filmName'],
                    'show_time': test_order_info['showTime'],
                    'hall_name': test_order_info['hallName'],
                    'seat_info': test_order_info['seatInfo'],
                    'cinema_name': test_order_info['cinemaName'],
                    'is_generated': True
                }
                
                print(f"[调试] 发送生成的二维码数据:")
                print(f"[调试] - 显示类型: {qr_data['display_type']}")
                print(f"[调试] - 取票码: {qr_data['ticket_code']}")
                print(f"[调试] - 数据大小: {qr_data['data_size']} bytes")
                
                event_bus.show_qrcode.emit(qr_data)
                
                self.status_label.setText("✅ 生成的二维码已发送")
            else:
                self.status_label.setText("❌ 二维码生成失败")
                
        except Exception as e:
            print(f"[调试] 测试2错误: {e}")
            self.status_label.setText(f"❌ 测试2失败: {e}")
    
    def test_ticket_code_info(self):
        """测试3: 发送取票码信息"""
        try:
            self.status_label.setText("🚀 发送取票码信息...")
            
            ticket_data = {
                'order_no': 'DEBUG_ORDER_456',
                'ticket_code': 'TICKET789012345',
                'film_name': '调试影片名称',
                'show_time': '2025-06-02 21:30',
                'hall_name': '调试影厅',
                'seat_info': '调试座位信息',
                'cinema_name': '调试影院名称',
                'display_type': 'ticket_code'
            }
            
            print(f"[调试] 发送取票码信息:")
            print(f"[调试] - 显示类型: {ticket_data['display_type']}")
            print(f"[调试] - 取票码: {ticket_data['ticket_code']}")
            print(f"[调试] - 影片: {ticket_data['film_name']}")
            
            event_bus.show_qrcode.emit(ticket_data)
            
            self.status_label.setText("✅ 取票码信息已发送")
            
        except Exception as e:
            print(f"[调试] 测试3错误: {e}")
            self.status_label.setText(f"❌ 测试3失败: {e}")
    
    def on_qrcode_received(self, qr_data):
        """接收到二维码数据"""
        try:
            print(f"[调试] 🎯 收到二维码显示事件")
            print(f"[调试] 🔍 数据类型: {type(qr_data)}")
            
            # 更新日志
            log_text = f"收到事件: {type(qr_data)}\n"
            
            if isinstance(qr_data, dict):
                display_type = qr_data.get('display_type', 'unknown')
                log_text += f"显示类型: {display_type}\n"
                
                if display_type == 'generated_qrcode':
                    # 处理生成的二维码
                    ticket_code = qr_data.get('ticket_code', '')
                    qr_bytes = qr_data.get('qr_bytes')
                    
                    log_text += f"取票码: {ticket_code}\n"
                    log_text += f"二维码: {len(qr_bytes) if qr_bytes else 0} bytes\n"
                    
                    # 尝试显示二维码图片
                    if qr_bytes:
                        success = self.display_qrcode_image(qr_bytes)
                        if success:
                            log_text += "✅ 二维码图片显示成功"
                        else:
                            log_text += "❌ 二维码图片显示失败"
                            self.qr_display.setText(f"取票码: {ticket_code}\n(图片显示失败)")
                    
                elif display_type == 'ticket_code':
                    # 处理取票码文本
                    ticket_code = qr_data.get('ticket_code', '')
                    film_name = qr_data.get('film_name', '')
                    
                    log_text += f"取票码: {ticket_code}\n"
                    log_text += f"影片: {film_name}\n"
                    
                    # 显示文本信息
                    info_text = f"🎬 {film_name}\n"
                    info_text += f"🎫 取票码: {ticket_code}\n"
                    info_text += f"📋 订单号: {qr_data.get('order_no', '')}"
                    
                    self.qr_display.setText(info_text)
                    self.qr_display.setStyleSheet("""
                        QLabel {
                            color: #1976d2;
                            font: bold 11px "Microsoft YaHei";
                            background-color: #e3f2fd;
                            border: 2px solid #2196f3;
                            padding: 15px;
                            border-radius: 8px;
                        }
                    """)
                    
                    log_text += "✅ 取票码信息显示成功"
                
                else:
                    log_text += f"未知显示类型: {display_type}"
                    
            elif isinstance(qr_data, str):
                # 处理文本消息
                log_text += f"文本内容: {qr_data}\n"
                
                self.qr_display.setText(qr_data)
                self.qr_display.setStyleSheet("""
                    QLabel {
                        color: #2e7d32;
                        font: bold 12px "Microsoft YaHei";
                        background-color: #e8f5e8;
                        border: 2px solid #4caf50;
                        padding: 20px;
                        border-radius: 5px;
                    }
                """)
                
                log_text += "✅ 文本消息显示成功"
            
            else:
                log_text += f"未知数据格式: {type(qr_data)}"
            
            self.log_label.setText(log_text)
            
        except Exception as e:
            print(f"[调试] 处理二维码数据错误: {e}")
            self.log_label.setText(f"❌ 处理错误: {e}")
    
    def display_qrcode_image(self, qr_bytes):
        """显示二维码图片"""
        try:
            from PyQt5.QtCore import QByteArray
            
            # 转换为QPixmap
            byte_array = QByteArray(qr_bytes)
            pixmap = QPixmap()
            success = pixmap.loadFromData(byte_array)
            
            if success and not pixmap.isNull():
                # 缩放图片
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                # 显示图片
                self.qr_display.setPixmap(scaled_pixmap)
                self.qr_display.setText("")
                self.qr_display.setStyleSheet("""
                    QLabel {
                        background-color: #ffffff;
                        border: 2px solid #4CAF50;
                        border-radius: 5px;
                        padding: 10px;
                    }
                """)
                
                print(f"[调试] 二维码图片显示成功: {pixmap.width()}x{pixmap.height()}")
                return True
            else:
                print(f"[调试] 二维码图片加载失败")
                return False
                
        except Exception as e:
            print(f"[调试] 显示二维码图片错误: {e}")
            return False

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建调试窗口
    window = QRCodeDebugWindow()
    window.show()
    
    print("🧪 二维码显示调试工具启动")
    print("=" * 50)
    print("1. 点击测试按钮发送不同类型的数据")
    print("2. 观察事件总线是否正常工作")
    print("3. 检查二维码显示是否正确")
    print("=" * 50)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
