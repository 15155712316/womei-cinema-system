#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位图面板组件 - 重构版本
"""

from typing import Dict, List, Optional, Set, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QScrollArea, QFrame, QLineEdit, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QPalette
from utils.signals import event_bus, event_handler


class SeatButton(QPushButton):
    """座位按钮"""
    
    def __init__(self, seat_data: dict, parent=None):
        super().__init__(parent)
        
        self.seat_data = seat_data
        self.row = seat_data.get('row', 0)
        self.col = seat_data.get('col', 0)
        self.seat_num = seat_data.get('num', f"{self.row}-{self.col}")
        self.status = seat_data.get('status', 'available')
        
        # 设置按钮属性
        self.setFixedSize(30, 25)
        self.setText(str(self.col))
        self.setFont(QFont("Arial", 8))
        
        # 设置样式
        self._update_style()
        
        # 连接点击事件
        self.clicked.connect(self._on_clicked)
    
    def _update_style(self):
        """更新按钮样式"""
        if self.status == 'available':
            # 可选座位 - 绿色
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #45a049;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.setEnabled(True)
        elif self.status == 'selected':
            # 已选座位 - 蓝色
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: 1px solid #1976D2;
                    border-radius: 3px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            self.setEnabled(True)
        elif self.status == 'sold':
            # 已售座位 - 红色
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: 1px solid #d32f2f;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            self.setEnabled(False)
        else:
            # 不可用座位 - 灰色
            self.setStyleSheet("""
                QPushButton {
                    background-color: #9E9E9E;
                    color: white;
                    border: 1px solid #757575;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            self.setEnabled(False)
    
    def _on_clicked(self):
        """按钮点击处理"""
        if self.status == 'available':
            self.status = 'selected'
        elif self.status == 'selected':
            self.status = 'available'
        
        self._update_style()
        
        # 通知父组件
        if self.parent():
            self.parent().on_seat_clicked(self)
    
    def set_status(self, status: str):
        """设置座位状态"""
        self.status = status
        self._update_style()


class SeatMapPanel(QWidget):
    """座位图面板"""
    
    # 信号定义
    seat_selected = pyqtSignal(list)  # 座位选择变化
    order_submitted = pyqtSignal(dict)  # 提交订单
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self.seat_matrix = []  # 座位矩阵
        self.seat_buttons = {}  # 座位按钮映射 {(row, col): button}
        self.selected_seats = set()  # 已选座位集合 {(row, col)}
        self.hall_info = {}  # 影厅信息
        
        # 初始化UI
        self._init_ui()
        
        # 连接事件总线
        self._connect_events()
        
        print("[座位图面板] 初始化完成")
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 座位选择输入区
        input_group = QGroupBox("座位选择")
        input_layout = QHBoxLayout(input_group)
        
        QLabel("选择座位:", input_group)
        self.seat_input = QLineEdit()
        self.seat_input.setPlaceholderText("请点击座位图选择座位...")
        self.seat_input.setReadOnly(True)
        input_layout.addWidget(QLabel("选择座位:"))
        input_layout.addWidget(self.seat_input)
        
        layout.addWidget(input_group)
        
        # 座位图区域
        self.seat_scroll = QScrollArea()
        self.seat_scroll.setWidgetResizable(True)
        self.seat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.seat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 座位图容器
        self.seat_container = QWidget()
        self.seat_layout = QVBoxLayout(self.seat_container)
        self.seat_layout.setAlignment(Qt.AlignCenter)
        
        # 默认提示
        self.placeholder_label = QLabel("座位图将在此显示\n\n请先选择影院、影片、日期和场次")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("""
            QLabel {
                color: #999999;
                font: 14px "Microsoft YaHei";
                background-color: #ffffff;
                border: 1px dashed #cccccc;
                padding: 60px;
                border-radius: 5px;
            }
        """)
        self.seat_layout.addWidget(self.placeholder_label)
        
        self.seat_scroll.setWidget(self.seat_container)
        layout.addWidget(self.seat_scroll)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("清空选择")
        self.clear_button.clicked.connect(self.clear_selection)
        self.clear_button.setEnabled(False)
        
        self.submit_button = QPushButton("提交订单")
        self.submit_button.clicked.connect(self.submit_order)
        self.submit_button.setEnabled(False)
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.submit_button)
        
        layout.addLayout(button_layout)
        
        # 座位状态说明
        legend_layout = QHBoxLayout()
        
        # 可选座位
        available_btn = QPushButton("可选")
        available_btn.setFixedSize(50, 25)
        available_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #45a049;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        available_btn.setEnabled(False)
        
        # 已选座位
        selected_btn = QPushButton("已选")
        selected_btn.setFixedSize(50, 25)
        selected_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: 1px solid #1976D2;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        selected_btn.setEnabled(False)
        
        # 已售座位
        sold_btn = QPushButton("已售")
        sold_btn.setFixedSize(50, 25)
        sold_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: 1px solid #d32f2f;
                border-radius: 3px;
                font-weight: bold;
            }
        """)
        sold_btn.setEnabled(False)
        
        legend_layout.addWidget(QLabel("座位状态:"))
        legend_layout.addWidget(available_btn)
        legend_layout.addWidget(QLabel("可选"))
        legend_layout.addWidget(selected_btn)
        legend_layout.addWidget(QLabel("已选"))
        legend_layout.addWidget(sold_btn)
        legend_layout.addWidget(QLabel("已售"))
        legend_layout.addStretch()
        
        layout.addLayout(legend_layout)
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.seat_map_loaded.connect(self.update_seat_data)
        event_bus.seat_map_loading.connect(self._on_seat_map_loading)
        event_bus.seat_map_error.connect(self._on_seat_map_error)
    
    @event_handler("seat_map_loaded")
    def update_seat_data(self, seat_data: dict):
        """更新座位数据"""
        try:
            print("[座位图面板] 开始更新座位数据")
            
            # 解析座位数据
            seat_matrix = self._parse_seat_data(seat_data)
            
            if seat_matrix:
                self.seat_matrix = seat_matrix
                self.hall_info = {
                    'name': seat_data.get('hname', '未知影厅'),
                    'screen_type': seat_data.get('screentype', ''),
                    'seat_count': seat_data.get('seatcount', 0)
                }
                
                # 渲染座位图
                self._render_seat_map()
                
                print(f"[座位图面板] 座位图更新成功: {self.hall_info['name']}")
            else:
                self._show_error("座位数据解析失败")
                
        except Exception as e:
            print(f"[座位图面板] 更新座位数据错误: {e}")
            self._show_error(f"更新座位数据失败: {str(e)}")
    
    def _parse_seat_data(self, seat_data: dict) -> List[List[Optional[dict]]]:
        """解析座位数据为矩阵"""
        try:
            seats_array = seat_data.get('seats', [])
            if not seats_array:
                return []
            
            # 分析座位矩阵尺寸
            max_row = max(seat.get('rn', 0) for seat in seats_array)
            max_col = max(seat.get('cn', 0) for seat in seats_array)
            
            if max_row == 0 or max_col == 0:
                return []
            
            # 创建座位矩阵
            seat_matrix = []
            for row in range(max_row):
                seat_row = [None] * max_col
                seat_matrix.append(seat_row)
            
            # 填充座位数据
            for seat in seats_array:
                row_num = seat.get('rn', 0) - 1  # 转为0基索引
                col_num = seat.get('cn', 0) - 1
                
                if 0 <= row_num < max_row and 0 <= col_num < max_col:
                    # 解析座位状态
                    seat_state = seat.get('s', 'F')
                    if seat_state == 'F':
                        status = 'available'
                    elif seat_state == 'B':
                        status = 'sold'
                    else:
                        status = 'unavailable'
                    
                    seat_info = {
                        'row': seat.get('rn', row_num + 1),
                        'col': seat.get('cn', col_num + 1),
                        'num': f"{seat.get('rn', row_num + 1)}-{seat.get('cn', col_num + 1)}",
                        'status': status,
                        'price': 0,
                        'seatname': seat.get('sn', ''),
                        'original_data': seat
                    }
                    
                    seat_matrix[row_num][col_num] = seat_info
            
            return seat_matrix
            
        except Exception as e:
            print(f"[座位图面板] 解析座位数据错误: {e}")
            return []
    
    def _render_seat_map(self):
        """渲染座位图"""
        try:
            # 清空现有内容
            self._clear_seat_layout()
            
            if not self.seat_matrix:
                self._show_placeholder("没有座位数据")
                return
            
            # 创建座位图网格
            seat_grid = QGridLayout()
            seat_grid.setSpacing(2)
            
            # 添加行号标签
            for row_idx, seat_row in enumerate(self.seat_matrix):
                row_label = QLabel(str(row_idx + 1))
                row_label.setFixedSize(20, 25)
                row_label.setAlignment(Qt.AlignCenter)
                row_label.setStyleSheet("font-weight: bold; color: #666;")
                seat_grid.addWidget(row_label, row_idx, 0)
                
                # 添加座位按钮
                for col_idx, seat_data in enumerate(seat_row):
                    if seat_data:
                        seat_button = SeatButton(seat_data, self)
                        seat_grid.addWidget(seat_button, row_idx, col_idx + 1)
                        
                        # 保存按钮引用
                        self.seat_buttons[(row_idx + 1, col_idx + 1)] = seat_button
            
            # 添加屏幕标识
            screen_label = QLabel("屏幕")
            screen_label.setAlignment(Qt.AlignCenter)
            screen_label.setStyleSheet("""
                QLabel {
                    background-color: #333;
                    color: white;
                    padding: 5px;
                    border-radius: 3px;
                    font-weight: bold;
                }
            """)
            
            # 创建座位图容器
            seat_widget = QWidget()
            seat_layout = QVBoxLayout(seat_widget)
            seat_layout.addWidget(screen_label)
            seat_layout.addLayout(seat_grid)
            seat_layout.setAlignment(Qt.AlignCenter)
            
            # 更新容器
            self.seat_layout.addWidget(seat_widget)
            
            # 启用操作按钮
            self.clear_button.setEnabled(True)
            
            print("[座位图面板] 座位图渲染完成")
            
        except Exception as e:
            print(f"[座位图面板] 渲染座位图错误: {e}")
            self._show_error(f"渲染座位图失败: {str(e)}")
    
    def _clear_seat_layout(self):
        """清空座位布局"""
        while self.seat_layout.count():
            child = self.seat_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.seat_buttons.clear()
        self.selected_seats.clear()
    
    def _show_placeholder(self, message: str):
        """显示占位符"""
        self.placeholder_label.setText(message)
        self.seat_layout.addWidget(self.placeholder_label)
    
    def _show_error(self, message: str):
        """显示错误信息"""
        self._show_placeholder(f"加载失败\n\n{message}")
    
    @event_handler("seat_map_loading")
    def _on_seat_map_loading(self):
        """座位图加载中 - 🆕 移除加载提示"""
        # 🆕 不显示加载提示，直接等待座位图数据
        pass
    
    @event_handler("seat_map_error")
    def _on_seat_map_error(self, error_msg: str):
        """座位图加载错误"""
        self._show_error(error_msg)
    
    def on_seat_clicked(self, seat_button: SeatButton):
        """座位按钮点击处理"""
        try:
            seat_pos = (seat_button.row, seat_button.col)
            
            if seat_button.status == 'selected':
                self.selected_seats.add(seat_pos)
            else:
                self.selected_seats.discard(seat_pos)
            
            # 更新座位输入框
            self._update_seat_input()
            
            # 更新提交按钮状态
            self.submit_button.setEnabled(len(self.selected_seats) > 0)
            
            # 发送座位选择信号
            selected_seat_data = []
            for row, col in self.selected_seats:
                if (row, col) in self.seat_buttons:
                    button = self.seat_buttons[(row, col)]
                    selected_seat_data.append(button.seat_data)
            
            self.seat_selected.emit(selected_seat_data)
            
        except Exception as e:
            print(f"[座位图面板] 座位点击处理错误: {e}")
    
    def _update_seat_input(self):
        """更新座位输入框"""
        if self.selected_seats:
            seat_names = [f"{row}-{col}" for row, col in sorted(self.selected_seats)]
            self.seat_input.setText(", ".join(seat_names))
        else:
            self.seat_input.setText("")
    
    def clear_selection(self):
        """清空选择"""
        try:
            # 重置所有已选座位
            for row, col in self.selected_seats.copy():
                if (row, col) in self.seat_buttons:
                    button = self.seat_buttons[(row, col)]
                    button.set_status('available')
            
            self.selected_seats.clear()
            self._update_seat_input()
            self.submit_button.setEnabled(False)
            
            # 发送清空信号
            self.seat_selected.emit([])
            
        except Exception as e:
            print(f"[座位图面板] 清空选择错误: {e}")
    
    def submit_order(self):
        """提交订单"""
        try:
            if not self.selected_seats:
                return
            
            # 构建选中座位数据
            selected_seat_data = []
            for row, col in self.selected_seats:
                if (row, col) in self.seat_buttons:
                    button = self.seat_buttons[(row, col)]
                    selected_seat_data.append(button.seat_data)
            
            # 发送提交订单信号
            order_data = {
                'seats': selected_seat_data,
                'hall_info': self.hall_info,
                'trigger_type': 'seat_map_panel'
            }
            
            self.order_submitted.emit(order_data)
            
        except Exception as e:
            print(f"[座位图面板] 提交订单错误: {e}")
    
    def get_selected_seats(self) -> List[dict]:
        """获取选中的座位数据"""
        selected_seat_data = []
        for row, col in self.selected_seats:
            if (row, col) in self.seat_buttons:
                button = self.seat_buttons[(row, col)]
                selected_seat_data.append(button.seat_data)
        return selected_seat_data

    def set_enabled(self, enabled: bool):
        """设置面板启用状态"""
        self.clear_button.setEnabled(enabled and len(self.selected_seats) > 0)
        self.submit_button.setEnabled(enabled and len(self.selected_seats) > 0)

        # 设置所有座位按钮状态
        for button in self.seat_buttons.values():
            if button.status in ['available', 'selected']:
                button.setEnabled(enabled)
