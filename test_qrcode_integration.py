#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码显示功能集成测试
模拟完整的二维码显示流程
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

# 导入项目模块
from utils.signals import event_bus
from services.order_api import get_order_qrcode_api

class QRCodeTestWindow(QWidget):
    """二维码测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.connect_events()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("二维码显示功能测试")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title = QLabel("二维码显示功能测试")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        layout.addWidget(title)
        
        # 测试按钮
        self.test_btn = QPushButton("🧪 测试获取二维码")
        self.test_btn.setMinimumHeight(40)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font: bold 12px "Microsoft YaHei";
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.test_btn.clicked.connect(self.test_qrcode)
        layout.addWidget(self.test_btn)
        
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
        
        # 二维码显示区域
        self.qr_display = QLabel("二维码将在此显示")
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
        
        # 数据信息显示
        self.info_label = QLabel("")
        self.info_label.setAlignment(Qt.AlignLeft)
        self.info_label.setStyleSheet("""
            QLabel {
                color: #333333;
                font: 10px "Microsoft YaHei";
                padding: 10px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.info_label)
    
    def connect_events(self):
        """连接事件"""
        # 监听二维码显示事件
        event_bus.show_qrcode.connect(self.on_qrcode_received)
    
    def test_qrcode(self):
        """测试二维码获取和显示"""
        try:
            self.status_label.setText("🚀 正在获取二维码...")
            self.test_btn.setEnabled(False)
            
            # 测试参数
            order_no = "202506021611295648804"
            cinema_id = "35fec8259e74"
            
            print(f"[测试] 开始获取二维码: 订单={order_no}, 影院={cinema_id}")
            
            # 延迟执行API调用，避免阻塞UI
            QTimer.singleShot(100, lambda: self.call_qrcode_api(order_no, cinema_id))
            
        except Exception as e:
            print(f"[测试] 测试错误: {e}")
            self.status_label.setText(f"❌ 测试失败: {e}")
            self.test_btn.setEnabled(True)
    
    def call_qrcode_api(self, order_no, cinema_id):
        """调用二维码API - 修复：测试新的取票码获取流程"""
        try:
            from services.order_api import get_order_detail

            # 🔧 添加账号认证信息
            test_account = {
                "userid": "14700283316",
                "openid": "oAOCp7fvQZ57uCG-5H0XZyUSbO-4",
                "token": "a53201ca598cfcc8",
                "cinemaid": "35fec8259e74"
            }

            # 🎯 第一步：获取订单详情，提取取票码
            print(f"[测试] 步骤1: 获取订单详情...")
            detail_params = {
                'orderno': order_no,
                'groupid': '',
                'cinemaid': cinema_id,
                'cardno': test_account.get('cardno', ''),
                'userid': test_account['userid'],
                'openid': test_account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': test_account['token'],
                'source': '2'
            }

            detail_result = get_order_detail(detail_params)

            if detail_result and detail_result.get('resultCode') == '0':
                # 🎯 第二步：从订单详情中提取取票码
                detail_data = detail_result.get('resultData', {})
                ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
                ds_code = detail_data.get('dsValidateCode', '')

                print(f"[测试] 订单详情获取成功:")
                print(f"[测试] - ticketCode: {ticket_code}")
                print(f"[测试] - dsValidateCode: {ds_code}")

                # 确定最终的取票码
                final_ticket_code = ds_code or ticket_code

                if final_ticket_code:
                    print(f"[测试] ✅ 找到取票码: {final_ticket_code}")

                    # 🎯 第三步：创建取票码数据并发送
                    ticket_data = {
                        'order_no': order_no,
                        'ticket_code': final_ticket_code,
                        'film_name': detail_data.get('filmName', '测试影片'),
                        'show_time': detail_data.get('showTime', '测试时间'),
                        'hall_name': detail_data.get('hallName', '测试影厅'),
                        'seat_info': detail_data.get('seatInfo', '测试座位'),
                        'cinema_name': detail_data.get('cinemaName', '测试影院'),
                        'display_type': 'ticket_code'
                    }

                    # 发送取票码事件
                    print(f"[测试] 发送取票码显示事件...")
                    event_bus.show_qrcode.emit(ticket_data)

                    self.status_label.setText("✅ 取票码获取成功，已发送显示事件")

                    # 更新信息显示
                    info_text = f"订单号: {order_no}\n取票码: {final_ticket_code}\n影片: {ticket_data['film_name']}"
                    self.info_label.setText(info_text)

                else:
                    print(f"[测试] ⚠️ 订单详情中没有找到取票码，尝试获取二维码图片...")
                    # 如果没有取票码，尝试获取二维码图片
                    qr_result = get_order_qrcode_api(order_no, cinema_id, test_account)

                    if qr_result:
                        print(f"[测试] 二维码获取成功: {len(qr_result)} bytes")

                        # 分析数据格式
                        if qr_result.startswith(b'\x89PNG'):
                            data_format = "PNG"
                        elif qr_result.startswith(b'\xff\xd8\xff'):
                            data_format = "JPEG"
                        elif qr_result.startswith(b'GIF'):
                            data_format = "GIF"
                        else:
                            data_format = "UNKNOWN"

                        # 创建二维码数据
                        qr_data = {
                            'order_no': order_no,
                            'qr_bytes': qr_result,
                            'data_size': len(qr_result),
                            'data_format': data_format,
                            'display_type': 'qr_image'
                        }

                        # 发送事件
                        print(f"[测试] 发送二维码显示事件...")
                        event_bus.show_qrcode.emit(qr_data)

                        self.status_label.setText("✅ 二维码获取成功，已发送显示事件")
                    else:
                        print(f"[测试] 二维码获取失败")
                        self.status_label.setText("❌ 二维码获取失败")
            else:
                error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
                print(f"[测试] 获取订单详情失败: {error_msg}")
                self.status_label.setText(f"❌ 获取订单详情失败: {error_msg}")

            self.test_btn.setEnabled(True)
            
        except Exception as e:
            print(f"[测试] API调用错误: {e}")
            self.status_label.setText(f"❌ API调用失败: {e}")
            self.test_btn.setEnabled(True)
    
    def on_qrcode_received(self, qr_data):
        """接收到二维码数据"""
        try:
            print(f"[测试] 收到二维码显示事件: {type(qr_data)}")
            
            if isinstance(qr_data, dict):
                order_no = qr_data.get('order_no', '')
                qr_bytes = qr_data.get('qr_bytes')
                data_size = qr_data.get('data_size', 0)
                data_format = qr_data.get('data_format', 'UNKNOWN')
                
                print(f"[测试] 处理二维码数据: 订单={order_no}, 大小={data_size}, 格式={data_format}")
                
                # 更新信息显示
                info_text = f"订单号: {order_no}\n数据大小: {data_size} bytes\n数据格式: {data_format}"
                self.info_label.setText(info_text)
                
                # 尝试显示图片
                if qr_bytes and len(qr_bytes) > 0:
                    success = self.display_qrcode_image(qr_bytes)
                    if success:
                        self.status_label.setText("✅ 二维码图片显示成功")
                    else:
                        self.status_label.setText("⚠️ 二维码数据无法显示为图片")
                        self.qr_display.setText(f"订单 {order_no} 取票码\n(图片格式: {data_format})")
                else:
                    self.status_label.setText("⚠️ 二维码数据为空")
            else:
                # 文本格式
                print(f"[测试] 收到文本消息: {qr_data}")
                self.qr_display.setText(str(qr_data))
                self.status_label.setText("✅ 显示文本消息")
                
        except Exception as e:
            print(f"[测试] 处理二维码数据错误: {e}")
            self.status_label.setText(f"❌ 处理错误: {e}")
    
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
                
                print(f"[测试] 二维码图片显示成功: {pixmap.width()}x{pixmap.height()}")
                return True
            else:
                print(f"[测试] 二维码图片加载失败")
                return False
                
        except Exception as e:
            print(f"[测试] 显示二维码图片错误: {e}")
            return False

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QRCodeTestWindow()
    window.show()
    
    print("🧪 二维码显示功能集成测试启动")
    print("=" * 50)
    print("1. 点击'测试获取二维码'按钮")
    print("2. 观察二维码是否正确显示")
    print("3. 检查控制台输出的调试信息")
    print("=" * 50)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
