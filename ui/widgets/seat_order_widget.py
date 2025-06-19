#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位选择和订单管理模块
负责座位选择、订单创建和支付处理
"""

from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, Qt

# 导入自定义组件
from ui.widgets.classic_components import (
    ClassicGroupBox, ClassicButton, ClassicLineEdit, ClassicLabel, ClassicTextEdit
)
from ui.interfaces.plugin_interface import IWidgetInterface, event_bus


class SeatOrderWidget(QWidget):
    """座位选择和订单管理组件"""
    
    # 定义信号
    order_created = pyqtSignal(dict)  # 订单创建信号
    order_paid = pyqtSignal(str)  # 订单支付信号
    seat_selected = pyqtSignal(str)  # 座位选择信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self.current_account = None
        self.current_cinema = None
        self.current_movie = None
        self.current_session = None
        self.selected_seats = []
        self.current_order = None
        
        # 实现IWidgetInterface接口
        self._widget_interface = IWidgetInterface()
        
        # 初始化界面
        self.initialize()
        
        # 连接全局事件
        self._connect_global_events()
    
    def initialize(self) -> None:
        """初始化组件"""
        self._setup_ui()
        self._connect_signals()
    
    def cleanup(self) -> None:
        """清理组件资源"""
        # 断开全局事件连接
        event_bus.account_changed.disconnect(self._on_account_changed)
        event_bus.cinema_selected.disconnect(self._on_cinema_selected)
        
        # 清理数据
        self.current_account = None
        self.current_order = None
        self.selected_seats.clear()
    
    def get_widget(self) -> QWidget:
        """获取Qt组件"""
        return self
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 座位区域
        self.seat_group = ClassicGroupBox("座位选择")
        self._build_seat_area()
        layout.addWidget(self.seat_group, 3)
        
        # 订单详情区域
        self.order_group = ClassicGroupBox("订单详情")
        self._build_order_detail_area()
        layout.addWidget(self.order_group, 2)
    
    def _build_seat_area(self):
        """构建座位选择区域"""
        layout = QVBoxLayout(self.seat_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(10)
        
        # 座位选择信息
        seat_info_layout = QHBoxLayout()
        seat_label = ClassicLabel("选择座位:")
        self.seat_input = ClassicLineEdit()
        self.seat_input.setPlaceholderText("座位选择")
        seat_info_layout.addWidget(seat_label)
        seat_info_layout.addWidget(self.seat_input)
        layout.addLayout(seat_info_layout)
        
        # 座位图区域（占位）
        self.seat_placeholder = ClassicLabel(
            "座位图将在此显示\n\n请先选择影院、影片、日期和场次",
            "default"
        )
        self.seat_placeholder.setAlignment(Qt.AlignCenter)
        self.seat_placeholder.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 14px "Microsoft YaHei";
                background-color: #ffffff;
                border: 1px dashed #cccccc;
                padding: 60px;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.seat_placeholder)
        
        # 提交订单按钮
        self.submit_btn = ClassicButton("提交订单", "success")
        self.submit_btn.setMinimumHeight(35)
        layout.addWidget(self.submit_btn)
    
    def _build_order_detail_area(self):
        """构建订单详情区域"""
        layout = QVBoxLayout(self.order_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 用户信息显示
        self.user_info = ClassicLabel("当前账号: 未选择", "info")
        layout.addWidget(self.user_info)
        
        # 订单详情文本
        self.order_detail = ClassicTextEdit(read_only=True)
        self.order_detail.setPlaceholderText("订单详情将在此显示...")
        layout.addWidget(self.order_detail)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        # 一键支付按钮
        self.pay_btn = ClassicButton("一键支付", "warning")
        self.pay_btn.setMinimumHeight(35)
        self.pay_btn.setEnabled(False)  # 初始禁用
        
        # 取消订单按钮
        self.cancel_btn = ClassicButton("取消订单", "default")
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.setEnabled(False)  # 初始禁用
        
        button_layout.addWidget(self.pay_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def _connect_signals(self):
        """连接信号槽"""
        # 按钮事件
        self.submit_btn.clicked.connect(self._on_submit_order)
        self.pay_btn.clicked.connect(self._on_pay_order)
        self.cancel_btn.clicked.connect(self._on_cancel_order)
        
        # 座位输入事件
        self.seat_input.textChanged.connect(self._on_seat_input_changed)
    
    def _connect_global_events(self):
        """连接全局事件"""
        # 监听账号切换事件
        event_bus.account_changed.connect(self._on_account_changed)
        
        # 监听影院选择事件
        event_bus.cinema_selected.connect(self._on_cinema_selected)
    
    def _on_account_changed(self, account_data: dict):
        """账号切换处理"""
        try:
            self.current_account = account_data
            userid = account_data.get("userid", "未知账号")
            balance = account_data.get("balance", 0)
            
            # 更新用户信息显示
            self.user_info.setText(f"当前账号: {userid} (余额:{balance})")
            
            
        except Exception as e:
            pass

    def _on_cinema_selected(self, cinema_name: str):
        """影院选择处理"""
        try:
            self.current_cinema = cinema_name
            
            # 更新座位图占位符
            self.seat_placeholder.setText(
                f"已选择影院: {cinema_name}\n\n"
                f"请继续选择影片、日期和场次\n"
                f"座位图将在选择完成后显示"
            )
            
            
        except Exception as e:
            pass

    def _on_seat_input_changed(self, text: str):
        """座位输入变化处理"""
        try:
            # 解析座位输入（例如：A1,A2,B3）
            seats = [seat.strip() for seat in text.split(',') if seat.strip()]
            self.selected_seats = seats
            
            # 发出座位选择信号
            if seats:
                self.seat_selected.emit(','.join(seats))
            
            # 更新提交按钮状态
            self.submit_btn.setEnabled(len(seats) > 0 and self.current_account is not None)
            
        except Exception as e:
            pass

    def _on_submit_order(self):
        """提交订单处理"""
        try:
            # 验证必要条件
            if not self.current_account:
                QMessageBox.warning(self, "提交失败", "请先选择账号")
                return
            
            if not self.selected_seats:
                QMessageBox.warning(self, "提交失败", "请先选择座位")
                return
            
            if not self.current_cinema:
                QMessageBox.warning(self, "提交失败", "请先选择影院")
                return
            
            # 构建订单数据
            order_data = {
                "order_id": f"ORDER{int(__import__('time').time())}",
                "account": self.current_account,
                "cinema": self.current_cinema,
                "movie": self.current_movie or "未选择影片",
                "session": self.current_session or "未选择场次",
                "seats": self.selected_seats,
                "status": "待支付",
                "amount": len(self.selected_seats) * 35.0,  # 假设每张票35元
                "create_time": __import__('time').strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 确认提交
            reply = QMessageBox.question(
                self, "确认提交",
                f"确认提交订单？\n\n"
                f"影院：{order_data['cinema']}\n"
                f"影片：{order_data['movie']}\n"
                f"座位：{', '.join(order_data['seats'])}\n"
                f"金额：¥{order_data['amount']:.2f}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 模拟订单创建成功
                self.current_order = order_data
                
                # 更新订单详情显示
                self._update_order_detail(order_data)
                
                # 启用支付和取消按钮
                self.pay_btn.setEnabled(True)
                self.cancel_btn.setEnabled(True)
                
                # 禁用提交按钮
                self.submit_btn.setEnabled(False)
                
                # 发出订单创建信号
                self.order_created.emit(order_data)
                
                # 发布全局事件
                event_bus.order_created.emit(order_data)
                
                QMessageBox.information(self, "提交成功", f"订单创建成功！\n订单号：{order_data['order_id']}")
                
            
        except Exception as e:
            QMessageBox.critical(self, "提交错误", f"提交订单失败: {str(e)}")
    
    def _on_pay_order(self):
        """支付订单处理"""
        try:
            if not self.current_order:
                QMessageBox.warning(self, "支付失败", "没有待支付的订单")
                return
            
            order_amount = self.current_order.get("amount", 0)
            account_balance = self.current_account.get("balance", 0)
            
            # 检查余额
            if account_balance < order_amount:
                QMessageBox.warning(
                    self, "支付失败", 
                    f"账户余额不足\n"
                    f"订单金额：¥{order_amount:.2f}\n"
                    f"账户余额：¥{account_balance:.2f}"
                )
                return
            
            # 确认支付
            reply = QMessageBox.question(
                self, "确认支付",
                f"确认支付订单？\n\n"
                f"订单号：{self.current_order['order_id']}\n"
                f"金额：¥{order_amount:.2f}\n"
                f"余额：¥{account_balance:.2f}",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 模拟支付成功
                self.current_order["status"] = "已支付"
                self.current_order["pay_time"] = __import__('time').strftime("%Y-%m-%d %H:%M:%S")
                
                # 更新账户余额（这里只是模拟，实际应该通过业务服务更新）
                self.current_account["balance"] -= order_amount
                
                # 更新订单详情显示
                self._update_order_detail(self.current_order)
                
                # 禁用支付和取消按钮
                self.pay_btn.setEnabled(False)
                self.cancel_btn.setEnabled(False)
                
                # 发出支付成功信号
                self.order_paid.emit(self.current_order["order_id"])
                
                # 发布全局事件
                event_bus.order_paid.emit(self.current_order["order_id"])
                
                QMessageBox.information(
                    self, "支付成功", 
                    f"订单支付成功！\n"
                    f"订单号：{self.current_order['order_id']}\n"
                    f"剩余余额：¥{self.current_account['balance']:.2f}"
                )
                
            
        except Exception as e:
            QMessageBox.critical(self, "支付错误", f"支付失败: {str(e)}")
    
    def _on_cancel_order(self):
        """取消订单处理"""
        try:
            if not self.current_order:
                QMessageBox.warning(self, "取消失败", "没有可取消的订单")
                return
            
            # 确认取消
            reply = QMessageBox.question(
                self, "确认取消",
                f"确认取消订单？\n\n"
                f"订单号：{self.current_order['order_id']}\n"
                f"座位：{', '.join(self.current_order['seats'])}\n"
                f"取消后座位将被释放",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 模拟取消成功
                order_id = self.current_order["order_id"]
                self.current_order = None
                
                # 清空订单详情
                self.order_detail.clear()
                
                # 重置按钮状态
                self.pay_btn.setEnabled(False)
                self.cancel_btn.setEnabled(False)
                self.submit_btn.setEnabled(len(self.selected_seats) > 0 and self.current_account is not None)
                
                QMessageBox.information(self, "取消成功", f"订单已取消\n订单号：{order_id}")
                
            
        except Exception as e:
            QMessageBox.critical(self, "取消错误", f"取消订单失败: {str(e)}")
    
    def _update_order_detail(self, order_data: dict):
        """更新订单详情显示"""
        try:
            detail_text = f"""订单详情：
            
