#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位面板 - PyQt5版本
模仿tkinter版本的规则网格布局显示座位图
"""

from typing import Callable, Optional, Dict, List, Set, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette

class SeatMapPanelPyQt5(QWidget):
    """座位面板 - PyQt5版本，模仿tkinter布局"""
    
    # 信号定义
    seat_selected = pyqtSignal(list)  # 选座变化信号
    
    def __init__(self, parent=None, seat_data=None):
        super().__init__(parent)
        
        # 数据
        self.seat_data = seat_data or []
        self.selected_seats: Set[Tuple[int, int]] = set()
        self._priceinfo = {}
        self.account_getter = lambda: {}
        self.on_seat_selected = None
        self.on_submit_order = None
        
        # UI组件
        self.seat_buttons: Dict[Tuple[int, int], QPushButton] = {}
        
        self._init_ui()
        self._draw_seats()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)
        
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 座位网格容器
        self.seat_widget = QWidget()
        self.seat_layout = QGridLayout(self.seat_widget)
        self.seat_layout.setSpacing(2)  # 座位之间的间距
        
        self.scroll_area.setWidget(self.seat_widget)
        layout.addWidget(self.scroll_area, 1)
        
        # 🆕 简化底部信息区 - 移除图例
        bottom_layout = QVBoxLayout()
        
        # 选座信息 - 简洁显示
        self.info_label = QLabel("请选择座位")
        self.info_label.setFont(QFont("Microsoft YaHei", 10))
        self.info_label.setStyleSheet("""
            QLabel { 
                color: #333; 
                padding: 8px; 
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        bottom_layout.addWidget(self.info_label)
        
        # 提交订单按钮
        button_layout = QHBoxLayout()
        self.submit_btn = QPushButton("提交订单")
        self.submit_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.submit_btn.clicked.connect(self._on_submit_order_click)
        self._setup_submit_button_style(self.submit_btn)
        button_layout.addWidget(self.submit_btn)
        button_layout.addStretch()
        bottom_layout.addLayout(button_layout)
        
        layout.addLayout(bottom_layout)
        
        # 设置滚动区域样式
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #fff;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)
    
    def _setup_submit_button_style(self, button: QPushButton):
        """设置提交按钮样式"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font: bold 12px "Microsoft YaHei";
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                min-width: 120px;
                min-height: 40px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #fff;
            }
        """)
    
    def _draw_seats(self):
        """绘制所有座位 - 使用网格布局模仿tkinter风格"""
        # 清空现有布局
        for i in reversed(range(self.seat_layout.count())):
            child = self.seat_layout.itemAt(i)
            if child.widget():
                child.widget().deleteLater()
        
        self.seat_buttons.clear()
        
        if not self.seat_data:
            # 显示空状态
            empty_label = QLabel("暂无座位数据")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setStyleSheet("color: #6c757d; font: 14px 'Microsoft YaHei';")
            self.seat_layout.addWidget(empty_label, 0, 0)
            return
        
        print(f"[座位面板] 开始绘制座位图，数据: {len(self.seat_data)} 行")
        
        # 计算最大列数用于行号标签定位
        max_col = 0
        for row in self.seat_data:
            for seat in row:
                if seat:
                    col_num = seat.get('col', 0)
                    max_col = max(max_col, col_num)
        
        print(f"[座位面板] 最大列数: {max_col}")
        
        # 绘制每一行
        for r, row in enumerate(self.seat_data):
            if not row:
                continue
            
            # 获取行号（从第一个非空座位获取）
            row_num = None
            for seat in row:
                if seat:
                    row_num = seat.get('row', r + 1)
                    break
            
            if row_num is None:
                continue
            
            # 创建行号标签（放在第0列）- 🆕 更简洁的数字显示
            row_label = QLabel(f"{row_num}")
            row_label.setAlignment(Qt.AlignCenter)
            row_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
            row_label.setStyleSheet("""
                QLabel {
                    color: #6c757d;
                    background-color: transparent;
                    border: none;
                    padding: 2px;
                    min-width: 24px;
                    min-height: 32px;
                    font-weight: bold;
                }
            """)
            self.seat_layout.addWidget(row_label, r, 0)
            
            # 绘制这一行的座位
            for c, seat in enumerate(row):
                if seat is None:
                    continue
                
                # 确保使用正确的列号，而不是数组索引
                col_num = seat.get('col', c + 1)
                # 由于第0列是行号标签，座位从第1列开始，所以实际列位置是col_num
                grid_col = col_num
                
                status = seat.get('status', 'available')
                if status == 'empty':
                    continue
                
                # 创建座位按钮 - 更现代化的样式
                seat_btn = QPushButton()
                seat_btn.setFixedSize(36, 36)  # 稍微增大尺寸
                
                # 座位编号显示优化 - 直接显示列号
                btn_text = str(col_num)
                seat_btn.setText(btn_text)
                
                # 设置样式
                self._update_seat_button_style(seat_btn, status)
                
                # 设置点击事件
                if status == "available":
                    seat_btn.clicked.connect(lambda checked, r=r, c=c: self.toggle_seat(r, c))
                    seat_btn.setCursor(Qt.PointingHandCursor)
                else:
                    seat_btn.setEnabled(False)
                
                # 添加到布局
                self.seat_layout.addWidget(seat_btn, r, grid_col)
                
                # 保存引用
                self.seat_buttons[(r, c)] = seat_btn
        
        print(f"[座位面板] 座位图绘制完成，共{len(self.seat_buttons)}个座位")
        
        # 更新信息显示
        self.update_info_label()
    
    def _update_seat_button_style(self, button: QPushButton, status: str):
        """更新座位按钮样式 - 现代化设计"""
        if status == "available":
            # 可选座位 - 清新的蓝色
            button.setStyleSheet("""
                QPushButton {
                    background-color: #e3f2fd;
                    border: 2px solid #2196f3;
                    color: #1976d2;
                    font: bold 10px "Microsoft YaHei";
                    border-radius: 6px;
                }
                QPushButton:hover {
                    background-color: #bbdefb;
                    border-color: #1976d2;
                }
                QPushButton:pressed {
                    background-color: #90caf9;
                }
            """)
        elif status == "sold":
            # 已售座位 - 温和的灰色
            button.setStyleSheet("""
                QPushButton {
                    background-color: #f5f5f5;
                    border: 2px solid #9e9e9e;
                    color: #757575;
                    font: 10px "Microsoft YaHei";
                    border-radius: 6px;
                }
            """)
        elif status == "selected":
            # 选中座位 - 鲜明的绿色
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    border: 2px solid #388e3c;
                    color: #fff;
                    font: bold 10px "Microsoft YaHei";
                    border-radius: 6px;
                }
            """)
        else:
            # 其他状态 - 默认样式
            button.setStyleSheet("""
                QPushButton {
                    background-color: #fafafa;
                    border: 2px solid #e0e0e0;
                    color: #bdbdbd;
                    font: 10px "Microsoft YaHei";
                    border-radius: 6px;
                }
            """)
    
    def toggle_seat(self, r: int, c: int):
        """切换座位选中状态"""
        if (r, c) not in self.seat_buttons:
            return
        
        seat = self.seat_data[r][c]
        key = (r, c)
        
        if key in self.selected_seats:
            # 取消选中
            self.selected_seats.remove(key)
            # 恢复原始状态
            original_data = seat.get('original_data', {})
            original_state = original_data.get('s', 'F')
            if original_state == 'B':
                seat['status'] = 'sold'
            elif original_state == 'F':
                seat['status'] = 'available'
            else:
                seat['status'] = 'unavailable'
        else:
            # 选中
            self.selected_seats.add(key)
            seat['status'] = "selected"
        
        # 更新按钮样式
        seat_btn = self.seat_buttons[key]
        self._update_seat_button_style(seat_btn, seat['status'])
        
        # 触发选座回调
        if self.on_seat_selected:
            selected = [self.seat_data[r][c] for (r, c) in self.selected_seats]
            self.on_seat_selected(selected)
        
        # 发送信号
        selected_seats = [self.seat_data[r][c] for (r, c) in self.selected_seats]
        self.seat_selected.emit(selected_seats)
        
        # 更新信息显示
        self.update_info_label()
        
        print(f"[座位面板] 座位{seat.get('num', f'{r+1}-{c+1}')}切换为: {seat['status']}")
    
    def update_seat_data(self, seat_data: List[List]):
        """更新座位数据并重绘"""
        self.seat_data = seat_data or []
        self.selected_seats.clear()
        self._draw_seats()
        print(f"[座位面板] 更新座位数据: {len(self.seat_data)} 行")
    
    def update_seats(self, seat_data: List[List]):
        """更新座位数据（兼容原接口）"""
        self.update_seat_data(seat_data)
    
    def get_selected_seats(self) -> List[str]:
        """获取选中座位编号列表"""
        return [self.seat_data[r][c]['num'] for (r, c) in self.selected_seats]
    
    def get_selected_seat_objects(self) -> List[Dict]:
        """获取选中座位对象列表"""
        return [self.seat_data[r][c] for (r, c) in self.selected_seats]
    
    def update_info_label(self):
        """更新信息显示 - 简洁明了"""
        selected_count = len(self.selected_seats)
        if selected_count == 0:
            self.info_label.setText("👆 请点击上方座位进行选择")
        else:
            selected_nums = self.get_selected_seats()
            price_per_seat = 35.0  # 假设价格
            total_price = selected_count * price_per_seat
            self.info_label.setText(f"✅ 已选 {selected_count} 个座位: {', '.join(selected_nums)} | 总计: ¥{total_price:.0f}")
    
    def set_on_seat_selected(self, callback: Callable):
        """设置选座回调函数"""
        self.on_seat_selected = callback
    
    def set_on_submit_order(self, callback: Callable):
        """设置提交订单回调函数"""
        self.on_submit_order = callback
    
    def set_account_getter(self, getter: Callable):
        """设置获取账号信息的函数"""
        self.account_getter = getter
    
    def set_priceinfo(self, priceinfo: Dict):
        """设置价格信息"""
        self._priceinfo = priceinfo
    
    def _on_submit_order_click(self):
        """提交订单按钮点击事件"""
        if not self.selected_seats:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提交订单", "请先选择座位")
            return
        
        if self.on_submit_order:
            selected_seat_objects = self.get_selected_seat_objects()
            self.on_submit_order(selected_seat_objects)
        
        print(f"[座位面板] 提交订单，选中座位: {self.get_selected_seats()}")
    
    def clear_selection(self):
        """清空选择"""
        for (r, c) in list(self.selected_seats):
            seat = self.seat_data[r][c]
            # 恢复原始状态
            original_data = seat.get('original_data', {})
            original_state = original_data.get('s', 'F')
            if original_state == 'B':
                seat['status'] = 'sold'
            elif original_state == 'F':
                seat['status'] = 'available'
            else:
                seat['status'] = 'unavailable'
            
            if (r, c) in self.seat_buttons:
                seat_btn = self.seat_buttons[(r, c)]
                self._update_seat_button_style(seat_btn, seat['status'])
        
        self.selected_seats.clear()
        self.update_info_label()
    
    def set_enabled(self, enabled: bool):
        """设置是否可用"""
        self.scroll_area.setEnabled(enabled)
        self.submit_btn.setEnabled(enabled)
    
    def get_seat_count_info(self) -> Dict:
        """获取座位统计信息"""
        total = 0
        available = 0
        sold = 0
        selected = len(self.selected_seats)
        
        for row in self.seat_data:
            for seat in row:
                if seat is not None and seat.get('status') != 'empty':
                    total += 1
                    status = seat.get('status', 'available')
                    if status == 'available':
                        available += 1
                    elif status == 'sold':
                        sold += 1
        
        return {
            'total': total,
            'available': available,
            'sold': sold,
            'selected': selected
        } 