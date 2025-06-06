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
from PyQt5.QtCore import Qt, pyqtSignal, QPoint
from PyQt5.QtGui import QFont, QPalette, QMouseEvent

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

        # 🆕 拖拽滚动相关属性
        self.is_dragging = False
        self.last_mouse_pos = QPoint()
        self.drag_start_pos = QPoint()

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

        # 🆕 启用鼠标拖拽滚动功能
        self.scroll_area.setMouseTracking(True)
        self.scroll_area.mousePressEvent = self._scroll_area_mouse_press
        self.scroll_area.mouseMoveEvent = self._scroll_area_mouse_move
        self.scroll_area.mouseReleaseEvent = self._scroll_area_mouse_release
        
        # 座位网格容器
        self.seat_widget = QWidget()
        self.seat_layout = QGridLayout(self.seat_widget)
        self.seat_layout.setSpacing(2)  # 座位之间的间距

        # 🔧 修复：设置座位图居中对齐
        self.seat_layout.setAlignment(Qt.AlignCenter)

        self.scroll_area.setWidget(self.seat_widget)
        layout.addWidget(self.scroll_area, 1)
        
        # 🆕 简化底部信息区 - 完全移除选座信息区域，为座位图腾出更多空间
        bottom_layout = QVBoxLayout()

        # 移除选座信息区域，直接显示提交按钮
        
        # 提交订单按钮 - 集成选座信息，居中显示
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # 左侧弹性空间
        self.submit_btn = QPushButton("提交订单")
        self.submit_btn.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        self.submit_btn.clicked.connect(self._on_submit_order_click)
        self._setup_submit_button_style(self.submit_btn)
        button_layout.addWidget(self.submit_btn)
        button_layout.addStretch()  # 右侧弹性空间
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
        """设置提交按钮样式 - 集成选座信息，居中显示，高度增加四分之一"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font: bold 11px "Microsoft YaHei";
                border: none;
                padding: 6px 20px;
                border-radius: 4px;
                min-width: 200px;
                min-height: 25px;
                max-height: 25px;
                text-align: center;
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
                # 🆕 修复：为空位也创建占位符，确保物理间隔正确显示
                grid_col = c + 1  # 由于第0列是行号标签，座位从第1列开始

                if seat is None:
                    # 🆕 为空位创建透明占位符，保持物理间隔
                    spacer = QLabel("")
                    spacer.setFixedSize(36, 36)
                    spacer.setStyleSheet("background-color: transparent; border: none;")
                    self.seat_layout.addWidget(spacer, r, grid_col)
                    continue

                # 确保使用正确的列号，而不是数组索引
                col_num = seat.get('col', c + 1)

                status = seat.get('status', 'available')
                if status == 'empty':
                    # 🆕 为empty状态也创建占位符
                    spacer = QLabel("")
                    spacer.setFixedSize(36, 36)
                    spacer.setStyleSheet("background-color: transparent; border: none;")
                    self.seat_layout.addWidget(spacer, r, grid_col)
                    continue
                
                # 创建座位按钮 - 更现代化的样式
                seat_btn = QPushButton()
                seat_btn.setFixedSize(36, 36)  # 稍微增大尺寸
                
                # 🆕 修复：显示真实座位号（n字段）
                # 物理座位号（rn, cn）用于构建座位图布局
                # 真实座位号（r, n）用于显示和提交
                real_seat_num = seat.get('num', '')  # 这里的num已经是处理过的真实座位号n
                if not real_seat_num:
                    # 备选：使用物理列号
                    real_seat_num = str(seat.get('col', col_num))

                seat_btn.setText(real_seat_num)
                
                # 设置样式
                self._update_seat_button_style(seat_btn, status)
                
                # 设置点击事件
                if status == "available":
                    # 🆕 使用自定义的座位按钮点击处理，支持拖拽滚动
                    seat_btn.clicked.connect(lambda checked, r=r, c=c: self._seat_button_clicked(r, c))
                    seat_btn.setCursor(Qt.PointingHandCursor)

                    # 🆕 为座位按钮添加鼠标事件处理
                    seat_btn.mousePressEvent = lambda event, r=r, c=c: self._seat_button_mouse_press(event, r, c)
                    seat_btn.mouseMoveEvent = lambda event, r=r, c=c: self._seat_button_mouse_move(event, r, c)
                    seat_btn.mouseReleaseEvent = lambda event, r=r, c=c: self._seat_button_mouse_release(event, r, c)
                else:
                    seat_btn.setEnabled(False)
                
                # 添加到布局 - 🆕 使用正确的网格位置
                self.seat_layout.addWidget(seat_btn, r, grid_col)
                
                # 保存引用
                self.seat_buttons[(r, c)] = seat_btn
        
        print(f"[座位面板] 座位图绘制完成，共{len(self.seat_buttons)}个座位")

        # 初始化按钮文字
        self._update_submit_button_text()
    
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

        print(f"[座位面板] 座位{seat.get('num', f'{r+1}-{c+1}')}切换为: {seat['status']}")
        print(f"[座位面板] 当前已选座位数: {len(self.selected_seats)}")

        # 更新提交按钮文字
        self._update_submit_button_text()
    
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
    
    def _update_submit_button_text(self):
        """更新提交按钮文字 - 集成选座信息"""
        selected_count = len(self.selected_seats)
        if selected_count == 0:
            self.submit_btn.setText("提交订单")
        else:
            # 获取选中座位的排号信息
            selected_seats_info = []
            for (r, c) in self.selected_seats:
                seat = self.seat_data[r][c]
                # 获取座位的排号和列号
                row_num = seat.get('row', r + 1)
                col_num = seat.get('col', c + 1)
                seat_info = f"{row_num}排{col_num}"
                selected_seats_info.append(seat_info)

            # 按钮文字格式：提交订单 5排13 5排12
            seats_text = " ".join(selected_seats_info)
            self.submit_btn.setText(f"提交订单 {seats_text}")

        print(f"[座位面板] 按钮文字已更新: '{self.submit_btn.text()}'")
    
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
        print(f"[座位面板] 座位状态已重置，已选座位已清空")

        # 更新提交按钮文字
        self._update_submit_button_text()
    
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

    # 🆕 鼠标拖拽滚动功能实现
    def _scroll_area_mouse_press(self, event: QMouseEvent):
        """滚动区域鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.last_mouse_pos = event.pos()
            self.drag_start_pos = event.pos()
            # 设置拖拽光标
            self.scroll_area.setCursor(Qt.ClosedHandCursor)
            print(f"[座位面板] 开始拖拽滚动，起始位置: {event.pos()}")

    def _scroll_area_mouse_move(self, event: QMouseEvent):
        """滚动区域鼠标移动事件"""
        if self.is_dragging and event.buttons() & Qt.LeftButton:
            # 计算鼠标移动的距离
            delta = event.pos() - self.last_mouse_pos

            # 获取滚动条
            h_scrollbar = self.scroll_area.horizontalScrollBar()
            v_scrollbar = self.scroll_area.verticalScrollBar()

            # 根据鼠标移动方向调整滚动位置
            # 注意：鼠标向右移动时，我们希望内容向右移动（即滚动条向左移动）
            # 所以滚动值的变化方向与鼠标移动方向相反
            new_h_value = h_scrollbar.value() - delta.x()
            new_v_value = v_scrollbar.value() - delta.y()

            # 限制滚动范围
            new_h_value = max(h_scrollbar.minimum(), min(h_scrollbar.maximum(), new_h_value))
            new_v_value = max(v_scrollbar.minimum(), min(v_scrollbar.maximum(), new_v_value))

            # 设置新的滚动位置
            h_scrollbar.setValue(new_h_value)
            v_scrollbar.setValue(new_v_value)

            # 更新鼠标位置
            self.last_mouse_pos = event.pos()

            # 调试输出（可选）
            # print(f"[座位面板] 拖拽滚动，delta: {delta}, 滚动位置: H={new_h_value}, V={new_v_value}")

    def _scroll_area_mouse_release(self, event: QMouseEvent):
        """滚动区域鼠标释放事件"""
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            # 恢复默认光标
            self.scroll_area.setCursor(Qt.ArrowCursor)

            # 计算总的拖拽距离
            total_delta = event.pos() - self.drag_start_pos
            print(f"[座位面板] 结束拖拽滚动，总移动距离: {total_delta}")

            # 重置位置
            self.last_mouse_pos = QPoint()
            self.drag_start_pos = QPoint()

    # 🆕 座位按钮鼠标事件处理（支持拖拽滚动）
    def _seat_button_mouse_press(self, event: QMouseEvent, r: int, c: int):
        """座位按钮鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 记录按下位置，用于判断是点击还是拖拽
            self.drag_start_pos = event.globalPos()
            self.last_mouse_pos = event.globalPos()
            # 暂时不设置拖拽状态，等移动一定距离后再判断

    def _seat_button_mouse_move(self, event: QMouseEvent, r: int, c: int):
        """座位按钮鼠标移动事件"""
        if event.buttons() & Qt.LeftButton:
            # 计算移动距离
            move_distance = (event.globalPos() - self.drag_start_pos).manhattanLength()

            # 如果移动距离超过阈值，开始拖拽滚动
            if move_distance > 5 and not self.is_dragging:  # 5像素的拖拽阈值
                self.is_dragging = True
                self.scroll_area.setCursor(Qt.ClosedHandCursor)
                print(f"[座位面板] 在座位按钮上开始拖拽滚动")

            # 如果正在拖拽，执行滚动
            if self.is_dragging:
                # 计算鼠标移动的距离
                delta = event.globalPos() - self.last_mouse_pos

                # 获取滚动条
                h_scrollbar = self.scroll_area.horizontalScrollBar()
                v_scrollbar = self.scroll_area.verticalScrollBar()

                # 根据鼠标移动方向调整滚动位置
                new_h_value = h_scrollbar.value() - delta.x()
                new_v_value = v_scrollbar.value() - delta.y()

                # 限制滚动范围
                new_h_value = max(h_scrollbar.minimum(), min(h_scrollbar.maximum(), new_h_value))
                new_v_value = max(v_scrollbar.minimum(), min(v_scrollbar.maximum(), new_v_value))

                # 设置新的滚动位置
                h_scrollbar.setValue(new_h_value)
                v_scrollbar.setValue(new_v_value)

                # 更新鼠标位置
                self.last_mouse_pos = event.globalPos()

    def _seat_button_mouse_release(self, event: QMouseEvent, r: int, c: int):
        """座位按钮鼠标释放事件"""
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                # 如果是拖拽，结束拖拽状态
                self.is_dragging = False
                self.scroll_area.setCursor(Qt.ArrowCursor)
                print(f"[座位面板] 在座位按钮上结束拖拽滚动")

                # 重置位置
                self.last_mouse_pos = QPoint()
                self.drag_start_pos = QPoint()
            else:
                # 如果不是拖拽，执行座位选择
                move_distance = (event.globalPos() - self.drag_start_pos).manhattanLength()
                if move_distance <= 5:  # 只有在移动距离很小时才认为是点击
                    self.toggle_seat(r, c)

    def _seat_button_clicked(self, r: int, c: int):
        """座位按钮点击事件（备用，主要逻辑在mouse_release中处理）"""
        # 这个方法现在主要作为备用，实际的点击逻辑在_seat_button_mouse_release中处理
        # 如果没有拖拽，mouse_release会调用toggle_seat
        pass