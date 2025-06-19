#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经典风格UI组件库
提供统一的经典风格UI组件
"""

from PyQt5.QtWidgets import (
    QGroupBox, QPushButton, QLineEdit, QComboBox, QTableWidget, 
    QTabWidget, QTextEdit, QLabel, QListWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from typing import Any


class ClassicGroupBox(QGroupBox):
    """经典风格分组框"""
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置经典分组框样式"""
        self.setStyleSheet("""
            QGroupBox {
                font: bold 12px "Microsoft YaHei";
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #333333;
                background-color: #f9f9f9;
            }
        """)


class ClassicButton(QPushButton):
    """经典风格按钮"""
    
    def __init__(self, text="", button_type="default", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()
    
    def _setup_style(self):
        """设置按钮样式"""
        if self.button_type == "primary":
            style = """
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: 1px solid #0078d4;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                    border-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                    border-color: #005a9e;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    border-color: #cccccc;
                    color: #888888;
                }
            """
        elif self.button_type == "success":
            style = """
                QPushButton {
                    background-color: #107c10;
                    color: white;
                    border: 1px solid #107c10;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #0e6e0e;
                    border-color: #0e6e0e;
                }
                QPushButton:pressed {
                    background-color: #0c5c0c;
                    border-color: #0c5c0c;
                }
            """
        elif self.button_type == "warning":
            style = """
                QPushButton {
                    background-color: #ff8c00;
                    color: white;
                    border: 1px solid #ff8c00;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #e67c00;
                    border-color: #e67c00;
                }
                QPushButton:pressed {
                    background-color: #cc6c00;
                    border-color: #cc6c00;
                }
            """
        elif self.button_type == "danger":
            style = """
                QPushButton {
                    background-color: #d13438;
                    color: white;
                    border: 1px solid #d13438;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #b92b2f;
                    border-color: #b92b2f;
                }
                QPushButton:pressed {
                    background-color: #a12226;
                    border-color: #a12226;
                }
            """
        else:  # default
            style = """
                QPushButton {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 8px 16px;
                    border-radius: 3px;
                    font: 11px "Microsoft YaHei";
                    min-width: 60px;
                    min-height: 24px;
                }
                QPushButton:hover {
                    background-color: #f5f5f5;
                    border-color: #999999;
                }
                QPushButton:pressed {
                    background-color: #e6e6e6;
                    border-color: #888888;
                }
            """
        
        self.setStyleSheet(style)


class ClassicLineEdit(QLineEdit):
    """经典风格输入框"""
    
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        if placeholder:
            self.setPlaceholderText(placeholder)
        self._setup_style()
    
    def _setup_style(self):
        """设置输入框样式"""
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #cccccc;
                border-radius: 3px;
                padding: 6px 8px;
                font: 11px "Microsoft YaHei";
                background-color: #ffffff;
                color: #333333;
                selection-background-color: #0078d4;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
            QLineEdit:hover {
                border-color: #999999;
            }
        """)


class ClassicComboBox(QComboBox):
    """经典风格下拉框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置下拉框样式 - 最终修复版本"""
        self.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 6px 12px;
                font: 13px "Microsoft YaHei";
                color: #333333;
                min-width: 320px;
                min-height: 26px;
                background-color: white !important;
                background: white !important;
            }
            QComboBox:focus {
                border-color: #4a90e2;
                outline: none;
                background-color: white !important;
            }
            QComboBox:hover {
                border-color: #a0a0a0;
                background-color: white !important;
            }
            QComboBox:disabled {
                background-color: #f5f5f5;
                color: #999999;
                border-color: #e0e0e0;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background: transparent;
                subcontrol-origin: padding;
                subcontrol-position: top right;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #666666;
                margin-top: 2px;
                margin-right: 5px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #333333;
            }
            QComboBox::down-arrow:pressed {
                border-top-color: #000000;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                background-color: #ffffff;
                selection-background-color: #4a90e2;
                selection-color: white;
                font: 13px "Microsoft YaHei";
                padding: 6px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 10px 12px;
                border: none;
                border-radius: 4px;
                margin: 2px;
                background: transparent;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #f0f8ff;
                color: #333333;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #4a90e2;
                color: white;
            }
        """)


