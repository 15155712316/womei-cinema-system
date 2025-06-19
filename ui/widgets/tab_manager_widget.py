#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tab页面管理模块
负责管理所有Tab页面的显示和功能
"""

import random
import time
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox, QDialog, QDialogButtonBox, QMenu, QFrame, QScrollArea
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QColor, QFont

# 导入自定义组件
from ui.widgets.classic_components import (
    ClassicTabWidget, ClassicGroupBox, ClassicButton, ClassicLineEdit, 
    ClassicComboBox, ClassicTableWidget, ClassicTextEdit, ClassicLabel, ClassicListWidget
)
from ui.interfaces.plugin_interface import IWidgetInterface, event_bus

# 导入消息管理器
from services.ui_utils import MessageManager


class TabManagerWidget(QWidget):
    """Tab页面管理组件"""
    
    # 定义信号
    cinema_selected = pyqtSignal(str)  # 影院选择信号
    order_submitted = pyqtSignal(dict)  # 订单提交信号
    coupon_bound = pyqtSignal(dict)  # 券绑定信号
    coupon_exchanged = pyqtSignal(dict)  # 兑换券信号
    session_selected = pyqtSignal(dict)  # 🆕 场次选择信号，用于触发座位图加载
    seat_load_requested = pyqtSignal(dict)  # 🆕 座位图加载请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # 初始化状态
        self.current_account = None
        self.cinemas_data = []
        self.current_points = 0

        # 🆕 六级联动状态变量（移除系统选择）
        self.current_city = None            # 当前城市
        self.current_cinema_data = None     # 当前影院数据
        self.current_movie = None           # 当前电影
        self.current_date = None            # 当前日期
        self.current_session = None         # 当前场次

        # 🆕 六级联动数据缓存（移除系统列表）
        self.cities_data = []               # 城市列表
        self.movies_data = []               # 电影列表
        self.dates_data = []                # 日期列表
        self.sessions_data = []             # 场次列表

        # 🆕 API实例
        self.api_instance = None

        # 添加数据缓存
        self.order_data_cache = []

        # 实现IWidgetInterface接口
        self._widget_interface = IWidgetInterface()

        # 初始化界面
        self.initialize()

        # 连接全局事件
        self._connect_global_events()
    
    def initialize(self) -> None:
        """初始化组件"""
        self._setup_ui()
        self._connect_signals()

        # 🆕 UI创建完成后初始化沃美联动（移除系统选择）
        self._init_cascade()

        # 加载示例数据
        self._load_sample_data()
    
    def cleanup(self) -> None:
        """清理组件资源"""
        # 断开全局事件连接
        event_bus.account_changed.disconnect(self._on_account_changed)
        
        # 清理数据
        self.current_account = None
        self.cinemas_data.clear()
    
    def get_widget(self) -> QWidget:
        """获取Qt组件"""
        return self
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # 创建Tab组件
        self.tab_widget = ClassicTabWidget()
        self._create_tab_pages()
        
        layout.addWidget(self.tab_widget)
    
    def _create_tab_pages(self):
        """创建所有Tab页面"""
        # Tab1: 出票
        self.ticket_tab = QWidget()
        self._build_ticket_tab()
        self.tab_widget.addTab(self.ticket_tab, "出票")
        
        # Tab2: 绑券
        self.bind_coupon_tab = QWidget()
        self._build_bind_coupon_tab()
        self.tab_widget.addTab(self.bind_coupon_tab, "绑券")
        
        # Tab3: 兑换券
        self.exchange_coupon_tab = QWidget()
        self._build_exchange_coupon_tab()
        self.tab_widget.addTab(self.exchange_coupon_tab, "兑换券")
        
        # Tab4: 订单
        self.order_tab = QWidget()
        self._build_order_tab()
        self.tab_widget.addTab(self.order_tab, "订单")
        
        # Tab5: 影院
        self.cinema_tab = QWidget()
        self._build_cinema_tab()
        self.tab_widget.addTab(self.cinema_tab, "影院")
    
    def _build_ticket_tab(self):
        """构建出票Tab页面"""
        layout = QHBoxLayout(self.ticket_tab)
        layout.setSpacing(10)
        
        # 左侧：影院选择 - 缩小比例，给券列表更多空间
        cinema_group = ClassicGroupBox("影院选择")
        self._build_cinema_select(cinema_group)
        layout.addWidget(cinema_group, 40)  # 从55改为40

        # 右侧：可用券列表 - 增加比例
        coupon_group = ClassicGroupBox("可用券列表")
        self._build_coupon_list(coupon_group)
        layout.addWidget(coupon_group, 60)  # 从45改为60
    
    def _build_cinema_select(self, parent_group):
        """构建七级联动选择区域：系统→城市→影院→电影→日期→场次→座位"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(0, 20, 10, 10)
        layout.setSpacing(5)

        # 当前账号显示
        self.current_account_label = ClassicLabel("当前账号: 未选择", "info")
        layout.addWidget(self.current_account_label)



        # 🆕 第二级：城市选择
        city_layout = QHBoxLayout()
        city_layout.setContentsMargins(0, 0, 0, 0)
        city_label = ClassicLabel("城市:")
        city_label.setFixedWidth(30)
        city_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        city_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.city_combo = ClassicComboBox()
        self.city_combo.addItem("加载中...")
        self.city_combo.setFixedWidth(320)
        self.city_combo.setEnabled(True)  # 启用城市选择
        city_layout.addWidget(city_label)
        city_layout.addSpacing(5)
        city_layout.addWidget(self.city_combo)
        city_layout.addStretch()
        layout.addLayout(city_layout)

        # 第三级：影院选择
        cinema_layout = QHBoxLayout()
        cinema_layout.setContentsMargins(0, 0, 0, 0)
        cinema_label = ClassicLabel("影院:")
        cinema_label.setFixedWidth(30)
        cinema_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cinema_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.cinema_combo = ClassicComboBox()
        self.cinema_combo.addItem("请先选择城市")
        self.cinema_combo.setFixedWidth(320)
        self.cinema_combo.setEnabled(False)
        cinema_layout.addWidget(cinema_label)
        cinema_layout.addSpacing(5)
        cinema_layout.addWidget(self.cinema_combo)
        cinema_layout.addStretch()
        layout.addLayout(cinema_layout)
        
        # 第四级：影片选择
        movie_layout = QHBoxLayout()
        movie_layout.setContentsMargins(0, 0, 0, 0)
        movie_label = ClassicLabel("影片:")
        movie_label.setFixedWidth(30)
        movie_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        movie_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.movie_combo = ClassicComboBox()
        self.movie_combo.addItems(["请先选择影院"])
        self.movie_combo.setFixedWidth(320)
        self.movie_combo.setEnabled(False)
        movie_layout.addWidget(movie_label)
        movie_layout.addSpacing(5)
        movie_layout.addWidget(self.movie_combo)
        movie_layout.addStretch()
        layout.addLayout(movie_layout)

        # 第五级：日期选择
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_label = ClassicLabel("日期:")
        date_label.setFixedWidth(30)
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        date_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.date_combo = ClassicComboBox()
        self.date_combo.addItems(["请先选择影片"])
        self.date_combo.setFixedWidth(320)
        self.date_combo.setEnabled(False)
        date_layout.addWidget(date_label)
        date_layout.addSpacing(5)
        date_layout.addWidget(self.date_combo)
        date_layout.addStretch()
        layout.addLayout(date_layout)

        # 第六级：场次选择
        session_layout = QHBoxLayout()
        session_layout.setContentsMargins(0, 0, 0, 0)
        session_label = ClassicLabel("场次:")
        session_label.setFixedWidth(30)
        session_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        session_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.session_combo = ClassicComboBox()
        self.session_combo.addItems(["请先选择日期"])
        self.session_combo.setFixedWidth(320)
        self.session_combo.setEnabled(False)
        session_layout.addWidget(session_label)
        session_layout.addSpacing(5)
        session_layout.addWidget(self.session_combo)
        session_layout.addStretch()
        layout.addLayout(session_layout)
        
        # 选座按钮 - 缩小高度，避免占用座位区域空间
        self.submit_order_btn = ClassicButton("选座", "success")
        self.submit_order_btn.setMinimumHeight(20)  # 进一步缩小到20px
        self.submit_order_btn.setMaximumHeight(20)  # 限制最大高度为20px
        # 覆盖样式中的padding设置
        self.submit_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #107c10;
                color: white;
                border: 1px solid #107c10;
                padding: 2px 8px;
                border-radius: 3px;
                font: 10px "Microsoft YaHei";
                min-width: 60px;
                min-height: 20px;
                max-height: 20px;
            }
            QPushButton:hover {
                background-color: #0e6e0e;
                border-color: #0e6e0e;
            }
            QPushButton:pressed {
                background-color: #0c5e0c;
                border-color: #0c5e0c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #888888;
            }
        """)
        self.submit_order_btn.setEnabled(False)  # 初始禁用，需要选择完所有选项后启用
        layout.addWidget(self.submit_order_btn)
        
        layout.addStretch()
    
    def _build_coupon_list(self, parent_group):
        """构建券列表区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(8)
        
        # 券列表 - 初始为空白状态
        self.coupon_list = ClassicListWidget()
        # 不添加任何初始项目，保持空白

        layout.addWidget(self.coupon_list)
    
    def _build_bind_coupon_tab(self):
        """构建绑券Tab页面 - 直接从第二部分文档复制并适配PyQt5"""
        main_layout = QHBoxLayout(self.bind_coupon_tab)
        
        # 左侧输入区
        input_frame = QWidget()
        input_layout = QVBoxLayout(input_frame)
        
        # 当前账号信息显示
        self.bind_account_info = ClassicLabel("当前账号：未选择")
        self.bind_account_info.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        self.bind_account_info.setStyleSheet("QLabel { color: red; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
        self.bind_account_info.setWordWrap(True)
        input_layout.addWidget(self.bind_account_info)
        
        # 提示标签
        input_layout.addWidget(ClassicLabel("每行一个券号："))
        
        # 券号输入框
        self.coupon_text = ClassicTextEdit()
        self.coupon_text.setFixedHeight(200)
        self.coupon_text.setPlaceholderText("请在此输入券号，每行一个\n例如：\nAB1234567890\nCD2345678901\nEF3456789012")
        input_layout.addWidget(self.coupon_text)
        
        # 绑定按钮
        bind_btn = ClassicButton("绑定当前账号", "success")
        bind_btn.setMinimumHeight(35)
        bind_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                font: bold 11px "Microsoft YaHei";
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        bind_btn.clicked.connect(self.on_bind_coupons)
        input_layout.addWidget(bind_btn)
        
        main_layout.addWidget(input_frame)
        
        # 右侧日志区
        log_frame = QWidget()
        log_layout = QVBoxLayout(log_frame)
        
        log_layout.addWidget(ClassicLabel("绑定日志："))
        
        self.bind_log_text = ClassicTextEdit(read_only=True)
        self.bind_log_text.setStyleSheet("QTextEdit { background-color: #f8f9fa; }")
        log_layout.addWidget(self.bind_log_text)
        
        copy_log_btn = ClassicButton("复制日志", "default")
        copy_log_btn.clicked.connect(self.copy_bind_log)
        log_layout.addWidget(copy_log_btn)
        
        main_layout.addWidget(log_frame)
        
        # 设置左右区域比例
        main_layout.setStretch(0, 1)  # 左侧占1份
        main_layout.setStretch(1, 1)  # 右侧占1份

    def on_bind_coupons(self):
        """绑券功能 - 直接从源代码复制核心逻辑"""
        account = getattr(self, 'current_account', None)
        if not account:
            MessageManager.show_error(self, "未选中账号", "请先在左侧账号列表选择要绑定的账号！", auto_close=False)
            return
        
        # 验证账号信息完整性
        required_fields = ['cinemaid', 'userid', 'openid', 'token']
        for field in required_fields:
            if not account.get(field):
                MessageManager.show_error(self, "账号信息不完整", f"当前账号缺少{field}字段，请重新登录！", auto_close=False)
                return
        
        print(f"[券绑定] 使用账号: {account.get('userid')} @ {account.get('cinemaid')}")
        print(f"[券绑定] Token: {account.get('token', '')[:10]}...")
        
        coupon_codes = self.coupon_text.toPlainText().strip().split('\n')
        coupon_codes = [c.strip() for c in coupon_codes if c.strip()]
        if not coupon_codes:
            MessageManager.show_error(self, "无券号", "请输入至少一个券号！", auto_close=False)
            return
        
        # 不显示进度提示，直接开始绑定
        print(f"[券绑定] 即将绑定{len(coupon_codes)}张券")
        
        # 执行绑定
        self.perform_batch_bind(account, coupon_codes)

    def perform_batch_bind(self, account, coupon_codes):
        """执行批量绑券 - 基于现有API"""
        log_lines = []
        success, fail = 0, 0
        fail_codes = []
        
        # 导入现有的绑券API
        from services.order_api import bind_coupon
        from PyQt5.QtWidgets import QApplication
        
        for i, code in enumerate(coupon_codes, 1):
            params = {
                'couponcode': code,
                'cinemaid': account['cinemaid'],
                'userid': account['userid'],
                'openid': account['openid'],
                'token': account['token'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'source': '2',
                'groupid': '',
                'cardno': account.get('cardno', '')
            }
            
            print(f"[券绑定] 正在绑定第{i}/{len(coupon_codes)}张券: {code}")
            
            try:
                res = bind_coupon(params)
                print(f"[券绑定] 券{code}绑定结果: {res}")
                
                if res.get('resultCode') == '0':
                    log_lines.append(f"券{code} 绑定成功")
                    success += 1
                else:
                    error_desc = res.get('resultDesc', '未知错误')
                    log_lines.append(f"券{code} 绑定失败：{error_desc}")
                    fail += 1
                    fail_codes.append(code)
                    
                    # 特殊处理token失效问题
                    if 'TOKEN_INVALID' in error_desc:
                        log_lines.append(f"  -> Token可能已失效，建议重新登录账号")
                        
            except Exception as e:
                error_msg = str(e)
                log_lines.append(f"券{code} 绑定失败：{error_msg}")
                fail += 1
                fail_codes.append(code)
                print(f"[券绑定] 券{code}绑定异常: {e}")
            
            # 添加0.2秒延迟（除了最后一张券）
            if i < len(coupon_codes):
                print(f"[券绑定] 等待0.2秒后绑定下一张券...")
                QApplication.processEvents()  # 处理界面事件
                time.sleep(0.2)
        
        # 更新UI并显示总结
        self.update_bind_log(log_lines, success, fail, fail_codes, len(coupon_codes))

    def update_bind_log(self, log_lines, success, fail, fail_codes, total):
        """更新绑定日志显示"""
        log_lines.append(f"\n=== 绑定完成 ===")
        log_lines.append(f"共{total}张券，绑定成功{success}，失败{fail}")
        if fail_codes:
            log_lines.append(f"失败券号：{', '.join(fail_codes)}")
        
        # 如果全部失败且都是TOKEN_INVALID，给出建议
        if fail == total and all('TOKEN_INVALID' in line for line in log_lines if '绑定失败' in line):
            log_lines.append(f"\n*** 建议 ***")
            log_lines.append(f"所有券都显示TOKEN_INVALID错误")
            log_lines.append(f"请尝试：")
            log_lines.append(f"1. 重新登录当前账号")
            log_lines.append(f"2. 检查账号是否在对应影院有效")
            log_lines.append(f"3. 确认券号格式是否正确")
        
        self.bind_log_text.setPlainText("\n".join(log_lines))
        
        # 不显示完成提示弹窗，只在日志中记录
        print(f"[券绑定] 绑定完成：成功{success}张券，失败{fail}张券")

    def copy_bind_log(self):
        """复制绑定日志"""
        log = self.bind_log_text.toPlainText().strip()
        if log:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(log)
            # 不显示复制成功弹窗，只在控制台记录
            print(f"[券绑定] 日志内容已复制到剪贴板")
        else:
            # 不显示错误弹窗，只在控制台记录
            print(f"[券绑定] 没有日志内容可复制")

    def update_bind_account_info(self):
        """更新券绑定界面的账号信息显示"""
        account = getattr(self, 'current_account', None)
        if hasattr(self, 'bind_account_info'):
            if account:
                # 获取影院名称
                cinema_name = "未知影院"
                try:
                    from services.cinema_manager import cinema_manager
                    cinemas = cinema_manager.load_cinema_list()
                    for cinema in cinemas:
                        if cinema.get('cinemaid') == account.get('cinemaid'):
                            cinema_name = cinema.get('cinemaShortName', '未知影院')
                            break
                except:
                    pass

                # 适配沃美简化账号格式
                phone = account.get('phone', '未知账号')
                info_text = f"当前账号：{phone}\n影院：{cinema_name}"
                self.bind_account_info.setText(info_text)
                self.bind_account_info.setStyleSheet("QLabel { color: blue; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
            else:
                self.bind_account_info.setText("请先选择账号和影院")
                self.bind_account_info.setStyleSheet("QLabel { color: red; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")

    def update_exchange_account_info(self):
        """🔧 更新兑换券界面的账号信息显示"""
        account = getattr(self, 'current_account', None)
        if hasattr(self, 'exchange_account_info'):
            if account:
                # 获取影院名称
                cinema_name = "未知影院"
                try:
                    from services.cinema_manager import cinema_manager
                    cinemas = cinema_manager.load_cinema_list()
                    for cinema in cinemas:
                        if cinema.get('cinemaid') == account.get('cinemaid'):
                            cinema_name = cinema.get('cinemaShortName', '未知影院')
                            break
                except:
                    pass

                # 适配沃美简化账号格式
                phone = account.get('phone', '未知账号')
                info_text = f"当前账号：{phone}\n影院：{cinema_name}"
                self.exchange_account_info.setText(info_text)
                self.exchange_account_info.setStyleSheet("QLabel { color: blue; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
            else:
                self.exchange_account_info.setText("请先选择账号和影院")
                self.exchange_account_info.setStyleSheet("QLabel { color: red; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
        else:
            # 如果兑换券界面没有账号信息显示组件，则跳过更新
            print(f"[Tab管理器] 兑换券界面无账号信息显示组件，跳过更新")

    def _build_exchange_coupon_tab(self):
        """构建兑换券Tab页面 - 基于第二部分文档完整实现"""
        layout = QVBoxLayout(self.exchange_coupon_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 控制按钮区 - 刷新按钮和统计信息
        control_frame = QWidget()
        control_layout = QHBoxLayout(control_frame)

        refresh_btn = ClassicButton("刷新券列表", "default")
        refresh_btn.clicked.connect(self.refresh_coupon_exchange_list)
        control_layout.addWidget(refresh_btn)

        # 券统计信息显示 - 初始为空白
        self.coupon_stats_label = ClassicLabel("")
        self.coupon_stats_label.setStyleSheet("color: #666; font-size: 12px; margin-left: 10px;")
        control_layout.addWidget(self.coupon_stats_label)

        control_layout.addStretch()
        layout.addWidget(control_frame)
        
        # 可兑换券列表表格 - 显示券名称、券码和有效期
        self.exchange_coupon_table = ClassicTableWidget()
        self.exchange_coupon_table.setColumnCount(3)
        self.exchange_coupon_table.setHorizontalHeaderLabels(["券名称", "券码", "有效期"])

        # 设置列宽
        header = self.exchange_coupon_table.horizontalHeader()
        header.resizeSection(0, 150)  # 券名称
        header.resizeSection(1, 120)  # 券码
        header.resizeSection(2, 100)  # 有效期

        layout.addWidget(self.exchange_coupon_table)
        
        # 初始化数据
        self.exchange_coupon_data = []

    def refresh_coupon_exchange_list(self):
        """刷新可兑换券列表 - 基于真实API实现"""
        # 🔍 步骤1：参数校验
        account = getattr(self, 'current_account', None)
        if not account:
            MessageManager.show_error(self, "未选择账号", "请先选择账号！", auto_close=False)
            return
        
        cinemaid = self.get_selected_cinemaid()
        if not cinemaid:
            MessageManager.show_error(self, "未选择影院", "请先选择影院！", auto_close=False)
            return
        
        # 检查账号必要字段
        required_fields = ['userid', 'token', 'openid', 'cinemaid']
        for field in required_fields:
            if not account.get(field):
                MessageManager.show_error(self, "账号信息不完整", f"账号缺少{field}字段，请重新登录！", auto_close=False)
                return
        
        print(f"[券列表刷新] 开始获取券列表")
        print(f"[券列表刷新] 账号: {account.get('userid')} @ 影院: {cinemaid}")
        
        # 防止重复请求
        if getattr(self, '_coupon_refreshing', False):
            print(f"[券列表] 正在刷新中，跳过重复请求")
            return
        
        self._coupon_refreshing = True
        
        try:
            # 🎨 步骤2：UI状态更新
            refresh_btn = self.sender()  # 获取触发的按钮
            if refresh_btn:
                refresh_btn.setText("刷新中...")
                refresh_btn.setEnabled(False)
            
            # 表格显示加载状态
            self.exchange_coupon_table.setRowCount(1)
            loading_item = self.exchange_coupon_table.__class__.createItem("正在获取券列表，请稍候...")
            loading_item.setBackground(QColor('#e3f2fd'))
            self.exchange_coupon_table.setItem(0, 0, loading_item)
            self.exchange_coupon_table.setSpan(0, 0, 1, 5)  # 合并所有列
            
            # 强制UI更新
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
            
            # 🌐 步骤3：调用真实API接口
            try:
                from services.order_api import get_coupon_list
                
                # 构建API请求参数（与现有API完全对接）
                params = {
                    'voucherType': 0,        # 券类型：0=全部
                    'pageNo': 1,             # 页码
                    'groupid': '',           # 集团ID（通常为空）
                    'cinemaid': cinemaid,    # 影院ID
                    'cardno': account.get('cardno', ''),  # 会员卡号
                    'userid': account['userid'],          # 用户ID（手机号）
                    'openid': account['openid'],          # 微信openid
                    'CVersion': '3.9.12',    # 客户端版本
                    'OS': 'Windows',         # 操作系统
                    'token': account['token'],            # 访问令牌
                    'source': '2'           # 来源：2=小程序
                }
                
                print(f"[券列表API] 请求参数: {params}")
                
                # 调用API（这是关键步骤）
                coupon_result = get_coupon_list(params)
                
                print(f"[券列表API] 响应结果: {coupon_result}")
                
                # 🔄 步骤4：处理API响应
                if coupon_result and coupon_result.get('resultCode') == '0':
                    # 成功获取券列表
                    result_data = coupon_result.get('resultData', {})

                    # 🔧 修复：检查result_data是否为None
                    if result_data is None:
                        print("[券列表API] resultData为None，使用空列表")
                        vouchers = []
                    elif not isinstance(result_data, dict):
                        print(f"[券列表API] resultData类型错误: {type(result_data)}，使用空列表")
                        vouchers = []
                    else:
                        vouchers = result_data.get('vouchers', [])
                    
                    print(f"[券列表解析] 获取到 {len(vouchers)} 张券")
                    
                    # 数据验证和清洗
                    valid_vouchers = []
                    for voucher in vouchers:
                        if self.validate_voucher_data(voucher):
                            valid_vouchers.append(voucher)
                        else:
                            print(f"[券列表解析] 跳过无效券数据: {voucher}")
                    
                    # 更新券列表显示
                    self.update_coupon_table(valid_vouchers)
                    
                    # 更新状态信息
                    status_text = f"获取成功：共{len(valid_vouchers)}张券"
                    if len(vouchers) != len(valid_vouchers):
                        status_text += f"（已过滤{len(vouchers) - len(valid_vouchers)}张无效券）"
                    
                    # 更新账号兑换记录
                    self.add_exchange_record_info(f"刷新券列表成功 - {status_text}")
                    
                else:
                    # API调用失败的处理
                    error_msg = coupon_result.get('resultDesc', '未知错误') if coupon_result else '网络连接失败'
                    print(f"[券列表API] 失败: {error_msg}")
                    
                    # 显示错误信息
                    self.show_coupon_error(error_msg)
                    status_text = f"获取失败：{error_msg}"
                    
                    # 记录错误
                    self.add_exchange_record_info(f"刷新券列表失败 - {error_msg}")
                    
            except Exception as api_error:
                error_msg = f"API调用异常：{str(api_error)}"
                print(f"[券列表API] 异常: {api_error}")
                self.show_coupon_error(error_msg)
                status_text = error_msg
                self.add_exchange_record_info(f"刷新券列表异常 - {error_msg}")
            
            # 恢复UI状态
            self.restore_coupon_ui_state(status_text)
            
        finally:
            self._coupon_refreshing = False

    def validate_voucher_data(self, voucher):
        """验证券数据的完整性"""
        if not isinstance(voucher, dict):
            return False
        
        # 必要字段检查
        required_fields = ['couponname', 'couponcode']
        for field in required_fields:
            if not voucher.get(field):
                print(f"[券数据验证] 缺少必要字段: {field}")
                return False
        
        # 有效期检查（如果有的话）
        if 'expireddate' in voucher:
            expire_date = voucher.get('expireddate', '')
            try:
                from datetime import datetime
                expire_datetime = datetime.strptime(expire_date, '%Y-%m-%d')
                current_datetime = datetime.now()
                
                # 标记过期状态
                voucher['is_expired'] = expire_datetime < current_datetime
            except ValueError:
                print(f"[券数据验证] 无效的有效期格式: {expire_date}")
                voucher['is_expired'] = True
        else:
            voucher['is_expired'] = False
        
        # 设置默认状态
        if 'status' not in voucher:
            voucher['status'] = 'available'
        
        # 设置默认面值
        if 'faceValue' not in voucher:
            voucher['faceValue'] = 0.0
        
        return True

    def show_coupon_error(self, error_msg):
        """显示券列表获取错误"""
        self.exchange_coupon_table.setRowCount(1)
        self.exchange_coupon_table.clearSpans()

        # 根据错误类型显示不同的提示
        if 'TOKEN_INVALID' in error_msg or 'token' in error_msg.lower():
            display_msg = "登录状态已失效，请重新登录账号"
            suggestion = "建议：点击账号列表中的'重新登录'按钮"
        elif 'NETWORK' in error_msg or '网络' in error_msg:
            display_msg = "网络连接失败，请检查网络"
            suggestion = "建议：检查网络连接后重试"
        elif 'PERMISSION' in error_msg or '权限' in error_msg:
            display_msg = "账号权限不足或影院不匹配"
            suggestion = "建议：确认账号是否属于当前影院"
        else:
            display_msg = f"获取失败：{error_msg}"
            suggestion = ""

        error_item = self.exchange_coupon_table.__class__.createItem(display_msg)
        error_item.setBackground(QColor('#f8d7da'))  # 红色背景
        self.exchange_coupon_table.setItem(0, 0, error_item)
        self.exchange_coupon_table.setSpan(0, 0, 1, 3)  # 合并3列

        if suggestion:
            self.exchange_coupon_table.setRowCount(2)
            suggestion_item = self.exchange_coupon_table.__class__.createItem(suggestion)
            suggestion_item.setBackground(QColor('#fff3cd'))  # 黄色背景
            self.exchange_coupon_table.setItem(1, 0, suggestion_item)
            self.exchange_coupon_table.setSpan(1, 0, 1, 3)  # 合并3列

        # 更新统计信息为错误状态
        self.coupon_stats_label.setText("券信息：获取失败")
        self.coupon_stats_label.setStyleSheet("color: #d32f2f; font-size: 12px; margin-left: 10px; font-weight: bold;")

    def add_exchange_record_info(self, message):
        """添加兑换记录信息 - 简化版本，只打印日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[券列表记录] {timestamp} - {message}")

    def restore_coupon_ui_state(self, status_text=""):
        """恢复UI状态"""
        # 查找刷新按钮并恢复状态
        for child in self.exchange_coupon_tab.findChildren(ClassicButton):
            if child.text() in ["刷新中...", "刷新券列表"]:
                child.setText("刷新券列表")
                child.setEnabled(True)
                break
        
        # 清除表格合并
        self.exchange_coupon_table.clearSpans()
        
        print(f"[券列表刷新] 完成 - {status_text}")

    def update_coupon_table(self, vouchers):
        """更新券列表表格显示 - 只显示没过期没使用的券"""
        # 清空加载状态
        self.exchange_coupon_table.setRowCount(0)
        self.exchange_coupon_table.clearSpans()

        # 过滤券：只显示没过期没使用的券
        valid_vouchers = []
        for voucher in vouchers:
            # 检查是否过期 - 使用多个字段判断
            is_expired = (
                voucher.get('is_expired', False) or
                voucher.get('expired', '0') == '1' or
                voucher.get('leftDays', 0) < 0
            )

            # 检查是否已使用 - 使用真实API字段
            is_redeemed = voucher.get('redeemed', '0') == '1'
            is_used = voucher.get('status') in ['used', 'consumed', 'redeemed'] if voucher.get('status') else False

            # 只保留未过期且未使用的券
            if not is_expired and not is_redeemed and not is_used:
                valid_vouchers.append(voucher)

        if not valid_vouchers:
            # 无可用券的情况
            self.exchange_coupon_table.setRowCount(1)
            no_coupon_item = self.exchange_coupon_table.__class__.createItem("暂无可用优惠券")
            no_coupon_item.setBackground(QColor('#f8f9fa'))
            self.exchange_coupon_table.setItem(0, 0, no_coupon_item)
            self.exchange_coupon_table.setSpan(0, 0, 1, 3)  # 合并3列

            # 更新统计信息
            self.update_coupon_stats(len(vouchers), 0)
            return

        # 按有效期排序（即将过期的在前）
        valid_vouchers.sort(key=lambda v: v.get('expireddate', '9999-12-31'))

        # 设置表格行数
        self.exchange_coupon_table.setRowCount(len(valid_vouchers))

        # 填充券数据 - 显示券名称、券码和有效期
        for row, voucher in enumerate(valid_vouchers):
            # 券名称
            name = voucher.get('couponname', '未知券')
            name_item = self.exchange_coupon_table.__class__.createItem(name)
            self.exchange_coupon_table.setItem(row, 0, name_item)

            # 券码
            code = voucher.get('couponcode', '无券码')
            code_item = self.exchange_coupon_table.__class__.createItem(code)
            self.exchange_coupon_table.setItem(row, 1, code_item)

            # 有效期
            expire_date = voucher.get('expireddate', '未知')
            expire_item = self.exchange_coupon_table.__class__.createItem(expire_date)

            # 根据剩余天数设置颜色
            left_days = voucher.get('leftDays', 0)
            if left_days <= 3:
                expire_item.setBackground(QColor('#f8d7da'))  # 红色背景 - 即将过期
            elif left_days <= 7:
                expire_item.setBackground(QColor('#fff3cd'))  # 黄色背景 - 快过期
            else:
                expire_item.setBackground(QColor('#d4edda'))  # 绿色背景 - 正常

            self.exchange_coupon_table.setItem(row, 2, expire_item)

        # 保存券数据到缓存
        self.exchange_coupon_data = valid_vouchers

        # 更新统计信息
        self.update_coupon_stats(len(vouchers), len(valid_vouchers))

        print(f"[券列表UI] 表格更新完成，显示 {len(valid_vouchers)} 张可用券（已过滤 {len(vouchers) - len(valid_vouchers)} 张不可用券）")

    def update_coupon_stats(self, total_count, valid_count):
        """更新券统计信息显示"""
        try:
            filtered_count = total_count - valid_count

            # 构建统计信息文本
            stats_parts = []

            # 总数信息
            stats_parts.append(f"总计: {total_count}张")

            # 可用数信息
            if valid_count > 0:
                stats_parts.append(f"可用: {valid_count}张")

            # 过滤数信息
            if filtered_count > 0:
                stats_parts.append(f"已过滤: {filtered_count}张")

            # 组合显示文本
            if total_count == 0:
                stats_text = "券信息：暂无券数据"
            elif valid_count == 0:
                stats_text = f"券信息：{stats_parts[0]}，全部不可用"
            else:
                stats_text = f"券信息：{' | '.join(stats_parts)}"

            # 更新显示
            self.coupon_stats_label.setText(stats_text)

            # 根据可用券数量设置颜色
            if valid_count == 0:
                color = "#d32f2f"  # 红色 - 无可用券
            elif valid_count <= 3:
                color = "#f57c00"  # 橙色 - 券较少
            else:
                color = "#388e3c"  # 绿色 - 券充足

            self.coupon_stats_label.setStyleSheet(f"color: {color}; font-size: 12px; margin-left: 10px; font-weight: bold;")

            print(f"[券统计] 更新统计信息: {stats_text}")

        except Exception as e:
            print(f"[券统计] 更新统计信息失败: {e}")
            self.coupon_stats_label.setText("券信息：统计失败")

    def reset_coupon_lists(self):
        """重置所有券列表为空白状态"""
        try:
            # 重置可用券列表
            if hasattr(self, 'coupon_list'):
                self.coupon_list.clear()
                print(f"[券列表重置] 可用券列表已清空")

            # 重置兑换券表格
            if hasattr(self, 'exchange_coupon_table'):
                self.exchange_coupon_table.setRowCount(0)
                self.exchange_coupon_table.clearSpans()
                print(f"[券列表重置] 兑换券表格已清空")

            # 重置券统计信息
            if hasattr(self, 'coupon_stats_label'):
                self.coupon_stats_label.setText("")
                print(f"[券列表重置] 券统计信息已清空")

            # 清空券数据缓存
            self.exchange_coupon_data = []

            print(f"[券列表重置] 所有券列表已重置为空白状态")

        except Exception as e:
            print(f"[券列表重置] 重置失败: {e}")

    def filter_exchange_coupons(self):
        """筛选兑换券 - 已简化，不再需要筛选功能"""
        pass

    def _build_order_tab(self):
        """构建订单Tab页面"""
        layout = QVBoxLayout(self.order_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        self.order_refresh_btn = ClassicButton("刷新", "default")
        self.order_refresh_btn.setMaximumWidth(80)
        button_layout.addWidget(self.order_refresh_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 订单表格
        self.order_table = ClassicTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["影片", "影院", "状态", "订单号"])

        # 🔧 修复：设置表格为只读模式，防止双击编辑
        from PyQt5.QtWidgets import QAbstractItemView
        self.order_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 设置选择模式为整行选择
        self.order_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 设置列宽
        header = self.order_table.horizontalHeader()
        header.resizeSection(0, 150)  # 影片
        header.resizeSection(1, 180)  # 影院
        header.resizeSection(2, 150)  # 状态

        # 设置行高
        self.order_table.verticalHeader().setDefaultSectionSize(36)

        # 设置右键菜单
        self.order_table.setContextMenuPolicy(Qt.CustomContextMenu)
        
        layout.addWidget(self.order_table)

        # 不加载示例数据，等待用户手动刷新

    def _on_add_cinema(self):
        """添加影院功能 - 🆕 简化输入，自动获取影院名称"""
        # 创建添加影院对话框
        add_dialog = QDialog(self)
        add_dialog.setWindowTitle("添加影院")
        add_dialog.setFixedSize(450, 350)

        # 对话框布局
        layout = QVBoxLayout(add_dialog)

        # 🆕 添加说明文字
        info_label = ClassicLabel("请输入API域名和影院ID，系统将自动获取影院名称")
        info_label.setStyleSheet("color: #666; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(info_label)

        # 域名输入
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(ClassicLabel("API域名:"))
        domain_input = ClassicLineEdit()
        domain_input.setPlaceholderText("例如：www.heibaiyingye.cn")
        domain_layout.addWidget(domain_input)
        layout.addLayout(domain_layout)

        # 影院ID输入
        id_layout = QHBoxLayout()
        id_layout.addWidget(ClassicLabel("影院ID:"))
        id_input = ClassicLineEdit()
        id_input.setPlaceholderText("例如：35fec8259e74")
        id_layout.addWidget(id_input)
        layout.addLayout(id_layout)

        # 🆕 验证结果显示区域
        result_layout = QVBoxLayout()
        result_label = ClassicLabel("验证结果:")
        result_text = ClassicLabel("请输入域名和影院ID后点击验证")
        result_text.setStyleSheet("color: #666; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #f9f9f9;")
        result_layout.addWidget(result_label)
        result_layout.addWidget(result_text)
        layout.addLayout(result_layout)

        # 按钮
        button_layout = QHBoxLayout()
        validate_btn = ClassicButton("验证并添加", "primary")
        cancel_btn = ClassicButton("取消", "default")
        button_layout.addWidget(validate_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        # 🆕 事件绑定 - 验证并添加
        def validate_and_add():
            domain = domain_input.text().strip()
            cinema_id = id_input.text().strip()

            # 验证输入
            if not all([domain, cinema_id]):
                QMessageBox.warning(add_dialog, "输入错误", "请填写API域名和影院ID！")
                return

            # 标准化域名格式
            if domain.startswith(('http://', 'https://')):
                # 移除协议前缀，只保留域名
                domain = domain.replace('https://', '').replace('http://', '')

            # 验证影院ID格式
            if len(cinema_id) != 12:
                QMessageBox.warning(add_dialog, "格式错误", "影院ID必须是12位字符！")
                return

            # 🆕 调用新的验证和添加方法
            success = self.validate_and_add_cinema(domain, cinema_id, result_text, add_dialog)
            if success:
                add_dialog.accept()

        validate_btn.clicked.connect(validate_and_add)
        cancel_btn.clicked.connect(add_dialog.reject)

        add_dialog.exec_()

    def validate_and_add_cinema(self, domain: str, cinema_id: str, result_text, dialog):
        """🆕 验证API并自动获取影院名称，然后添加影院"""
        try:
            result_text.setText("🔄 正在验证API和获取影院信息...")
            result_text.setStyleSheet("color: #2196f3; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #f0f8ff;")

            # 强制刷新界面
            dialog.repaint()

            # 🆕 调用影院信息API获取影院名称
            from services.cinema_info_api import get_cinema_info, format_cinema_data

            print(f"[添加影院] 开始验证影院: 域名={domain}, ID={cinema_id}")

            # 调用API获取影院信息
            cinema_info = get_cinema_info(domain, cinema_id)

            if not cinema_info:
                result_text.setText("❌ API验证失败：无法获取影院信息\n请检查域名和影院ID是否正确")
                result_text.setStyleSheet("color: #f44336; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #ffebee;")
                return False

            # 🆕 从API响应中提取影院名称
            cinema_name = cinema_info.get('cinemaShortName', '')
            if not cinema_name:
                result_text.setText("❌ 获取影院名称失败：API响应中缺少影院名称\n请确认影院ID是否正确")
                result_text.setStyleSheet("color: #f44336; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #ffebee;")
                return False

            # 🆕 显示验证成功信息
            success_text = f"✅ 验证成功！\n影院名称: {cinema_name}\n城市: {cinema_info.get('cityName', '未知')}\n地址: {cinema_info.get('cinemaAddress', '未知')}"
            result_text.setText(success_text)
            result_text.setStyleSheet("color: #4caf50; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #f1f8e9;")

            print(f"[添加影院] ✅ 验证成功: {cinema_name}")

            # 🆕 检查影院是否已存在
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()

            for cinema in cinemas:
                if cinema.get('cinemaid') == cinema_id:
                    result_text.setText(f"❌ 添加失败：影院ID {cinema_id} 已存在\n影院名称: {cinema.get('cinemaShortName', '未知')}")
                    result_text.setStyleSheet("color: #ff9800; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #fff3e0;")
                    return False

            # 🆕 使用标准的数据格式化方法
            cinema_data = format_cinema_data(cinema_info, domain, cinema_id)

            # 添加到影院列表
            cinemas.append(cinema_data)

            # 保存到文件
            if cinema_manager.save_cinema_list(cinemas):
                # 🆕 刷新界面
                self._refresh_cinema_table_display()
                self._update_cinema_stats()

                # 🆕 刷新出票Tab的影院列表
                self._refresh_ticket_tab_cinema_list()

                result_text.setText(f"🎉 添加成功！\n影院名称: {cinema_name}\n已添加到系统中")
                result_text.setStyleSheet("color: #4caf50; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #f1f8e9;")

                print(f"[添加影院] ✅ 影院添加成功: {cinema_name}")

                QMessageBox.information(dialog, "添加成功", f"影院 {cinema_name} 已成功添加！")
                return True
            else:
                result_text.setText("❌ 保存失败：无法保存影院数据到文件")
                result_text.setStyleSheet("color: #f44336; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #ffebee;")
                return False

        except Exception as e:
            error_msg = f"❌ 验证过程出错：{str(e)}"
            result_text.setText(error_msg)
            result_text.setStyleSheet("color: #f44336; padding: 10px; border: 1px solid #ddd; border-radius: 4px; background: #ffebee;")
            print(f"[添加影院] 验证错误: {e}")
            return False

    def _refresh_ticket_tab_cinema_list(self):
        """刷新出票Tab的影院列表"""
        try:
            print(f"[Tab管理器] 🔄 刷新出票Tab影院列表")

            # 重新加载影院数据
            self._load_sample_data()

            # 发送全局事件通知主窗口刷新
            from utils.signals import event_bus
            from services.cinema_manager import cinema_manager

            # 获取最新的影院列表并发送事件
            updated_cinemas = cinema_manager.load_cinema_list()
            event_bus.cinema_list_updated.emit(updated_cinemas)

            print(f"[Tab管理器] ✅ 出票Tab影院列表刷新完成")

        except Exception as e:
            print(f"[Tab管理器] 刷新出票Tab影院列表错误: {e}")

    def add_cinema_to_list(self, name, domain, cinema_id):
        """添加影院到数据文件 - 基于现有cinema_manager"""
        try:
            # 使用现有的cinema_manager
            from services.cinema_manager import cinema_manager
            from datetime import datetime
            
            # 新影院数据
            new_cinema = {
                "cinemaShortName": name,
                "domain": domain,
                "cinemaid": cinema_id,
                "status": "active",
                "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 加载现有影院列表
            cinemas = cinema_manager.load_cinema_list()
            
            # 检查是否已存在
            for cinema in cinemas:
                if cinema.get('cinemaid') == cinema_id:
                    QMessageBox.warning(self, "添加失败", f"影院ID {cinema_id} 已存在！")
                    return False
            
            # 添加新影院
            cinemas.append(new_cinema)
            
            # 保存到文件
            cinema_manager.save_cinema_list(cinemas)
            
            # 立即刷新界面显示
            self._refresh_cinema_table_display()
            
            # 更新统计信息
            self._update_cinema_stats()
            
            QMessageBox.information(self, "添加成功", f"影院 {name} 已成功添加！")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "添加失败", f"添加影院时发生错误：{str(e)}")
            return False
    
    def _on_delete_cinema(self):
        """删除选中的影院 - 基于现有逻辑"""
        # 获取选中的影院
        selected_items = self.cinema_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "未选择影院", "请先选择要删除的影院！")
            return
        
        # 获取选中行的影院ID
        row = self.cinema_table.currentRow()
        if row < 0:
            return
            
        cinema_id_item = self.cinema_table.item(row, 1)  # 影院ID在第1列
        cinema_name_item = self.cinema_table.item(row, 0)  # 影院名称在第0列
        
        if not cinema_id_item or not cinema_name_item:
            return
            
        cinema_id = cinema_id_item.text()
        cinema_name = cinema_name_item.text()
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除影院 {cinema_name} ({cinema_id}) 吗？\n\n注意：删除后该影院的所有账号也将失效！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.delete_cinema_from_list(cinema_id, cinema_name)

    def delete_cinema_from_list(self, cinema_id, cinema_name):
        """从数据文件中删除影院"""
        try:
            from services.cinema_manager import cinema_manager
            
            # 加载影院列表
            cinemas = cinema_manager.load_cinema_list()
            
            # 查找并删除影院
            original_count = len(cinemas)
            cinemas = [c for c in cinemas if c.get('cinemaid') != cinema_id]
            
            if len(cinemas) == original_count:
                QMessageBox.warning(self, "删除失败", f"未找到影院ID {cinema_id}！")
                return False
            
            # 保存更新后的列表
            cinema_manager.save_cinema_list(cinemas)
            
            # 同时清理该影院的账号数据
            self.cleanup_cinema_accounts(cinema_id)
            
            # 立即刷新界面 - 修复显示问题
            self._refresh_cinema_table_display()

            # 更新统计信息
            self._update_cinema_stats()

            # 🆕 刷新出票Tab的影院列表
            self._refresh_ticket_tab_cinema_list()

            QMessageBox.information(self, "删除成功", f"影院 {cinema_name} 已删除！")
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "删除失败", f"删除影院时发生错误：{str(e)}")
            return False

    def cleanup_cinema_accounts(self, cinema_id):
        """清理删除影院的相关账号"""
        try:
            import json
            import os
            
            accounts_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'accounts.json')
            
            if os.path.exists(accounts_file):
                with open(accounts_file, "r", encoding="utf-8") as f:
                    accounts = json.load(f)
                
                # 过滤掉该影院的账号
                filtered_accounts = [acc for acc in accounts if acc.get('cinemaid') != cinema_id]
                
                with open(accounts_file, "w", encoding="utf-8") as f:
                    json.dump(filtered_accounts, f, ensure_ascii=False, indent=2)
                    
                print(f"[Tab管理器] 已清理影院 {cinema_id} 的相关账号")
                
        except Exception as e:
            print(f"[Tab管理器] 清理账号数据时出错: {e}")
    
    def _refresh_cinema_table_display(self):
        """刷新影院表格显示"""
        try:
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()
            
            # 清空表格
            self.cinema_table.setRowCount(0)
            
            # 重新填充数据
            for i, cinema in enumerate(cinemas):
                self.cinema_table.insertRow(i)
                
                # 影院名称
                name_item = self.cinema_table.__class__.createItem(cinema.get('cinemaShortName', '未知影院'))
                self.cinema_table.setItem(i, 0, name_item)
                
                # 影院ID
                id_item = self.cinema_table.__class__.createItem(cinema.get('cinemaid', ''))
                self.cinema_table.setItem(i, 1, id_item)
                
                # 操作
                operation_item = self.cinema_table.__class__.createItem("详情")
                self.cinema_table.setItem(i, 2, operation_item)
            
            print(f"[Tab管理器] 影院表格已刷新，当前显示 {len(cinemas)} 个影院")
            
        except Exception as e:
            print(f"[Tab管理器] 刷新影院表格错误: {e}")

    def _update_cinema_stats(self):
        """更新影院统计信息"""
        try:
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()
            
            total_count = len(cinemas)
            active_count = sum(1 for c in cinemas if c.get('status', 'active') == 'active')
            
            stats_text = f"总影院数: {total_count} | 活跃影院: {active_count} | 最后更新: {time.strftime('%Y-%m-%d %H:%M:%S')}"
            self.cinema_stats_label.setText(stats_text)
            
        except Exception as e:
            self.cinema_stats_label.setText(f"统计信息获取失败: {str(e)}")
    
    def _load_sample_data(self):
        """初始化下拉框状态（完全移除本地数据依赖）"""
        try:
            print("[Tab管理器] 🚫 已移除本地影院文件依赖")
            print("[Tab管理器] 🔄 沃美系统：所有数据通过API动态获取")

            # 清理并初始化所有下拉框为默认状态
            self._reset_all_combos_to_default()

            # 沃美系统使用六级联动，城市数据在_init_cascade中通过API加载
            print("[Tab管理器] 下拉框初始化完成，准备通过API加载城市数据")

        except Exception as e:
            print(f"[Tab管理器] 初始化下拉框错误: {e}")
            # 确保下拉框至少有默认状态
            self._reset_all_combos_to_default()

    def _reset_all_combos_to_default(self):
        """重置所有下拉框到默认状态（不重置城市下拉框）"""
        try:
            # 🔧 不重置城市下拉框，因为城市数据是通过API加载的
            # 城市下拉框由_init_cascade方法管理，不在这里重置

            # 影院下拉框
            if hasattr(self, 'cinema_combo'):
                self.cinema_combo.clear()
                self.cinema_combo.addItem("请先选择城市")
                self.cinema_combo.setEnabled(False)

            # 电影下拉框
            if hasattr(self, 'movie_combo'):
                self.movie_combo.clear()
                self.movie_combo.addItem("请先选择影院")
                self.movie_combo.setEnabled(False)

            # 日期下拉框
            if hasattr(self, 'date_combo'):
                self.date_combo.clear()
                self.date_combo.addItem("请先选择影片")
                self.date_combo.setEnabled(False)

            # 场次下拉框
            if hasattr(self, 'session_combo'):
                self.session_combo.clear()
                self.session_combo.addItem("请先选择日期")
                self.session_combo.setEnabled(False)

            print("[Tab管理器] 所有下拉框已重置为默认状态（保留城市数据）")

        except Exception as e:
            print(f"[Tab管理器] 重置下拉框错误: {e}")
    

    
    def _load_sample_cinemas(self):
        """加载示例影院数据"""
        try:
            sample_cinemas = [
                {
                    "name": "华夏优加金太都会",
                    "id": "35fec8259e74",
                    "address": "高新大都会负一层"
                },
                {
                    "name": "深影国际影城(佐伦虹湾购物中心店)",
                    "id": "11b7e4bcc265", 
                    "address": "福田区北环大道6098号佐伦虹湾购物中心"
                },
                {
                    "name": "深圳万友影城BCMall店",
                    "id": "0f1e21d86ac8",
                    "address": "罗湖区布心路3008号BCMALl4楼"
                }
            ]
            
            self.cinema_table.setRowCount(len(sample_cinemas))
            for i, cinema in enumerate(sample_cinemas):
                self.cinema_table.setItem(i, 0, self.cinema_table.__class__.createItem(cinema["name"]))
                self.cinema_table.setItem(i, 1, self.cinema_table.__class__.createItem(cinema["id"]))
                self.cinema_table.setItem(i, 2, self.cinema_table.__class__.createItem(cinema["address"]))
                
        except Exception as e:
            print(f"[Tab管理器] 加载影院错误: {e}")
    
    def update_cinema_list(self, cinemas: List[Dict]):
        """更新影院列表"""
        try:
            self.cinemas_data = cinemas
            
            # 更新下拉框
            self.cinema_combo.clear()
            for cinema in cinemas:
                name = cinema.get("cinemaShortName", cinema.get("name", ""))
                if name:
                    self.cinema_combo.addItem(name)
            
        except Exception as e:
            print(f"[Tab管理器] 更新影院列表错误: {e}")


    
    def _load_cinema_list(self):
        """加载影院列表"""
        try:
            # 使用新的刷新显示方法
            self._refresh_cinema_table_display()
            
            # 初始化统计信息
            self._update_cinema_stats()
            
            # 同时加载影片列表
            self._load_movie_list()
            
        except Exception as e:
            print(f"[Tab管理器] 加载影院列表错误: {e}")
            # 加载示例数据作为后备
            self._load_sample_cinemas()

    def _load_movie_list(self):
        """加载影片列表到座位图区域"""
        try:
            if hasattr(self, 'movie_combo'):
                self.movie_combo.clear()
                self.movie_combo.addItem("请选择影片")
                
                # 添加示例影片
                movies = [
                    "阿凡达：水之道",
                    "流浪地球2", 
                    "满江红",
                    "熊出没·伴我熊心",
                    "深海"
                ]
                
                for movie in movies:
                    self.movie_combo.addItem(movie)
                    
        except Exception as e:
            print(f"[Tab管理器] 加载影片列表错误: {e}")
    
    def get_selected_cinemaid(self):
        """获取当前选择的影院ID"""
        try:
            # 🔧 修复：优先从当前影院数据获取
            if hasattr(self, 'current_cinema_data') and self.current_cinema_data:
                cinemaid = self.current_cinema_data.get('cinemaid')
                if cinemaid:
                    print(f"[Tab管理器] 从当前影院数据获取ID: {cinemaid}")
                    return cinemaid

            # 🔧 修复：从当前账号中获取影院ID
            if hasattr(self, 'current_account') and self.current_account:
                cinemaid = self.current_account.get('cinemaid')
                if cinemaid:
                    print(f"[Tab管理器] 从当前账号获取影院ID: {cinemaid}")
                    return cinemaid

            # 🔧 修复：从影院下拉框选择获取
            if hasattr(self, 'cinema_combo') and self.cinema_combo.currentText():
                cinema_name = self.cinema_combo.currentText()
                if hasattr(self, 'cinemas_data') and self.cinemas_data:
                    for cinema in self.cinemas_data:
                        if cinema.get('cinemaShortName') == cinema_name:
                            cinemaid = cinema.get('cinemaid')
                            print(f"[Tab管理器] 从下拉框选择获取影院ID: {cinemaid}")
                            return cinemaid

            # 如果没有当前账号，尝试从影院表格获取第一个影院ID
            if hasattr(self, 'cinema_table') and self.cinema_table.rowCount() > 0:
                id_item = self.cinema_table.item(0, 1)
                if id_item:
                    cinemaid = id_item.text()
                    print(f"[Tab管理器] 从影院表格获取ID: {cinemaid}")
                    return cinemaid

            # 默认返回一个测试影院ID
            print(f"[Tab管理器] 使用默认影院ID")
            return "11b7e4bcc265"

        except Exception as e:
            print(f"[Tab管理器] 获取影院ID错误: {e}")
            return "11b7e4bcc265"

    def _connect_signals(self):
        """连接信号槽"""
        try:
            # Tab切换信号 - 🆕 添加Tab切换监听
            if hasattr(self, 'tab_widget'):
                self.tab_widget.currentChanged.connect(self._on_tab_changed)

            # 🆕 六级联动信号连接（移除系统选择）
            if hasattr(self, 'city_combo'):
                self.city_combo.currentTextChanged.connect(self._on_city_changed)
            if hasattr(self, 'cinema_combo'):
                self.cinema_combo.currentTextChanged.connect(self._on_cinema_changed)
            if hasattr(self, 'movie_combo'):
                self.movie_combo.currentTextChanged.connect(self._on_movie_changed)
            if hasattr(self, 'date_combo'):
                self.date_combo.currentTextChanged.connect(self._on_date_changed)
            if hasattr(self, 'session_combo'):
                self.session_combo.currentTextChanged.connect(self._on_session_changed)
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.clicked.connect(self._on_submit_order)

            # 订单Tab信号
            if hasattr(self, 'order_refresh_btn'):
                self.order_refresh_btn.clicked.connect(self._on_refresh_orders)
            if hasattr(self, 'order_table'):
                self.order_table.customContextMenuRequested.connect(self._show_order_context_menu)
                self.order_table.itemDoubleClicked.connect(self._on_order_double_click)

            print("[Tab管理器] 信号连接完成")

        except Exception as e:
            print(f"[Tab管理器] 信号连接错误: {e}")

    def _on_tab_changed(self, index: int):
        """Tab切换处理 - 🆕 实现订单Tab自动刷新"""
        try:
            if not hasattr(self, 'tab_widget'):
                return

            # 获取当前Tab的文本
            tab_text = self.tab_widget.tabText(index)
            print(f"[Tab管理器] 🔄 Tab切换到: {tab_text} (索引: {index})")

            # 🎯 当切换到订单Tab时，自动触发刷新
            if tab_text == "订单":
                print(f"[Tab管理器] 🎯 检测到切换到订单Tab，准备自动刷新...")

                # 延迟100ms执行刷新，确保Tab切换完成
                QTimer.singleShot(100, self._auto_refresh_orders)

        except Exception as e:
            print(f"[Tab管理器] Tab切换处理错误: {e}")

    def _auto_refresh_orders(self):
        """自动刷新订单数据"""
        try:
            print(f"[Tab管理器] 🔄 开始自动刷新订单数据...")

            # 检查订单刷新按钮是否存在
            if hasattr(self, 'order_refresh_btn') and self.order_refresh_btn:
                print(f"[Tab管理器] ✅ 找到订单刷新按钮，模拟点击...")

                # 模拟点击刷新按钮
                self.order_refresh_btn.click()

                print(f"[Tab管理器] 🎉 订单自动刷新完成")
            else:
                print(f"[Tab管理器] ❌ 未找到订单刷新按钮")

        except Exception as e:
            print(f"[Tab管理器] 自动刷新订单错误: {e}")

    def _connect_global_events(self):
        """连接全局事件"""
        # 监听账号切换事件
        event_bus.account_changed.connect(self._on_account_changed)
    
    def _on_account_changed(self, account_data: dict):
        """账号切换处理（适配沃美简化账号格式）"""
        try:
            self.current_account = account_data

            # 沃美系统简化账号格式：只需要token和phone两个字段
            phone = account_data.get("phone", "未知账号")  # 使用phone作为用户标识
            token = account_data.get("token", "")

            # 更新各Tab页面的账号显示
            if hasattr(self, 'current_account_label'):
                account_info = f"当前账号: {phone}"  # 简化显示，不显示余额
                self.current_account_label.setText(account_info)

            # 更新绑券界面（如果需要）
            self.update_bind_account_info()

            # 更新兑换券界面（如果需要）
            self.update_exchange_account_info()

            # 沃美系统不需要积分信息
            self.current_points = 0

            print(f"[Tab管理器] 沃美账号切换: {phone}")
            print(f"[Tab管理器] Token: {token[:20]}...{token[-10:] if len(token) > 30 else token}")

        except Exception as e:
            print(f"[Tab管理器] 账号切换错误: {e}")
    
    def _on_cinema_changed(self, cinema_text: str):
        """影院选择变化处理 - 使用沃美电影服务加载电影数据"""
        try:
            if not cinema_text or cinema_text in ["加载中...", "请选择影院", "加载失败"]:
                return

            print(f"[Tab管理器] 影院切换: {cinema_text}")

            # 🆕 重置券列表
            self.reset_coupon_lists()

            # 🆕 禁用选座按钮 - 影院切换时
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)
                print(f"[Tab管理器] 影院切换，选座按钮已禁用")

            # 重置下级联动状态
            self._reset_cascade_from_level(3)  # 重置电影及以下级别

            # 查找选中的影院数据（确保使用沃美数据格式）
            selected_cinema = None
            if hasattr(self, 'cinemas_data') and self.cinemas_data:
                for cinema in self.cinemas_data:
                    # 沃美系统使用cinema_name字段
                    cinema_name = cinema.get('cinema_name', '')
                    if cinema_name == cinema_text:
                        selected_cinema = cinema
                        print(f"[Tab管理器] 找到沃美影院: {cinema_name} (ID: {cinema.get('cinema_id')})")
                        break

            if not selected_cinema:
                print(f"[Tab管理器] 未找到影院数据: {cinema_text}")
                self.movie_combo.clear()
                self.movie_combo.addItem("影院数据错误")
                return

            # 保存当前影院数据（确保使用沃美格式）
            self.current_cinema_data = selected_cinema
            cinema_id = selected_cinema.get('cinema_id')  # 沃美系统使用cinema_id
            cinema_name = selected_cinema.get('cinema_name')  # 沃美系统使用cinema_name
            print(f"[Tab管理器] 保存当前沃美影院数据: {cinema_name} (ID: {cinema_id})")

            # 发出影院选择信号
            self.cinema_selected.emit(cinema_text)

            # 发布全局影院选择事件
            from utils.signals import event_bus
            event_bus.cinema_selected.emit(selected_cinema)

            # 直接加载电影数据（沃美系统不需要账号验证）
            self._load_movies_for_cinema_womei(selected_cinema)
                
        except Exception as e:
            print(f"[Tab管理器] 影院选择错误: {e}")
            self._set_movie_combo_error("影院选择失败")

    def _load_movies_for_cinema_womei(self, cinema_data):
        """使用沃美电影服务为指定影院加载电影数据（增强调试功能）"""
        try:
            print(f"[电影调试] ==================== 开始加载影院电影列表 ====================")

            # 设置加载状态
            self.movie_combo.clear()
            self.movie_combo.addItem("加载电影中...")
            self.movie_combo.setEnabled(False)

            # 获取沃美影院ID和名称
            cinema_id = cinema_data.get('cinema_id')  # 沃美系统使用cinema_id
            cinema_name = cinema_data.get('cinema_name')  # 沃美系统使用cinema_name

            print(f"[电影调试] 影院信息:")
            print(f"  - 影院名称: {cinema_name}")
            print(f"  - 影院ID: {cinema_id}")

            if not cinema_id:
                print(f"[电影调试] ❌ 影院ID缺失: {cinema_data}")
                self._set_movie_combo_error("影院ID缺失")
                return

            # 获取沃美电影服务实例
            from services.womei_film_service import get_womei_film_service

            # 🔧 修正：使用统一的token获取方法
            token = self._get_current_token()
            print(f"[Tab管理器] 使用token: {token[:20]}...")

            film_service = get_womei_film_service(token)

            # 🔧 详细的电影API调用调试
            print(f"[电影调试] 调用电影API: get_movies(cinema_id={cinema_id})")
            movies_result = film_service.get_movies(cinema_id)

            # 🔧 详细的响应调试
            print(f"[电影调试] API响应结果:")
            print(f"  - success: {movies_result.get('success')}")
            print(f"  - total: {movies_result.get('total', 'N/A')}")
            print(f"  - error: {movies_result.get('error', 'N/A')}")

            if movies_result.get('success'):
                movies = movies_result.get('movies', [])
                print(f"[电影调试] ✅ 成功获取电影数据:")
                print(f"  - 电影数量: {len(movies)}")

                # 🔧 显示前3部电影的详细信息
                for i, movie in enumerate(movies[:3]):
                    movie_name = movie.get('name', '未知电影')
                    movie_id = movie.get('movie_id', 'N/A')  # 修复：沃美API使用movie_id字段
                    print(f"  - 电影 {i+1}: {movie_name} (ID: {movie_id})")

                if len(movies) > 3:
                    print(f"  - ... 还有 {len(movies) - 3} 部电影")

                if movies:
                    self._update_movie_combo_womei(movies)
                    print(f"[电影调试] ✅ 电影下拉框更新完成")

                    # 🔧 自动选择第一个电影
                    if len(movies) > 0:
                        first_movie = movies[0]
                        movie_name = first_movie.get('name', '未知电影')  # 修复字段名
                        print(f"[电影调试] 🎯 自动选择第一个电影: {movie_name}")

                        # 延迟选择，确保下拉框已更新
                        QTimer.singleShot(100, lambda: self._auto_select_first_movie(movie_name))
                else:
                    print(f"[电影调试] ❌ 该影院暂无电影")
                    self._set_movie_combo_error("该影院暂无电影")
            else:
                error = movies_result.get('error', '未知错误')
                print(f"[电影调试] ❌ 获取电影失败: {error}")
                self._set_movie_combo_error(f"获取电影失败: {error}")

        except Exception as e:
            print(f"[Tab管理器] 加载沃美电影数据错误: {e}")
            import traceback
            traceback.print_exc()
            self._set_movie_combo_error("加载电影异常")

    def _update_movie_combo_womei(self, movies):
        """更新电影下拉框（沃美数据格式，增强调试功能）"""
        try:
            print(f"[电影调试] 开始更新电影下拉框...")

            # 清空并设置默认选项
            self.movie_combo.clear()
            self.movie_combo.addItem("请选择电影")

            # 保存电影数据
            self.current_movies = movies
            print(f"[电影调试] 保存电影数据: {len(movies)} 部电影")

            # 添加电影到下拉框
            for i, movie in enumerate(movies):
                movie_name = movie.get('name', '未知电影')
                movie_id = movie.get('movie_id', 'N/A')  # 修复：沃美API使用movie_id字段
                self.movie_combo.addItem(movie_name)

                # 只显示前3部电影的详细信息
                if i < 3:
                    print(f"[电影调试] 添加电影 {i+1}: {movie_name} (ID: {movie_id})")

            # 🔧 确保下拉框启用状态正确
            self.movie_combo.setEnabled(True)
            print(f"[电影调试] ✅ 电影下拉框更新完成:")
            print(f"  - 总电影数: {len(movies)}")
            print(f"  - 下拉框项目数: {self.movie_combo.count()}")
            print(f"  - 启用状态: {self.movie_combo.isEnabled()}")

        except Exception as e:
            print(f"[电影调试] ❌ 更新电影下拉框失败: {e}")
            import traceback
            traceback.print_exc()
            self._set_movie_combo_error("更新电影列表失败")

    def _set_movie_combo_error(self, error_msg):
        """设置电影下拉框错误状态"""
        self.movie_combo.clear()
        self.movie_combo.addItem(error_msg)
        self.movie_combo.setEnabled(True)

    def _check_cinema_has_accounts(self, cinema_id: str) -> bool:
        """简化的账号检查（总是返回True）"""
        try:
            print(f"[Tab管理器] 简化账号检查，不再关联影院")
            return True  # 总是返回True，不再检查影院关联

        except Exception as e:
            print(f"[Tab管理器] 账号检查错误: {e}")
            return True  # 即使出错也返回True

    def _check_and_load_movies(self, selected_cinema):
        """检查账号状态并加载影片数据"""
        try:
            # 🆕 更强的账号状态检查逻辑
            if not self.current_account:
                print("[Tab管理器] 等待账号选择...")
                self.movie_combo.clear()
                self.movie_combo.addItem("等待账号选择...")
                
                # 🆕 只延迟检查一次，避免无限循环
                QTimer.singleShot(1000, lambda: self._final_check_and_load_movies(selected_cinema))
                return
            
            print(f"[Tab管理器] 账号已选择: {self.current_account.get('userid', 'N/A')}")
            
            # 调用影片API
            self._load_movies_for_cinema(selected_cinema)
                
        except Exception as e:
            print(f"[Tab管理器] 检查账号状态错误: {e}")
            self.movie_combo.clear()
            self.movie_combo.addItem("加载失败")
    
    def _final_check_and_load_movies(self, selected_cinema):
        """最终检查账号状态并加载影片数据 - 避免无限循环"""
        try:
            if not self.current_account:
                print("[Tab管理器] 最终检查：仍未选择账号，停止重试")
                self.movie_combo.clear()
                self.movie_combo.addItem("请选择账号")
                return
            
            print(f"[Tab管理器] 最终检查：账号已选择: {self.current_account.get('userid', 'N/A')}")
            
            # 调用影片API
            self._load_movies_for_cinema(selected_cinema)
                
        except Exception as e:
            print(f"[Tab管理器] 最终检查错误: {e}")
            self.movie_combo.clear()
            self.movie_combo.addItem("加载失败")

    def _load_movies_for_cinema(self, cinema_data):
        """为指定影院加载影片数据"""
        try:
            from services.film_service import get_films, normalize_film_data
            
            # 获取影院参数 - 🆕 修复字段名称
            base_url = cinema_data.get('base_url', '')
            cinemaid = cinema_data.get('cinemaid', '')
            
            print(f"[Tab管理器] 影院数据检查:")
            print(f"  - 影院名称: {cinema_data.get('cinemaShortName', 'N/A')}")
            print(f"  - 影院ID: {cinemaid}")
            print(f"  - 域名: {base_url}")
            
            if not base_url or not cinemaid:
                print(f"[Tab管理器] 影院参数不完整: base_url={base_url}, cinemaid={cinemaid}")
                self.movie_combo.clear()
                self.movie_combo.addItem("影院参数错误")
                return
            
            # 获取账号参数
            account = self.current_account
            if not account:
                print(f"[Tab管理器] 当前账号为空")
                self.movie_combo.clear()
                self.movie_combo.addItem("账号信息缺失")
                return
                
            openid = account.get('openid', '')
            userid = account.get('userid', '')
            token = account.get('token', '')
            
            print(f"[Tab管理器] 账号数据检查:")
            print(f"  - 用户ID: {userid}")
            print(f"  - OpenID: {openid[:10]}..." if openid else "  - OpenID: 空")
            print(f"  - Token: {token[:10]}..." if token else "  - Token: 空")
            
            if not all([openid, userid, token]):
                print(f"[Tab管理器] 账号参数不完整")
                self.movie_combo.clear()
                self.movie_combo.addItem("账号信息不完整")
                return
            
            print(f"[Tab管理器] 开始调用影片API...")
            print(f"[Tab管理器] API URL: https://{base_url}/MiniTicket/index.php/MiniFilm/getAllFilmsIndexNew")
            
            # 调用API获取影片数据
            films_data = get_films(base_url, cinemaid, openid, userid, token)
            
            print(f"[Tab管理器] API响应数据类型: {type(films_data)}")
            print(f"[Tab管理器] API响应数据长度: {len(str(films_data)) if films_data else 0}")
            
            if not films_data:
                print("[Tab管理器] API返回空数据")
                self.movie_combo.clear()
                self.movie_combo.addItem("暂无影片")
                return
            
            # 🆕 详细调试API响应结构
            print(f"[Tab管理器] API响应keys: {list(films_data.keys()) if isinstance(films_data, dict) else '非字典类型'}")
            
            # 🆕 正确保存原始数据
            self.raw_films_data = films_data  # 保存完整的原始数据
            films = films_data.get('films', [])
            shows = films_data.get('shows', {})
            
            print(f"[Tab管理器] 原始数据影片数量: {len(films)}")
            print(f"[Tab管理器] 原始数据排期数量: {len(shows)}")
            
            # 🆕 调试films和shows的具体结构
            if films:
                first_film = films[0]
                print(f"[Tab管理器] 第一个影片数据: {first_film}")
                print(f"[Tab管理器] 第一个影片数据字段: {list(first_film.keys())}")
            
            if shows:
                print(f"[Tab管理器] shows结构keys: {list(shows.keys())[:3]}")  # 只显示前3个
                first_film_key = list(shows.keys())[0]
                first_film_shows = shows[first_film_key]
                print(f"[Tab管理器] 第一个影片的排期结构: {type(first_film_shows)}")
                if isinstance(first_film_shows, dict):
                    print(f"[Tab管理器] 第一个影片排期日期keys: {list(first_film_shows.keys())[:3]}")
                    first_date = list(first_film_shows.keys())[0] if first_film_shows else None
                    if first_date:
                        first_date_sessions = first_film_shows[first_date]
                        print(f"[Tab管理器] 第一个日期的场次数量: {len(first_date_sessions) if isinstance(first_date_sessions, list) else '非列表类型'}")
                        if isinstance(first_date_sessions, list) and first_date_sessions:
                            first_session = first_date_sessions[0]
                            print(f"[Tab管理器] 第一个场次数据: {first_session}")
                            print(f"[Tab管理器] 第一个场次数据字段: {list(first_session.keys()) if isinstance(first_session, dict) else '非字典类型'}")
            
            # 🆕 添加原始数据字段检查
            if films:
                first_film = films[0]
                print(f"[Tab管理器] 第一个影片数据字段: {list(first_film.keys())}")
            if shows:
                first_film_key = list(shows.keys())[0]
                first_date = list(shows[first_film_key].keys())[0] if shows[first_film_key] else None
                if first_date:
                    first_session = shows[first_film_key][first_date][0] if shows[first_film_key][first_date] else {}
                    print(f"[Tab管理器] 第一个场次数据字段: {list(first_session.keys())}")
            
            # 🆕 构建影片数据结构，包含排期信息
            self.current_movies = []  # 保存影片列表，用于影片切换时查找
            
            # 更新影片下拉框
            self.movie_combo.clear()
            
            if films:
                for i, film in enumerate(films):
                    # 🆕 使用原始数据的正确字段名
                    film_name = film.get('fn', '未知影片')  # 'fn' 是影片名称字段
                    film_id = film.get('fno', '')  # 🆕 修复关联字段：使用 'fno' 而不是 'fno'
                    film_code = film.get('fc', '')  # 'fc' 是影片编码
                    
                    print(f"[Tab管理器] 处理影片 {i+1}: {film_name}")
                    print(f"  - fno: {film_id}")
                    print(f"  - fc: {film_code}")
                    
                    # 🆕 尝试多种可能的关联字段
                    film_plans = None
                    
                    # 方法1: 使用 fno 关联
                    if film_id and film_id in shows:
                        film_plans = shows[film_id]
                        print(f"  - 使用fno关联成功，排期数据: {len(film_plans) if isinstance(film_plans, dict) else '非字典'}")
                    
                    # 方法2: 使用 fc 关联
                    elif film_code and film_code in shows:
                        film_plans = shows[film_code]
                        print(f"  - 使用fc关联成功，排期数据: {len(film_plans) if isinstance(film_plans, dict) else '非字典'}")
                    
                    # 方法3: 尝试直接用索引关联
                    elif i < len(list(shows.keys())):
                        shows_keys = list(shows.keys())
                        film_plans = shows[shows_keys[i]]
                        print(f"  - 使用索引关联，key: {shows_keys[i]}")
                    
                    else:
                        print(f"  - 未找到排期数据")
                        film_plans = {}
                    
                    # 🆕 为每个影片添加对应的排期数据
                    film_with_plans = film.copy()
                    
                    # 将排期数据转换为plans列表格式
                    plans = []
                    if film_plans and isinstance(film_plans, dict):
                        for date, sessions in film_plans.items():
                            if isinstance(sessions, list):
                                for session in sessions:
                                    # 为每个场次添加日期信息
                                    session_with_date = session.copy()
                                    session_with_date['show_date'] = date
                                    session_with_date['k'] = f"{date} {session.get('q', '')}"  # 完整的时间信息
                                    plans.append(session_with_date)
                    
                    film_with_plans['plans'] = plans
                    self.current_movies.append(film_with_plans)
                    
                    print(f"[Tab管理器] 影片 {i+1}: {film_name} (排期数: {len(plans)})")
                    self.movie_combo.addItem(film_name)
                    
                print(f"[Tab管理器] 影片列表更新完成，共{len(self.current_movies)}个影片")
            else:
                self.movie_combo.addItem("暂无影片")
                print(f"[Tab管理器] 没有可用影片")
                
        except Exception as e:
            print(f"[Tab管理器] 加载影片数据错误: {e}")
            import traceback
            traceback.print_exc()
            self.movie_combo.clear()
            self.movie_combo.addItem("加载失败")

    def _on_movie_changed(self, movie_text: str):
        """电影选择变化处理 - 使用沃美电影服务获取场次数据"""
        try:
            if not movie_text or movie_text in ["请选择电影", "加载电影中...", "该影院暂无电影", "加载失败"]:
                return

            print(f"[Tab管理器] 电影切换: {movie_text}")

            # 重置券列表
            self.reset_coupon_lists()

            # 禁用选座按钮
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)
                print(f"[Tab管理器] 电影切换，选座按钮已禁用")

            # 重置下级联动状态
            self._reset_cascade_from_level(4)  # 重置日期及以下级别

            # 获取选中的电影数据
            selected_movie = None
            if hasattr(self, 'current_movies') and self.current_movies:
                movie_index = self.movie_combo.currentIndex() - 1  # 减去"请选择电影"选项
                if 0 <= movie_index < len(self.current_movies):
                    selected_movie = self.current_movies[movie_index]

            if not selected_movie:
                print(f"[Tab管理器] 未找到电影数据: {movie_text}")
                self._set_date_combo_error("未找到电影数据")
                return

            # 保存当前电影数据
            self.current_movie_data = selected_movie
            movie_id = selected_movie.get('movie_id') or selected_movie.get('id')

            print(f"[Tab管理器] 🎬 开始获取电影场次: {movie_text} (ID: {movie_id})")

            # 获取沃美影院ID
            cinema_id = None
            if hasattr(self, 'current_cinema_data') and self.current_cinema_data:
                cinema_id = self.current_cinema_data.get('cinema_id')  # 沃美系统使用cinema_id

            if not cinema_id or not movie_id:
                print(f"[Tab管理器] 缺少必要参数: cinema_id={cinema_id}, movie_id={movie_id}")
                self._set_date_combo_error("参数缺失")
                return

            # 设置加载状态
            self.date_combo.clear()
            self.date_combo.addItem("加载日期中...")
            self.date_combo.setEnabled(False)

            # 获取沃美电影服务实例
            from services.womei_film_service import get_womei_film_service
            token = self._get_current_token()
            film_service = get_womei_film_service(token)

            # 调用场次API
            shows_result = film_service.get_shows(cinema_id, str(movie_id))

            if shows_result.get('success'):
                shows_data = shows_result.get('shows', {})  # 沃美返回按日期分组的字典
                total_shows = shows_result.get('total', 0)
                print(f"[Tab管理器] ✅ 成功获取 {total_shows} 个场次")

                if shows_data and isinstance(shows_data, dict):
                    # 从按日期分组的数据中提取有效日期
                    valid_dates = []
                    for date, date_data in shows_data.items():
                        schedules = date_data.get('schedules', [])
                        if schedules:  # 只添加有场次的日期
                            valid_dates.append(date)

                    if valid_dates:
                        sorted_dates = sorted(valid_dates)
                        self._update_date_combo_womei_new(shows_data, sorted_dates)

                        # 🔧 自动选择第一个日期
                        if len(sorted_dates) > 0:
                            first_date = sorted_dates[0]
                            print(f"[Tab管理器] 🎯 自动选择第一个日期: {first_date}")

                            # 延迟选择，确保下拉框已更新
                            QTimer.singleShot(100, lambda: self._auto_select_first_date(first_date))
                    else:
                        self._set_date_combo_error("该电影暂无场次")
                else:
                    self._set_date_combo_error("该电影暂无场次")
            else:
                error = shows_result.get('error', '未知错误')
                print(f"[Tab管理器] ❌ 获取场次失败: {error}")
                self._set_date_combo_error(f"获取场次失败: {error}")
            
        except Exception as e:
            print(f"[Tab管理器] 电影选择错误: {e}")
            import traceback
            traceback.print_exc()
            self._set_date_combo_error("电影选择异常")

    def _update_date_combo_womei_new(self, shows_data, valid_dates):
        """更新日期下拉框（沃美按日期分组的数据格式）"""
        try:
            # 保存完整的场次数据（按日期分组）
            self.current_shows_data = shows_data

            # 更新日期下拉框
            self.date_combo.clear()
            self.date_combo.addItem("请选择日期")

            for date in valid_dates:
                self.date_combo.addItem(date)

            self.date_combo.setEnabled(True)
            print(f"[Tab管理器] 日期下拉框已更新，共 {len(valid_dates)} 个有效日期")

        except Exception as e:
            print(f"[Tab管理器] 更新日期下拉框失败: {e}")
            self._set_date_combo_error("更新日期列表失败")

    def _update_date_combo_womei(self, shows):
        """更新日期下拉框（沃美场次数据格式）- 兼容旧版本"""
        try:
            # 保存场次数据
            self.current_shows_data = shows

            # 提取所有日期
            dates = set()
            for show in shows:
                show_date = show.get('show_date', '')
                if show_date:
                    dates.add(show_date)

            # 排序日期
            sorted_dates = sorted(list(dates))

            # 更新日期下拉框
            self.date_combo.clear()
            self.date_combo.addItem("请选择日期")

            for date in sorted_dates:
                self.date_combo.addItem(date)

            self.date_combo.setEnabled(True)
            print(f"[Tab管理器] 日期下拉框已更新，共 {len(sorted_dates)} 个日期")

        except Exception as e:
            print(f"[Tab管理器] 更新日期下拉框失败: {e}")
            self._set_date_combo_error("更新日期列表失败")

    def _set_date_combo_error(self, error_msg):
        """设置日期下拉框错误状态"""
        self.date_combo.clear()
        self.date_combo.addItem(error_msg)
        self.date_combo.setEnabled(True)

        # 同时重置场次下拉框
        self.session_combo.clear()
        self.session_combo.addItem("请先选择日期")
        self.session_combo.setEnabled(True)

    def _on_date_changed(self, date_text: str):
        """日期选择变化处理 - 筛选指定日期的场次"""
        try:
            if not date_text or date_text in ["请选择日期", "加载日期中...", "该电影暂无场次", "获取场次失败"]:
                return

            # 检查场次数据是否存在
            if not hasattr(self, 'current_shows_data') or not self.current_shows_data:
                print(f"[Tab管理器] 场次数据未加载")
                self._set_session_combo_error("场次数据未加载")
                return

            print(f"[Tab管理器] 日期切换: {date_text}")

            # 重置券列表
            self.reset_coupon_lists()

            # 禁用选座按钮
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)
                print(f"[Tab管理器] 日期切换，选座按钮已禁用")

            # 重置下级联动状态
            self._reset_cascade_from_level(5)  # 重置场次及以下级别

            # 从按日期分组的数据中筛选指定日期的场次
            matching_sessions = []

            if isinstance(self.current_shows_data, dict):
                # 新格式：按日期分组的数据
                date_data = self.current_shows_data.get(date_text, {})
                schedules = date_data.get('schedules', [])
                matching_sessions = schedules
                print(f"[Tab管理器] 从分组数据筛选日期 {date_text}: {len(matching_sessions)} 个场次")
            else:
                # 旧格式：场次数组（兼容性处理）
                for show in self.current_shows_data:
                    show_date = show.get('show_date', '')
                    if show_date == date_text:
                        matching_sessions.append(show)
                print(f"[Tab管理器] 从数组数据筛选日期 {date_text}: {len(matching_sessions)} 个场次")

            # 更新场次下拉框
            if matching_sessions:
                self._update_session_combo_womei(matching_sessions)
                print(f"[Tab管理器] ✅ 筛选到 {len(matching_sessions)} 个场次")
            else:
                self._set_session_combo_error("该日期暂无场次")
                print(f"[Tab管理器] ❌ 该日期无场次: {date_text}")
            
        except Exception as e:
            print(f"[Tab管理器] 日期选择错误: {e}")
            import traceback
            traceback.print_exc()
            self._set_session_combo_error("日期选择异常")

    def _update_session_combo_womei(self, sessions):
        """更新场次下拉框（沃美场次数据格式）"""
        try:
            # 保存当前日期的场次数据
            self.current_date_sessions = sessions

            # 更新场次下拉框
            self.session_combo.clear()
            self.session_combo.addItem("请选择场次")

            for session in sessions:
                session_text = self._format_session_text_womei(session)
                self.session_combo.addItem(session_text)

            self.session_combo.setEnabled(True)
            print(f"[Tab管理器] 场次下拉框已更新，共 {len(sessions)} 个场次")

            # 🔧 自动选择第一个场次
            if len(sessions) > 0:
                first_session = sessions[0]
                session_text = self._format_session_text_womei(first_session)
                print(f"[Tab管理器] 🎯 自动选择第一个场次: {session_text}")

                # 延迟选择，确保下拉框已更新
                QTimer.singleShot(100, lambda: self._auto_select_first_session(session_text))

        except Exception as e:
            print(f"[Tab管理器] 更新场次下拉框失败: {e}")
            self._set_session_combo_error("更新场次列表失败")

    def _format_session_text_womei(self, session):
        """格式化沃美场次显示文本"""
        try:
            show_time = session.get('show_time', '')
            hall_name = session.get('hall_name', '')
            selling_price = session.get('selling_price', 0)  # 沃美使用selling_price字段
            show_type = session.get('show_type', '')
            language = session.get('language', '')

            # 构建显示文本
            parts = []
            if show_time:
                parts.append(show_time)
            if hall_name:
                parts.append(hall_name)
            if show_type:
                parts.append(show_type)
            if language:
                parts.append(language)
            if selling_price:
                parts.append(f"¥{selling_price}")

            # 格式化显示文本
            if parts:
                return " ".join(parts)
            else:
                return "场次信息"

        except Exception as e:
            print(f"[Tab管理器] 格式化场次文本失败: {e}")
            return "场次信息错误"

    def _set_session_combo_error(self, error_msg):
        """设置场次下拉框错误状态"""
        self.session_combo.clear()
        self.session_combo.addItem(error_msg)
        self.session_combo.setEnabled(True)

    def _on_session_changed(self, session_text: str):
        """场次选择变化处理 - 使用沃美电影服务获取座位图"""
        try:
            if not session_text or session_text in ["请选择场次", "该日期暂无场次", "更新场次列表失败", "日期选择异常"]:
                return

            # 检查场次数据是否存在
            if not hasattr(self, 'current_date_sessions') or not self.current_date_sessions:
                print(f"[Tab管理器] 场次数据未加载")
                return

            print(f"[Tab管理器] 🎬 场次切换: {session_text}")

            # 重置券列表
            self.reset_coupon_lists()

            # 获取选中的场次数据
            selected_session = None
            session_index = self.session_combo.currentIndex() - 1  # 减去"请选择场次"选项
            print(f"[Tab管理器] 🔍 场次索引: {session_index}, 总场次数: {len(self.current_date_sessions)}")

            if 0 <= session_index < len(self.current_date_sessions):
                selected_session = self.current_date_sessions[session_index]
                print(f"[Tab管理器] ✅ 找到场次数据: {selected_session}")

            if not selected_session:
                print(f"[Tab管理器] ❌ 未找到场次数据: {session_text}")
                return
            
            # 🆕 保存当前场次数据供订单创建使用
            self.current_session_data = selected_session
            # print(f"[Tab管理器] 保存当前场次数据: {selected_session}")
            
            # 获取当前选择的完整信息
            cinema_text = self.cinema_combo.currentText() if hasattr(self, 'cinema_combo') else ""
            movie_text = self.movie_combo.currentText() if hasattr(self, 'movie_combo') else ""
            date_text = self.date_combo.currentText() if hasattr(self, 'date_combo') else ""
            
            # 🆕 查找影院详细数据 - 修复逻辑
            print(f"[Tab管理器] 🔍 查找影院数据:")
            print(f"  - 目标影院名: {cinema_text}")
            print(f"  - cinemas_data存在: {hasattr(self, 'cinemas_data')}")
            print(f"  - cinemas_data长度: {len(self.cinemas_data) if hasattr(self, 'cinemas_data') and self.cinemas_data else 0}")

            cinema_data = None
            if hasattr(self, 'cinemas_data') and self.cinemas_data:
                print(f"[Tab管理器] 🔍 在影院列表中查找:")
                for i, cinema in enumerate(self.cinemas_data):
                    cinema_name = cinema.get('cinema_name')  # 沃美系统字段
                    cinema_short_name = cinema.get('cinemaShortName')  # 华联系统字段
                    print(f"  影院 {i+1}: cinema_name='{cinema_name}', cinemaShortName='{cinema_short_name}'")

                    # 同时检查两种字段名
                    if cinema_name == cinema_text or cinema_short_name == cinema_text:
                        cinema_data = cinema
                        print(f"[Tab管理器] ✅ 找到影院数据: {cinema_name or cinema_short_name}")
                        print(f"  - cinema_id: {cinema.get('cinema_id')}")
                        print(f"  - cinemaid: {cinema.get('cinemaid')}")
                        print(f"  - base_url: {cinema.get('base_url')}")
                        break

            if not cinema_data:
                print(f"[Tab管理器] ❌ 未找到影院数据: {cinema_text}")
                print(f"[Tab管理器] 可用影院列表:")
                if hasattr(self, 'cinemas_data') and self.cinemas_data:
                    for i, c in enumerate(self.cinemas_data):
                        print(f"  {i+1}. cinema_name: '{c.get('cinema_name')}', cinemaShortName: '{c.get('cinemaShortName')}'")
                else:
                    print(f"  无数据")

                # 🆕 尝试从影院管理器重新加载数据
                try:
                    print(f"[Tab管理器] 🔄 尝试重新加载影院数据...")
                    from services.cinema_manager import cinema_manager
                    cinemas = cinema_manager.load_cinema_list()
                    self.cinemas_data = cinemas
                    print(f"[Tab管理器] 重新加载了 {len(cinemas)} 个影院")

                    # 重新查找
                    for cinema in cinemas:
                        cinema_name = cinema.get('cinema_name')
                        cinema_short_name = cinema.get('cinemaShortName')
                        if cinema_name == cinema_text or cinema_short_name == cinema_text:
                            cinema_data = cinema
                            print(f"[Tab管理器] ✅ 重新加载后找到影院数据: {cinema_name or cinema_short_name}")
                            break
                except Exception as reload_error:
                    print(f"[Tab管理器] ❌ 重新加载影院数据失败: {reload_error}")
            
            # 构建场次信息对象
            print(f"[Tab管理器] 📋 构建session_info:")
            print(f"  - selected_session: {selected_session}")
            print(f"  - cinema_text: {cinema_text}")
            print(f"  - movie_text: {movie_text}")
            print(f"  - date_text: {date_text}")
            print(f"  - session_text: {session_text}")
            print(f"  - current_account: {bool(self.current_account)}")
            print(f"  - cinema_data: {cinema_data}")

            session_info = {
                'session_data': selected_session,
                'cinema_name': cinema_text,
                'movie_name': movie_text,
                'show_date': date_text,
                'session_text': session_text,
                'account': self.current_account,
                'cinema_data': cinema_data  # 🆕 确保传递完整的影院数据
            }

            print(f"[Tab管理器] 🚀 发出场次选择信号: {session_text}")
            print(f"[Tab管理器] 📋 session_info完整内容: {session_info}")
            print(f"[Tab管理器] 🔍 影院数据验证: {cinema_data.get('base_url') if cinema_data else 'None'}")

            # 🆕 启用选座按钮 - 当用户选择完场次后
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(True)
                print(f"[Tab管理器] 选座按钮已启用")

            # 保存当前场次数据
            self.current_session_data = selected_session

            # 获取必要参数
            cinema_id = None
            hall_id = selected_session.get('hall_id')
            schedule_id = selected_session.get('schedule_id') or selected_session.get('id')

            if hasattr(self, 'current_cinema_data') and self.current_cinema_data:
                cinema_id = self.current_cinema_data.get('cinema_id')  # 沃美系统使用cinema_id

            if not all([cinema_id, hall_id, schedule_id]):
                print(f"[Tab管理器] 缺少座位图参数: cinema_id={cinema_id}, hall_id={hall_id}, schedule_id={schedule_id}")
                return

            print(f"[Tab管理器] 🎯 开始获取座位图:")
            print(f"  - 影院ID: {cinema_id}")
            print(f"  - 影厅ID: {hall_id}")
            print(f"  - 场次ID: {schedule_id}")

            # 调用沃美座位图API
            self._load_seat_map_womei(cinema_id, hall_id, schedule_id, selected_session)

        except Exception as e:
            print(f"[Tab管理器] 场次选择错误: {e}")
            import traceback
            traceback.print_exc()

    def _load_seat_map_womei(self, cinema_id, hall_id, schedule_id, session_data):
        """使用沃美电影服务获取座位图"""
        try:
            print(f"[Tab管理器] 🪑 开始获取沃美座位图")

            # 获取沃美电影服务实例
            from services.womei_film_service import get_womei_film_service

            # 🔧 修复：使用当前账号的token而不是硬编码token
            current_token = self.current_account.get('token', '') if self.current_account else ''
            if not current_token:
                print(f"[Tab管理器] ❌ 当前账号token为空，无法获取座位图")
                return

            print(f"[Tab管理器] 🔑 使用账号token: {current_token[:20]}...")
            film_service = get_womei_film_service(current_token)

            # 🆕 使用准确座位数据API（对比两个API识别已售座位）
            hall_result = film_service.get_accurate_seat_data(cinema_id, hall_id, schedule_id, debug=True)

            if hall_result.get('success'):
                hall_info = hall_result.get('hall_info', {})
                print(f"[Tab管理器] ✅ 成功获取座位图数据")

                # 构建正确的session_info对象（主窗口期望的格式）
                print(f"[Tab管理器] 📋 构建session_info对象:")
                print(f"  - session_data: {session_data}")
                print(f"  - current_account: {bool(self.current_account)}")
                print(f"  - current_cinema_data: {bool(hasattr(self, 'current_cinema_data'))}")

                # 获取影院数据
                cinema_data = None
                if hasattr(self, 'current_cinema_data') and self.current_cinema_data:
                    cinema_data = self.current_cinema_data.copy()
                    # 确保包含主窗口需要的字段
                    if 'cinemaid' not in cinema_data and 'cinema_id' in cinema_data:
                        cinema_data['cinemaid'] = cinema_data['cinema_id']
                    if 'cinemaShortName' not in cinema_data and 'cinema_name' in cinema_data:
                        cinema_data['cinemaShortName'] = cinema_data['cinema_name']
                    print(f"  - 使用current_cinema_data: {cinema_data}")
                else:
                    print(f"  - current_cinema_data不存在，尝试构建...")
                    # 尝试从当前选择构建影院数据
                    cinema_text = self.cinema_combo.currentText() if hasattr(self, 'cinema_combo') else ""
                    if cinema_text and hasattr(self, 'cinemas_data') and self.cinemas_data:
                        for cinema in self.cinemas_data:
                            if (cinema.get('cinema_name') == cinema_text or
                                cinema.get('cinemaShortName') == cinema_text):
                                cinema_data = cinema.copy()
                                # 确保包含主窗口需要的字段
                                if 'cinemaid' not in cinema_data and 'cinema_id' in cinema_data:
                                    cinema_data['cinemaid'] = cinema_data['cinema_id']
                                if 'cinemaShortName' not in cinema_data and 'cinema_name' in cinema_data:
                                    cinema_data['cinemaShortName'] = cinema_data['cinema_name']
                                print(f"  - 从cinemas_data找到: {cinema_data}")
                                break

                # 构建主窗口期望的session_info格式
                session_info = {
                    'session_data': session_data,
                    'account': self.current_account,
                    'cinema_data': cinema_data,
                    'hall_info': hall_info,  # 额外添加座位图数据
                    'session_text': self._format_session_text_womei(session_data)
                }

                print(f"[Tab管理器] 📋 最终session_info:")
                print(f"  - session_data: {bool(session_info.get('session_data'))}")
                print(f"  - account: {bool(session_info.get('account'))}")
                print(f"  - cinema_data: {bool(session_info.get('cinema_data'))}")
                print(f"  - hall_info: {bool(session_info.get('hall_info'))}")

                # 发出座位图加载信号
                self.session_selected.emit(session_info)

                # 启用选座按钮
                if hasattr(self, 'submit_order_btn'):
                    self.submit_order_btn.setEnabled(True)
                    print(f"[Tab管理器] 座位图加载完成，选座按钮已启用")

            else:
                error = hall_result.get('error', '未知错误')
                print(f"[Tab管理器] ❌ 获取座位图失败: {error}")

        except Exception as e:
            print(f"[Tab管理器] 获取沃美座位图异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_submit_order(self):
        """选座按钮处理 - 加载座位图"""
        try:
            if not self.current_account:
                MessageManager.show_error(self, "选座失败", "请先选择账号", auto_close=False)
                return

            # 获取所有选择的信息
            cinema_text = self.cinema_combo.currentText() if hasattr(self, 'cinema_combo') else ""
            movie_text = self.movie_combo.currentText() if hasattr(self, 'movie_combo') else ""
            date_text = self.date_combo.currentText() if hasattr(self, 'date_combo') else ""
            session_text = self.session_combo.currentText() if hasattr(self, 'session_combo') else ""

            # 验证选择完整性
            if not all([cinema_text, movie_text, date_text, session_text]):
                MessageManager.show_error(self, "选择不完整", "请完成影院、影片、日期、场次的选择！", auto_close=False)
                return

            # 验证选择有效性
            invalid_texts = ["加载中...", "请先选择", "暂无", "加载失败", "错误"]
            if any(invalid in cinema_text for invalid in invalid_texts) or \
               any(invalid in movie_text for invalid in invalid_texts) or \
               any(invalid in date_text for invalid in invalid_texts) or \
               any(invalid in session_text for invalid in invalid_texts):
                MessageManager.show_error(self, "选择无效", "请重新选择有效的影院、影片、日期和场次！", auto_close=False)
                return

            # 🆕 发出座位图加载信号让主窗口处理
            # 构建座位图加载信息
            seat_load_info = {
                "account": self.current_account,
                "cinema_name": cinema_text,
                "movie_name": movie_text,
                "show_date": date_text,
                "session_text": session_text,
                "session_data": getattr(self, 'current_session_data', {}),
                "trigger_type": "tab_seat_selection"  # 标识来源为选座
            }

            print(f"[Tab管理器] 发出座位图加载信号:")
            print(f"  影院: {cinema_text}")
            print(f"  影片: {movie_text}")
            print(f"  日期: {date_text}")
            print(f"  场次: {session_text}")

            # 发出座位图加载信号，让主窗口处理
            self.seat_load_requested.emit(seat_load_info)

            # 🆕 移除加载提示信息，直接加载座位图

        except Exception as e:
            MessageManager.show_error(self, "选座错误", f"加载座位图失败: {str(e)}", auto_close=False)
            print(f"[Tab管理器] 选座错误: {e}")
            import traceback
            traceback.print_exc()
    
    def _on_refresh_orders(self):
        """刷新订单列表"""
        try:
            account = getattr(self, 'current_account', None)
            if not account:
                MessageManager.show_error(self, "未选择账号", "请先选择账号！", auto_close=False)
                return

            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                MessageManager.show_error(self, "未选择影院", "请先选择影院！", auto_close=False)
                return

            # 显示加载状态
            self.order_refresh_btn.setText("刷新中...")
            self.order_refresh_btn.setEnabled(False)

            # 调用现有的订单API - 使用标准参数格式
            from services.order_api import get_order_list

            # 🔧 修复：使用标准API参数格式
            params = {
                'pageNo': 1,                           # 标准参数名
                'groupid': '',                         # 集团ID
                'cinemaid': cinemaid,                  # 影院ID
                'cardno': account.get('cardno', ''),   # 会员卡号
                'userid': account['userid'],           # 用户ID
                'openid': account['openid'],           # 微信openid
                'CVersion': '3.9.12',                  # 客户端版本
                'OS': 'Windows',                       # 操作系统
                'token': account['token'],             # 访问令牌
                'source': '2'                          # 来源：2=小程序
            }

            print(f"[订单刷新] 请求参数: {params}")
            result = get_order_list(params)
            print(f"[订单刷新] API响应: {result}")

            if result.get('resultCode') == '0':
                # 🔧 修复：详细分析API返回的数据结构
                result_data = result.get('resultData', {})

                # 🔧 修复：检查result_data是否为None
                if result_data is None:
                    print("[订单刷新] resultData为None，使用空列表")
                    orders = []
                    self.update_order_table(orders)
                    return

                print(f"[订单刷新] API返回数据结构分析:")
                print(f"  - resultData类型: {type(result_data)}")
                print(f"  - resultData内容: {result_data}")

                if isinstance(result_data, dict):
                    print(f"  - resultData字段: {list(result_data.keys())}")

                # 🔧 尝试多种可能的数据路径
                orders = None

                # 路径1: resultData.orders
                if isinstance(result_data, dict) and 'orders' in result_data:
                    orders = result_data['orders']
                    print(f"[订单刷新] 使用路径 resultData.orders，获取到 {len(orders)} 个订单")

                # 路径2: resultData.orderList
                elif isinstance(result_data, dict) and 'orderList' in result_data:
                    orders = result_data['orderList']
                    print(f"[订单刷新] 使用路径 resultData.orderList，获取到 {len(orders)} 个订单")

                # 路径3: resultData.data.orders
                elif isinstance(result_data, dict) and 'data' in result_data and isinstance(result_data['data'], dict):
                    data = result_data['data']
                    if 'orders' in data:
                        orders = data['orders']
                        print(f"[订单刷新] 使用路径 resultData.data.orders，获取到 {len(orders)} 个订单")
                    elif 'orderList' in data:
                        orders = data['orderList']
                        print(f"[订单刷新] 使用路径 resultData.data.orderList，获取到 {len(orders)} 个订单")

                # 路径4: 直接是数组
                elif isinstance(result_data, list):
                    orders = result_data
                    print(f"[订单刷新] resultData直接是数组，获取到 {len(orders)} 个订单")

                if orders is None:
                    orders = []
                    print(f"[订单刷新] 未找到订单数据，使用空数组")

                # 🔧 分析第一个订单的数据结构（简化版）
                if orders and len(orders) > 0:
                    first_order = orders[0]
                    print(f"[订单刷新] 第一个订单数据结构:")
                    print(f"  - 订单类型: {type(first_order)}")
                    if isinstance(first_order, dict):
                        print(f"  - 订单字段: {list(first_order.keys())}")
                        # 只显示关键字段的值
                        key_fields = ['orderName', 'orderS', 'orderno']
                        for field in key_fields:
                            if field in first_order:
                                print(f"  - {field}: {first_order[field]}")

                self.update_order_table(orders)

                # 不显示成功弹窗，只在控制台记录
                print(f"[订单刷新] 订单列表刷新成功，共 {len(orders)} 个订单")
            else:
                error_msg = result.get('resultDesc', '获取订单列表失败')
                print(f"[订单刷新] 获取失败: {error_msg}")
                MessageManager.show_error(self, "获取失败", error_msg, auto_close=False)

                # 清空表格而不是显示示例数据
                self.order_table.setRowCount(0)

        except Exception as e:
            print(f"[订单刷新] 异常: {e}")
            import traceback
            traceback.print_exc()
            MessageManager.show_error(self, "刷新失败", f"刷新订单列表时出错：{str(e)}", auto_close=False)

        finally:
            # 恢复按钮状态
            self.order_refresh_btn.setText("刷新")
            self.order_refresh_btn.setEnabled(True)

    def update_order_table(self, orders):
        """更新订单表格显示"""
        try:
            self.order_table.setRowCount(len(orders))
            self.order_data_cache = orders

            for row, order in enumerate(orders):
                print(f"[订单表格] 处理订单 {row}")

                # 🔧 修复：影片名称 - 根据实际API数据调整
                movie_name = (order.get('orderName') or      # ✅ 实际字段名
                             order.get('movieName') or
                             order.get('movie') or
                             order.get('filmName') or
                             order.get('film_name') or
                             order.get('movieN') or
                             order.get('filmN') or
                             order.get('fn') or
                             order.get('name') or
                             '未知影片')
                print(f"[订单表格] 订单 {row} 影片名称: {movie_name}")
                self.order_table.setItem(row, 0, self.order_table.__class__.createItem(movie_name))

                # 🔧 修复：影院名称 - 从当前选择的影院获取
                # 由于API数据中没有影院名称，从当前选择的影院获取
                if hasattr(self, 'current_cinema_data') and self.current_cinema_data:
                    cinema_name = self.current_cinema_data.get('cinemaShortName', '当前影院')
                elif hasattr(self, 'cinema_combo') and self.cinema_combo.currentText():
                    cinema_name = self.cinema_combo.currentText()
                else:
                    cinema_name = '未知影院'
                print(f"[订单表格] 订单 {row} 影院名称: {cinema_name}")
                self.order_table.setItem(row, 1, self.order_table.__class__.createItem(cinema_name))

                # 🔧 修复：订单状态 - 根据实际API数据调整
                status_text = (order.get('orderS') or        # ✅ 实际字段名
                              order.get('status') or
                              order.get('state') or
                              order.get('orderState'))

                # 也检查状态码
                status_code = order.get('orderStatus') or order.get('orderState')

                print(f"[订单表格] 订单 {row} 状态信息: status_code={status_code}, status_text={status_text}")

                if status_text:
                    # 直接使用状态文本
                    status = status_text
                elif status_code is not None:
                    # 使用状态码转换
                    status = self.get_order_status_text(status_code)
                else:
                    status = '未知状态'

                print(f"[订单表格] 订单 {row} 最终状态: {status}")

                # 根据状态设置颜色 - 适配实际状态文本
                if '待支付' in status or '待付款' in status or '待使用' in status:
                    self.order_table.add_colored_item(row, 2, status, "#ff9800")
                elif '已支付' in status or '已完成' in status or '已付款' in status:
                    self.order_table.add_colored_item(row, 2, status, "#4caf50")
                elif '已取票' in status:
                    self.order_table.add_colored_item(row, 2, status, "#2196f3")
                elif '已取消' in status:
                    self.order_table.add_colored_item(row, 2, status, "#f44336")
                else:
                    self.order_table.setItem(row, 2, self.order_table.__class__.createItem(status))

                # 🔧 修复：订单号 - 根据实际API数据调整
                order_no = (order.get('orderno') or          # ✅ 实际字段名
                           order.get('orderNo') or
                           order.get('order_id') or
                           order.get('orderid') or
                           order.get('orderN') or
                           order.get('on') or
                           order.get('id') or
                           '无订单号')
                print(f"[订单表格] 订单 {row} 订单号: {order_no}")
                self.order_table.setItem(row, 3, self.order_table.__class__.createItem(order_no))

            print(f"[订单表格] 成功更新 {len(orders)} 个订单到表格")

        except Exception as e:
            print(f"[订单表格] 更新订单表格错误: {e}")
            import traceback
            traceback.print_exc()

    def get_order_status_text(self, status_code):
        """转换订单状态码为中文"""
        status_map = {
            0: "待支付",
            1: "已支付",
            2: "已取票",
            3: "已取消",
            4: "已退款",
            5: "支付失败"
        }
        return status_map.get(status_code, "未知状态")

    def _on_order_double_click(self, item):
        """订单双击事件 - 查看订单二维码"""
        try:
            if not item:
                return

            row = item.row()
            if not hasattr(self, 'order_data_cache') or row >= len(self.order_data_cache):
                return

            order = self.order_data_cache[row]
            print(f"[订单二维码] 双击查看订单二维码")

            # 🎯 获取订单状态，只有已支付状态的订单才能查看二维码
            status_text = order.get('orderS', '')
            print(f"[订单二维码] 订单状态: {status_text}")

            # 🎯 状态限制：只有已支付状态的订单才能查看二维码
            allowed_statuses = ['已完成', '待使用', '已支付', '已付款', '已取票']

            # 🔧 临时修改：允许所有状态查看二维码（用于测试）
            print(f"[订单二维码] 订单状态检查: '{status_text}'")
            print(f"[订单二维码] 允许的状态: {allowed_statuses}")

            status_check_passed = any(status in status_text for status in allowed_statuses)
            print(f"[订单二维码] 状态检查结果: {status_check_passed}")

            if not status_check_passed:
                print(f"[订单二维码] ⚠️ 订单状态 '{status_text}' 通常不支持查看二维码，但继续执行（测试模式）")
                # return  # 注释掉这行，允许所有状态查看二维码

            # 🎯 获取订单号
            order_no = order.get('orderno')
            if not order_no:
                print(f"[订单二维码] 订单号不存在")
                return

            # 🎯 获取影院ID
            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                print(f"[订单二维码] 影院ID不存在")
                return

            print(f"[订单二维码] 开始获取订单 {order_no} 的二维码")

            # 🎯 调用二维码API
            self._get_and_show_qrcode(order_no, cinemaid)

        except Exception as e:
            print(f"[订单二维码] 双击处理错误: {e}")
            import traceback
            traceback.print_exc()

    def _get_and_show_qrcode(self, order_no, cinemaid):
        """获取并显示订单二维码 - 修复：先获取订单详情，再生成取票码二维码"""
        try:
            from services.order_api import get_order_detail, get_order_qrcode_api

            print(f"[订单二维码] 🚀 开始获取订单取票码: 订单号={order_no}, 影院ID={cinemaid}")

            # 🔧 获取当前账号信息
            account = getattr(self, 'current_account', None)
            if not account:
                print(f"[订单二维码] ❌ 当前账号为空，无法获取取票码")
                return

            print(f"[订单二维码] 📋 使用账号认证: {account.get('userid', 'N/A')}")

            # 🎯 第一步：获取订单详情，提取取票码
            print(f"[订单二维码] 📋 步骤1: 获取订单详情...")
            detail_params = {
                'orderno': order_no,
                'groupid': '',
                'cinemaid': cinemaid,
                'cardno': account.get('cardno', ''),
                'userid': account['userid'],
                'openid': account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account['token'],
                'source': '2'
            }

            detail_result = get_order_detail(detail_params)

            if not detail_result or detail_result.get('resultCode') != '0':
                error_msg = detail_result.get('resultDesc', '获取订单详情失败') if detail_result else '网络错误'
                print(f"[订单二维码] ❌ 获取订单详情失败: {error_msg}")
                return

            # 🎯 第二步：从订单详情中提取取票码
            detail_data = detail_result.get('resultData', {})

            # 🔧 修复：检查detail_data是否为None
            if detail_data is None:
                print("[订单二维码] ❌ 订单详情数据为None")
                return

            if not isinstance(detail_data, dict):
                print(f"[订单二维码] ❌ 订单详情数据类型错误: {type(detail_data)}")
                return

            # 🔧 修改：使用qrCode字段作为取票码
            qr_code = detail_data.get('qrCode', '')
            ticket_code = detail_data.get('ticketCode', '') or detail_data.get('ticketcode', '')
            ds_code = detail_data.get('dsValidateCode', '')

            print(f"[订单二维码] 📋 订单详情获取成功:")
            print(f"[订单二维码] 📋 - qrCode: {qr_code}")
            print(f"[订单二维码] 📋 - ticketCode: {ticket_code}")
            print(f"[订单二维码] 📋 - dsValidateCode: {ds_code}")

            # 🎯 确定最终的取票码（优先使用qrCode）
            final_ticket_code = qr_code or ds_code or ticket_code

            # 🎯 第三步：生成取票码二维码并显示
            if final_ticket_code:
                print(f"[订单二维码] ✅ 找到取票码: {final_ticket_code}")

                # 🎯 生成取票码二维码并保存到本地
                self._generate_and_show_ticket_qrcode(order_no, final_ticket_code, detail_data, cinemaid)

            else:
                print(f"[订单二维码] ⚠️ 订单详情中没有找到取票码")

                # 显示订单详情信息
                self._show_ticket_code_text(order_no, "无取票码", detail_data)



        except Exception as e:
            print(f"[订单二维码] ❌ 获取二维码错误: {e}")
            import traceback
            traceback.print_exc()

    def _show_ticket_code_text(self, order_no, ticket_code, detail_data):
        """显示取票码文本信息"""
        try:
            print(f"[订单二维码] 📱 显示取票码文本: {ticket_code}")

            # 构建详细的取票信息
            film_name = detail_data.get('filmName', '未知影片')
            show_time = detail_data.get('showTime', '未知时间')
            hall_name = detail_data.get('hallName', '未知影厅')
            seat_info = detail_data.get('seatInfo', '未知座位')
            cinema_name = detail_data.get('cinemaName', '未知影院')

            # 创建包含完整信息的取票码数据
            ticket_data = {
                'order_no': order_no,
                'ticket_code': ticket_code,
                'film_name': film_name,
                'show_time': show_time,
                'hall_name': hall_name,
                'seat_info': seat_info,
                'cinema_name': cinema_name,
                'display_type': 'ticket_code'  # 标识这是取票码而不是二维码图片
            }

            print(f"[订单二维码] 📤 发送取票码信息到主窗口:")
            print(f"[订单二维码] 📤 - 订单号: {order_no}")
            print(f"[订单二维码] 📤 - 取票码: {ticket_code}")
            print(f"[订单二维码] 📤 - 影片: {film_name}")
            print(f"[订单二维码] 📤 - 时间: {show_time}")

            # 🎯 通过事件总线发送取票码信息
            from utils.signals import event_bus
            event_bus.show_qrcode.emit(ticket_data)

            print(f"[订单二维码] ✅ 取票码信息已发送到主窗口显示")

        except Exception as e:
            print(f"[订单二维码] ❌ 显示取票码文本错误: {e}")
            import traceback
            traceback.print_exc()

    def _show_qrcode_image_with_text(self, qr_bytes, order_no, detail_data):
        """显示二维码图片（配合文本信息）"""
        try:
            print(f"[订单二维码] 🖼️ 显示二维码图片配合文本信息")

            # 分析数据格式
            if qr_bytes.startswith(b'\x89PNG'):
                data_format = "PNG"
            elif qr_bytes.startswith(b'\xff\xd8\xff'):
                data_format = "JPEG"
            elif qr_bytes.startswith(b'GIF'):
                data_format = "GIF"
            else:
                data_format = "UNKNOWN"

            # 🎯 创建组合显示数据（文本+图片）
            combined_data = {
                'order_no': order_no,
                'qr_bytes': qr_bytes,
                'data_size': len(qr_bytes),
                'data_format': data_format,
                'display_type': 'combined',  # 标识为组合显示
                # 包含文本信息
                'ticket_code': detail_data.get('dsValidateCode', '') or detail_data.get('ticketCode', '') or detail_data.get('ticketcode', ''),
                'film_name': detail_data.get('filmName', ''),
                'show_time': detail_data.get('showTime', ''),
                'hall_name': detail_data.get('hallName', ''),
                'seat_info': detail_data.get('seatInfo', ''),
                'cinema_name': detail_data.get('cinemaName', '')
            }

            print(f"[订单二维码] 📤 发送组合显示数据到主窗口:")
            print(f"[订单二维码] 📤 - 订单号: {order_no}")
            print(f"[订单二维码] 📤 - 取票码: {combined_data['ticket_code']}")
            print(f"[订单二维码] 📤 - 图片大小: {len(qr_bytes)} bytes")
            print(f"[订单二维码] 📤 - 图片格式: {data_format}")

            # 🎯 通过事件总线发送组合数据
            from utils.signals import event_bus
            event_bus.show_qrcode.emit(combined_data)

            print(f"[订单二维码] ✅ 组合显示数据已发送到主窗口")

        except Exception as e:
            print(f"[订单二维码] ❌ 显示组合信息错误: {e}")
            import traceback
            traceback.print_exc()

    def _generate_and_show_ticket_qrcode(self, order_no, ticket_code, detail_data, cinema_id):
        """生成并显示取票码二维码"""
        try:
            print(f"[订单二维码] 🎯 开始生成取票码二维码")
            print(f"[订单二维码] 📋 取票码: {ticket_code}")

            # 🔧 直接导入完整二维码生成器（根据诊断结果，模块是可用的）
            from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image
            print(f"[订单二维码] ✅ 二维码生成器导入成功")

            # 🎯 生成二维码图片
            qr_bytes = generate_ticket_qrcode(ticket_code, detail_data)

            if qr_bytes:
                print(f"[订单二维码] ✅ 取票码二维码生成成功: {len(qr_bytes)} bytes")

                # 🎯 保存二维码图片到本地
                save_path = save_qrcode_image(qr_bytes, order_no, cinema_id)
                if save_path:
                    print(f"[订单二维码] 💾 二维码图片已保存: {save_path}")

                # 🎯 创建组合显示数据
                combined_data = {
                    'order_no': order_no,
                    'qr_bytes': qr_bytes,
                    'qr_path': save_path,  # 🎯 添加图片路径
                    'data_size': len(qr_bytes),
                    'data_format': 'PNG',
                    'display_type': 'generated_qrcode',  # 标识为生成的二维码
                    'ticket_code': ticket_code,
                    'film_name': detail_data.get('filmName', ''),
                    'show_time': detail_data.get('showTime', ''),
                    'hall_name': detail_data.get('hallName', ''),
                    'seat_info': detail_data.get('seatInfo', ''),
                    'cinema_name': detail_data.get('cinemaName', ''),
                    'is_generated': True  # 标识这是自主生成的二维码
                }

                print(f"[订单二维码] 📤 发送生成的二维码数据到主窗口:")
                print(f"[订单二维码] 📤 - 订单号: {order_no}")
                print(f"[订单二维码] 📤 - 取票码: {ticket_code}")
                print(f"[订单二维码] 📤 - 图片大小: {len(qr_bytes)} bytes")
                print(f"[订单二维码] 📤 - 显示类型: 生成的取票码二维码")

                # 🎯 通过事件总线发送数据
                from utils.signals import event_bus
                event_bus.show_qrcode.emit(combined_data)

                print(f"[订单二维码] ✅ 生成的二维码数据已发送到主窗口显示")

            else:
                print(f"[订单二维码] ❌ 取票码二维码生成失败")
                # 降级显示文本信息
                self._show_ticket_code_text(order_no, ticket_code, detail_data)

        except Exception as e:
            print(f"[订单二维码] ❌ 生成取票码二维码错误: {e}")
            import traceback
            traceback.print_exc()
            # 降级显示文本信息
            self._show_ticket_code_text(order_no, ticket_code, detail_data)

    def _show_order_context_menu(self, position):
        """显示订单右键菜单"""
        try:
            item = self.order_table.itemAt(position)
            if not item:
                return

            row = item.row()
            if not hasattr(self, 'order_data_cache') or row >= len(self.order_data_cache):
                return

            order = self.order_data_cache[row]
            status = order.get('orderStatus', -1)

            # 创建右键菜单
            menu = QMenu(self)

            # 查看详情（所有订单都可以）
            detail_action = menu.addAction("查看详情")
            detail_action.triggered.connect(lambda: self._show_order_detail_dialog(order))

            # 取消订单（只有待支付订单可以）
            if status == 0:  # 待支付
                menu.addSeparator()
                cancel_action = menu.addAction("取消订单")
                cancel_action.triggered.connect(lambda: self._cancel_order(order))

            # 查看二维码（已支付订单可以）
            status_text = order.get('orderS', '')
            allowed_statuses = ['已完成', '待使用', '已支付', '已付款', '已取票']
            if any(status in status_text for status in allowed_statuses):
                menu.addSeparator()
                qr_action = menu.addAction("查看取票码")
                qr_action.triggered.connect(lambda: self._show_order_qrcode_from_menu(order))

            # 显示菜单
            menu.exec_(self.order_table.mapToGlobal(position))

        except Exception as e:
            print(f"[订单菜单] 右键菜单错误: {e}")
            import traceback
            traceback.print_exc()

    def _show_order_detail_dialog(self, order):
        """显示订单详情对话框"""
        try:
            account = getattr(self, 'current_account', None)
            if not account:
                MessageManager.show_error(self, "错误", "缺少账号信息", auto_close=False)
                return

            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                MessageManager.show_error(self, "错误", "缺少影院信息", auto_close=False)
                return

            # 获取订单号
            order_no = (order.get('orderNo') or
                       order.get('orderno') or
                       order.get('order_id') or
                       order.get('orderid'))

            if not order_no:
                MessageManager.show_error(self, "错误", "订单号不存在", auto_close=False)
                return

            # 调用订单详情API
            from services.order_api import get_order_detail

            params = {
                'orderno': order_no,
                'groupid': '',
                'cinemaid': cinemaid,
                'cardno': account.get('cardno', ''),
                'userid': account['userid'],
                'openid': account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account['token'],
                'source': '2'
            }

            print(f"[订单详情] 获取订单详情: {order_no}")
            result = get_order_detail(params)

            if result and result.get('resultCode') == '0':
                detail_data = result.get('resultData', {})
                self._display_order_detail(detail_data, order_no)
            else:
                error_msg = result.get('resultDesc', '获取订单详情失败') if result else '网络错误'
                MessageManager.show_error(self, "获取失败", error_msg, auto_close=False)

        except Exception as e:
            print(f"[订单详情] 获取详情错误: {e}")
            import traceback
            traceback.print_exc()
            MessageManager.show_error(self, "错误", f"获取订单详情时出错：{str(e)}", auto_close=False)

    def _cancel_order(self, order):
        """取消订单"""
        try:
            account = getattr(self, 'current_account', None)
            if not account:
                MessageManager.show_error(self, "错误", "缺少账号信息", auto_close=False)
                return

            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                MessageManager.show_error(self, "错误", "缺少影院信息", auto_close=False)
                return

            # 获取订单号
            order_no = (order.get('orderNo') or
                       order.get('orderno') or
                       order.get('order_id') or
                       order.get('orderid'))

            if not order_no:
                MessageManager.show_error(self, "错误", "订单号不存在", auto_close=False)
                return

            # 确认取消
            reply = QMessageBox.question(self, "确认取消",
                                       f"确定要取消订单 {order_no} 吗？",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

            if reply != QMessageBox.Yes:
                return

            # 调用取消订单API
            from services.order_api import cancel_order

            params = {
                'orderno': order_no,
                'groupid': '',
                'cinemaid': cinemaid,
                'cardno': account.get('cardno', ''),
                'userid': account['userid'],
                'openid': account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account['token'],
                'source': '2'
            }

            print(f"[取消订单] 取消订单: {order_no}")
            result = cancel_order(params)

            if result and result.get('resultCode') == '0':
                print(f"[取消订单] 订单取消成功: {order_no}")
                MessageManager.show_success(self, "取消成功", "订单已成功取消", auto_close=True)
                # 自动刷新订单列表
                self._on_refresh_orders()
            else:
                error_msg = result.get('resultDesc', '取消订单失败') if result else '网络错误'
                MessageManager.show_error(self, "取消失败", error_msg, auto_close=False)

        except Exception as e:
            print(f"[取消订单] 取消订单错误: {e}")
            import traceback
            traceback.print_exc()
            MessageManager.show_error(self, "错误", f"取消订单时出错：{str(e)}", auto_close=False)

    def _show_order_qrcode_from_menu(self, order):
        """从右键菜单显示订单二维码"""
        try:
            # 获取订单号
            order_no = order.get('orderno')
            if not order_no:
                print(f"[订单二维码] 订单号不存在")
                return

            # 获取影院ID
            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                print(f"[订单二维码] 影院ID不存在")
                return

            print(f"[订单二维码] 右键菜单获取订单 {order_no} 的二维码")

            # 🎯 调用统一的二维码获取方法
            self._get_and_show_qrcode(order_no, cinemaid)

        except Exception as e:
            print(f"[订单二维码] 右键菜单获取二维码错误: {e}")
            import traceback
            traceback.print_exc()

    def _display_order_detail(self, detail_data, order_no):
        """显示订单详情信息"""
        try:
            # 构建详情文本
            details = f"订单详情\n{'='*30}\n\n"
            details += f"订单号: {order_no}\n\n"

            # 影片信息
            movie = detail_data.get('movieName', detail_data.get('movie', '未知影片'))
            details += f"影片: {movie}\n\n"

            # 时间信息
            show_time = detail_data.get('showTime', '')
            if not show_time:
                date = detail_data.get('date', '')
                session = detail_data.get('session', '')
                if date and session:
                    show_time = f"{date} {session}"
            details += f"时间: {show_time}\n\n"

            # 影厅信息
            cinema = detail_data.get('cinemaName', detail_data.get('cinema', '未知影院'))
            hall = detail_data.get('hallName', detail_data.get('hall_name', ''))
            if hall:
                details += f"影厅: {hall}\n\n"
            else:
                details += f"影院: {cinema}\n\n"

            # 座位信息
            seats = detail_data.get('seats', [])
            if isinstance(seats, list) and seats:
                seat_str = " ".join(seats)
                details += f"座位: {seat_str}\n\n"
            else:
                details += f"座位: {seats}\n\n"

            # 价格信息
            amount = detail_data.get('amount', detail_data.get('totalPrice', 0))
            details += f"金额: ¥{amount}\n\n"

            # 状态信息
            status = self.get_order_status_text(detail_data.get('orderStatus', -1))
            details += f"状态: {status}"

            # 显示详情对话框
            dialog = QMessageBox(self)
            dialog.setWindowTitle("订单详情")
            dialog.setText(details)
            dialog.setStandardButtons(QMessageBox.Ok)
            dialog.exec_()

        except Exception as e:
            print(f"[订单详情] 显示详情错误: {e}")
            import traceback
            traceback.print_exc()

    def _build_cinema_tab(self):
        """构建影院Tab页面"""
        layout = QVBoxLayout(self.cinema_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 操作按钮区
        button_layout = QHBoxLayout()
        
        add_cinema_btn = ClassicButton("添加影院", "success")
        add_cinema_btn.clicked.connect(self._on_add_cinema)
        button_layout.addWidget(add_cinema_btn)
        
        delete_cinema_btn = ClassicButton("删除影院", "danger")
        delete_cinema_btn.clicked.connect(self._on_delete_cinema)
        button_layout.addWidget(delete_cinema_btn)
        
        refresh_cinema_btn = ClassicButton("刷新列表", "default")
        refresh_cinema_btn.clicked.connect(self._load_cinema_list)
        button_layout.addWidget(refresh_cinema_btn)

        # 🆕 添加影院采集按钮
        cinema_collect_btn = ClassicButton("影院采集", "primary")
        cinema_collect_btn.clicked.connect(self._on_cinema_collect)
        button_layout.addWidget(cinema_collect_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # 影院列表表格
        self.cinema_table = ClassicTableWidget()
        self.cinema_table.setColumnCount(3)
        self.cinema_table.setHorizontalHeaderLabels(["影院名称", "影院ID", "操作"])
        
        # 设置列宽
        header = self.cinema_table.horizontalHeader()
        header.resizeSection(0, 200)  # 影院名称
        header.resizeSection(1, 150)  # 影院ID
        header.resizeSection(2, 100)  # 操作
        
        # 设置行高
        self.cinema_table.verticalHeader().setDefaultSectionSize(36)
        
        layout.addWidget(self.cinema_table)
        
        # 统计信息
        self.cinema_stats_label = ClassicLabel("影院统计信息加载中...")
        self.cinema_stats_label.setStyleSheet("QLabel { color: #666; font-size: 12px; }")
        layout.addWidget(self.cinema_stats_label)
        
        # 加载影院数据
        self._load_cinema_list()

    def _on_cinema_collect(self):
        """🆕 影院采集功能 - 打开curl命令输入对话框"""
        try:
            print("[影院采集] 🚀 启动影院采集功能")

            # 导入curl参数提取对话框
            from ui.dialogs.auto_parameter_extractor import AutoParameterExtractor

            # 创建并显示对话框
            extractor_dialog = AutoParameterExtractor(self)
            extractor_dialog.setWindowTitle("影院采集 - curl命令解析")

            # 设置对话框的回调函数，用于处理采集完成后的刷新
            extractor_dialog.collection_completed = self._on_collection_completed

            # 显示对话框
            result = extractor_dialog.exec_()

            if result == QDialog.Accepted:
                print("[影院采集] ✅ 用户确认采集操作")
            else:
                print("[影院采集] ❌ 用户取消采集操作")

        except Exception as e:
            print(f"[影院采集] 启动采集功能错误: {e}")
            QMessageBox.critical(
                self,
                "启动失败",
                f"启动影院采集功能时发生错误：\n{str(e)}\n\n请检查系统配置。"
            )

    def _on_collection_completed(self, success: bool, message: str = ""):
        """🆕 影院采集完成后的回调处理"""
        try:
            print(f"[影院采集] 📋 采集完成回调: success={success}, message={message}")

            if success:
                # 🆕 采集成功后刷新所有相关界面
                print("[影院采集] 🔄 开始刷新界面...")

                # 1. 刷新影院表格显示
                self._refresh_cinema_table_display()

                # 2. 更新统计信息
                self._update_cinema_stats()

                # 3. 刷新出票Tab的影院列表
                self._refresh_ticket_tab_cinema_list()

                # 4. 显示成功提示
                QMessageBox.information(
                    self,
                    "采集成功",
                    f"🎉 影院采集完成！\n\n{message}\n\n所有相关界面已自动刷新。"
                )

                print("[影院采集] ✅ 界面刷新完成")

            else:
                # 采集失败，显示错误信息
                QMessageBox.warning(
                    self,
                    "采集失败",
                    f"❌ 影院采集失败：\n\n{message}\n\n请检查curl命令格式或网络连接。"
                )

        except Exception as e:
            print(f"[影院采集] 采集完成回调错误: {e}")
            QMessageBox.critical(
                self,
                "回调错误",
                f"处理采集结果时发生错误：\n{str(e)}"
            )

    def _format_session_text(self, session):
        """格式化场次显示文本 - 简洁版本"""
        try:
            # 🆕 简化显示格式，只显示核心信息
            time_info = session.get('q', '')  # 时间
            hall_info = session.get('t', '')  # 影厅名
            price_info = session.get('tbprice', 0)  # 票价
            
            # 简化时间显示 - 只显示时分，去掉秒
            if time_info and ':' in time_info:
                try:
                    # 提取时分部分
                    time_parts = time_info.split(':')
                    if len(time_parts) >= 2:
                        time_display = f"{time_parts[0]}:{time_parts[1]}"
                    else:
                        time_display = time_info
                except:
                    time_display = time_info
            else:
                time_display = time_info or '未知时间'
            
            # 简化影厅显示
            hall_display = hall_info or '影厅'
            
            # 价格显示
            if price_info and price_info > 0:
                price_display = f"¥{price_info}"
            else:
                price_display = "¥-"
            
            # 🆕 紧凑格式：时间 影厅 价格
            session_text = f"{time_display} {hall_display} {price_display}"
            
            print(f"[Tab管理器] 格式化场次: {session_text}")
            return session_text
            
        except Exception as e:
            print(f"[Tab管理器] 格式化场次错误: {e}")
            print(f"[Tab管理器] 原始场次数据: {session}")
            return "场次信息错误"

    # 🆕 ========== 六级联动方法（移除系统选择）==========

    def _init_cascade(self):
        """初始化联动（直接从城市开始）"""
        try:
            print("[Tab管理器] 🚀 初始化沃美影院联动系统")

            # 直接加载沃美系统的城市列表
            self._load_cities_for_womei()

            print(f"[Tab管理器] ✅ 沃美影院联动初始化完成")

        except Exception as e:
            print(f"[Tab管理器] ❌ 联动初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def _get_current_token(self):
        """从accounts.json文件获取当前token"""
        try:
            import json
            import os

            # 优先使用当前账号的token
            if hasattr(self, 'current_account') and self.current_account:
                account_token = self.current_account.get('token')
                if account_token:
                    return account_token

            # 从accounts.json文件加载token
            accounts_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'accounts.json')
            if os.path.exists(accounts_file):
                with open(accounts_file, "r", encoding="utf-8") as f:
                    accounts = json.load(f)

                if accounts and len(accounts) > 0:
                    return accounts[0].get('token', '1bb7e07bb7c832f17322b61c790aeed2')

            # 备用token
            return '1bb7e07bb7c832f17322b61c790aeed2'

        except Exception as e:
            print(f"[Tab管理器] 获取token失败: {e}")
            return '1bb7e07bb7c832f17322b61c790aeed2'

    def _load_cities_for_womei(self):
        """加载沃美系统的城市列表"""
        try:
            print("[城市调试] ==================== 开始加载沃美城市列表 ====================")

            # 更新城市下拉框状态
            if hasattr(self, 'city_combo'):
                self.city_combo.clear()
                self.city_combo.addItem("加载中...")
                self.city_combo.setEnabled(True)  # 保持启用状态

            # 使用沃美电影服务获取城市列表
            from services.womei_film_service import get_womei_film_service

            # 🔧 修正：从accounts.json文件获取最新token
            token = self._get_current_token()
            print(f"[城市调试] 使用token: {token[:20]}...")

            # 🔧 详细的API调用调试
            print(f"[城市调试] 创建沃美电影服务实例...")
            film_service = get_womei_film_service(token)

            print(f"[城市调试] 调用城市API: get_cities()")
            cities_result = film_service.get_cities()

            # 🔧 详细的响应调试
            print(f"[城市调试] API响应结果:")
            print(f"  - success: {cities_result.get('success')}")
            print(f"  - total: {cities_result.get('total', 'N/A')}")
            print(f"  - error: {cities_result.get('error', 'N/A')}")

            if cities_result.get('success'):
                cities = cities_result.get('cities', [])
                print(f"[城市调试] ✅ 成功获取城市数据:")
                print(f"  - 城市数量: {len(cities)}")

                # 🔧 显示前5个城市的详细信息
                for i, city in enumerate(cities[:5]):
                    city_name = city.get('city_name', '未知城市')
                    city_id = city.get('city_id', 'N/A')
                    cinemas_count = len(city.get('cinemas', []))
                    print(f"  - 城市 {i+1}: {city_name} (ID: {city_id}, 影院数: {cinemas_count})")

                if len(cities) > 5:
                    print(f"  - ... 还有 {len(cities) - 5} 个城市")

                # 保存数据并更新下拉框
                self.cities_data = cities
                self._update_city_combo()
                print(f"[城市调试] ✅ 城市下拉框更新完成")

                # 🆕 启用自动选择第一个城市的机制
                if len(cities) > 0:
                    first_city = cities[0]
                    city_name = first_city.get('city_name', '未知城市')
                    print(f"[城市调试] 🚀 启用自动选择城市机制，将自动选择第一个城市")
                    print(f"[城市调试] 第一个城市: {city_name}（即将自动选择）")

                    # 延迟自动选择，确保下拉框更新完成
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(100, lambda: self._auto_select_first_city(city_name))

            else:
                error = cities_result.get('error', '未知错误')
                print(f"[城市调试] ❌ 加载城市失败: {error}")
                if hasattr(self, 'city_combo'):
                    self.city_combo.clear()
                    self.city_combo.addItem("加载失败")

        except Exception as e:
            print(f"[城市调试] ❌ 加载沃美城市列表异常: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'city_combo'):
                self.city_combo.clear()
                self.city_combo.addItem("加载失败")

    def _auto_select_first_city(self, city_name: str):
        """自动选择第一个城市"""
        try:
            if hasattr(self, 'city_combo') and self.city_combo.count() > 1:
                # 查找城市在下拉框中的索引
                for i in range(self.city_combo.count()):
                    if self.city_combo.itemText(i) == city_name:
                        self.city_combo.setCurrentIndex(i)
                        print(f"[城市调试] ✅ 自动选择城市完成: {city_name}")
                        break
        except Exception as e:
            print(f"[城市调试] 自动选择城市失败: {e}")

    def _on_city_changed(self, city_name: str):
        """城市选择变化处理"""
        try:
            if city_name in ["加载中...", "请选择城市", "加载失败"] or not city_name:
                self._reset_cascade_from_level(2)  # 重置从影院开始的所有级别
                return

            # 查找对应的城市
            selected_city = None
            for city in self.cities_data:
                if city.get('city_name') == city_name:  # 沃美系统使用city_name字段
                    selected_city = city
                    break

            if not selected_city:
                print(f"[Tab管理器] 未找到城市: {city_name}")
                return

            self.current_city = selected_city
            print(f"[Tab管理器] 🏙️ 城市选择: {city_name} (ID: {selected_city.get('city_id')})")

            # 重置下级选择
            self._reset_cascade_from_level(2)

            # 加载影院列表
            self._load_cinemas_for_city(selected_city)

        except Exception as e:
            print(f"[Tab管理器] 城市选择处理失败: {e}")
            import traceback
            traceback.print_exc()

    def _reset_cascade_from_level(self, level: int):
        """从指定级别开始重置联动选择"""
        try:
            if level <= 1:  # 重置城市及以下
                if hasattr(self, 'city_combo'):
                    self.city_combo.clear()
                    self.city_combo.addItem("请选择城市")
                    self.city_combo.setEnabled(True)
                self.current_city = None
                self.cities_data = []

            if level <= 2:  # 重置影院及以下
                if hasattr(self, 'cinema_combo'):
                    self.cinema_combo.clear()
                    self.cinema_combo.addItem("请先选择城市")
                    self.cinema_combo.setEnabled(False)
                self.current_cinema_data = None
                self.cinemas_data = []

            if level <= 3:  # 重置电影及以下
                if hasattr(self, 'movie_combo'):
                    self.movie_combo.clear()
                    self.movie_combo.addItem("请先选择影院")
                    self.movie_combo.setEnabled(False)
                self.current_movie = None
                self.movies_data = []

            if level <= 4:  # 重置日期及以下
                if hasattr(self, 'date_combo'):
                    self.date_combo.clear()
                    self.date_combo.addItem("请先选择影片")
                    self.date_combo.setEnabled(False)
                self.current_date = None
                self.dates_data = []

            if level <= 5:  # 重置场次及以下
                if hasattr(self, 'session_combo'):
                    self.session_combo.clear()
                    self.session_combo.addItem("请先选择日期")
                    self.session_combo.setEnabled(False)
                self.current_session = None
                self.sessions_data = []

            # 禁用选座按钮
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)

        except Exception as e:
            print(f"[Tab管理器] 重置联动失败: {e}")



    def _update_city_combo(self):
        """更新城市下拉框（修复信号冲突问题）"""
        try:
            print(f"[城市调试] 开始更新城市下拉框...")

            if not hasattr(self, 'city_combo'):
                print(f"[城市调试] ❌ 未找到city_combo属性")
                return

            # 🔧 暂时断开信号连接，防止更新过程中触发信号
            self.city_combo.currentTextChanged.disconnect()

            # 清空并重新填充城市下拉框
            self.city_combo.clear()
            self.city_combo.addItem("请选择城市")

            # 添加城市数据
            for city in self.cities_data:
                city_name = city.get('city_name', '未知城市')  # 沃美系统使用city_name字段
                self.city_combo.addItem(city_name)

            # 启用下拉框并重新连接信号
            self.city_combo.setEnabled(True)
            self.city_combo.currentTextChanged.connect(self._on_city_changed)

            print(f"[Tab管理器] 城市下拉框已更新，共 {len(self.cities_data)} 个城市")

        except Exception as e:
            print(f"[Tab管理器] 更新城市下拉框失败: {e}")

            # 确保信号重新连接
            try:
                self.city_combo.currentTextChanged.connect(self._on_city_changed)
            except:
                pass

    def _load_cinemas_for_city(self, city_data):
        """为指定城市加载影院列表 - 完全通过沃美API动态获取"""
        try:
            city_name = city_data.get('city_name', '未知城市')
            city_id = city_data.get('city_id', '')
            print(f"[影院调试] ==================== 开始加载城市影院列表 ====================")
            print(f"[影院调试] 城市: {city_name} (ID: {city_id})")

            # 更新影院下拉框状态
            if hasattr(self, 'cinema_combo'):
                self.cinema_combo.clear()
                self.cinema_combo.addItem("加载中...")
                self.cinema_combo.setEnabled(False)

            # 🔧 完全移除对本地cinema_info.json的依赖，直接使用城市数据中的影院信息
            cinemas = city_data.get('cinemas', [])
            print(f"[影院调试] 城市数据中的影院数量: {len(cinemas)}")

            if cinemas:
                # 🔧 显示前3个影院的详细信息
                print(f"[影院调试] ✅ 从城市数据获取影院列表:")
                for i, cinema in enumerate(cinemas[:3]):
                    cinema_name = cinema.get('cinema_name', '未知影院')
                    cinema_id = cinema.get('cinema_id', 'N/A')
                    print(f"  - 影院 {i+1}: {cinema_name} (ID: {cinema_id})")

                if len(cinemas) > 3:
                    print(f"  - ... 还有 {len(cinemas) - 3} 个影院")

                # 使用城市数据中的影院列表
                self.cinemas_data = cinemas
                self._update_cinema_combo()
                print(f"[影院调试] ✅ 影院下拉框更新完成，共 {len(cinemas)} 个影院")

                # 🆕 启用自动选择第一个影院的机制
                if len(cinemas) > 0:
                    first_cinema = cinemas[0]
                    cinema_name = first_cinema.get('cinema_name', '未知影院')
                    print(f"[影院调试] 🚀 启用自动选择影院机制，将自动选择第一个影院")
                    print(f"[影院调试] 第一个影院: {cinema_name}（即将自动选择）")

                    # 延迟自动选择，确保下拉框更新完成
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(200, lambda: self._auto_select_first_cinema(cinema_name))
            else:
                # 如果城市数据中没有影院，尝试调用影院API
                print(f"[Tab管理器] 城市数据中无影院，尝试调用影院API")

                from services.womei_film_service import get_womei_film_service
                token = self._get_current_token()
                film_service = get_womei_film_service(token)

                # 获取所有影院，然后筛选该城市的影院
                cinemas_result = film_service.get_cinemas()

                if cinemas_result.get('success'):
                    all_cinemas = cinemas_result.get('cinemas', [])
                    city_id = city_data.get('city_id')

                    # 筛选该城市的影院
                    city_cinemas = []
                    for cinema in all_cinemas:
                        if cinema.get('city_id') == city_id:
                            city_cinemas.append(cinema)

                    if city_cinemas:
                        self.cinemas_data = city_cinemas
                        self._update_cinema_combo()
                        print(f"[Tab管理器] ✅ API筛选到 {len(city_cinemas)} 个影院")
                    else:
                        print(f"[Tab管理器] ❌ 该城市无影院")
                        self._set_cinema_combo_error("该城市暂无影院")
                else:
                    error = cinemas_result.get('error', '未知错误')
                    print(f"[Tab管理器] ❌ 影院API失败: {error}")
                    self._set_cinema_combo_error(f"加载影院失败: {error}")

        except Exception as e:
            print(f"[Tab管理器] 加载影院列表失败: {e}")
            import traceback
            traceback.print_exc()
            self._set_cinema_combo_error("加载影院异常")

    def _auto_select_first_cinema(self, cinema_name: str):
        """自动选择第一个影院"""
        try:
            if hasattr(self, 'cinema_combo') and self.cinema_combo.count() > 1:
                # 查找影院在下拉框中的索引
                for i in range(self.cinema_combo.count()):
                    if self.cinema_combo.itemText(i) == cinema_name:
                        self.cinema_combo.setCurrentIndex(i)
                        print(f"[Tab管理器] ✅ 自动选择影院完成: {cinema_name}")
                        break
        except Exception as e:
            print(f"[Tab管理器] 自动选择影院失败: {e}")

    def _auto_select_first_movie(self, movie_name: str):
        """自动选择第一个电影"""
        try:
            if hasattr(self, 'movie_combo') and self.movie_combo.count() > 1:
                # 查找电影在下拉框中的索引
                for i in range(self.movie_combo.count()):
                    if self.movie_combo.itemText(i) == movie_name:
                        self.movie_combo.setCurrentIndex(i)
                        print(f"[Tab管理器] ✅ 自动选择电影完成: {movie_name}")
                        break
        except Exception as e:
            print(f"[Tab管理器] 自动选择电影失败: {e}")

    def _auto_select_first_date(self, date_text: str):
        """自动选择第一个日期"""
        try:
            if hasattr(self, 'date_combo') and self.date_combo.count() > 1:
                # 查找日期在下拉框中的索引
                for i in range(self.date_combo.count()):
                    if self.date_combo.itemText(i) == date_text:
                        self.date_combo.setCurrentIndex(i)
                        print(f"[Tab管理器] ✅ 自动选择日期完成: {date_text}")
                        break
        except Exception as e:
            print(f"[Tab管理器] 自动选择日期失败: {e}")

    def _auto_select_first_session(self, session_text: str):
        """自动选择第一个场次"""
        try:
            if hasattr(self, 'session_combo') and self.session_combo.count() > 1:
                # 查找场次在下拉框中的索引
                for i in range(self.session_combo.count()):
                    if self.session_combo.itemText(i) == session_text:
                        self.session_combo.setCurrentIndex(i)
                        print(f"[Tab管理器] ✅ 自动选择场次完成: {session_text}")
                        break
        except Exception as e:
            print(f"[Tab管理器] 自动选择场次失败: {e}")

    def _set_cinema_combo_error(self, error_msg):
        """设置影院下拉框错误状态"""
        if hasattr(self, 'cinema_combo'):
            self.cinema_combo.clear()
            self.cinema_combo.addItem(error_msg)
            self.cinema_combo.setEnabled(True)

        # 同时重置下级联动
        self._reset_cascade_from_level(3)

    def _update_cinema_combo(self):
        """更新影院下拉框（沃美数据格式）"""
        try:
            if not hasattr(self, 'cinema_combo'):
                return

            self.cinema_combo.clear()
            self.cinema_combo.addItem("请选择影院")

            for cinema in self.cinemas_data:
                # 沃美系统使用cinema_name字段
                cinema_name = cinema.get('cinema_name', '未知影院')
                self.cinema_combo.addItem(cinema_name)

            self.cinema_combo.setEnabled(True)
            print(f"[Tab管理器] 影院下拉框已更新，共 {len(self.cinemas_data)} 个沃美影院")

            # 显示影院详情用于调试
            if self.cinemas_data:
                first_cinema = self.cinemas_data[0]
                print(f"[Tab管理器] 第一个影院示例: {first_cinema.get('cinema_name')} (ID: {first_cinema.get('cinema_id')})")

        except Exception as e:
            print(f"[Tab管理器] 更新影院下拉框失败: {e}")
            self._set_cinema_combo_error("更新影院列表失败")
