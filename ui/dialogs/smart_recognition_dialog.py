"""
智能识别对话框

功能：
1. 显示识别结果
2. 提供用户确认和调整选项
3. 显示匹配进度和状态
4. 支持一键确认或分步确认
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QGroupBox, QProgressBar, QListWidget, QListWidgetItem,
    QSplitter, QFrame, QScrollArea, QWidget, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon
from typing import Dict, List, Any, Optional

from services.smart_recognition import OrderInfo, MatchResult


class SmartRecognitionDialog(QDialog):
    """智能识别对话框"""
    
    # 信号定义
    recognition_confirmed = pyqtSignal(dict)  # 确认识别结果
    recognition_cancelled = pyqtSignal()     # 取消识别
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_info = None
        self.match_result = None
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("智能订单识别")
        self.setFixedSize(800, 600)
        self.setModal(True)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        title_label = QLabel("🤖 智能订单识别")
        title_label.setFont(QFont("Microsoft YaHei", 16, QFont.Bold))
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        title_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(title_layout)
        
        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧：原始文本和解析结果
        left_widget = self.create_left_panel()
        splitter.addWidget(left_widget)
        
        # 右侧：匹配结果和操作
        right_widget = self.create_right_panel()
        splitter.addWidget(right_widget)
        
        # 设置分割器比例
        splitter.setSizes([400, 400])
        
        # 底部按钮区域
        button_layout = QHBoxLayout()
        
        self.auto_fill_btn = QPushButton("🚀 一键自动填充")
        self.auto_fill_btn.setFixedHeight(35)
        self.auto_fill_btn.clicked.connect(self.on_auto_fill)
        
        self.manual_confirm_btn = QPushButton("✋ 手动确认")
        self.manual_confirm_btn.setFixedHeight(35)
        self.manual_confirm_btn.clicked.connect(self.on_manual_confirm)
        
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.setFixedHeight(35)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.auto_fill_btn)
        button_layout.addWidget(self.manual_confirm_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(button_layout)
        
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 原始文本组
        text_group = QGroupBox("📋 原始订单信息")
        text_layout = QVBoxLayout(text_group)
        
        self.raw_text_edit = QTextEdit()
        self.raw_text_edit.setMaximumHeight(150)
        self.raw_text_edit.setPlaceholderText("剪贴板内容将显示在这里...")
        text_layout.addWidget(self.raw_text_edit)
        
        layout.addWidget(text_group)
        
        # 解析结果组
        parse_group = QGroupBox("🔍 解析结果")
        parse_layout = QVBoxLayout(parse_group)
        
        # 创建解析结果显示区域
        self.parse_result_widget = QWidget()
        self.parse_result_layout = QGridLayout(self.parse_result_widget)
        self.parse_result_layout.setSpacing(8)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.parse_result_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(300)
        
        parse_layout.addWidget(scroll_area)
        layout.addWidget(parse_group)
        
        return widget
        
    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 匹配状态组
        status_group = QGroupBox("📊 匹配状态")
        status_layout = QVBoxLayout(status_group)
        
        self.status_list = QListWidget()
        self.status_list.setMaximumHeight(120)
        status_layout.addWidget(self.status_list)
        
        # 置信度显示
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("匹配置信度:"))
        
        self.confidence_label = QLabel("0%")
        self.confidence_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        confidence_layout.addWidget(self.confidence_label)
        confidence_layout.addStretch()
        
        status_layout.addLayout(confidence_layout)
        layout.addWidget(status_group)
        
        # 匹配结果组
        result_group = QGroupBox("🎯 匹配结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_list = QListWidget()
        result_layout.addWidget(self.result_list)
        
        layout.addWidget(result_group)
        
        # 建议组
        suggestion_group = QGroupBox("💡 建议")
        suggestion_layout = QVBoxLayout(suggestion_group)
        
        self.suggestion_list = QListWidget()
        self.suggestion_list.setMaximumHeight(100)
        suggestion_layout.addWidget(self.suggestion_list)
        
        layout.addWidget(suggestion_group)
        
        return widget
    
    def setup_styles(self):
        """设置样式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            
            QGroupBox {
                font: bold 12px "Microsoft YaHei";
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #333333;
            }
            
            QTextEdit {
                border: 1px solid #dddddd;
                border-radius: 4px;
                padding: 8px;
                font: 11px "Microsoft YaHei";
                background-color: #fafafa;
            }
            
            QListWidget {
                border: 1px solid #dddddd;
                border-radius: 4px;
                background-color: white;
                font: 11px "Microsoft YaHei";
            }
            
            QListWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eeeeee;
            }
            
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font: bold 11px "Microsoft YaHei";
            }
            
            QPushButton:hover {
                background-color: #1976d2;
            }
            
            QPushButton:pressed {
                background-color: #0d47a1;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #999999;
            }
            
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                text-align: center;
                font: 10px "Microsoft YaHei";
            }
            
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 3px;
            }
        """)
    
    def show_recognition_result(self, order_info: OrderInfo, match_result: MatchResult):
        """显示识别结果"""
        self.order_info = order_info
        self.match_result = match_result
        
        # 显示原始文本
        self.raw_text_edit.setPlainText(order_info.raw_text)
        
        # 显示解析结果
        self.display_parse_result(order_info)
        
        # 显示匹配状态
        self.display_match_status(match_result)
        
        # 显示匹配结果
        self.display_match_result(match_result)
        
        # 显示建议
        self.display_suggestions(match_result)
        
        # 更新按钮状态
        self.update_button_states(match_result)
    
    def display_parse_result(self, order_info: OrderInfo):
        """显示解析结果"""
        # 清空现有内容
        for i in reversed(range(self.parse_result_layout.count())):
            self.parse_result_layout.itemAt(i).widget().setParent(None)
        
        row = 0
        fields = [
            ("订单号", order_info.order_id),
            ("城市", order_info.city),
            ("影院", order_info.cinema_name),
            ("地址", order_info.cinema_address),
            ("影片", order_info.movie_name),
            ("场次", order_info.session_time),
            ("影厅", order_info.hall_name),
            ("座位", ", ".join(order_info.seats)),
            ("价格", f"¥{order_info.price}" if order_info.price > 0 else "")
        ]
        
        for label_text, value in fields:
            if value:  # 只显示有值的字段
                label = QLabel(f"{label_text}:")
                label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
                label.setFixedWidth(60)
                
                value_label = QLabel(str(value))
                value_label.setWordWrap(True)
                value_label.setStyleSheet("color: #333333; padding: 2px;")
                
                self.parse_result_layout.addWidget(label, row, 0)
                self.parse_result_layout.addWidget(value_label, row, 1)
                row += 1
    
    def display_match_status(self, match_result: MatchResult):
        """显示匹配状态"""
        self.status_list.clear()
        
        # 影院匹配状态
        cinema_status = "✅ 影院匹配成功" if match_result.cinema_match else "❌ 影院匹配失败"
        self.status_list.addItem(cinema_status)
        
        # 影片匹配状态
        movie_status = "✅ 影片匹配成功" if match_result.movie_match else "❌ 影片匹配失败"
        self.status_list.addItem(movie_status)
        
        # 场次匹配状态
        session_status = "✅ 场次匹配成功" if match_result.session_match else "❌ 场次匹配失败"
        self.status_list.addItem(session_status)
        
        # 座位匹配状态
        seat_status = f"✅ 座位匹配成功 ({len(match_result.seat_matches)}个)" if match_result.seat_matches else "❌ 座位匹配失败"
        self.status_list.addItem(seat_status)
        
        # 更新置信度
        confidence_percent = int(match_result.confidence_score * 100)
        self.confidence_label.setText(f"{confidence_percent}%")
        
        # 根据置信度设置颜色
        if confidence_percent >= 80:
            color = "#4caf50"  # 绿色
        elif confidence_percent >= 60:
            color = "#ff9800"  # 橙色
        else:
            color = "#f44336"  # 红色
        
        self.confidence_label.setStyleSheet(f"color: {color};")
    
    def display_match_result(self, match_result: MatchResult):
        """显示匹配结果详情"""
        self.result_list.clear()
        
        if match_result.cinema_match:
            cinema_name = match_result.cinema_match.get('cinemaShortName', '未知')
            self.result_list.addItem(f"🏢 影院: {cinema_name}")
        
        if match_result.movie_match:
            movie_name = match_result.movie_match.get('name', '未知')
            self.result_list.addItem(f"🎬 影片: {movie_name}")
        
        if match_result.session_match:
            session_time = match_result.session_match.get('time', '未知')
            self.result_list.addItem(f"⏰ 场次: {session_time}")
        
        if match_result.seat_matches:
            for seat in match_result.seat_matches:
                seat_str = seat.get('seat_str', f"{seat.get('row')}排{seat.get('col')}座")
                self.result_list.addItem(f"💺 座位: {seat_str}")
    
    def display_suggestions(self, match_result: MatchResult):
        """显示建议"""
        self.suggestion_list.clear()
        
        for suggestion in match_result.suggestions:
            self.suggestion_list.addItem(f"💡 {suggestion}")
        
        if not match_result.suggestions:
            self.suggestion_list.addItem("✨ 所有信息匹配良好，可以直接确认")
    
    def update_button_states(self, match_result: MatchResult):
        """更新按钮状态"""
        # 根据匹配结果启用/禁用按钮
        has_basic_match = match_result.cinema_match is not None
        
        self.auto_fill_btn.setEnabled(has_basic_match and match_result.confidence_score >= 0.6)
        self.manual_confirm_btn.setEnabled(has_basic_match)
        
        # 更新按钮样式
        if match_result.confidence_score >= 0.8:
            self.auto_fill_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4caf50;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font: bold 11px "Microsoft YaHei";
                }
                QPushButton:hover {
                    background-color: #388e3c;
                }
            """)
    
    def show_progress(self, message: str = "识别中..."):
        """显示进度"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 不确定进度
        
        # 模拟进度更新
        QTimer.singleShot(500, lambda: self.progress_bar.setValue(25))
        QTimer.singleShot(1000, lambda: self.progress_bar.setValue(50))
        QTimer.singleShot(1500, lambda: self.progress_bar.setValue(75))
        QTimer.singleShot(2000, lambda: self.progress_bar.setValue(100))
        QTimer.singleShot(2500, lambda: self.progress_bar.setVisible(False))
    
    def on_auto_fill(self):
        """一键自动填充"""
        if self.order_info and self.match_result:
            result_data = {
                'order_info': self.order_info,
                'match_result': self.match_result,
                'auto_fill': True
            }
            self.recognition_confirmed.emit(result_data)
            self.accept()
    
    def on_manual_confirm(self):
        """手动确认"""
        if self.order_info and self.match_result:
            result_data = {
                'order_info': self.order_info,
                'match_result': self.match_result,
                'auto_fill': False
            }
            self.recognition_confirmed.emit(result_data)
            self.accept()