class ClassicTableWidget(QTableWidget):
    """经典风格表格"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
        self._setup_properties()
    
    def _setup_style(self):
        """设置表格样式"""
        self.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                gridline-color: #e0e0e0;
                font: 11px "Microsoft YaHei";
            }
            QTableWidget::item {
                padding: 6px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: #e6f3ff;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 6px;
                font: bold 11px "Microsoft YaHei";
                color: #333333;
            }
        """)
    
    def _setup_properties(self):
        """设置表格属性"""
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
    
    def add_row_with_data(self, data_list: list, user_data: Any = None):
        """添加一行数据"""
        try:
            row_count = self.rowCount()
            self.setRowCount(row_count + 1)
            
            for col, data in enumerate(data_list):
                if col < self.columnCount():
                    item = QTableWidgetItem(str(data))
                    if user_data is not None and col == 0:
                        item.setData(Qt.UserRole, user_data)
                    self.setItem(row_count, col, item)
                    
        except Exception as e:
            pass

    def add_colored_item(self, row: int, col: int, text: str, color: str):
        """添加有颜色的表格项"""
        try:
            item = QTableWidgetItem(text)
            item.setForeground(QColor(color))
            self.setItem(row, col, item)
            
        except Exception as e:
            pass

    def clear_all_data(self):
        """清空所有数据"""
        try:
            self.setRowCount(0)
        except Exception as e:
            pass


class ClassicTabWidget(QTabWidget):
    """经典风格Tab页"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置Tab样式"""
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                margin-top: -1px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                color: #333333;
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid #cccccc;
                border-bottom: none;
                font: 11px "Microsoft YaHei";
                min-width: 60px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover:!selected {
                background: #e6e6e6;
            }
        """)


class ClassicTextEdit(QTextEdit):
    """经典风格文本编辑器"""
    
    def __init__(self, read_only=False, parent=None):
        super().__init__(parent)
        self.setReadOnly(read_only)
        self._setup_style()
    
    def _setup_style(self):
        """设置文本编辑器样式"""
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font: 11px "Microsoft YaHei";
                padding: 8px;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)


class ClassicLabel(QLabel):
    """经典风格标签"""
    
    def __init__(self, text="", label_type="default", parent=None):
        super().__init__(text, parent)
        self.label_type = label_type
        self._setup_style()
    
    def _setup_style(self):
        """设置标签样式"""
        if self.label_type == "info":
            style = """
                QLabel {
                    color: #0078d4;
                    font: bold 12px "Microsoft YaHei";
                    padding: 8px;
                    background-color: #e6f3ff;
                    border: 1px solid #b3d9ff;
                    border-radius: 3px;
                }
            """
        elif self.label_type == "warning":
            style = """
                QLabel {
                    color: #ff8c00;
                    font: bold 12px "Microsoft YaHei";
                    padding: 8px;
                    background-color: #fff4e6;
                    border: 1px solid #ffd9b3;
                    border-radius: 3px;
                }
            """
        elif self.label_type == "error":
            style = """
                QLabel {
                    color: #f44336;
                    font: bold 12px "Microsoft YaHei";
                    padding: 8px;
                    background-color: #ffebee;
                    border: 1px solid #ffcdd2;
                    border-radius: 3px;
                }
            """
        else:  # default
            style = """
                QLabel {
                    color: #333333;
                    font: 12px "Microsoft YaHei";
                }
            """
        
        self.setStyleSheet(style)


class ClassicListWidget(QListWidget):
    """经典风格列表组件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_style()
    
    def _setup_style(self):
        """设置列表样式"""
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #cccccc;
                background-color: #ffffff;
                font: 11px "Microsoft YaHei";
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e6f3ff;
            }
        """)


def apply_classic_theme_to_widget(widget):
    """将经典主题应用到指定组件"""
    try:
        widget.setStyleSheet("""
            QWidget {
                font-family: 'Microsoft YaHei';
                font-size: 12px;
                background-color: #f0f0f0;
            }
            
            QMainWindow {
                background-color: #f0f0f0;
            }
            
            QGroupBox {
                font: bold 12px "Microsoft YaHei";
                color: #333333;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                background-color: #f9f9f9;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
        """)
        
    except Exception as e:
        pass


# 主题应用函数的导出
__all__ = [
    'ClassicGroupBox', 'ClassicButton', 'ClassicLineEdit', 'ClassicComboBox',
    'ClassicTableWidget', 'ClassicTabWidget', 'ClassicTextEdit', 'ClassicLabel',
    'ClassicListWidget', 'apply_classic_theme_to_widget'
] 