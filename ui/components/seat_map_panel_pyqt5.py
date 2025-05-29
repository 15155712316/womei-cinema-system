#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
座位面板 - PyQt5版本
使用QGraphicsView和QGraphicsScene实现座位图显示和交互功能
"""

from typing import Callable, Optional, Dict, List, Set, Tuple
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem,
    QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt5.QtGui import QFont, QBrush, QColor, QPen, QPainter

class SeatItem(QGraphicsRectItem):
    """座位图形项"""
    
    def __init__(self, row: int, col: int, seat_data: Dict, parent=None):
        super().__init__(parent)
        self.row = row
        self.col = col
        self.seat_data = seat_data
        self.seat_panel = None  # 座位面板引用
        
        # 设置基本属性
        self.setRect(0, 0, 32, 32)
        self.setPen(QPen(QColor("#000"), 1))
        
        # 创建文本项
        self.text_item = QGraphicsTextItem(self)
        self.text_item.setPos(8, 8)  # 居中位置
        
        # 更新显示
        self.update_display()
    
    def set_seat_panel(self, seat_panel):
        """设置座位面板引用"""
        self.seat_panel = seat_panel
    
    def update_display(self):
        """更新座位显示"""
        status = self.seat_data.get('status', 'available')
        num = str(self.seat_data.get('num', ''))
        
        # 设置背景色
        if status == "available":
            self.setBrush(QBrush(QColor("#fff")))
        elif status == "sold":
            self.setBrush(QBrush(QColor("#bdbdbd")))
        elif status == "selected":
            self.setBrush(QBrush(QColor("#00FF00")))
        else:
            self.setBrush(QBrush(QColor("#fff")))
        
        # 设置文本
        self.text_item.setPlainText(num)
        
        # 设置字体和颜色
        font = QFont("微软雅黑", 9)
        if status == "sold":
            font.setBold(True)
        self.text_item.setFont(font)
        
        # 设置文本颜色
        if status == "sold":
            self.text_item.setDefaultTextColor(QColor("#000"))
        elif status == "selected":
            self.text_item.setDefaultTextColor(QColor("#fff"))
        else:
            self.text_item.setDefaultTextColor(QColor("#000"))
        
        # 设置可点击性
        if status == "available":
            self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
            self.setCursor(Qt.ArrowCursor)
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.LeftButton:
            status = self.seat_data.get('status', 'available')
            if status == "available" or status == "selected":
                if self.seat_panel:
                    self.seat_panel.toggle_seat(self.row, self.col)
        super().mousePressEvent(event)

class SeatMapPanelPyQt5(QWidget):
    """座位面板 - PyQt5版本"""
    
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
        self.seat_items: Dict[Tuple[int, int], SeatItem] = {}
        
        self._init_ui()
        self._draw_seats()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 创建座位图区域
        self.graphics_view = QGraphicsView()
        self.graphics_scene = QGraphicsScene()
        self.graphics_view.setScene(self.graphics_scene)
        
        # 设置视图属性
        self.graphics_view.setRenderHint(QPainter.Antialiasing)
        self.graphics_view.setDragMode(QGraphicsView.ScrollHandDrag)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 设置样式
        self.graphics_view.setStyleSheet("""
            QGraphicsView {
                background-color: #fff;
                border: 1px solid #ccc;
                border-radius: 2px;
            }
        """)
        
        layout.addWidget(self.graphics_view, 1)
        
        # 底部按钮区
        button_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("提交订单")
        self.submit_btn.setFont(QFont("微软雅黑", 11, QFont.Bold))
        self.submit_btn.clicked.connect(self._on_submit_order_click)
        self._setup_submit_button_style(self.submit_btn)
        
        button_layout.addWidget(self.submit_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 信息显示区
        self.info_label = QLabel("请选择座位")
        self.info_label.setFont(QFont("微软雅黑", 10))
        self.info_label.setStyleSheet("QLabel { color: #666; }")
        layout.addWidget(self.info_label)
    
    def _setup_submit_button_style(self, button: QPushButton):
        """设置提交按钮样式"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font: bold 11px "Microsoft YaHei";
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                min-width: 100px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1e7e34;
            }
            QPushButton:pressed {
                background-color: #155724;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
    
    def _draw_seats(self):
        """绘制所有座位"""
        # 清空现有内容
        self.graphics_scene.clear()
        self.seat_items.clear()
        
        if not self.seat_data:
            return
        
        # 座位格子参数
        cell_w, cell_h = 32, 32
        pad_x, pad_y = 4, 4
        label_w = 16
        
        for r, row in enumerate(self.seat_data):
            # 计算行位置
            y = pad_y + r * (cell_h + pad_y)
            
            # 获取行号标签
            row_label = "?"
            for seat in row:
                if seat is not None:
                    row_label = str(seat.get('row', r+1))
                    break
            
            # 创建行号标签
            row_text = QGraphicsTextItem(row_label)
            row_text.setFont(QFont("微软雅黑", 8, QFont.Bold))
            row_text.setDefaultTextColor(QColor("#333"))
            row_text.setPos(0, y + cell_h//2 - 8)
            self.graphics_scene.addItem(row_text)
            
            for c, seat in enumerate(row):
                if seat is None:
                    continue
                
                cn = int(seat.get('cn', c+1))
                x = label_w + pad_x + (cn-1) * (cell_w + pad_x)
                status = seat.get('status', 'available')
                
                if status == 'empty':
                    continue
                
                # 创建座位项
                seat_item = SeatItem(r, c, seat)
                seat_item.set_seat_panel(self)
                seat_item.setPos(x, y)
                
                self.graphics_scene.addItem(seat_item)
                self.seat_items[(r, c)] = seat_item
        
        # 调整场景大小
        self.graphics_scene.setSceneRect(self.graphics_scene.itemsBoundingRect())
        
        # 更新信息显示
        self.update_info_label()
    
    def toggle_seat(self, r: int, c: int):
        """切换座位选中状态"""
        if (r, c) not in self.seat_items:
            return
        
        seat = self.seat_data[r][c]
        key = (r, c)
        
        if key in self.selected_seats:
            # 取消选中
            self.selected_seats.remove(key)
            seat['status'] = 'available' if seat.get('s', 'F') == 'F' else 'sold'
        else:
            # 选中
            self.selected_seats.add(key)
            seat['status'] = "selected"
        
        # 更新座位显示
        seat_item = self.seat_items[key]
        seat_item.update_display()
        
        # 触发选座回调
        if self.on_seat_selected:
            selected = [self.seat_data[r][c] for (r, c) in self.selected_seats]
            self.on_seat_selected(selected)
        
        # 发送信号
        selected_seats = [self.seat_data[r][c] for (r, c) in self.selected_seats]
        self.seat_selected.emit(selected_seats)
        
        # 更新信息显示
        self.update_info_label()
    
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
        """更新信息显示"""
        selected_count = len(self.selected_seats)
        if selected_count == 0:
            self.info_label.setText("请选择座位")
        else:
            selected_nums = self.get_selected_seats()
            self.info_label.setText(f"已选择 {selected_count} 个座位: {', '.join(selected_nums)}")
    
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
    
    def clear_selection(self):
        """清空选择"""
        for (r, c) in list(self.selected_seats):
            seat = self.seat_data[r][c]
            seat['status'] = 'available' if seat.get('s', 'F') == 'F' else 'sold'
            
            if (r, c) in self.seat_items:
                self.seat_items[(r, c)].update_display()
        
        self.selected_seats.clear()
        self.update_info_label()
    
    def set_enabled(self, enabled: bool):
        """设置是否可用"""
        self.graphics_view.setEnabled(enabled)
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