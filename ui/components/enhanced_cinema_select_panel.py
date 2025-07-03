#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版影院选择面板 - 七级联动第三级
基于"系统+城市"的双重筛选影院选择
"""

from typing import Callable, Optional, Dict, List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QMessageBox, QGroupBox, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFont

from config.cinema_systems_config import CinemaSystemType, cinema_system_manager
from services.unified_cinema_api import CinemaAPIFactory

class CinemaLoadThread(QThread):
    """影院数据加载线程"""
    
    # 定义信号
    cinemas_loaded = pyqtSignal(list)  # 影院加载完成信号
    load_error = pyqtSignal(str)       # 加载错误信号
    
    def __init__(self, system_type: CinemaSystemType, city_id: Optional[str] = None, token: Optional[str] = None):
        super().__init__()
        self.system_type = system_type
        self.city_id = city_id
        self.token = token
    
    def run(self):
        """执行影院数据加载"""
        try:
            pass
            
            # 创建API实例
            api = CinemaAPIFactory.create_api(self.system_type, self.token)
            
            # 获取影院列表
            cinemas = api.get_cinemas(self.city_id)
            
            print(f"[影院加载线程] 成功加载 {len(cinemas)} 个影院")
            self.cinemas_loaded.emit(cinemas)
            
        except Exception as e:
            error_msg = f"加载影院列表失败: {str(e)}"
            print(f"[影院加载线程] {error_msg}")
            self.load_error.emit(error_msg)

class EnhancedCinemaSelectPanel(QWidget):
    """增强版影院选择面板"""
    
    # 定义信号
    cinema_changed = pyqtSignal(dict)    # 影院切换信号
    loading_started = pyqtSignal()       # 开始加载信号
    loading_finished = pyqtSignal()     # 加载完成信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 状态变量
        self.current_system: Optional[CinemaSystemType] = None
        self.current_city: Optional[Dict] = None
        self.current_cinema: Optional[Dict] = None
        self.cinemas_data: List[Dict] = []
        self.load_thread: Optional[CinemaLoadThread] = None
        
        # 回调函数
        self.on_cinema_changed: Optional[Callable] = None
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 创建分组框
        group_box = QGroupBox("影院选择")
        group_box.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(group_box)
        
        group_layout = QVBoxLayout(group_box)
        group_layout.setSpacing(8)
        
        # 上级选择状态显示
        self.context_widget = QWidget()
        context_layout = QVBoxLayout(self.context_widget)
        context_layout.setContentsMargins(0, 0, 0, 0)
        context_layout.setSpacing(4)
        
        # 系统信息
        system_info_layout = QHBoxLayout()
        system_info_layout.addWidget(QLabel("当前系统："))
        self.system_label = QLabel("未选择")
        self.system_label.setFont(QFont("Microsoft YaHei", 9))
        self.system_label.setStyleSheet("color: #666;")
        system_info_layout.addWidget(self.system_label)
        system_info_layout.addStretch()
        context_layout.addLayout(system_info_layout)
        
        # 城市信息
        city_info_layout = QHBoxLayout()
        city_info_layout.addWidget(QLabel("当前城市："))
        self.city_label = QLabel("未选择")
        self.city_label.setFont(QFont("Microsoft YaHei", 9))
        self.city_label.setStyleSheet("color: #666;")
        city_info_layout.addWidget(self.city_label)
        city_info_layout.addStretch()
        context_layout.addLayout(city_info_layout)
        
        group_layout.addWidget(self.context_widget)
        
        # 影院选择区域
        cinema_widget = QWidget()
        cinema_layout = QHBoxLayout(cinema_widget)
        cinema_layout.setContentsMargins(0, 0, 0, 0)
        cinema_layout.setSpacing(10)
        
        # 影院选择标签
        cinema_label = QLabel("选择影院：")
        cinema_label.setFont(QFont("Microsoft YaHei", 9))
        cinema_label.setFixedWidth(70)
        cinema_layout.addWidget(cinema_label)
        
        # 影院下拉框
        self.cinema_combo = QComboBox()
        self.cinema_combo.setFont(QFont("Microsoft YaHei", 9))
        self.cinema_combo.setMinimumWidth(250)
        self.cinema_combo.setStyleSheet("""
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
        self.cinema_combo.currentTextChanged.connect(self.on_cinema_select)
        cinema_layout.addWidget(self.cinema_combo)
        
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
        self.refresh_button.clicked.connect(self.refresh_cinemas)
        cinema_layout.addWidget(self.refresh_button)
        
        cinema_layout.addStretch()
        group_layout.addWidget(cinema_widget)
        
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
        self.status_label = QLabel("请先选择系统和城市")
        self.status_label.setFont(QFont("Microsoft YaHei", 8))
        self.status_label.setStyleSheet("color: #999; padding: 5px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        group_layout.addWidget(self.status_label)
        
        # 当前影院信息显示
        self.current_cinema_widget = QWidget()
        current_cinema_layout = QVBoxLayout(self.current_cinema_widget)
        current_cinema_layout.setContentsMargins(0, 0, 0, 0)
        current_cinema_layout.setSpacing(5)
        
        # 影院名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("当前影院："))
        self.current_cinema_label = QLabel("未选择")
        self.current_cinema_label.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
        self.current_cinema_label.setStyleSheet("color: #2196F3;")
        name_layout.addWidget(self.current_cinema_label)
        name_layout.addStretch()
        
        # 影院统计
        self.cinema_count_label = QLabel("")
        self.cinema_count_label.setFont(QFont("Microsoft YaHei", 8))
        self.cinema_count_label.setStyleSheet("color: #666;")
        name_layout.addWidget(self.cinema_count_label)
        current_cinema_layout.addLayout(name_layout)
        
        # 影院详细信息
        self.cinema_info_text = QTextEdit()
        self.cinema_info_text.setMaximumHeight(60)
        self.cinema_info_text.setFont(QFont("Microsoft YaHei", 8))
        self.cinema_info_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #eee;
                border-radius: 4px;
                background-color: #f9f9f9;
                padding: 5px;
            }
        """)
        self.cinema_info_text.setReadOnly(True)
        current_cinema_layout.addWidget(self.cinema_info_text)
        
        group_layout.addWidget(self.current_cinema_widget)
        self.current_cinema_widget.setVisible(False)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 初始状态设置
        self.set_enabled(False)
    
    def set_context(self, system_type: CinemaSystemType, city_data: Optional[Dict] = None):
        """设置上下文（系统和城市）"""
        try:
            print(f"[影院选择] 设置上下文 - 系统: {system_type.value}, 城市: {city_data}")
            
            # 更新系统
            self.current_system = system_type
            
            # 获取系统配置
            from config.cinema_systems_config import CinemaSystemConfig
            config = CinemaSystemConfig.get_system_config(system_type)
            
            # 更新系统显示
            self.system_label.setText(config["display_name"])
            self.system_label.setStyleSheet(f"color: {config['ui_config']['theme_color']};")
            
            # 更新城市
            self.current_city = city_data
            if city_data:
                city_name = city_data.get('name', '未知城市')
                self.city_label.setText(city_name)
                self.city_label.setStyleSheet("color: #333;")
                
                # 启用组件并加载影院
                self.set_enabled(True)
                self.load_cinemas()
            else:
                self.city_label.setText("未选择")
                self.city_label.setStyleSheet("color: #666;")
                self.set_enabled(False)
                self.clear_selection()
            
        except Exception as e:
            print(f"[影院选择] 设置上下文失败: {e}")
            self.status_label.setText(f"设置上下文失败: {str(e)}")
    
    def load_cinemas(self):
        """加载影院列表"""
        if not self.current_system or not self.current_city:
            self.status_label.setText("请先选择系统和城市")
            return
        
        try:
            city_id = self.current_city.get('id')
            
            # 显示加载状态
            self.show_loading(True)
            self.status_label.setText("正在加载影院列表...")
            
            # 清空现有数据
            self.cinema_combo.clear()
            self.cinemas_data.clear()
            
            # 创建加载线程
            token = cinema_system_manager.current_token
            self.load_thread = CinemaLoadThread(self.current_system, city_id, token)
            
            # 连接信号
            self.load_thread.cinemas_loaded.connect(self.on_cinemas_loaded)
            self.load_thread.load_error.connect(self.on_load_error)
            
            # 启动线程
            self.load_thread.start()
            
            # 发送加载开始信号
            self.loading_started.emit()
            
        except Exception as e:
            print(f"[影院选择] 启动加载失败: {e}")
            self.show_loading(False)
            self.status_label.setText(f"启动加载失败: {str(e)}")

    def on_cinemas_loaded(self, cinemas: List[Dict]):
        """影院加载完成处理"""
        try:
            pass

            # 保存数据
            self.cinemas_data = cinemas

            # 更新下拉框
            self.cinema_combo.clear()
            if cinemas:
                cinema_names = [cinema.get('name', '未知影院') for cinema in cinemas]
                self.cinema_combo.addItems(cinema_names)

                # 自动选择第一个影院
                if cinema_names:
                    self.cinema_combo.setCurrentIndex(0)
                    # on_cinema_select 会自动被触发

                self.status_label.setText(f"加载完成，共 {len(cinemas)} 个影院")
                self.cinema_count_label.setText(f"({len(cinemas)} 个影院)")
            else:
                self.cinema_combo.addItem("暂无影院数据")
                self.status_label.setText("暂无影院数据")
                self.cinema_count_label.setText("(0 个影院)")

            # 隐藏加载状态
            self.show_loading(False)

            # 发送加载完成信号
            self.loading_finished.emit()

        except Exception as e:
            print(f"[影院选择] 处理影院数据失败: {e}")
            self.on_load_error(f"处理影院数据失败: {str(e)}")

    def on_load_error(self, error_msg: str):
        """影院加载错误处理"""
        print(f"[影院选择] 加载错误: {error_msg}")

        # 隐藏加载状态
        self.show_loading(False)

        # 显示错误信息
        self.status_label.setText(error_msg)
        self.cinema_combo.clear()
        self.cinema_combo.addItem("加载失败")

        # 显示错误对话框
        QMessageBox.warning(self, "加载失败", error_msg)

    def show_loading(self, show: bool):
        """显示/隐藏加载状态"""
        if show:
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # 无限进度条
            self.refresh_button.setEnabled(False)
            self.cinema_combo.setEnabled(False)
        else:
            self.progress_bar.setVisible(False)
            self.refresh_button.setEnabled(True)
            self.cinema_combo.setEnabled(True)

    def on_cinema_select(self, cinema_name: str):
        """影院选择事件处理"""
        if not cinema_name or cinema_name in ["加载失败", "暂无影院数据"]:
            return

        try:
            print(f"[影院选择] 选择影院: {cinema_name}")

            # 查找影院数据
            selected_cinema = None
            for cinema in self.cinemas_data:
                if cinema.get('name') == cinema_name:
                    selected_cinema = cinema
                    break

            if not selected_cinema:
                print(f"[影院选择] 未找到影院数据: {cinema_name}")
                return

            # 更新当前影院
            self.current_cinema = selected_cinema

            # 更新UI显示
            self.current_cinema_label.setText(cinema_name)
            self.current_cinema_widget.setVisible(True)

            # 显示影院详细信息
            self.update_cinema_info(selected_cinema)

            # 发送影院切换信号
            self.cinema_changed.emit(selected_cinema)

            # 调用回调函数
            if self.on_cinema_changed:
                self.on_cinema_changed(selected_cinema)


        except Exception as e:
            print(f"[影院选择] 影院选择失败: {e}")
            QMessageBox.warning(self, "选择失败", f"影院选择失败: {str(e)}")

    def update_cinema_info(self, cinema_data: Dict):
        """更新影院详细信息显示"""
        try:
            info_lines = []

            # 影院地址
            address = cinema_data.get('address', '')
            if address:
                info_lines.append(f"地址: {address}")

            # 影院电话
            phone = cinema_data.get('phone', '')
            if phone:
                info_lines.append(f"电话: {phone}")

            # 影院ID
            cinema_id = cinema_data.get('id', '')
            if cinema_id:
                info_lines.append(f"ID: {cinema_id}")

            # 系统类型
            system_type = cinema_data.get('system_type', '')
            if system_type:
                info_lines.append(f"系统: {system_type}")

            # 如果没有详细信息，显示基本信息
            if not info_lines:
                info_lines.append("暂无详细信息")

            self.cinema_info_text.setText('\n'.join(info_lines))

        except Exception as e:
            print(f"[影院选择] 更新影院信息失败: {e}")
            self.cinema_info_text.setText("信息显示失败")

    def refresh_cinemas(self):
        """刷新影院列表"""
        print("[影院选择] 手动刷新影院列表")
        self.load_cinemas()

    def clear_selection(self):
        """清空选择状态"""
        self.current_cinema = None
        self.cinemas_data.clear()
        self.cinema_combo.clear()
        self.current_cinema_label.setText("未选择")
        self.current_cinema_widget.setVisible(False)
        self.cinema_count_label.setText("")
        self.cinema_info_text.clear()
        self.status_label.setText("请选择系统和城市")

    def get_current_cinema(self) -> Optional[Dict]:
        """获取当前选择的影院"""
        return self.current_cinema

    def get_cinemas_data(self) -> List[Dict]:
        """获取所有影院数据"""
        return self.cinemas_data.copy()

    def set_cinema_changed_callback(self, callback: Callable):
        """设置影院切换回调函数"""
        self.on_cinema_changed = callback

    def is_cinema_selected(self) -> bool:
        """检查是否已选择影院"""
        return self.current_cinema is not None

    def get_selected_cinema_id(self) -> Optional[str]:
        """获取选择的影院ID"""
        if self.current_cinema:
            return self.current_cinema.get('id')
        return None

    def set_enabled(self, enabled: bool):
        """设置组件启用状态"""
        self.cinema_combo.setEnabled(enabled)
        self.refresh_button.setEnabled(enabled)

        if not enabled:
            self.status_label.setText("请先完成上级选择")
            self.clear_selection()
        elif self.current_system and self.current_city:
            self.status_label.setText("可以选择影院")

    def closeEvent(self, event):
        """组件关闭事件"""
        # 停止加载线程
        if self.load_thread and self.load_thread.isRunning():
            self.load_thread.terminate()
            self.load_thread.wait()
        event.accept()