订单号：{order_data.get('order_id', 'N/A')}
状态：{order_data.get('status', 'N/A')}
影院：{order_data.get('cinema', 'N/A')}
影片：{order_data.get('movie', 'N/A')}
场次：{order_data.get('session', 'N/A')}
座位：{', '.join(order_data.get('seats', []))}
金额：¥{order_data.get('amount', 0):.2f}
创建时间：{order_data.get('create_time', 'N/A')}"""
            
            if order_data.get('pay_time'):
                detail_text += f"\n支付时间：{order_data['pay_time']}"
            
            self.order_detail.setPlainText(detail_text)
            
        except Exception as e:
            pass

    def set_movie_session(self, movie: str, session: str):
        """设置影片和场次信息"""
        try:
            self.current_movie = movie
            self.current_session = session
            
            # 更新座位图占位符
            if self.current_cinema:
                self.seat_placeholder.setText(
                    f"影院：{self.current_cinema}\n"
                    f"影片：{movie}\n"
                    f"场次：{session}\n\n"
                    f"请在上方输入座位号（例如：A1,A2,B3）"
                )
            
        except Exception as e:
            pass

    def clear_selection(self):
        """清除选择"""
        try:
            self.seat_input.clear()
            self.selected_seats.clear()
            self.current_order = None
            
            # 重置按钮状态
            self.submit_btn.setEnabled(False)
            self.pay_btn.setEnabled(False)
            self.cancel_btn.setEnabled(False)
            
            # 清空订单详情
            self.order_detail.clear()
            
        except Exception as e:
            pass

    def get_current_order(self) -> Optional[Dict]:
        """获取当前订单"""
        return self.current_order
    
    def get_selected_seats(self) -> List[str]:
        """获取选中的座位"""
        return self.selected_seats.copy() 