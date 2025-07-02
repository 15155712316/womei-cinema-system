#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市选择面板 - 七级联动第二级
基于选定的影院系统动态加载和选择城市
"""

from typing import Callable, Optional, Dict, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QProgressBar
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont

from config.cinema_systems_config import CinemaSystemType, cinema_system_manager
from services.unified_cinema_api import CinemaAPIFactory

class CityLoadThread(QThread):
    """城市数据加载线程"""

    # 定义信号
    cities_loaded = pyqtSignal(list)  # 城市加载完成信号
    load_error = pyqtSignal(str)      # 加载错误信号

    def __init__(self, system_type: CinemaSystemType, token: Optional[str] = None):
        super().__init__()
        self.system_type = system_type
        self.token = token

    def run(self):
        """执行城市数据加载"""
        try:
            # 调试打印已移除

            # 创建API实例
            api = CinemaAPIFactory.create_api(self.system_type, self.token)

            # 获取城市列表
            cities = api.get_cities()

            print(f"[城市加载线程] 成功加载 {len(cities)} 个城市")
            self.cities_loaded.emit(cities)

        except Exception as e:
            error_msg = f"加载城市列表失败: {str(e)}"
            print(f"[城市加载线程] {error_msg}")
            self.load_error.emit(error_msg)

class CitySelectPanel(QWidget):
    """城市选择面板"""

    # 定义信号
    city_changed = pyqtSignal(dict)  # 城市切换信号，传递城市信息
    loading_started = pyqtSignal()   # 开始加载信号
    loading_finished = pyqtSignal() # 加载完成信号

    def __init__(self, parent=None):
        super().__init__(parent)

        # 状态变量
        self.current_system: Optional[CinemaSystemType] = None
        self.current_city: Optional[Dict] = None
        self.cities_data: List[Dict] = []
        self.load_thread: Optional[CityLoadThread] = None

        # 回调函数
        self.on_city_changed: Optional[Callable] = None

        self.init_ui()

        # 延迟初始化，等待系统选择
        QTimer.singleShot(100, self.check_initial_system)

    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # 创建分组框
        group_box = QGroupBox("城市选择")
        group_box.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(group_box)

        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(8)

        # 系统状态显示
        self.system_status_widget = QWidget()
        system_layout = QHBoxLayout(self.system_status_widget)
        system_layout.setContentsMargins(0, 0, 0, 0)

        system_layout.addWidget(QLabel("当前系统："))
        self.system_label = QLabel("未选择系统")
        self.system_label.setFont(QFont("Microsoft YaHei", 9))
        self.system_label.setStyleSheet("color: #666;")
        system_layout.addWidget(self.system_label)
        system_layout.addStretch()

        group_layout.addWidget(self.system_status_widget)

        # 城市选择区域
        city_widget = QWidget()
        city_layout = QHBoxLayout(city_widget)
        city_layout.setContentsMargins(0, 0, 0, 0)
        city_layout.setSpacing(10)

        # 城市选择标签
        city_label = QLabel("选择城市：")
        city_label.setFont(QFont("Microsoft YaHei", 9))
        city_label.setFixedWidth(70)
        city_layout.addWidget(city_label)

        # 城市下拉框
        self.city_combo = QComboBox()
        self.city_combo.setFont(QFont("Microsoft YaHei", 9))
        self.city_combo.setMinimumWidth(200)
        self.city_combo.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #2196F3;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
        """)
        self.city_combo.currentTextChanged.connect(self.on_city_select)
        city_layout.addWidget(self.city_combo)

        # 刷新按钮
        self.refresh_button = QPushButton("刷新")
        self.refresh_button.setFont(QFont("Microsoft YaHei", 9))
        self.refresh_button.setFixedSize(60, 32)
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #bbb;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_cities)
        city_layout.addWidget(self.refresh_button)

        city_layout.addStretch()
        group_layout.addWidget(city_widget)

        # 加载进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
                font-size: 12px;
            }
            QProgressBar::chunk {
                background-color: #2196F3;
                border-radius: 3px;
            }
        """)
        group_layout.addWidget(self.progress_bar)

        # 状态信息显示
        self.status_label = QLabel("请先选择影院系统")
        self.status_label.setFont(QFont("Microsoft YaHei", 8))
        self.status_label.setStyleSheet("color: #999; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.status_label)

        # 当前城市信息显示
        self.current_city_widget = QWidget()
        current_city_layout = QHBoxLayout(self.current_city_widget)
        current_city_layout.setContentsMargins(0, 0, 0, 0)

        current_city_layout.addWidget(QLabel("当前城市："))
        self.current_city_label = QLabel("未选择")
        self.current_city_label.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        self.current_city_label.setStyleSheet("color: #2196F3;")
        current_city_layout.addWidget(self.current_city_label)
        current_city_layout.addStretch()

        # 城市统计信息
        self.city_count_label = QLabel("")
        self.city_count_label.setFont(QFont("Microsoft YaHei", 8))
        self.city_count_label.setStyleSheet("color: #666;")
        current_city_layout.addWidget(self.city_count_label)

        group_layout.addWidget(self.current_city_widget)
        self.current_city_widget.setVisible(False)

        # 添加弹性空间
        layout.addStretch()

    def check_initial_system(self):
        """检查初始系统设置"""
        current_system = cinema_system_manager.get_current_system()
        if current_system:
            self.set_current_system(current_system)

    def set_current_system(self, system_type: CinemaSystemType):
        """设置当前影院系统"""
        try:
            print(f"[城市选择] 设置当前系统: {system_type.value}")

            # 更新系统状态
            self.current_system = system_type

            # 获取系统配置
            from config.cinema_systems_config import CinemaSystemConfig
            config = CinemaSystemConfig.get_system_config(system_type)

            # 更新UI显示
            self.system_label.setText(config["display_name"])
            self.system_label.setStyleSheet(f"color: {config['ui_config']['theme_color']};")

            # 清空当前选择
            self.clear_selection()

            # 自动加载城市列表
            self.load_cities()

        except Exception as e:
            print(f"[城市选择] 设置系统失败: {e}")
            self.status_label.setText(f"设置系统失败: {str(e)}")

    def load_cities(self):
        """加载城市列表"""
        if not self.current_system:
            self.status_label.setText("请先选择影院系统")
            return

        try:
            # 调试打印已移除

            # 显示加载状态
            self.show_loading(True)
            self.status_label.setText("正在加载城市列表...")

            # 清空现有数据
            self.city_combo.clear()
            self.cities_data.clear()

            # 创建加载线程
            token = cinema_system_manager.current_token
            self.load_thread = CityLoadThread(self.current_system, token)

            # 连接信号
            self.load_thread.cities_loaded.connect(self.on_cities_loaded)
            self.load_thread.load_error.connect(self.on_load_error)

            # 启动线程
            self.load_thread.start()

            # 发送加载开始信号
            self.loading_started.emit()

        except Exception as e:
            print(f"[城市选择] 启动加载失败: {e}")
            self.show_loading(False)
            self.status_label.setText(f"启动加载失败: {str(e)}")

    def on_cities_loaded(self, cities: List[Dict]):
        """城市加载完成处理"""
        try:
            # 调试打印已移除

            # 保存数据
            self.cities_data = cities

            # 更新下拉框
            self.city_combo.clear()
            if cities:
                city_names = [city.get('name', '未知城市') for city in cities]
                self.city_combo.addItems(city_names)

                # 自动选择第一个城市
                if city_names:
                    self.city_combo.setCurrentIndex(0)
                    # on_city_select 会自动被触发

                self.status_label.setText(f"加载完成，共 {len(cities)} 个城市")
                self.city_count_label.setText(f"({len(cities)} 个城市)")
            else:
                self.city_combo.addItem("暂无城市数据")
                self.status_label.setText("暂无城市数据")
                self.city_count_label.setText("(0 个城市)")

            # 隐藏加载状态
            self.show_loading(False)

            # 发送加载完成信号
            self.loading_finished.emit()

        except Exception as e:
            print(f"[城市选择] 处理城市数据失败: {e}")
            self.on_load_error(f"处理城市数据失败: {str(e)}")

    def on_load_error(self, error_msg: str):
        """城市加载错误处理"""
        print(f"[城市选择] 加载错误: {error_msg}")

        # 隐藏加载状态
        self.show_loading(False)

        # 显示错误信息
        self.status_label.setText(error_msg)
        self.city_combo.clear()
        self.city_combo.addItem("加载失败")

        # 显示错误对话框
        QMessageBox.warning(self, "加载失败", error_msg)

    def show_loading(self, show: bool):
        """显示/隐藏加载状态"""
        if show:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            self.refresh_button.setEnabled(False)
            self.city_combo.setEnabled(False)
        else:
            self.progress_bar.setVisible(False)
            self.refresh_button.setEnabled(True)
            self.city_combo.setEnabled(True)

    def on_city_select(self, city_name: str):
        """城市选择事件处理"""
        if not city_name or city_name in ["加载失败", "暂无城市数据"]:
            return

        try:
            print(f"[城市选择] 选择城市: {city_name}")

            # 查找城市数据
            selected_city = None
            for city in self.cities_data:
                if city.get('name') == city_name:
                    selected_city = city
                    break

            if not selected_city:
                print(f"[城市选择] 未找到城市数据: {city_name}")
                return

            # 更新当前城市
            self.current_city = selected_city

            # 更新UI显示
            self.current_city_label.setText(city_name)
            self.current_city_widget.setVisible(True)

            # 发送城市切换信号
            self.city_changed.emit(selected_city)

            # 调用回调函数
            if self.on_city_changed:
                self.on_city_changed(selected_city)

            # 调试打印已移除

        except Exception as e:
            print(f"[城市选择] 城市选择失败: {e}")
            QMessageBox.warning(self, "选择失败", f"城市选择失败: {str(e)}")

    def refresh_cities(self):
        """刷新城市列表"""
        print("[城市选择] 手动刷新城市列表")
        self.load_cities()

    def clear_selection(self):
        """清空选择状态"""
        self.current_city = None
        self.cities_data.clear()
        self.city_combo.clear()
        self.current_city_label.setText("未选择")
        self.current_city_widget.setVisible(False)
        self.city_count_label.setText("")
        self.status_label.setText("请加载城市列表")

    def get_current_city(self) -> Optional[Dict]:
        """获取当前选择的城市"""
        return self.current_city

    def get_cities_data(self) -> List[Dict]:
        """获取所有城市数据"""
        return self.cities_data.copy()

    def set_city_changed_callback(self, callback: Callable):
        """设置城市切换回调函数"""
        self.on_city_changed = callback

    def is_city_selected(self) -> bool:
        """检查是否已选择城市"""
        return self.current_city is not None

    def get_selected_city_id(self) -> Optional[str]:
        """获取选择的城市ID"""
        if self.current_city:
            return self.current_city.get('id')
        return None

    def set_enabled(self, enabled: bool):
        """设置组件启用状态"""
        self.city_combo.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)

        if not enabled:
            self.status_label.setText("请先完成上级选择")
        elif self.current_system:
            self.status_label.setText("可以选择城市")

    def closeEvent(self, event):
        """组件关闭事件"""
        # 停止加载线程
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.terminate()
            self.load_thread.wait()
        event.accept()