#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI组件工厂类 - 统一UI组件创建
自动生成，用于减少UI组件创建的重复代码
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class UIComponentFactory:
    """UI组件工厂类"""
    
    # 统一样式定义
    BUTTON_STYLE = """
        QPushButton {
            background-color: #4CAF50;
            border: none;
            color: white;
            padding: 8px 16px;
            text-align: center;
            font-size: 14px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
    """
    
    LABEL_STYLE = """
        QLabel {
            color: #333;
            font-size: 14px;
            padding: 4px;
        }
    """
    
    @staticmethod
    def create_styled_button(text: str, callback=None, style=None):
        """创建带样式的按钮"""
        button = QPushButton(text)
        button.setStyleSheet(style or UIComponentFactory.BUTTON_STYLE)
        if callback:
            button.clicked.connect(callback)
        return button
    
    @staticmethod
    def create_styled_label(text: str, alignment=Qt.AlignLeft, style=None):
        """创建带样式的标签"""
        label = QLabel(text)
        label.setAlignment(alignment)
        label.setStyleSheet(style or UIComponentFactory.LABEL_STYLE)
        return label
    
    @staticmethod
    def create_vertical_layout(widget=None, spacing=5, margins=(5, 5, 5, 5)):
        """创建垂直布局"""
        layout = QVBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        if widget:
            widget.setLayout(layout)
        return layout
    
    @staticmethod
    def create_horizontal_layout(widget=None, spacing=5, margins=(5, 5, 5, 5)):
        """创建水平布局"""
        layout = QHBoxLayout()
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)
        if widget:
            widget.setLayout(layout)
        return layout
    
    @staticmethod
    def add_widgets_to_layout(layout, widgets, stretch_factors=None):
        """批量添加组件到布局"""
        for i, widget in enumerate(widgets):
            if stretch_factors and i < len(stretch_factors):
                layout.addWidget(widget, stretch_factors[i])
            else:
                layout.addWidget(widget)
    
    @staticmethod
    def create_group_box(title: str, layout_type='vertical'):
        """创建分组框"""
        group_box = QGroupBox(title)
        if layout_type == 'vertical':
            layout = UIComponentFactory.create_vertical_layout()
        else:
            layout = UIComponentFactory.create_horizontal_layout()
        group_box.setLayout(layout)
        return group_box, layout
