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
        """构建影院选择区域"""
        layout = QVBoxLayout(parent_group)
        layout.setContentsMargins(0, 20, 10, 10)  # 🆕 左边距改为0，让下拉框与账号信息对齐
        layout.setSpacing(5)  # 🆕 减少垂直间距，让整体更紧密
        
        # 当前账号显示
        self.current_account_label = ClassicLabel("当前账号: 未选择", "info")
        layout.addWidget(self.current_account_label)
        
        # 影院选择 - 🆕 简化布局，与账号信息区域左边缘对齐
        cinema_layout = QHBoxLayout()
        cinema_layout.setContentsMargins(0, 0, 0, 0)
        cinema_label = ClassicLabel("影院:")
        cinema_label.setFixedWidth(30)
        cinema_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cinema_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.cinema_combo = ClassicComboBox()
        self.cinema_combo.addItem("加载中...")
        # 🆕 设置下拉框宽度
        self.cinema_combo.setFixedWidth(320)
        cinema_layout.addWidget(cinema_label)
        cinema_layout.addSpacing(5)
        cinema_layout.addWidget(self.cinema_combo)
        cinema_layout.addStretch()
        layout.addLayout(cinema_layout)
        
        # 影片选择 - 🆕 简化布局，与账号信息区域左边缘对齐
        movie_layout = QHBoxLayout()
        movie_layout.setContentsMargins(0, 0, 0, 0)
        movie_label = ClassicLabel("影片:")
        movie_label.setFixedWidth(30)
        movie_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        movie_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.movie_combo = ClassicComboBox()
        self.movie_combo.addItems(["请先选择影院"])
        # 🆕 设置下拉框宽度
        self.movie_combo.setFixedWidth(320)
        movie_layout.addWidget(movie_label)
        movie_layout.addSpacing(5)
        movie_layout.addWidget(self.movie_combo)
        movie_layout.addStretch()
        layout.addLayout(movie_layout)
        
        # 日期选择 - 🆕 简化布局，与账号信息区域左边缘对齐
        date_layout = QHBoxLayout()
        date_layout.setContentsMargins(0, 0, 0, 0)
        date_label = ClassicLabel("日期:")
        date_label.setFixedWidth(30)
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        date_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.date_combo = ClassicComboBox()
        self.date_combo.addItems(["请先选择影片"])
        # 🆕 设置下拉框宽度
        self.date_combo.setFixedWidth(320)
        date_layout.addWidget(date_label)
        date_layout.addSpacing(5)
        date_layout.addWidget(self.date_combo)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # 场次选择 - 🆕 简化布局，与账号信息区域左边缘对齐
        session_layout = QHBoxLayout()
        session_layout.setContentsMargins(0, 0, 0, 0)
        session_label = ClassicLabel("场次:")
        session_label.setFixedWidth(30)
        session_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        session_label.setStyleSheet("QLabel { color: #333333; font: 12px 'Microsoft YaHei'; background: transparent; }")
        self.session_combo = ClassicComboBox()
        self.session_combo.addItems(["请先选择日期"])
        # 🆕 设置下拉框宽度
        self.session_combo.setFixedWidth(320)
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
        
        # 添加进度提示
        MessageManager.show_info(self, "开始绑定", f"即将绑定{len(coupon_codes)}张券，每张券间隔0.2秒，请稍候...", auto_close=True)
        
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
        
        # 完成提示
        if success > 0:
            MessageManager.show_success(self, "绑定完成", f"成功绑定{success}张券，失败{fail}张券", auto_close=True)
        else:
            MessageManager.show_error(self, "绑定失败", f"所有{fail}张券绑定失败，请检查账号状态和券号", auto_close=False)

    def copy_bind_log(self):
        """复制绑定日志"""
        log = self.bind_log_text.toPlainText().strip()
        if log:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(log)
            MessageManager.show_success(self, "复制成功", "日志内容已复制到剪贴板！", auto_close=True)
        else:
            MessageManager.show_error(self, "无内容", "没有日志内容可复制", auto_close=False)

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
                
                info_text = (f"当前账号：{account['userid']}\n"
                           f"影院：{cinema_name}\n"
                           f"余额：{account.get('balance', 0)}  积分：{account.get('score', 0)}")
                self.bind_account_info.setText(info_text)
                self.bind_account_info.setStyleSheet("QLabel { color: blue; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")
            else:
                self.bind_account_info.setText("请先选择账号和影院")
                self.bind_account_info.setStyleSheet("QLabel { color: red; background-color: #fff; padding: 10px; border: 1px solid #ddd; }")

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
        
        # 加载示例订单数据
        self._load_sample_orders()

    def _on_add_cinema(self):
        """添加影院功能 - 直接从源代码复制"""
        # 创建添加影院对话框
        add_dialog = QDialog(self)
        add_dialog.setWindowTitle("添加影院")
        add_dialog.setFixedSize(400, 300)
        
        # 对话框布局
        layout = QVBoxLayout(add_dialog)
        
        # 影院名称输入
        name_layout = QHBoxLayout()
        name_layout.addWidget(ClassicLabel("影院名称:"))
        name_input = ClassicLineEdit()
        name_input.setPlaceholderText("例如：万友影城")
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # 域名输入
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(ClassicLabel("API域名:"))
        domain_input = ClassicLineEdit()
        domain_input.setPlaceholderText("例如：api.cinema.com")
        domain_layout.addWidget(domain_input)
        layout.addLayout(domain_layout)
        
        # 影院ID输入
        id_layout = QHBoxLayout()
        id_layout.addWidget(ClassicLabel("影院ID:"))
        id_input = ClassicLineEdit()
        id_input.setPlaceholderText("例如：11b7e4bcc265")
        id_layout.addWidget(id_input)
        layout.addLayout(id_layout)
        
        # 按钮
        button_layout = QHBoxLayout()
        confirm_btn = ClassicButton("确认添加", "success")
        cancel_btn = ClassicButton("取消", "default")
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # 事件绑定
        def validate_and_add():
            name = name_input.text().strip()
            domain = domain_input.text().strip()
            cinema_id = id_input.text().strip()
            
            # 验证输入
            if not all([name, domain, cinema_id]):
                QMessageBox.warning(add_dialog, "输入错误", "请填写完整的影院信息！")
                return
                
            # 验证域名格式
            if not domain.startswith(('http://', 'https://')):
                domain = f"https://{domain}"
                
            # 验证影院ID格式
            if len(cinema_id) != 12:
                QMessageBox.warning(add_dialog, "格式错误", "影院ID必须是12位字符！")
                return
                
            # 添加到影院列表
            self.add_cinema_to_list(name, domain, cinema_id)
            add_dialog.accept()
        
        confirm_btn.clicked.connect(validate_and_add)
        cancel_btn.clicked.connect(add_dialog.reject)
        
        add_dialog.exec_()

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
        """加载真实影院数据"""
        try:
            # 从影院管理器加载真实数据
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()
            
            self.cinema_combo.clear()
            self.cinemas_data = cinemas  # 保存完整的影院数据
            
            if cinemas:
                print(f"[Tab管理器] 加载了 {len(cinemas)} 个真实影院")
                for cinema in cinemas:
                    cinema_name = cinema.get('cinemaShortName', '未知影院')
                    self.cinema_combo.addItem(cinema_name)
            else:
                print("[Tab管理器] 未找到影院数据，加载示例数据")
                self.cinema_combo.addItems([
                    "华夏优加金太都会",
                    "深影国际影城(佐伦虹湾购物中心店)",
                    "深圳万友影城BCMall店"
                ])
                
        except Exception as e:
            print(f"[Tab管理器] 加载影院数据错误: {e}")
            # 加载示例数据作为后备
            self.cinema_combo.clear()
            self.cinema_combo.addItems([
                "华夏优加金太都会", 
                "深影国际影城(佐伦虹湾购物中心店)",
                "深圳万友影城BCMall店"
            ])
    
    def _load_sample_orders(self):
        """加载示例订单数据"""
        try:
            sample_orders = [
                {
                    "movie": "阿凡达：水之道",
                    "cinema": "深影国际影城(佐伦虹湾购物中心店)",
                    "status": "已完成",
                    "order_id": "ORDER2024122701"
                },
                {
                    "movie": "流浪地球2", 
                    "cinema": "深影国际影城(佐伦虹湾购物中心店)",
                    "status": "待支付",
                    "order_id": "ORDER2024122702"
                },
                {
                    "movie": "满江红",
                    "cinema": "华夏优加金太都会",
                    "status": "已取消",
                    "order_id": "ORDER2024122703"
                }
            ]
            
            self.order_table.setRowCount(len(sample_orders))
            for i, order in enumerate(sample_orders):
                self.order_table.setItem(i, 0, self.order_table.__class__.createItem(order["movie"]))
                self.order_table.setItem(i, 1, self.order_table.__class__.createItem(order["cinema"]))
                
                # 设置状态项的颜色
                if order["status"] == "已完成":
                    self.order_table.add_colored_item(i, 2, order["status"], "#4caf50")
                elif order["status"] == "待支付":
                    self.order_table.add_colored_item(i, 2, order["status"], "#ff9800")
                elif order["status"] == "已取消":
                    self.order_table.add_colored_item(i, 2, order["status"], "#f44336")
                else:
                    self.order_table.setItem(i, 2, self.order_table.__class__.createItem(order["status"]))
                
                self.order_table.setItem(i, 3, self.order_table.__class__.createItem(order["order_id"]))
                
        except Exception as e:
            print(f"[Tab管理器] 加载订单错误: {e}")
    
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

    def _show_order_context_menu(self, position):
        """显示订单右键菜单"""
        menu = QMenu()
        menu.addAction("查看详情", self._show_order_details)
        menu.addAction("取消订单", self._cancel_order)
        menu.exec_(self.order_table.viewport().mapToGlobal(position))

    def _show_order_details(self):
        """显示订单详情"""
        selected_items = self.order_table.selectedIndexes()
        if selected_items:
            row = selected_items[0].row()
            order = self.order_data_cache[row]
            self._show_order_details_dialog(order)

    def _show_order_details_dialog(self, order):
        """显示订单详情对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("订单详情")
        layout = QVBoxLayout(dialog)
        
        # 添加订单详情到对话框
        for key, value in order.items():
            if key != "account":
                label = ClassicLabel(f"{key}:")
                value_label = ClassicLabel(str(value))
                layout.addWidget(label)
                layout.addWidget(value_label)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        confirm_btn = ClassicButton("确认", "success")
        cancel_btn = ClassicButton("取消", "default")
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # 事件绑定
        confirm_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def _cancel_order(self):
        """取消订单"""
        selected_items = self.order_table.selectedIndexes()
        if selected_items:
            row = selected_items[0].row()
            order = self.order_data_cache[row]
            self._cancel_order_dialog(order)

    def _cancel_order_dialog(self, order):
        """显示取消订单对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("取消订单")
        layout = QVBoxLayout(dialog)
        
        # 添加取消订单的原因输入
        reason_layout = QHBoxLayout()
        reason_label = ClassicLabel("取消原因:")
        reason_input = ClassicTextEdit()
        reason_input.setPlaceholderText("请输入取消原因")
        reason_layout.addWidget(reason_label)
        reason_layout.addWidget(reason_input)
        layout.addLayout(reason_layout)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        confirm_btn = ClassicButton("确认取消", "success")
        cancel_btn = ClassicButton("取消", "default")
        button_layout.addWidget(confirm_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # 事件绑定
        def validate_and_cancel():
            reason = reason_input.toPlainText().strip()
            if not reason:
                QMessageBox.warning(dialog, "输入错误", "请输入取消原因")
                return
            
            # 处理取消逻辑
            self._handle_order_cancel(order, reason)
            dialog.accept()
        
        confirm_btn.clicked.connect(validate_and_cancel)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def _handle_order_cancel(self, order, reason):
        """处理取消订单逻辑"""
        # 实现取消订单的逻辑
        print(f"[Tab管理器] 取消订单: {order['order_id']}, 原因: {reason}")

    def _on_order_double_click(self, index):
        """处理订单表格的双击事件"""
        if index.column() == 0:  # 假设双击事件发生在第一列（影片列）
            selected_item = self.order_table.item(index.row(), index.column())
            if selected_item:
                movie_name = selected_item.text()
                self._show_movie_details(movie_name)

    def _show_movie_details(self, movie_name):
        """显示电影详情"""
        # 实现显示电影详情的逻辑
        print(f"[Tab管理器] 显示电影详情: {movie_name}")
    
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
            # 从当前账号中获取影院ID，或者从影院管理器中查找
            if hasattr(self, 'current_account') and self.current_account:
                return self.current_account.get('cinemaid')
                
            # 如果没有当前账号，尝试从影院表格获取第一个影院ID
            if hasattr(self, 'cinema_table') and self.cinema_table.rowCount() > 0:
                id_item = self.cinema_table.item(0, 1)
                if id_item:
                    return id_item.text()
                    
            # 默认返回一个测试影院ID
            return "11b7e4bcc265"
            
        except Exception as e:
            print(f"[Tab管理器] 获取影院ID错误: {e}")
            return "11b7e4bcc265"

    def _connect_signals(self):
        """连接信号槽"""
        try:
            # 出票Tab信号 - 检查组件是否存在再连接
            if hasattr(self, 'cinema_combo'):
                self.cinema_combo.currentTextChanged.connect(self._on_cinema_changed)
            if hasattr(self, 'movie_combo'):
                self.movie_combo.currentTextChanged.connect(self._on_movie_changed)
            if hasattr(self, 'date_combo'):
                self.date_combo.currentTextChanged.connect(self._on_date_changed)
            if hasattr(self, 'session_combo'):  # 🆕 添加场次选择信号连接
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
    
    def _connect_global_events(self):
        """连接全局事件"""
        # 监听账号切换事件
        event_bus.account_changed.connect(self._on_account_changed)
    
    def _on_account_changed(self, account_data: dict):
        """账号切换处理"""
        try:
            self.current_account = account_data
            userid = account_data.get("userid", "未知账号")
            balance = account_data.get("balance", 0)
            
            # 更新各Tab页面的账号显示
            if hasattr(self, 'current_account_label'):
                account_info = f"当前账号: {userid} (余额:{balance})"
                self.current_account_label.setText(account_info)
            
            # 更新绑券界面
            self.update_bind_account_info()
            
            # 更新兑换券界面
            self.update_exchange_account_info()
            
            # 更新积分显示
            self.current_points = account_data.get("score", 0)
            
            print(f"[Tab管理器] 账号切换: {userid}")
            
        except Exception as e:
            print(f"[Tab管理器] 账号切换错误: {e}")
    
    def _on_cinema_changed(self, cinema_text: str):
        """影院选择变化处理 - 加载真实影片数据"""
        try:
            if not cinema_text or cinema_text == "加载中...":
                return

            print(f"[Tab管理器] 影院切换: {cinema_text}")

            # 🆕 重置券列表
            self.reset_coupon_lists()

            # 🆕 禁用选座按钮 - 影院切换时
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)
                print(f"[Tab管理器] 影院切换，选座按钮已禁用")

            # 清空下级选择
            self.movie_combo.clear()
            self.date_combo.clear()
            self.session_combo.clear()
            
            self.movie_combo.addItem("加载影片中...")
            self.date_combo.addItem("请先选择影片")
            self.session_combo.addItem("请先选择日期")
            
            # 查找选中的影院数据
            selected_cinema = None
            if hasattr(self, 'cinemas_data') and self.cinemas_data:
                for cinema in self.cinemas_data:
                    if cinema.get('cinemaShortName') == cinema_text:
                        selected_cinema = cinema
                        break

            if not selected_cinema:
                print(f"[Tab管理器] 未找到影院数据: {cinema_text}")
                self.movie_combo.clear()
                self.movie_combo.addItem("影院数据错误")
                return

            # 🆕 保存当前影院数据 - 修复券选择功能需要的影院信息
            self.current_cinema_data = selected_cinema
            print(f"[Tab管理器] 保存当前影院数据: {selected_cinema.get('cinemaShortName')} (ID: {selected_cinema.get('cinemaid')})")

            # 🆕 发出影院选择信号 - 传递影院数据对象
            self.cinema_selected.emit(cinema_text)

            # 🆕 发布全局影院选择事件 - 传递完整影院数据
            event_bus.cinema_selected.emit(selected_cinema)
            
            # 🆕 延迟检查账号状态，等待账号组件处理完影院切换
            QTimer.singleShot(200, lambda: self._check_and_load_movies(selected_cinema))
                
        except Exception as e:
            print(f"[Tab管理器] 影院选择错误: {e}")
            self.movie_combo.clear()
            self.movie_combo.addItem("加载失败")
    
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
        """影片选择变化处理"""
        try:
            if not movie_text or movie_text in ["请先选择影院", "正在加载影片...", "暂无影片", "加载失败"]:
                return

            # 🆕 添加账号状态检查，避免循环错误
            if not self.current_account:
                # 静默返回，不输出错误日志
                return

            print(f"[Tab管理器] 影片切换: {movie_text}")

            # 🆕 重置券列表
            self.reset_coupon_lists()

            # 🆕 禁用选座按钮 - 影片切换时
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)
                print(f"[Tab管理器] 影片切换，选座按钮已禁用")

            # 获取选中的影片详细数据
            selected_movie = None
            if hasattr(self, 'current_movies') and self.current_movies:
                movie_index = self.movie_combo.currentIndex()
                if 0 <= movie_index < len(self.current_movies):
                    selected_movie = self.current_movies[movie_index]
            
            if not selected_movie:
                print(f"[Tab管理器] 未找到影片数据: {movie_text}")
                return
            
            # 清空日期和场次选择
            self.date_combo.clear()
            self.session_combo.clear()
            
            # 添加默认选项
            self.date_combo.addItem("请选择日期")
            self.session_combo.addItem("请先选择日期")
            
            # 从影片排期数据中提取日期列表
            dates = []
            plans = selected_movie.get('plans', [])
            
            if not plans:
                print(f"[Tab管理器] 影片排期数据未加载")
                self.date_combo.addItem("暂无排期")
                return
            
            # 收集所有日期
            for plan in plans:
                show_date = plan.get('k', '')  # 场次时间字段
                if show_date:
                    # 提取日期部分
                    date_part = show_date.split(' ')[0] if ' ' in show_date else show_date
                    if date_part and date_part not in dates:
                        dates.append(date_part)
            
            # 排序日期
            dates.sort()
            
            # 添加到下拉框
            if dates:
                for date in dates:
                    self.date_combo.addItem(date)
                print(f"[Tab管理器] 加载日期: {len(dates)} 个")
                
                # 🆕 自动选择第一个日期，触发四级联动
                if len(dates) > 0:
                    QTimer.singleShot(100, lambda: self.date_combo.setCurrentIndex(1))  # 索引1是第一个日期（索引0是"请选择日期"）
                    print(f"[Tab管理器] 自动选择第一个日期: {dates[0]}")
            else:
                self.date_combo.addItem("暂无日期")
            
            # 保存当前影片数据
            self.current_movie_data = selected_movie
            
        except Exception as e:
            print(f"[Tab管理器] 影片选择错误: {e}")

    def _on_date_changed(self, date_text: str):
        """日期选择变化处理"""
        try:
            if not date_text or date_text in ["请选择日期", "正在加载日期...", "暂无排期", "暂无日期"]:
                return
            
            # 🆕 添加数据状态检查，避免循环错误
            if not hasattr(self, 'current_movie_data') or not self.current_movie_data:
                # 静默返回，不输出错误日志
                return
                
            print(f"[Tab管理器] 日期切换: {date_text}")

            # 🆕 重置券列表
            self.reset_coupon_lists()

            # 🆕 禁用选座按钮 - 日期切换时
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(False)
                print(f"[Tab管理器] 日期切换，选座按钮已禁用")

            # 清空场次选择
            self.session_combo.clear()
            self.session_combo.addItem("请选择场次")
            
            # 从当前影片的排期中筛选指定日期的场次
            plans = self.current_movie_data.get('plans', [])
            if not plans:
                self.session_combo.addItem("暂无场次")
                return
            
            # 筛选匹配日期的场次
            matching_sessions = []
            for plan in plans:
                show_time = plan.get('k', '')  # 完整的场次时间
                if show_time:
                    # 提取日期部分进行匹配
                    date_part = show_time.split(' ')[0] if ' ' in show_time else show_time
                    if date_part == date_text:
                        matching_sessions.append(plan)
            
            # 添加场次到下拉框
            if matching_sessions:
                for session in matching_sessions:
                    session_text = self._format_session_text(session)
                    self.session_combo.addItem(session_text)
                print(f"[Tab管理器] 加载场次: {len(matching_sessions)} 个")
                
                # 保存当前日期的场次数据
                self.current_date_sessions = matching_sessions
                
                # 🆕 自动选择第一个场次，完成四级联动
                if len(matching_sessions) > 0:
                    QTimer.singleShot(100, lambda: self.session_combo.setCurrentIndex(1))  # 索引1是第一个场次（索引0是"请选择场次"）
                    print(f"[Tab管理器] 自动选择第一个场次")
            else:
                self.session_combo.addItem("暂无场次")
                self.current_date_sessions = []
            
        except Exception as e:
            print(f"[Tab管理器] 日期选择错误: {e}")

    def _on_session_changed(self, session_text: str):
        """场次选择变化处理 - 触发座位图加载"""
        try:
            if not session_text or session_text in ["请先选择日期", "加载场次中...", "暂无场次", "加载失败", "请选择场次"]:
                return
                
            # 🆕 添加数据状态检查，避免循环错误
            if not hasattr(self, 'current_date_sessions') or not self.current_date_sessions:
                # 静默返回，不输出错误日志
                return
                
            print(f"[Tab管理器] 场次切换: {session_text}")

            # 🆕 重置券列表
            self.reset_coupon_lists()

            # 获取选中的场次详细数据
            selected_session = None
            session_index = self.session_combo.currentIndex() - 1  # 减去"请选择场次"选项
            if 0 <= session_index < len(self.current_date_sessions):
                selected_session = self.current_date_sessions[session_index]
            
            if not selected_session:
                print(f"[Tab管理器] 未找到场次数据: {session_text}")
                return
            
            # 🆕 保存当前场次数据供订单创建使用
            self.current_session_data = selected_session
            print(f"[Tab管理器] 保存当前场次数据: {selected_session}")
            
            # 获取当前选择的完整信息
            cinema_text = self.cinema_combo.currentText() if hasattr(self, 'cinema_combo') else ""
            movie_text = self.movie_combo.currentText() if hasattr(self, 'movie_combo') else ""
            date_text = self.date_combo.currentText() if hasattr(self, 'date_combo') else ""
            
            # 🆕 查找影院详细数据 - 修复逻辑
            cinema_data = None
            if hasattr(self, 'cinemas_data') and self.cinemas_data:
                for cinema in self.cinemas_data:
                    if cinema.get('cinemaShortName') == cinema_text:
                        cinema_data = cinema
                        print(f"[Tab管理器] 找到影院数据: {cinema.get('cinemaShortName')} -> base_url: {cinema.get('base_url')}")
                        break
                        
            if not cinema_data:
                print(f"[Tab管理器] 未找到影院数据: {cinema_text}")
                print(f"[Tab管理器] 可用影院列表: {[c.get('cinemaShortName') for c in self.cinemas_data] if hasattr(self, 'cinemas_data') else '无数据'}")
                
                # 🆕 尝试从影院管理器重新加载数据
                try:
                    from services.cinema_manager import cinema_manager
                    cinemas = cinema_manager.load_cinema_list()
                    self.cinemas_data = cinemas
                    
                    # 重新查找
                    for cinema in cinemas:
                        if cinema.get('cinemaShortName') == cinema_text:
                            cinema_data = cinema
                            print(f"[Tab管理器] 重新加载后找到影院数据: {cinema.get('cinemaShortName')} -> base_url: {cinema.get('base_url')}")
                            break
                except Exception as reload_error:
                    print(f"[Tab管理器] 重新加载影院数据失败: {reload_error}")
            
            # 构建场次信息对象
            session_info = {
                'session_data': selected_session,
                'cinema_name': cinema_text,
                'movie_name': movie_text,
                'show_date': date_text,
                'session_text': session_text,
                'account': self.current_account,
                'cinema_data': cinema_data  # 🆕 确保传递完整的影院数据
            }
            
            print(f"[Tab管理器] 发出场次选择信号: {session_text}")
            print(f"[Tab管理器] 影院数据验证: {cinema_data.get('base_url') if cinema_data else 'None'}")

            # 🆕 启用选座按钮 - 当用户选择完场次后
            if hasattr(self, 'submit_order_btn'):
                self.submit_order_btn.setEnabled(True)
                print(f"[Tab管理器] 选座按钮已启用")

            # 发出场次选择信号，让主窗口处理座位图加载
            self.session_selected.emit(session_info)
            
        except Exception as e:
            print(f"[Tab管理器] 场次选择错误: {e}")
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
                QMessageBox.warning(self, "未选择账号", "请先选择账号！")
                return
            
            cinemaid = self.get_selected_cinemaid()
            if not cinemaid:
                QMessageBox.warning(self, "未选择影院", "请先选择影院！")
                return
            
            # 调用现有的订单API
            from services.order_api import get_order_list
            
            params = {
                'userid': account['userid'],
                'token': account['token'], 
                'openid': account['openid'],
                'cinemaid': cinemaid,
                'pageIndex': 1,
                'pageSize': 50
            }
            
            result = get_order_list(params)
            
            if result.get('resultCode') == '0':
                orders = result.get('data', {}).get('orderList', [])
                self.update_order_table(orders)
                QMessageBox.information(self, "刷新成功", f"已获取到 {len(orders)} 个订单")
            else:
                error_msg = result.get('resultDesc', '获取订单列表失败')
                QMessageBox.warning(self, "获取失败", error_msg)
                self._load_sample_orders()
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新订单列表时出错：{str(e)}")
            self._load_sample_orders()

    def update_order_table(self, orders):
        """更新订单表格显示"""
        try:
            self.order_table.setRowCount(len(orders))
            self.order_data_cache = orders
            
            for row, order in enumerate(orders):
                # 影片名称
                movie_name = order.get('movieName', '未知影片')
                self.order_table.setItem(row, 0, self.order_table.__class__.createItem(movie_name))
                
                # 影院名称
                cinema_name = order.get('cinemaName', '未知影院')
                self.order_table.setItem(row, 1, self.order_table.__class__.createItem(cinema_name))
                
                # 订单状态
                status = self.get_order_status_text(order.get('orderStatus', 0))
                
                # 根据状态设置颜色
                if '待支付' in status:
                    self.order_table.add_colored_item(row, 2, status, "#ff9800")
                elif '已支付' in status:
                    self.order_table.add_colored_item(row, 2, status, "#4caf50")
                elif '已取票' in status:
                    self.order_table.add_colored_item(row, 2, status, "#2196f3")
                elif '已取消' in status:
                    self.order_table.add_colored_item(row, 2, status, "#f44336")
                else:
                    self.order_table.setItem(row, 2, self.order_table.__class__.createItem(status))
                
                # 订单号
                order_no = order.get('orderNo', '无订单号')
                self.order_table.setItem(row, 3, self.order_table.__class__.createItem(order_no))
                
        except Exception as e:
            print(f"[Tab管理器] 更新订单表格错误: {e}")

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
 