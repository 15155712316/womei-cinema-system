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
    """座位面板 - PyQt5版本，模仿tkinter布局，支持多区域显示"""

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

        # 🆕 多区域支持
        self.area_data = []  # 存储区域信息
        self.area_colors = self._init_area_colors()  # 区域颜色映射

        # UI组件
        self.seat_buttons: Dict[Tuple[int, int], QPushButton] = {}

        # 🆕 拖拽滚动相关属性
        self.is_dragging = False
        self.last_mouse_pos = QPoint()
        self.drag_start_pos = QPoint()

        self._init_ui()
        self._draw_seats()

    def _init_area_colors(self) -> Dict[str, str]:
        """初始化区域颜色映射 - 柔和用户友好的色彩方案"""
        return {
            '默认区': '#F0F8FF',      # 淡蓝色 - 柔和清新
            '前排区域': '#FFE4B5',    # 柔和金色 - 温暖舒适
            '按摩区域': '#FFE4E1',    # 淡粉色 - 温和优雅
            '中心区域': '#E6F3FF'     # 浅蓝色 - 宁静专业
        }

    def _get_area_border_color(self, area_name: str) -> str:
        """根据区域名称获取边框颜色"""
        return self.area_colors.get(area_name, '#CCCCCC')  # 默认灰色

    def _update_area_info_display(self):
        """更新区域信息显示"""
        # 清空现有的区域信息标签
        for label in self.area_info_labels.values():
            label.deleteLater()
        self.area_info_labels.clear()

        # 收集区域信息
        area_info = {}
        for row in self.seat_data:
            for seat in row:
                if seat and seat.get('area_name'):
                    area_name = seat.get('area_name', '')
                    area_price = seat.get('area_price', 0)
                    if area_name and area_name not in area_info:
                        area_info[area_name] = area_price

        # 创建区域信息标签
        for area_name, area_price in area_info.items():
            area_color = self._get_area_border_color(area_name)

            # 创建区域信息标签 - 使用柔和的样式
            area_label = QLabel(f"{area_name} {area_price}元")
            area_label.setStyleSheet(f"""
                QLabel {{
                    background-color: {area_color};
                    border: 1px solid #ddd;
                    color: #555;
                    font: bold 11px "Microsoft YaHei";
                    padding: 6px 12px;
                    border-radius: 6px;
                    margin: 2px;
                }}
            """)

            self.area_info_layout.addWidget(area_label)
            self.area_info_labels[area_name] = area_label

        # 区域信息显示已更新

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

        # 🆕 区域价格信息显示
        self.area_info_layout = QHBoxLayout()
        self.area_info_layout.setAlignment(Qt.AlignCenter)
        self.area_info_labels = {}  # 存储区域信息标签
        layout.addLayout(self.area_info_layout)

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

            QPushButton:pressed {
                background-color: #004085;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: #fff;
            }
        """)
    
    def _draw_seats(self):
        """绘制所有座位 - 使用物理位置(x,y)确定显示位置，保存逻辑位置(row,col)用于订单"""
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

        # print(f"[座位面板] 开始绘制座位图，数据: {len(self.seat_data)} 行")

        # 🔧 重新设计：使用物理位置(x,y)来确定座位在网格中的显示位置
        # 首先收集所有座位的物理位置信息
        all_seats = []
        max_physical_x = 0
        max_physical_y = 0

        for row_index, row in enumerate(self.seat_data):
            for col_index, seat in enumerate(row):
                if seat:
                    # 获取物理位置（用于显示）
                    physical_x = seat.get('x', col_index + 1)  # 物理X坐标
                    physical_y = seat.get('y', row_index + 1)  # 物理Y坐标

                    # 获取逻辑位置（用于订单）
                    logical_row = seat.get('row', row_index + 1)  # 逻辑行号
                    logical_col = seat.get('col', col_index + 1)  # 逻辑列号

                    seat_info = {
                        'seat_data': seat,
                        'physical_x': physical_x,
                        'physical_y': physical_y,
                        'logical_row': logical_row,
                        'logical_col': logical_col,
                        'array_row': row_index,  # 数组索引
                        'array_col': col_index   # 数组索引
                    }
                    all_seats.append(seat_info)

                    max_physical_x = max(max_physical_x, physical_x)
                    max_physical_y = max(max_physical_y, physical_y)

        # 物理坐标范围和总座位数统计完成

        # 🔧 创建行号标签（基于物理Y坐标）
        displayed_rows = set()
        for seat_info in all_seats:
            physical_y = seat_info['physical_y']
            logical_row = seat_info['logical_row']

            if physical_y not in displayed_rows:
                displayed_rows.add(physical_y)

                # 创建行号标签（显示逻辑行号）
                row_label = QLabel(f"{logical_row}")
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
                # 使用物理Y坐标作为网格行，第0列放置行号标签
                self.seat_layout.addWidget(row_label, physical_y - 1, 0)

        # 🔧 绘制座位按钮（使用物理位置确定网格位置）
        for seat_info in all_seats:
            seat = seat_info['seat_data']
            physical_x = seat_info['physical_x']
            physical_y = seat_info['physical_y']
            logical_row = seat_info['logical_row']
            logical_col = seat_info['logical_col']
            array_row = seat_info['array_row']
            array_col = seat_info['array_col']

            # 🔧 计算网格位置：物理Y作为网格行，物理X+1作为网格列（第0列是行号标签）
            grid_row = physical_y - 1  # 转换为0基索引
            grid_col = physical_x      # 第0列是行号标签，座位从第1列开始

            status = seat.get('status', 'available')

            # 跳过空座位
            if status == 'empty':
                continue

            # 🔧 创建座位按钮 - 使用物理位置显示，保存逻辑位置信息
            seat_btn = QPushButton()

            # 🆕 检查是否为情侣座位
            seat_type = seat.get('type', 0)
            is_couple_seat = seat_type in [1, 2]

            if is_couple_seat:
                # 情侣座位使用更宽的尺寸
                seat_btn.setFixedSize(40, 36)
            else:
                # 普通座位
                seat_btn.setFixedSize(36, 36)

            # 🔧 显示逻辑座位号（用于用户识别）
            display_seat_num = seat.get('num', str(logical_col))
            seat_btn.setText(display_seat_num)

            # 🔧 获取座位所属区域信息
            area_name = seat.get('area_name', '')
            area_price = seat.get('area_price', 0)

            # 设置样式（包含区域边框和情侣座位样式）
            self._update_seat_button_style(seat_btn, status, area_name, seat_type)

            # 🔧 保存完整的座位信息到按钮
            seat_btn.area_name = area_name
            seat_btn.area_price = area_price
            seat_btn.seat_data = seat
            seat_btn.logical_row = logical_row      # 逻辑行号（用于订单）
            seat_btn.logical_col = logical_col      # 逻辑列号（用于订单）
            seat_btn.physical_x = physical_x        # 物理X坐标（用于显示）
            seat_btn.physical_y = physical_y        # 物理Y坐标（用于显示）
            seat_btn.array_row = array_row          # 数组行索引
            seat_btn.array_col = array_col          # 数组列索引

            # 🔧 设置点击事件（使用数组索引作为键）
            if status == "available":
                # 使用数组索引作为参数，保持与现有代码的兼容性
                seat_btn.clicked.connect(lambda checked, r=array_row, c=array_col: self._seat_button_clicked(r, c))
                seat_btn.setCursor(Qt.PointingHandCursor)

                # 为座位按钮添加鼠标事件处理
                seat_btn.mousePressEvent = lambda event, r=array_row, c=array_col: self._seat_button_mouse_press(event, r, c)
                seat_btn.mouseMoveEvent = lambda event, r=array_row, c=array_col: self._seat_button_mouse_move(event, r, c)
                seat_btn.mouseReleaseEvent = lambda event, r=array_row, c=array_col: self._seat_button_mouse_release(event, r, c)
            elif status == "unavailable":
                # 🆕 不可选择座位 - 完全禁用，无法点击
                seat_btn.setEnabled(False)
                seat_btn.setCursor(Qt.ForbiddenCursor)
            else:
                # 其他状态（已售、锁定等）- 禁用但保持可见
                seat_btn.setEnabled(False)

            # 🔧 添加到布局 - 使用物理位置确定网格位置
            self.seat_layout.addWidget(seat_btn, grid_row, grid_col)

            # 🔧 保存引用（使用数组索引作为键）
            self.seat_buttons[(array_row, array_col)] = seat_btn

            # print(f"[座位面板] 座位 {logical_row}排{logical_col}座 -> 网格位置({grid_row},{grid_col}), 物理位置({physical_x},{physical_y})")
        
        # print(f"[座位面板] 座位图绘制完成，共{len(self.seat_buttons)}个座位")

        # 🆕 更新区域信息显示
        self._update_area_info_display()

        # 初始化按钮文字
        self._update_submit_button_text()
    
    def _update_seat_button_style(self, button: QPushButton, status: str, area_name: str = '', seat_type: int = 0):
        """更新座位按钮样式 - 现代化设计，支持区域边框和情侣座位"""
        # 🆕 获取区域边框颜色
        area_border_color = self._get_area_border_color(area_name)

        # 🆕 检查是否为情侣座位
        is_couple_seat = seat_type in [1, 2]
        couple_left = seat_type == 1
        couple_right = seat_type == 2

        # 🆕 情侣座位的特殊边框样式
        if is_couple_seat:
            if couple_left:
                # 情侣座位左座 - 右边圆角较小，与右座连接
                border_radius = "6px 2px 2px 6px"
                couple_indicator = "💕"  # 爱心符号
            else:  # couple_right
                # 情侣座位右座 - 左边圆角较小，与左座连接
                border_radius = "2px 6px 6px 2px"
                couple_indicator = "💕"  # 爱心符号
        else:
            border_radius = "6px"
            couple_indicator = ""

        if status == "available":
            if is_couple_seat:
                # 情侣座位可选 - 特殊的粉色系，添加爱心图标
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #fce4ec;
                        border: 2px solid #e91e63;
                        color: #ad1457;
                        font: bold 9px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}

                    QPushButton:pressed {{
                        background-color: #f48fb1;
                        border: 2px solid #e91e63;
                    }}
                """)
                # 为可选的情侣座位添加爱心图标
                current_text = button.text()
                if not current_text.startswith('💕'):
                    button.setText(f"💕{current_text}")
            else:
                # 普通座位可选 - 清新的蓝色，外边框显示区域颜色
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #e3f2fd;
                        border: 2px solid {area_border_color};
                        color: #1976d2;
                        font: bold 10px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}

                    QPushButton:pressed {{
                        background-color: #90caf9;
                        border: 2px solid {area_border_color};
                    }}
                """)
        elif status == "sold":
            # 已售座位 - 明显的红色，让用户一眼看出不可选择
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #f44336;
                    border: 2px solid #d32f2f;
                    color: #ffffff;
                    font: bold 10px "Microsoft YaHei";
                    border-radius: {border_radius};
                }}
            """)
        elif status == "unavailable":
            # 🆕 不可选择座位 - 柔和的浅灰色，清晰但不突兀
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #e0e0e0;
                    border: 2px solid #bdbdbd;
                    color: #757575;
                    font: bold 10px "Microsoft YaHei";
                    border-radius: {border_radius};
                }}
            """)
            # 设置简洁的斜杠符号标识不可选择状态
            button.setText("/")
        elif status == "selected":
            if is_couple_seat:
                # 情侣座位选中 - 特殊的深粉色，添加爱心图标
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #e91e63;
                        border: 3px solid #ad1457;
                        color: #fff;
                        font: bold 9px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}
                """)
                # 为情侣座位添加爱心图标
                current_text = button.text()
                if not current_text.startswith('💕'):
                    button.setText(f"💕{current_text}")
            else:
                # 普通座位选中 - 鲜明的绿色，外边框显示区域颜色
                button.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #4caf50;
                        border: 2px solid {area_border_color};
                        color: #fff;
                        font: bold 10px "Microsoft YaHei";
                        border-radius: {border_radius};
                    }}
                """)
        else:
            # 其他状态 - 默认样式，外边框显示区域颜色
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: #fafafa;
                    border: 2px solid {area_border_color};
                    color: #bdbdbd;
                    font: 10px "Microsoft YaHei";
                    border-radius: {border_radius};
                }}
            """)
    
    def toggle_seat(self, r: int, c: int):
        """切换座位选中状态 - 支持逻辑位置和物理位置的区分，支持情侣座自动连选"""
        if (r, c) not in self.seat_buttons:
            return

        seat = self.seat_data[r][c]
        key = (r, c)
        seat_btn = self.seat_buttons[key]

        # 检查座位状态，如果是不可选择状态则直接返回
        seat_status = seat.get('status', 'available')
        if seat_status == 'unavailable':
            return

        # 检查其他不可选择状态
        if seat_status in ['sold', 'locked']:
            return

        # 🔧 获取座位的逻辑位置信息（用于显示和订单）
        logical_row = getattr(seat_btn, 'logical_row', seat.get('row', r + 1))
        logical_col = getattr(seat_btn, 'logical_col', seat.get('col', c + 1))
        area_name = seat.get('area_name', '')
        seat_type = seat.get('type', 0)

        # 🆕 情侣座位自动连选逻辑
        if seat_type in [1, 2]:  # 情侣座位
            self._handle_couple_seat_selection(r, c, seat, key, logical_row, logical_col, area_name, seat_type)
        else:
            # 普通座位处理
            self._handle_normal_seat_selection(r, c, seat, key, logical_row, logical_col, area_name, seat_type)

        # 触发选座回调
        if self.on_seat_selected:
            selected = [self.seat_data[r][c] for (r, c) in self.selected_seats]
            self.on_seat_selected(selected)

        # 发送信号
        selected_seats = [self.seat_data[r][c] for (r, c) in self.selected_seats]
        self.seat_selected.emit(selected_seats)

        # 座位选择状态已更新

        # 更新提交按钮文字
        self._update_submit_button_text()

    def _handle_couple_seat_selection(self, r: int, c: int, seat: dict, key: tuple, logical_row: int, logical_col: int, area_name: str, seat_type: int):
        """处理情侣座位选择逻辑"""
        from PyQt5.QtWidgets import QMessageBox

        # 查找配对的情侣座位
        partner_seat_info = self._find_couple_partner(r, c, seat, seat_type)

        if not partner_seat_info:
            QMessageBox.warning(self, "情侣座选择", f"无法找到 {logical_row}排{logical_col}座 的配对座位")
            return

        partner_r, partner_c, partner_seat, partner_key = partner_seat_info
        partner_logical_row = partner_seat.get('row', partner_r + 1)
        partner_logical_col = partner_seat.get('col', partner_c + 1)

        # 检查两个座位的状态
        if key in self.selected_seats and partner_key in self.selected_seats:
            # 两个座位都已选中，取消选择
            self._deselect_couple_seats(key, partner_key, seat, partner_seat, logical_row, logical_col, partner_logical_row, partner_logical_col, area_name)
        elif key not in self.selected_seats and partner_key not in self.selected_seats:
            # 两个座位都未选中，检查是否可选
            if self._can_select_couple_seats(seat, partner_seat, logical_row, logical_col, partner_logical_row, partner_logical_col):
                self._select_couple_seats(key, partner_key, seat, partner_seat, logical_row, logical_col, partner_logical_row, partner_logical_col, area_name, seat_type)
        else:
            # 只有一个座位被选中，这种情况不应该发生，但为了安全起见进行处理
            QMessageBox.warning(self, "情侣座选择", f"情侣座 {logical_row}排{logical_col}座 状态异常，请重新选择")
            # 重置两个座位的状态
            self._reset_couple_seats_status(key, partner_key, seat, partner_seat)

    def _handle_normal_seat_selection(self, r: int, c: int, seat: dict, key: tuple, logical_row: int, logical_col: int, area_name: str, seat_type: int):
        """处理普通座位选择逻辑"""
        seat_btn = self.seat_buttons[key]

        if key in self.selected_seats:
            # 取消选中
            self.selected_seats.remove(key)
            seat['status'] = 'available'
            # 取消选择座位
        else:
            # 选中
            self.selected_seats.add(key)
            seat['status'] = "selected"
            # 选择座位

        # 🔧 更新按钮样式时传递区域信息和座位类型
        self._update_seat_button_style(seat_btn, seat['status'], area_name, seat_type)

    def _find_couple_partner(self, r: int, c: int, seat: dict, seat_type: int):
        """查找情侣座位的配对座位"""
        # 获取当前座位的物理位置
        current_x = seat.get('x', c + 1)
        current_y = seat.get('y', r + 1)

        # 根据座位类型确定配对座位的位置
        if seat_type == 1:  # 左座，查找右座 (type=2)
            target_x = current_x + 1
            target_type = 2
        elif seat_type == 2:  # 右座，查找左座 (type=1)
            target_x = current_x - 1
            target_type = 1
        else:
            return None

        # 在座位矩阵中查找配对座位
        for row_idx, row in enumerate(self.seat_data):
            for col_idx, partner_seat in enumerate(row):
                if partner_seat and partner_seat.get('x') == target_x and partner_seat.get('y') == current_y:
                    # 验证座位类型是否匹配
                    if partner_seat.get('type') == target_type:
                        partner_key = (row_idx, col_idx)
                        return row_idx, col_idx, partner_seat, partner_key

        return None

    def _can_select_couple_seats(self, seat1: dict, seat2: dict, row1: int, col1: int, row2: int, col2: int) -> bool:
        """检查情侣座位是否可以选择"""
        # 检查两个座位的状态
        status1 = seat1.get('status', 'available')
        status2 = seat2.get('status', 'available')

        if status1 != 'available':
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "情侣座选择", f"{row1}排{col1}座 不可选择（状态：{status1}）")
            return False

        if status2 != 'available':
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "情侣座选择", f"{row2}排{col2}座 不可选择（状态：{status2}）")
            return False

        return True

    def _select_couple_seats(self, key1: tuple, key2: tuple, seat1: dict, seat2: dict,
                           row1: int, col1: int, row2: int, col2: int, area_name: str, seat_type: int):
        """选择情侣座位"""
        # 选中两个座位
        self.selected_seats.add(key1)
        self.selected_seats.add(key2)
        seat1['status'] = 'selected'
        seat2['status'] = 'selected'

        # 更新按钮样式
        btn1 = self.seat_buttons[key1]
        btn2 = self.seat_buttons[key2]
        self._update_seat_button_style(btn1, 'selected', area_name, seat1.get('type', 0))
        self._update_seat_button_style(btn2, 'selected', area_name, seat2.get('type', 0))

        # 选择情侣座位

    def _deselect_couple_seats(self, key1: tuple, key2: tuple, seat1: dict, seat2: dict,
                             row1: int, col1: int, row2: int, col2: int, area_name: str):
        """取消选择情侣座位"""
        # 取消选中两个座位
        self.selected_seats.discard(key1)
        self.selected_seats.discard(key2)
        seat1['status'] = 'available'
        seat2['status'] = 'available'

        # 更新按钮样式
        btn1 = self.seat_buttons[key1]
        btn2 = self.seat_buttons[key2]
        self._update_seat_button_style(btn1, 'available', area_name, seat1.get('type', 0))
        self._update_seat_button_style(btn2, 'available', area_name, seat2.get('type', 0))

        # 取消选择情侣座位

    def _reset_couple_seats_status(self, key1: tuple, key2: tuple, seat1: dict, seat2: dict):
        """重置情侣座位状态"""
        # 强制重置两个座位的状态
        self.selected_seats.discard(key1)
        self.selected_seats.discard(key2)
        seat1['status'] = 'available'
        seat2['status'] = 'available'

        # 更新按钮样式
        if key1 in self.seat_buttons:
            btn1 = self.seat_buttons[key1]
            area_name = seat1.get('area_name', '')
            self._update_seat_button_style(btn1, 'available', area_name, seat1.get('type', 0))

        if key2 in self.seat_buttons:
            btn2 = self.seat_buttons[key2]
            area_name = seat2.get('area_name', '')
            self._update_seat_button_style(btn2, 'available', area_name, seat2.get('type', 0))

        # 重置情侣座位状态

    def update_seat_data(self, seat_data: List[List]):
        """更新座位数据并重绘"""
        self.seat_data = seat_data or []
        self.selected_seats.clear()
        self._draw_seats()
        # 座位数据已更新

    def update_seat_data_with_areas(self, seat_data: List[List], area_data: List[Dict] = None):
        """更新座位数据并包含区域信息"""
        self.seat_data = seat_data or []
        self.area_data = area_data or []
        self.selected_seats.clear()

        # 🆕 如果提供了区域数据，确保座位数据包含区域信息
        if self.area_data:
            self._enrich_seat_data_with_area_info()

        self._draw_seats()
        # 座位数据（含区域信息）已更新

    def _enrich_seat_data_with_area_info(self):
        """为座位数据补充区域信息"""
        # 创建区域映射
        area_map = {}
        for area in self.area_data:
            area_name = area.get('area_name', '')
            area_price = area.get('area_price', 0)
            area_map[area_name] = area_price

        # 为座位数据补充区域信息
        for row in self.seat_data:
            for seat in row:
                if seat and not seat.get('area_name'):
                    # 如果座位没有区域信息，尝试从区域数据中匹配
                    # 这里可以根据实际需求实现匹配逻辑
                    seat['area_name'] = '默认区'  # 默认区域
                    seat['area_price'] = area_map.get('默认区', 0)
    
    def update_seats(self, seat_data: List[List]):
        """更新座位数据（兼容原接口）"""
        self.update_seat_data(seat_data)
    
    def get_selected_seats(self) -> List[str]:
        """获取选中座位编号列表 - 使用逻辑位置"""
        selected_seats = []
        for (r, c) in self.selected_seats:
            seat = self.seat_data[r][c]
            seat_btn = self.seat_buttons.get((r, c))

            # 🔧 使用逻辑位置构建座位编号
            if seat_btn:
                logical_row = getattr(seat_btn, 'logical_row', seat.get('row', r + 1))
                logical_col = getattr(seat_btn, 'logical_col', seat.get('col', c + 1))
                seat_num = f"{logical_row}排{logical_col}座"
            else:
                seat_num = seat.get('num', f"{r+1}-{c+1}")

            selected_seats.append(seat_num)

        return selected_seats

    def get_selected_seat_objects(self) -> List[Dict]:
        """获取选中座位对象列表 - 包含逻辑位置信息"""
        selected_seats = []
        for (r, c) in self.selected_seats:
            seat = self.seat_data[r][c]
            seat_btn = self.seat_buttons.get((r, c))

            # 🔧 构建包含逻辑位置信息的座位数据
            seat_info = seat.copy()
            if seat_btn:
                # 使用按钮中保存的逻辑位置信息
                seat_info['logical_row'] = getattr(seat_btn, 'logical_row', seat.get('row', r + 1))
                seat_info['logical_col'] = getattr(seat_btn, 'logical_col', seat.get('col', c + 1))
                seat_info['physical_x'] = getattr(seat_btn, 'physical_x', seat.get('x', c + 1))
                seat_info['physical_y'] = getattr(seat_btn, 'physical_y', seat.get('y', r + 1))

                # 🔧 确保订单提交时使用逻辑位置
                seat_info['row'] = seat_info['logical_row']
                seat_info['col'] = seat_info['logical_col']

            selected_seats.append(seat_info)

        return selected_seats

    def get_selected_seats_for_order(self) -> List[Dict]:
        """获取用于订单提交的座位信息 - 明确使用逻辑位置"""
        order_seats = []
        for (r, c) in self.selected_seats:
            seat = self.seat_data[r][c]
            seat_btn = self.seat_buttons.get((r, c))

            if seat_btn:
                # 🔧 构建订单座位信息，明确使用逻辑位置
                logical_row = getattr(seat_btn, 'logical_row', seat.get('row', r + 1))
                logical_col = getattr(seat_btn, 'logical_col', seat.get('col', c + 1))

                order_seat = {
                    'seat_no': seat.get('seat_no', ''),
                    'row': logical_row,      # 逻辑行号（用于订单）
                    'col': logical_col,      # 逻辑列号（用于订单）
                    'area_name': seat.get('area_name', ''),
                    'area_price': seat.get('area_price', 0),
                    'price': seat.get('price', seat.get('area_price', 0)),
                    'type': seat.get('type', 0),
                    'num': seat.get('num', str(logical_col))
                }
                order_seats.append(order_seat)

                print(f"[订单座位] {logical_row}排{logical_col}座 - {order_seat['area_name']} {order_seat['price']}元")

        return order_seats
    
    def _update_submit_button_text(self):
        """更新提交按钮文字 - 使用逻辑位置显示座位信息"""
        selected_count = len(self.selected_seats)
        if selected_count == 0:
            self.submit_btn.setText("提交订单")
        else:
            # 🔧 获取选中座位的逻辑位置信息
            selected_seats_info = []
            for (r, c) in self.selected_seats:
                seat = self.seat_data[r][c]
                seat_btn = self.seat_buttons.get((r, c))

                # 使用逻辑位置构建座位信息
                if seat_btn:
                    logical_row = getattr(seat_btn, 'logical_row', seat.get('row', r + 1))
                    logical_col = getattr(seat_btn, 'logical_col', seat.get('col', c + 1))
                    seat_info = f"{logical_row}排{logical_col}"
                else:
                    # 备用方案
                    row_num = seat.get('row', r + 1)
                    col_num = seat.get('col', c + 1)
                    seat_info = f"{row_num}排{col_num}"

                selected_seats_info.append(seat_info)

            # 按钮文字格式：提交订单 5排13 5排12
            seats_text = " ".join(selected_seats_info)
            self.submit_btn.setText(f"提交订单 {seats_text}")

        # 按钮文字已更新
    
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
        """提交订单按钮点击事件（修复影院数据传递问题）"""
        if not self.selected_seats:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "提交订单", "请先选择座位")
            return

        # 提交订单处理

        # 🔧 修复：构建完整的订单数据，包含session_info
        selected_seat_objects = self.get_selected_seat_objects()

        # 构建完整的订单数据
        order_data = {
            'seats': selected_seat_objects,
            'session_info': getattr(self, 'session_info', {}),  # 🆕 添加完整的session_info
            'trigger_type': 'seat_map_panel_pyqt5'
        }

        # 🔧 验证关键数据
        session_info = order_data.get('session_info', {})
        cinema_data = session_info.get('cinema_data')
        account = session_info.get('account')

        # 订单数据验证
        print(f"  - 座位数量: {len(selected_seat_objects)}")
        print(f"  - 影院数据: {'存在' if cinema_data else '缺失'}")
        print(f"  - 账号数据: {'存在' if account else '缺失'}")
        print(f"  - 场次数据: {'存在' if session_info.get('session_data') else '缺失'}")

        if not cinema_data:
            # 警告: 影院数据缺失
            pass

        if not account:
            # 警告: 账号数据缺失
            pass

        # 调用回调函数，传递完整的订单数据
        if self.on_submit_order:
            self.on_submit_order(order_data)  # 🔧 传递完整的订单数据而不只是座位数据

        # 订单提交回调已调用
    
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
                seat_type = seat.get('type', 0)
                area_name = seat.get('area_name', '')
                self._update_seat_button_style(seat_btn, seat['status'], area_name, seat_type)
        
        self.selected_seats.clear()
        # 座位状态已重置

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
        unavailable = 0
        locked = 0
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
                    elif status == 'unavailable':
                        unavailable += 1
                    elif status == 'locked':
                        locked += 1

        return {
            'total': total,
            'available': available,
            'sold': sold,
            'unavailable': unavailable,
            'locked': locked,
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
            # 开始拖拽滚动

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

            # 结束拖拽滚动

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
                # 在座位按钮上开始拖拽滚动

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
                # 在座位按钮上结束拖拽滚动

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