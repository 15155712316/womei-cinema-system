#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tab页面管理模块
负责管理所有Tab页面的显示和功能
"""

import random
import time
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor

# 导入自定义组件
from ui.widgets.classic_components import (
    ClassicTabWidget, ClassicGroupBox, ClassicButton, ClassicLineEdit, 
    ClassicComboBox, ClassicTableWidget, ClassicTextEdit, ClassicLabel, ClassicListWidget
)
from ui.interfaces.plugin_interface import IWidgetInterface, event_bus


class TabManagerWidget(QWidget):
    """Tab页面管理组件"""
    
    # 定义信号
    cinema_selected = pyqtSignal(str)  # 影院选择信号
    order_submitted = pyqtSignal(dict)  # 订单提交信号
    coupon_bound = pyqtSignal(dict)  # 券绑定信号
    coupon_exchanged = pyqtSignal(dict)  # 兑换券信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self.current_account = None
        self.cinemas_data = []
        self.current_points = 0
        
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
        
        # 加载示例数据
        self._load_sample_data()
    
    def cleanup(self) -> None:
        """清理组件资源"""
        # 断开全局事件连接
        event_bus.account_changed.disconnect(self._on_account_changed)
        
        # 清理数据
        self.current_account = None
        self.cinemas_data.clear()
    
    def get_widget(self) -> QWidget:
        """获取Qt组件"""
        return self
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 创建Tab组件
        self.tab_widget = ClassicTabWidget()
        self._create_tab_pages()
        
        layout.addWidget(self.tab_widget)
    
    def _create_tab_pages(self):
        """创建所有Tab页面"""
        # Tab1: 出票
        self.ticket_tab = QWidget()
        self._build_ticket_tab()
        self.tab_widget.addTab(self.ticket_tab, "出票")
        
        # Tab2: 绑券
        self.bind_coupon_tab = QWidget()
        self._build_bind_coupon_tab()
        self.tab_widget.addTab(self.bind_coupon_tab, "绑券")
        
        # Tab3: 兑换券
        self.exchange_coupon_tab = QWidget()
        self._build_exchange_coupon_tab()
        self.tab_widget.addTab(self.exchange_coupon_tab, "兑换券")
        
        # Tab4: 订单
        self.order_tab = QWidget()
        self._build_order_tab()
        self.tab_widget.addTab(self.order_tab, "订单")
        
        # Tab5: 影院
        self.cinema_tab = QWidget()
        self._build_cinema_tab()
        self.tab_widget.addTab(self.cinema_tab, "影院")
    
    def _build_ticket_tab(self):
        """构建出票Tab页面"""
        layout = QHBoxLayout(self.ticket_tab)
        layout.setSpacing(10)
        
        # 左侧：影院选择
        cinema_group = ClassicGroupBox("影院选择")
        self._build_cinema_select(cinema_group)
        layout.addWidget(cinema_group, 55)
        
        # 右侧：可用券列表
        coupon_group = ClassicGroupBox("可用券列表")
        self._build_coupon_list(coupon_group)
        layout.addWidget(coupon_group, 45)
    
    def _build_cinema_select(self, parent_group):
        """构建影院选择区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号显示
        self.current_account_label = ClassicLabel("当前账号: 未选择", "info")
        layout.addWidget(self.current_account_label)
        
        # 影院选择
        cinema_layout = QHBoxLayout()
        cinema_label = ClassicLabel("影院:")
        cinema_label.setMinimumWidth(40)
        self.cinema_combo = ClassicComboBox()
        self.cinema_combo.addItem("加载中...")
        cinema_layout.addWidget(cinema_label)
        cinema_layout.addWidget(self.cinema_combo)
        layout.addLayout(cinema_layout)
        
        # 影片选择
        movie_layout = QHBoxLayout()
        movie_label = ClassicLabel("影片:")
        movie_label.setMinimumWidth(40)
        self.movie_combo = ClassicComboBox()
        self.movie_combo.addItems(["请先选择影院"])
        movie_layout.addWidget(movie_label)
        movie_layout.addWidget(self.movie_combo)
        layout.addLayout(movie_layout)
        
        # 日期选择
        date_layout = QHBoxLayout()
        date_label = ClassicLabel("日期:")
        date_label.setMinimumWidth(40)
        self.date_combo = ClassicComboBox()
        self.date_combo.addItems(["请先选择影片"])
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_combo)
        layout.addLayout(date_layout)
        
        # 场次选择
        session_layout = QHBoxLayout()
        session_label = ClassicLabel("场次:")
        session_label.setMinimumWidth(40)
        self.session_combo = ClassicComboBox()
        self.session_combo.addItems(["请先选择日期"])
        session_layout.addWidget(session_label)
        session_layout.addWidget(self.session_combo)
        layout.addLayout(session_layout)
        
        # 提交订单按钮
        self.submit_order_btn = ClassicButton("提交订单", "success")
        self.submit_order_btn.setMinimumHeight(35)
        self.submit_order_btn.setEnabled(False)  # 初始禁用，需要选择完所有选项后启用
        layout.addWidget(self.submit_order_btn)
        
        layout.addStretch()
    
    def _build_coupon_list(self, parent_group):
        """构建券列表区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 券列表
        self.coupon_list = ClassicListWidget()
        self.coupon_list.addItem("10元代金券 (有效期至2024-12-31)")
        self.coupon_list.addItem("5折优惠券 (限周末使用)")
        self.coupon_list.addItem("买一送一券 (限工作日)")
        
        layout.addWidget(self.coupon_list)
    
    def _build_bind_coupon_tab(self):
        """构建绑券Tab页面"""
        layout = QVBoxLayout(self.bind_coupon_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号信息显示
        self.bind_account_label = ClassicLabel("当前账号: 未选择", "info")
        layout.addWidget(self.bind_account_label)
        
        # 主要内容区域
        content_layout = QHBoxLayout()
        
        # 左侧输入区
        left_group = ClassicGroupBox("每行一个券号：")
        left_layout = QVBoxLayout(left_group)
        
        self.coupon_input = ClassicTextEdit()
        self.coupon_input.setPlaceholderText("请在此输入券号，每行一个券号")
        left_layout.addWidget(self.coupon_input)
        
        self.bind_coupon_btn = ClassicButton("绑定当前账号", "success")
        self.bind_coupon_btn.setMinimumHeight(35)
        left_layout.addWidget(self.bind_coupon_btn)
        
        content_layout.addWidget(left_group, 1)
        
        # 右侧日志区
        right_group = ClassicGroupBox("绑定日志：")
        right_layout = QVBoxLayout(right_group)
        
        self.bind_log = ClassicTextEdit(read_only=True)
        self.bind_log.setPlaceholderText("绑定日志将在此显示...")
        right_layout.addWidget(self.bind_log)
        
        copy_log_layout = QHBoxLayout()
        copy_log_layout.addStretch()
        self.copy_log_btn = ClassicButton("复制日志", "default")
        self.copy_log_btn.setMaximumWidth(80)
        copy_log_layout.addWidget(self.copy_log_btn)
        right_layout.addLayout(copy_log_layout)
        
        content_layout.addWidget(right_group, 1)
        
        layout.addLayout(content_layout)
    
    def _build_exchange_coupon_tab(self):
        """构建兑换券Tab页面"""
        layout = QVBoxLayout(self.exchange_coupon_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 当前账号信息显示
        self.exchange_account_label = ClassicLabel("当前账号: 未选择", "info")
        layout.addWidget(self.exchange_account_label)
        
        # 兑换功能区域
        exchange_group = ClassicGroupBox("积分兑换券")
        exchange_layout = QGridLayout(exchange_group)
        
        # 积分信息
        points_label = ClassicLabel("当前积分:")
        self.points_display = ClassicLabel("0")
        self.points_display.setStyleSheet("font: bold 14px 'Microsoft YaHei'; color: #ff6600;")
        
        exchange_layout.addWidget(points_label, 0, 0)
        exchange_layout.addWidget(self.points_display, 0, 1)
        
        # 兑换选项
        exchange_type_label = ClassicLabel("兑换类型:")
        self.exchange_type_combo = ClassicComboBox()
        self.exchange_type_combo.addItems([
            "请选择兑换类型",
            "10元代金券 (需要100积分)",
            "5折优惠券 (需要200积分)",
            "买一送一券 (需要300积分)"
        ])
        
        exchange_layout.addWidget(exchange_type_label, 1, 0)
        exchange_layout.addWidget(self.exchange_type_combo, 1, 1)
        
        # 兑换数量
        quantity_label = ClassicLabel("兑换数量:")
        self.exchange_quantity = ClassicLineEdit("1")
        self.exchange_quantity.setMaximumWidth(100)
        
        exchange_layout.addWidget(quantity_label, 2, 0)
        exchange_layout.addWidget(self.exchange_quantity, 2, 1)
        
        # 兑换按钮
        self.exchange_btn = ClassicButton("立即兑换", "warning")
        self.exchange_btn.setMinimumHeight(35)
        exchange_layout.addWidget(self.exchange_btn, 3, 0, 1, 2)
        
        layout.addWidget(exchange_group)
        
        # 兑换记录
        record_group = ClassicGroupBox("兑换记录")
        record_layout = QVBoxLayout(record_group)
        
        self.exchange_record = ClassicTextEdit(read_only=True)
        self.exchange_record.setPlaceholderText("兑换记录将在此显示...")
        record_layout.addWidget(self.exchange_record)
        
        layout.addWidget(record_group)
    
    def _build_order_tab(self):
        """构建订单Tab页面"""
        layout = QVBoxLayout(self.order_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        self.order_refresh_btn = ClassicButton("刷新", "default")
        self.order_refresh_btn.setMaximumWidth(80)
        button_layout.addWidget(self.order_refresh_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 订单表格
        self.order_table = ClassicTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["影片", "影院", "状态", "订单号"])
        
        # 设置列宽
        header = self.order_table.horizontalHeader()
        header.resizeSection(0, 150)  # 影片
        header.resizeSection(1, 180)  # 影院  
        header.resizeSection(2, 150)  # 状态
        
        # 设置行高
        self.order_table.verticalHeader().setDefaultSectionSize(36)
        
        layout.addWidget(self.order_table)
        
        # 加载示例订单数据
        self._load_sample_orders()
    
    def _build_cinema_tab(self):
        """构建影院Tab页面"""
        layout = QVBoxLayout(self.cinema_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        self.cinema_refresh_btn = ClassicButton("刷新影院列表", "default")
        self.add_cinema_btn = ClassicButton("添加影院", "success")
        self.delete_cinema_btn = ClassicButton("删除影院", "warning")
        
        button_layout.addWidget(self.cinema_refresh_btn)
        button_layout.addWidget(self.add_cinema_btn)
        button_layout.addWidget(self.delete_cinema_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 影院表格
        self.cinema_table = ClassicTableWidget()
        self.cinema_table.setColumnCount(3)
        self.cinema_table.setHorizontalHeaderLabels(["影院名称", "影院ID", "地址"])
        
        # 设置列宽
        header = self.cinema_table.horizontalHeader()
        header.resizeSection(0, 200)  # 影院名称
        header.resizeSection(1, 150)  # 影院ID
        
        layout.addWidget(self.cinema_table)
        
        # 加载示例影院数据
        self._load_sample_cinemas()
    
    def _connect_signals(self):
        """连接信号槽"""
        # 出票Tab信号
        self.cinema_combo.currentTextChanged.connect(self._on_cinema_changed)
        self.movie_combo.currentTextChanged.connect(self._on_movie_changed)
        self.date_combo.currentTextChanged.connect(self._on_date_changed)
        self.session_combo.currentTextChanged.connect(self._on_session_changed)
        self.submit_order_btn.clicked.connect(self._on_submit_order)
        
        # 绑券Tab信号
        self.bind_coupon_btn.clicked.connect(self._on_bind_coupon)
        self.copy_log_btn.clicked.connect(self._on_copy_bind_log)
        
        # 兑换券Tab信号
        self.exchange_btn.clicked.connect(self._on_exchange_coupon)
        
        # 订单Tab信号
        self.order_refresh_btn.clicked.connect(self._on_refresh_orders)
        
        # 影院Tab信号
        self.cinema_refresh_btn.clicked.connect(self._on_refresh_cinemas)
        self.add_cinema_btn.clicked.connect(self._on_add_cinema)
        self.delete_cinema_btn.clicked.connect(self._on_delete_cinema)
    
    def _connect_global_events(self):
        """连接全局事件"""
        # 监听账号切换事件
        event_bus.account_changed.connect(self._on_account_changed)
    
    def _on_account_changed(self, account_data: dict):
        """账号切换处理"""
        try:
            self.current_account = account_data
            userid = account_data.get("userid", "未知账号")
            balance = account_data.get("balance", 0)
            
            # 更新各Tab页面的账号显示
            account_info = f"当前账号: {userid} (余额:{balance})"
            self.current_account_label.setText(account_info)
            self.bind_account_label.setText(account_info)
            self.exchange_account_label.setText(account_info)
            
            # 更新积分显示
            self.current_points = account_data.get("points", 0)
            self.points_display.setText(str(self.current_points))
            
            # 重新检查提交订单按钮状态
            self._check_submit_order_enabled()
            
            print(f"[Tab管理器] 账号切换: {userid}")
            
        except Exception as e:
            print(f"[Tab管理器] 账号切换错误: {e}")
    
    def _on_cinema_changed(self, cinema_text: str):
        """影院选择变化处理"""
        try:
            if cinema_text and cinema_text != "加载中...":
                # 模拟加载电影
                self.movie_combo.clear()
                self.movie_combo.addItems([
                    "阿凡达：水之道",
                    "流浪地球2",
                    "满江红"
                ])
                
                # 发出影院选择信号
                self.cinema_selected.emit(cinema_text)
                
                print(f"[Tab管理器] 影院切换: {cinema_text}")
        except Exception as e:
            print(f"[Tab管理器] 影院选择错误: {e}")
    
    def _on_movie_changed(self, movie_text: str):
        """影片选择变化处理"""
        try:
            if movie_text and movie_text not in ["请先选择影院"]:
                # 模拟加载日期
                self.date_combo.clear()
                self.date_combo.addItems([
                    "2024-12-27",
                    "2024-12-28", 
                    "2024-12-29"
                ])
        except Exception as e:
            print(f"[Tab管理器] 影片选择错误: {e}")
    
    def _on_date_changed(self, date_text: str):
        """日期选择变化处理"""
        try:
            if date_text and date_text not in ["请先选择影片"]:
                # 模拟加载场次
                self.session_combo.clear()
                self.session_combo.addItems([
                    "10:30",
                    "14:20",
                    "18:45",
                    "21:30"
                ])
        except Exception as e:
            print(f"[Tab管理器] 日期选择错误: {e}")
    
    def _on_session_changed(self, session_text: str):
        """场次选择变化处理"""
        try:
            if session_text and session_text not in ["请先选择日期"]:
                print(f"[Tab管理器] 选择场次: {session_text}")
                # 当选择了场次后，启用提交订单按钮
                self._check_submit_order_enabled()
            else:
                self.submit_order_btn.setEnabled(False)
        except Exception as e:
            print(f"[Tab管理器] 场次选择错误: {e}")
    
    def _check_submit_order_enabled(self):
        """检查是否可以启用提交订单按钮"""
        try:
            cinema = self.cinema_combo.currentText()
            movie = self.movie_combo.currentText()
            date = self.date_combo.currentText()
            session = self.session_combo.currentText()
            
            # 检查是否都已选择且不是默认提示文本
            enabled = (
                cinema and cinema not in ["加载中..."] and
                movie and movie not in ["请先选择影院"] and
                date and date not in ["请先选择影片"] and
                session and session not in ["请先选择日期"] and
                self.current_account is not None  # 必须选择了账号
            )
            
            self.submit_order_btn.setEnabled(enabled)
            
        except Exception as e:
            print(f"[Tab管理器] 检查提交按钮状态错误: {e}")
            self.submit_order_btn.setEnabled(False)
    
    def _on_submit_order(self):
        """提交订单处理"""
        try:
            # 获取选择的信息
            cinema = self.cinema_combo.currentText()
            movie = self.movie_combo.currentText()
            date = self.date_combo.currentText()
            session = self.session_combo.currentText()
            
            if not self.current_account:
                QMessageBox.warning(self, "提交失败", "请先选择账号")
                return
            
            # 创建订单数据
            order_data = {
                "order_id": f"ORDER{int(time.time())}",
                "account": self.current_account,
                "cinema": cinema,
                "movie": movie,
                "date": date,
                "session": session,
                "seats": "",  # 座位需要在座位选择区域输入
                "status": "待选座",
                "amount": 0.0,  # 价格需要根据座位数量计算
                "create_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "phone": self.current_account.get("phone", self.current_account.get("userid", ""))
            }
            
            # 发出订单提交信号
            self.order_submitted.emit(order_data)
            
            # 发布全局订单创建事件
            event_bus.order_created.emit(order_data)
            
            QMessageBox.information(
                self, "订单创建成功", 
                f"订单已创建！\n"
                f"订单号：{order_data['order_id']}\n"
                f"影院：{cinema}\n"
                f"影片：{movie}\n"
                f"场次：{date} {session}\n\n"
                f"请在座位选择区域选择座位"
            )
            
            print(f"[Tab管理器] 订单创建成功: {order_data['order_id']}")
            
        except Exception as e:
            QMessageBox.critical(self, "提交错误", f"提交订单失败: {str(e)}")
            print(f"[Tab管理器] 提交订单错误: {e}")
    
    def _on_bind_coupon(self):
        """绑定券处理"""
        try:
            coupon_text = self.coupon_input.toPlainText().strip()
            if not coupon_text:
                QMessageBox.warning(self, "输入错误", "请输入要绑定的券号")
                return
            
            if not self.current_account:
                QMessageBox.warning(self, "账号错误", "请先选择账号")
                return
            
            # 按行分割券号
            coupon_lines = [line.strip() for line in coupon_text.split('\n') if line.strip()]
            
            # 模拟绑定处理
            success_count = 0
            fail_count = 0
            log_text = f"开始绑定 {len(coupon_lines)} 个券号...\n"
            
            for coupon_code in coupon_lines:
                # 模拟绑定结果
                is_success = random.choice([True, True, False])  # 2/3概率成功
                
                if is_success:
                    success_count += 1
                    log_text += f"✅ 券号 {coupon_code} 绑定成功\n"
                else:
                    fail_count += 1
                    log_text += f"❌ 券号 {coupon_code} 绑定失败：券号无效或已使用\n"
            
            log_text += f"\n绑定完成：成功 {success_count} 个，失败 {fail_count} 个"
            
            # 更新日志
            self.bind_log.setPlainText(log_text)
            
            # 清空输入框
            self.coupon_input.clear()
            
            # 发出绑定信号
            bind_data = {
                "account": self.current_account,
                "success_count": success_count,
                "fail_count": fail_count
            }
            self.coupon_bound.emit(bind_data)
            
            QMessageBox.information(self, "绑定完成", f"券绑定完成\n成功：{success_count} 个\n失败：{fail_count} 个")
            
        except Exception as e:
            QMessageBox.critical(self, "绑定错误", f"券绑定失败: {str(e)}")
    
    def _on_copy_bind_log(self):
        """复制绑定日志"""
        try:
            log_text = self.bind_log.toPlainText()
            if log_text:
                from PyQt5.QtWidgets import QApplication
                clipboard = QApplication.clipboard()
                clipboard.setText(log_text)
                QMessageBox.information(self, "复制成功", "绑定日志已复制到剪贴板")
            else:
                QMessageBox.warning(self, "无内容", "没有日志内容可复制")
        except Exception as e:
            QMessageBox.critical(self, "复制错误", f"复制日志失败: {str(e)}")
    
    def _on_exchange_coupon(self):
        """兑换券处理"""
        try:
            exchange_type = self.exchange_type_combo.currentText()
            if exchange_type == "请选择兑换类型":
                QMessageBox.warning(self, "选择错误", "请选择兑换类型")
                return
            
            quantity_text = self.exchange_quantity.text().strip()
            try:
                quantity = int(quantity_text)
                if quantity <= 0:
                    raise ValueError("数量必须大于0")
            except ValueError:
                QMessageBox.warning(self, "输入错误", "请输入有效的兑换数量")
                return
            
            # 解析所需积分
            required_points = 0
            if "100积分" in exchange_type:
                required_points = 100
            elif "200积分" in exchange_type:
                required_points = 200
            elif "300积分" in exchange_type:
                required_points = 300
            
            total_required = required_points * quantity
            
            if self.current_points < total_required:
                QMessageBox.warning(
                    self, "积分不足", 
                    f"积分不足！\n当前积分：{self.current_points}\n需要积分：{total_required}"
                )
                return
            
            # 确认兑换
            reply = QMessageBox.question(
                self, "确认兑换",
                f"确认兑换 {quantity} 个 {exchange_type.split('(')[0]}？\n"
                f"将消耗 {total_required} 积分",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 模拟兑换成功
                self.current_points -= total_required
                self.points_display.setText(str(self.current_points))
                
                # 更新兑换记录
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                record_text = self.exchange_record.toPlainText()
                new_record = f"[{timestamp}] 兑换 {quantity} 个 {exchange_type.split('(')[0]}，消耗 {total_required} 积分\n"
                self.exchange_record.setPlainText(new_record + record_text)
                
                # 发出兑换信号
                exchange_data = {
                    "type": exchange_type,
                    "quantity": quantity,
                    "points_used": total_required
                }
                self.coupon_exchanged.emit(exchange_data)
                
                QMessageBox.information(self, "兑换成功", f"成功兑换 {quantity} 个券！")
            
        except Exception as e:
            QMessageBox.critical(self, "兑换错误", f"券兑换失败: {str(e)}")
    
    def _on_refresh_orders(self):
        """刷新订单列表"""
        try:
            self._load_sample_orders()
            QMessageBox.information(self, "刷新成功", "订单列表已刷新")
        except Exception as e:
            QMessageBox.critical(self, "刷新错误", f"刷新订单失败: {str(e)}")
    
    def _on_refresh_cinemas(self):
        """刷新影院列表"""
        try:
            self._load_sample_cinemas()
            QMessageBox.information(self, "刷新成功", "影院列表已刷新")
        except Exception as e:
            QMessageBox.critical(self, "刷新错误", f"刷新影院失败: {str(e)}")
    
    def _on_add_cinema(self):
        """添加影院"""
        QMessageBox.information(self, "功能提示", "添加影院功能待实现")
    
    def _on_delete_cinema(self):
        """删除影院"""
        try:
            current_row = self.cinema_table.currentRow()
            if current_row < 0:
                QMessageBox.warning(self, "选择错误", "请选择要删除的影院")
                return
            
            cinema_name = self.cinema_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(
                self, "确认删除",
                f"确认删除影院 {cinema_name}？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.cinema_table.removeRow(current_row)
                QMessageBox.information(self, "删除成功", f"已删除影院：{cinema_name}")
                
        except Exception as e:
            QMessageBox.critical(self, "删除错误", f"删除影院失败: {str(e)}")
    
    def _load_sample_data(self):
        """加载示例数据"""
        # 加载示例影院
        self.cinema_combo.clear()
        self.cinema_combo.addItems([
            "华夏优加金太都会",
            "深影国际影城(佐伦虹湾购物中心店)",
            "深圳万友影城BCMall店"
        ])
    
    def _load_sample_orders(self):
        """加载示例订单数据"""
        try:
            sample_orders = [
                {
                    "movie": "阿凡达：水之道",
                    "cinema": "深影国际影城(佐伦虹湾购物中心店)",
                    "status": "已完成",
                    "order_id": "ORDER2024122701"
                },
                {
                    "movie": "流浪地球2", 
                    "cinema": "深影国际影城(佐伦虹湾购物中心店)",
                    "status": "待支付",
                    "order_id": "ORDER2024122702"
                },
                {
                    "movie": "满江红",
                    "cinema": "华夏优加金太都会",
                    "status": "已取消",
                    "order_id": "ORDER2024122703"
                }
            ]
            
            self.order_table.setRowCount(len(sample_orders))
            for i, order in enumerate(sample_orders):
                self.order_table.setItem(i, 0, self.order_table.__class__.createItem(order["movie"]))
                self.order_table.setItem(i, 1, self.order_table.__class__.createItem(order["cinema"]))
                
                # 设置状态项的颜色
                if order["status"] == "已完成":
                    self.order_table.add_colored_item(i, 2, order["status"], "#4caf50")
                elif order["status"] == "待支付":
                    self.order_table.add_colored_item(i, 2, order["status"], "#ff9800")
                elif order["status"] == "已取消":
                    self.order_table.add_colored_item(i, 2, order["status"], "#f44336")
                else:
                    self.order_table.setItem(i, 2, self.order_table.__class__.createItem(order["status"]))
                
                self.order_table.setItem(i, 3, self.order_table.__class__.createItem(order["order_id"]))
                
        except Exception as e:
            print(f"[Tab管理器] 加载订单错误: {e}")
    
    def _load_sample_cinemas(self):
        """加载示例影院数据"""
        try:
            sample_cinemas = [
                {
                    "name": "华夏优加金太都会",
                    "id": "35fec8259e74",
                    "address": "高新大都会负一层"
                },
                {
                    "name": "深影国际影城(佐伦虹湾购物中心店)",
                    "id": "11b7e4bcc265", 
                    "address": "福田区北环大道6098号佐伦虹湾购物中心"
                },
                {
                    "name": "深圳万友影城BCMall店",
                    "id": "0f1e21d86ac8",
                    "address": "罗湖区布心路3008号BCMALl4楼"
                }
            ]
            
            self.cinema_table.setRowCount(len(sample_cinemas))
            for i, cinema in enumerate(sample_cinemas):
                self.cinema_table.setItem(i, 0, self.cinema_table.__class__.createItem(cinema["name"]))
                self.cinema_table.setItem(i, 1, self.cinema_table.__class__.createItem(cinema["id"]))
                self.cinema_table.setItem(i, 2, self.cinema_table.__class__.createItem(cinema["address"]))
                
        except Exception as e:
            print(f"[Tab管理器] 加载影院错误: {e}")
    
    def update_cinema_list(self, cinemas: List[Dict]):
        """更新影院列表"""
        try:
            self.cinemas_data = cinemas
            
            # 更新下拉框
            self.cinema_combo.clear()
            for cinema in cinemas:
                name = cinema.get("cinemaShortName", cinema.get("name", ""))
                if name:
                    self.cinema_combo.addItem(name)
            
        except Exception as e:
            print(f"[Tab管理器] 更新影院列表错误: {e}") 