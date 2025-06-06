#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影院面板组件 - 重构版本
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.signals import event_bus, event_handler


class CinemaPanel(QWidget):
    """影院面板"""
    
    # 信号定义
    cinema_selected = pyqtSignal(dict)  # 影院选择
    movie_selected = pyqtSignal(dict)  # 电影选择
    session_selected = pyqtSignal(dict)  # 场次选择
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self.cinema_list = []
        self.movie_list = []
        self.session_list = []
        self.current_cinema = None
        self.current_movie = None
        self.current_session = None
        
        # 初始化UI
        self._init_ui()
        
        # 连接事件总线
        self._connect_events()
        
        print("[影院面板] 初始化完成")
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 影院选择区
        cinema_group = QGroupBox("影院选择")
        cinema_layout = QVBoxLayout(cinema_group)
        
        cinema_select_layout = QHBoxLayout()
        cinema_select_layout.addWidget(QLabel("选择影院:"))
        
        self.cinema_combo = QComboBox()
        self.cinema_combo.currentTextChanged.connect(self._on_cinema_changed)
        self.cinema_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
        """)
        cinema_select_layout.addWidget(self.cinema_combo)
        
        cinema_layout.addLayout(cinema_select_layout)
        layout.addWidget(cinema_group)
        
        # 电影选择区
        movie_group = QGroupBox("电影选择")
        movie_layout = QVBoxLayout(movie_group)
        
        movie_select_layout = QHBoxLayout()
        movie_select_layout.addWidget(QLabel("选择电影:"))
        
        self.movie_combo = QComboBox()
        self.movie_combo.currentTextChanged.connect(self._on_movie_changed)
        self.movie_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
        """)
        movie_select_layout.addWidget(self.movie_combo)
        
        movie_layout.addLayout(movie_select_layout)
        layout.addWidget(movie_group)
        
        # 场次选择区
        session_group = QGroupBox("场次选择")
        session_layout = QVBoxLayout(session_group)
        
        # 场次表格
        self.session_table = QTableWidget()
        self.session_table.setColumnCount(4)
        self.session_table.setHorizontalHeaderLabels(["时间", "影厅", "价格", "状态"])
        
        # 设置表格样式
        self.session_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
                gridline-color: #eee;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
        # 设置表格属性
        self.session_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.session_table.setSelectionMode(QTableWidget.SingleSelection)
        self.session_table.horizontalHeader().setStretchLastSection(True)
        self.session_table.verticalHeader().setVisible(False)
        self.session_table.setAlternatingRowColors(True)
        
        # 连接选择信号
        self.session_table.itemSelectionChanged.connect(self._on_session_selection_changed)
        
        session_layout.addWidget(self.session_table)
        
        # 场次操作按钮
        session_button_layout = QHBoxLayout()
        self.select_session_button = QPushButton("选择场次")
        self.select_session_button.clicked.connect(self._on_select_session_clicked)
        self.select_session_button.setEnabled(False)
        
        session_button_layout.addStretch()
        session_button_layout.addWidget(self.select_session_button)
        session_layout.addLayout(session_button_layout)
        
        layout.addWidget(session_group)
        
        # 当前选择显示
        current_group = QGroupBox("当前选择")
        current_layout = QVBoxLayout(current_group)
        
        self.current_selection_label = QLabel("请选择影院、电影和场次")
        self.current_selection_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 10px;
                background-color: #f9f9f9;
                border-radius: 3px;
                border: 1px solid #eee;
            }
        """)
        current_layout.addWidget(self.current_selection_label)
        
        layout.addWidget(current_group)
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.cinema_list_updated.connect(self._on_cinema_list_updated)
        event_bus.movie_list_updated.connect(self._on_movie_list_updated)
        event_bus.session_list_updated.connect(self._on_session_list_updated)
        event_bus.cinema_selected.connect(self._on_cinema_selected)
        event_bus.movie_selected.connect(self._on_movie_selected)
        event_bus.session_selected.connect(self._on_session_selected)
    
    @event_handler("cinema_list_updated")
    def _on_cinema_list_updated(self, cinema_list: List[dict]):
        """影院列表更新处理"""
        self.cinema_list = cinema_list
        self._update_cinema_combo()
        
        print(f"[影院面板] 影院列表已更新: {len(cinema_list)} 个影院")
    
    @event_handler("movie_list_updated")
    def _on_movie_list_updated(self, movie_list: List[dict]):
        """电影列表更新处理"""
        self.movie_list = movie_list
        self._update_movie_combo()
        
        print(f"[影院面板] 电影列表已更新: {len(movie_list)} 部电影")
    
    @event_handler("session_list_updated")
    def _on_session_list_updated(self, session_list: List[dict]):
        """场次列表更新处理"""
        self.session_list = session_list
        self._update_session_table()
        
        print(f"[影院面板] 场次列表已更新: {len(session_list)} 个场次")
    
    @event_handler("cinema_selected")
    def _on_cinema_selected(self, cinema_data: dict):
        """影院选择处理"""
        self.current_cinema = cinema_data
        self._update_current_selection_display()
    
    @event_handler("movie_selected")
    def _on_movie_selected(self, movie_data: dict):
        """电影选择处理"""
        self.current_movie = movie_data
        self._update_current_selection_display()
    
    @event_handler("session_selected")
    def _on_session_selected(self, session_data: dict):
        """场次选择处理"""
        self.current_session = session_data
        self._update_current_selection_display()
    
    def _update_cinema_combo(self):
        """更新影院下拉框"""
        try:
            self.cinema_combo.clear()
            
            if not self.cinema_list:
                self.cinema_combo.addItem("暂无影院数据")
                self.cinema_combo.setEnabled(False)
                return
            
            self.cinema_combo.setEnabled(True)
            self.cinema_combo.addItem("请选择影院")
            
            for cinema in self.cinema_list:
                cinema_name = cinema.get('cinemaShortName', '未知影院')
                self.cinema_combo.addItem(cinema_name)
            
        except Exception as e:
            print(f"[影院面板] 更新影院下拉框错误: {e}")
    
    def _update_movie_combo(self):
        """更新电影下拉框"""
        try:
            self.movie_combo.clear()
            
            if not self.movie_list:
                self.movie_combo.addItem("暂无电影数据")
                self.movie_combo.setEnabled(False)
                return
            
            self.movie_combo.setEnabled(True)
            self.movie_combo.addItem("请选择电影")
            
            for movie in self.movie_list:
                movie_name = movie.get('name', '未知电影')
                self.movie_combo.addItem(movie_name)
            
        except Exception as e:
            print(f"[影院面板] 更新电影下拉框错误: {e}")
    
    def _update_session_table(self):
        """更新场次表格"""
        try:
            self.session_table.setRowCount(0)
            
            if not self.session_list:
                return
            
            self.session_table.setRowCount(len(self.session_list))
            
            for row, session in enumerate(self.session_list):
                # 时间
                time_item = QTableWidgetItem(session.get('time', 'N/A'))
                time_item.setData(Qt.UserRole, session)  # 存储场次数据
                self.session_table.setItem(row, 0, time_item)
                
                # 影厅
                hall_item = QTableWidgetItem(session.get('hall', 'N/A'))
                self.session_table.setItem(row, 1, hall_item)
                
                # 价格
                price_item = QTableWidgetItem(f"¥{session.get('price', '0.00')}")
                self.session_table.setItem(row, 2, price_item)
                
                # 状态
                status_item = QTableWidgetItem("可选")
                status_item.setForeground(Qt.darkGreen)
                self.session_table.setItem(row, 3, status_item)
            
            # 调整列宽
            self.session_table.resizeColumnsToContents()
            
        except Exception as e:
            print(f"[影院面板] 更新场次表格错误: {e}")
    
    def _update_current_selection_display(self):
        """更新当前选择显示"""
        try:
            parts = []
            
            if self.current_cinema:
                cinema_name = self.current_cinema.get('cinemaShortName', '未知影院')
                parts.append(f"影院: {cinema_name}")
            
            if self.current_movie:
                movie_name = self.current_movie.get('name', '未知电影')
                parts.append(f"电影: {movie_name}")
            
            if self.current_session:
                session_time = self.current_session.get('time', 'N/A')
                session_hall = self.current_session.get('hall', 'N/A')
                parts.append(f"场次: {session_time} ({session_hall})")
            
            if parts:
                self.current_selection_label.setText("\n".join(parts))
                self.current_selection_label.setStyleSheet("""
                    QLabel {
                        color: #2196F3;
                        font-size: 12px;
                        font-weight: bold;
                        padding: 10px;
                        background-color: #E3F2FD;
                        border-radius: 3px;
                        border: 1px solid #BBDEFB;
                    }
                """)
            else:
                self.current_selection_label.setText("请选择影院、电影和场次")
                self.current_selection_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-size: 12px;
                        padding: 10px;
                        background-color: #f9f9f9;
                        border-radius: 3px;
                        border: 1px solid #eee;
                    }
                """)
            
        except Exception as e:
            print(f"[影院面板] 更新当前选择显示错误: {e}")
    
    def _on_cinema_changed(self, cinema_name: str):
        """影院下拉框变化处理"""
        try:
            if cinema_name == "请选择影院" or cinema_name == "暂无影院数据":
                return
            
            # 查找对应的影院数据
            for cinema in self.cinema_list:
                if cinema.get('cinemaShortName') == cinema_name:
                    # 发送影院选择信号
                    self.cinema_selected.emit(cinema)
                    break
            
        except Exception as e:
            print(f"[影院面板] 影院变化处理错误: {e}")
    
    def _on_movie_changed(self, movie_name: str):
        """电影下拉框变化处理"""
        try:
            if movie_name == "请选择电影" or movie_name == "暂无电影数据":
                return
            
            # 查找对应的电影数据
            for movie in self.movie_list:
                if movie.get('name') == movie_name:
                    # 发送电影选择信号
                    self.movie_selected.emit(movie)
                    break
            
        except Exception as e:
            print(f"[影院面板] 电影变化处理错误: {e}")
    
    def _on_session_selection_changed(self):
        """场次选择变化处理"""
        try:
            current_row = self.session_table.currentRow()
            if current_row >= 0:
                self.select_session_button.setEnabled(True)
            else:
                self.select_session_button.setEnabled(False)
            
        except Exception as e:
            print(f"[影院面板] 场次选择变化处理错误: {e}")
    
    def _on_select_session_clicked(self):
        """选择场次按钮点击处理"""
        try:
            current_row = self.session_table.currentRow()
            if current_row < 0:
                return
            
            # 获取场次数据
            time_item = self.session_table.item(current_row, 0)
            if time_item:
                session_data = time_item.data(Qt.UserRole)
                if session_data:
                    # 发送场次选择信号
                    self.session_selected.emit(session_data)
            
        except Exception as e:
            print(f"[影院面板] 选择场次处理错误: {e}")
    
    def get_current_cinema(self) -> Optional[dict]:
        """获取当前影院"""
        return self.current_cinema
    
    def get_current_movie(self) -> Optional[dict]:
        """获取当前电影"""
        return self.current_movie
    
    def get_current_session(self) -> Optional[dict]:
        """获取当前场次"""
        return self.current_session
    
    def set_enabled(self, enabled: bool):
        """设置面板启用状态"""
        self.cinema_combo.setEnabled(enabled and len(self.cinema_list) > 0)
        self.movie_combo.setEnabled(enabled and len(self.movie_list) > 0)
        self.session_table.setEnabled(enabled)
        self.select_session_button.setEnabled(enabled and self.session_table.currentRow() >= 0)
