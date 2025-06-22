#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券管理组件
基于新开发的券管理API系统实现
"""

import time
from typing import Dict, List, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QApplication, QTableWidgetItem
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QThread, pyqtSlot
from PyQt5.QtGui import QColor

# 导入自定义组件
from ui.widgets.classic_components import (
    ClassicGroupBox, ClassicButton, ClassicTableWidget, ClassicLabel
)

# 导入券管理API
from api.voucher_api import get_voucher_api
from utils.voucher_utils import get_voucher_processor, get_voucher_formatter
from services.ui_utils import MessageManager

class VoucherLoadThread(QThread):
    """券数据加载线程"""
    
    # 定义信号
    data_loaded = pyqtSignal(dict)  # 数据加载完成信号
    error_occurred = pyqtSignal(str)  # 错误发生信号
    progress_updated = pyqtSignal(str)  # 进度更新信号
    
    def __init__(self, cinema_id: str, token: str, only_valid: bool = True):
        super().__init__()
        self.cinema_id = cinema_id
        self.token = token
        self.only_valid = only_valid
        self.voucher_api = get_voucher_api()
    
    def run(self):
        """执行券数据加载"""
        try:
            self.progress_updated.emit("正在获取券列表...")

            print(f"[券加载线程] 开始加载券数据")
            print(f"[券加载线程] 影院ID: {self.cinema_id}")
            print(f"[券加载线程] Token: {self.token[:20]}...")
            print(f"[券加载线程] 只显示有效券: {self.only_valid}")

            # 调用券管理API - 使用正确的方法
            if self.only_valid:
                from api.voucher_api import get_valid_vouchers
                print(f"[券加载线程] 调用get_valid_vouchers")
                result = get_valid_vouchers(self.cinema_id, self.token)
            else:
                print(f"[券加载线程] 调用get_user_vouchers")
                result = self.voucher_api.get_user_vouchers(
                    self.cinema_id,
                    self.token,
                    only_valid=self.only_valid
                )

            print(f"[券加载线程] API调用完成")
            print(f"[券加载线程] 结果成功: {result.get('success', False)}")

            if result['success']:
                data = result['data']
                vouchers = data.get('vouchers', [])
                print(f"[券加载线程] 券数量: {len(vouchers)}")
                if vouchers:
                    print(f"[券加载线程] 第一张券: {vouchers[0].get('voucher_name', '未知')}")

                self.progress_updated.emit("数据加载完成")
                print(f"[券加载线程] 准备发送数据信号...")
                self.data_loaded.emit(result['data'])
                print(f"[券加载线程] 数据信号已发送")

                # 🔧 强制处理事件队列，确保信号被处理
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
                print(f"[券加载线程] 强制处理事件队列完成")
            else:
                error_msg = result.get('message', '未知错误')
                print(f"[券加载线程] API调用失败: {error_msg}")
                self.error_occurred.emit(error_msg)

        except Exception as e:
            error_msg = f"加载券数据失败: {str(e)}"
            print(f"[券加载线程] 异常: {error_msg}")
            import traceback
            traceback.print_exc()
            self.error_occurred.emit(error_msg)

class VoucherWidget(QWidget):
    """券管理组件"""
    
    # 定义信号
    voucher_selected = pyqtSignal(dict)  # 券选择信号
    voucher_validated = pyqtSignal(dict)  # 券验证信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化状态
        self.current_account = None
        self.current_cinema_id = None
        self.vouchers_data = []
        self.statistics_data = {}
        
        # API实例
        self.voucher_api = get_voucher_api()
        self.voucher_processor = get_voucher_processor()
        self.voucher_formatter = get_voucher_formatter()
        
        # 加载线程
        self.load_thread = None
        
        # 初始化UI
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 控制按钮区
        self._create_control_area(layout)

        # 券列表表格（移除统计信息区）
        self._create_voucher_table(layout)
    
    def _create_control_area(self, parent_layout):
        """创建控制按钮区域"""
        control_group = ClassicGroupBox("券管理操作")
        control_layout = QHBoxLayout(control_group)
        
        # 刷新按钮
        self.refresh_btn = ClassicButton("刷新券列表", "primary")
        self.refresh_btn.setMaximumWidth(120)
        self.refresh_btn.clicked.connect(self.refresh_vouchers)
        control_layout.addWidget(self.refresh_btn)
        
        # 移除"只显示有效券"开关，默认只显示有效券
        
        # 状态标签
        self.status_label = ClassicLabel("请选择账号和影院")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; margin-left: 10px;")
        control_layout.addWidget(self.status_label)
        
        control_layout.addStretch()
        parent_layout.addWidget(control_group)
    

    
    def _create_voucher_table(self, parent_layout):
        """创建券列表表格"""
        table_group = ClassicGroupBox("券列表")
        table_layout = QVBoxLayout(table_group)
        
        # 创建表格（简化为3列）
        self.voucher_table = ClassicTableWidget()
        self.voucher_table.setColumnCount(3)
        self.voucher_table.setHorizontalHeaderLabels([
            "券名称", "券号", "有效期"
        ])

        # 设置列宽（调整为3列布局）
        header = self.voucher_table.horizontalHeader()
        header.resizeSection(0, 250)  # 券名称（增加宽度）
        header.resizeSection(1, 180)  # 券号（增加宽度）
        header.resizeSection(2, 150)  # 有效期（增加宽度）
        
        # 设置表格属性
        from PyQt5.QtWidgets import QAbstractItemView
        self.voucher_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.voucher_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 🎨 优化表格显示：设置统一的背景颜色，提高可见性
        self.voucher_table.setAlternatingRowColors(False)  # 关闭交替行颜色

        # 设置表格样式：所有行都使用清晰的背景色
        table_style = """
            QTableWidget {
                background-color: #f8f9fa;
                gridline-color: #dee2e6;
                selection-background-color: #e3f2fd;
                selection-color: #1976d2;
            }
            QTableWidget::item {
                background-color: #ffffff;
                color: #212529;
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
            QTableWidget::item:hover {
                background-color: #e3f2fd;
            }
        """
        self.voucher_table.setStyleSheet(table_style)
        
        # 连接选择信号
        self.voucher_table.itemSelectionChanged.connect(self._on_voucher_selected)
        
        table_layout.addWidget(self.voucher_table)
        parent_layout.addWidget(table_group)
        
        # 初始显示空状态
        self._show_empty_state()
    
    def _connect_signals(self):
        """连接信号槽"""
        pass
    
    def _show_empty_state(self):
        """显示空状态"""
        self.voucher_table.setRowCount(1)

        # 根据是否已设置账号和影院显示不同提示
        if self.current_account and self.current_cinema_id:
            empty_text = f"当前影院（{self.current_cinema_id}）没有有效券\n提示：券可能绑定到其他影院，请尝试切换影院"
        else:
            empty_text = "请先选择账号和影院，然后点击刷新券列表"

        empty_item = QTableWidgetItem(empty_text)
        empty_item.setBackground(QColor('#f8f9fa'))
        self.voucher_table.setItem(0, 0, empty_item)
        self.voucher_table.setSpan(0, 0, 1, 3)  # 调整为3列
    
    def _show_loading_state(self):
        """显示加载状态"""
        self.voucher_table.setRowCount(1)
        loading_item = QTableWidgetItem("正在加载券数据，请稍候...")
        loading_item.setBackground(QColor('#e3f2fd'))
        self.voucher_table.setItem(0, 0, loading_item)
        self.voucher_table.setSpan(0, 0, 1, 3)  # 调整为3列
        
        # 更新状态
        self.status_label.setText("正在加载...")
        self.refresh_btn.setText("加载中...")
        self.refresh_btn.setEnabled(False)
    
    def _show_error_state(self, error_msg: str):
        """显示错误状态"""
        self.voucher_table.setRowCount(1)
        self.voucher_table.clearSpans()

        error_item = QTableWidgetItem(f"加载失败: {error_msg}")
        error_item.setBackground(QColor('#f8d7da'))
        self.voucher_table.setItem(0, 0, error_item)
        self.voucher_table.setSpan(0, 0, 1, 3)  # 调整为3列
        
        # 更新状态
        self.status_label.setText(f"错误: {error_msg}")
        self.status_label.setStyleSheet("color: #d32f2f; font-size: 12px; margin-left: 10px;")
    
    def _restore_ui_state(self):
        """恢复UI状态"""
        self.refresh_btn.setText("刷新券列表")
        self.refresh_btn.setEnabled(True)
        self.voucher_table.clearSpans()
    
    def set_account_info(self, account: Dict[str, Any], cinema_id: str):
        """设置账号和影院信息"""
        self.current_account = account
        self.current_cinema_id = cinema_id
        
        # 更新状态显示
        if account and cinema_id:
            phone = account.get('phone', '未知')
            self.status_label.setText(f"账号: {phone} | 影院: {cinema_id}")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px; margin-left: 10px;")
        else:
            self.status_label.setText("请选择账号和影院")
            self.status_label.setStyleSheet("color: #666; font-size: 12px; margin-left: 10px;")
    
    def refresh_vouchers(self):
        """刷新券列表"""
        if not self.current_account or not self.current_cinema_id:
            MessageManager.show_error(self, "参数缺失", "请先选择账号和影院！")
            return

        token = self.current_account.get('token')
        if not token:
            MessageManager.show_error(self, "Token缺失", "账号Token无效，请重新登录！")
            return

        # 检查是否正在加载
        if self.load_thread and self.load_thread.isRunning():
            return

        # 显示加载状态
        self._show_loading_state()

        # ⚡ 性能优化：直接同步加载，减少延时
        try:
            print(f"[券组件] 开始快速同步加载券数据...")
            import time
            start_time = time.time()

            from api.voucher_api import get_valid_vouchers
            result = get_valid_vouchers(self.current_cinema_id, token)

            load_time = time.time() - start_time
            print(f"[券组件] API调用耗时: {load_time:.2f}秒")

            if result['success']:
                print(f"[券组件] 同步加载成功，直接处理数据...")
                self._on_data_loaded(result['data'])
            else:
                error_msg = result.get('message', '未知错误')
                print(f"[券组件] 同步加载失败: {error_msg}")
                self._on_error_occurred(error_msg)

        except Exception as e:
            error_msg = f"加载券数据失败: {str(e)}"
            print(f"[券组件] 同步加载异常: {error_msg}")
            import traceback
            traceback.print_exc()
            self._on_error_occurred(error_msg)
    
    @pyqtSlot(dict)
    def _on_data_loaded(self, data: Dict[str, Any]):
        """处理数据加载完成"""
        try:
            print(f"[券组件] 开始处理数据: {type(data)}")
            print(f"[券组件] 数据keys: {list(data.keys()) if isinstance(data, dict) else '不是字典'}")

            # 安全地获取券数据
            vouchers_raw = data.get('vouchers', [])
            self.statistics_data = data.get('statistics', {})

            print(f"[券组件] 原始券数据数量: {len(vouchers_raw)}")
            print(f"[券组件] 原始券数据类型: {type(vouchers_raw)}")

            # ⚡ 性能优化：简化数据处理，减少调试输出
            self.vouchers_data = []
            for voucher in vouchers_raw:
                if isinstance(voucher, dict):
                    # 如果已经是字典，直接使用
                    self.vouchers_data.append(voucher)
                else:
                    # 如果是对象，尝试转换
                    try:
                        if hasattr(voucher, 'to_dict'):
                            self.vouchers_data.append(voucher.to_dict())
                        else:
                            # 快速转换为字典
                            voucher_dict = {
                                'voucher_name': getattr(voucher, 'voucher_name', '未知券'),
                                'voucher_code_mask': getattr(voucher, 'voucher_code_mask', '无券号'),
                                'expire_time_string': getattr(voucher, 'expire_time_string', '未知'),
                                'is_valid': getattr(voucher, 'is_valid', lambda: False)() if callable(getattr(voucher, 'is_valid', None)) else False
                            }
                            self.vouchers_data.append(voucher_dict)
                    except Exception:
                        # 静默跳过错误数据，提升性能
                        continue

            print(f"[券组件] 最终券数据数量: {len(self.vouchers_data)}")

            # 更新UI显示
            print(f"[券组件] 开始更新UI...")
            self._update_voucher_table()

            # 恢复UI状态
            self._restore_ui_state()

            # 更新状态
            count = len(self.vouchers_data)
            self.status_label.setText(f"加载完成，共 {count} 张有效券")
            self.status_label.setStyleSheet("color: #4CAF50; font-size: 12px; margin-left: 10px;")

            print(f"[券组件] 数据处理完成，券数量: {count}")

        except Exception as e:
            print(f"[券组件] 处理数据失败: {e}")
            import traceback
            traceback.print_exc()
            self._on_error_occurred(f"处理数据失败: {str(e)}")
    
    @pyqtSlot(str)
    def _on_error_occurred(self, error_msg: str):
        """处理错误"""
        self._show_error_state(error_msg)
        self._restore_ui_state()
    
    @pyqtSlot(str)
    def _on_progress_updated(self, message: str):
        """处理进度更新"""
        self.status_label.setText(message)

    def _process_events(self):
        """定期处理事件队列"""
        from PyQt5.QtWidgets import QApplication
        QApplication.processEvents()

        # 如果加载完成，停止定时器
        if self.load_thread and not self.load_thread.isRunning():
            if hasattr(self, 'event_timer'):
                self.event_timer.stop()
    
    # 移除切换功能，始终只显示有效券
    
    def _update_voucher_table(self):
        """更新券列表表格"""
        print(f"[券组件-表格更新] 开始更新表格，券数据数量: {len(self.vouchers_data)}")

        if not self.vouchers_data:
            print(f"[券组件-表格更新] 券数据为空，显示空状态")
            self._show_empty_state()
            return

        print(f"[券组件-表格更新] 清空表格并设置行数: {len(self.vouchers_data)}")

        # 清空表格
        self.voucher_table.setRowCount(0)
        self.voucher_table.clearSpans()

        # 设置行数
        self.voucher_table.setRowCount(len(self.vouchers_data))
        print(f"[券组件-表格更新] 表格行数已设置为: {self.voucher_table.rowCount()}")
        print(f"[券组件-表格更新] 表格列数: {self.voucher_table.columnCount()}")

        # ⚡ 性能优化：快速填充数据，减少调试输出
        for row, voucher in enumerate(self.vouchers_data):
            try:
                if isinstance(voucher, dict):
                    # 券名称
                    name = voucher.get('voucher_name', '未知券')
                    name_item = QTableWidgetItem(str(name))
                    # 🎨 设置清晰的文字样式
                    name_item.setBackground(QColor('#ffffff'))
                    name_item.setForeground(QColor('#212529'))
                    self.voucher_table.setItem(row, 0, name_item)

                    # 券号（掩码）
                    code_mask = voucher.get('voucher_code_mask', '无券号')
                    code_item = QTableWidgetItem(str(code_mask))
                    # 🎨 设置清晰的文字样式
                    code_item.setBackground(QColor('#ffffff'))
                    code_item.setForeground(QColor('#212529'))
                    self.voucher_table.setItem(row, 1, code_item)

                    # 有效期
                    expire_str = voucher.get('expire_time_string', '未知')
                    expire_item = QTableWidgetItem(str(expire_str))
                    # 🎨 设置清晰的文字样式
                    expire_item.setBackground(QColor('#ffffff'))
                    expire_item.setForeground(QColor('#212529'))
                    self.voucher_table.setItem(row, 2, expire_item)
                else:
                    # 如果不是字典，显示错误信息
                    error_item = QTableWidgetItem("数据格式错误")
                    error_item.setBackground(QColor('#f8d7da'))  # 红色
                    self.voucher_table.setItem(row, 0, error_item)
                    self.voucher_table.setSpan(row, 0, 1, 3)  # 调整为3列

            except Exception:
                # ⚡ 性能优化：简化错误处理，减少调试输出
                error_item = QTableWidgetItem(f"第{row+1}行数据错误")
                error_item.setBackground(QColor('#f8d7da'))
                self.voucher_table.setItem(row, 0, error_item)
                self.voucher_table.setSpan(row, 0, 1, 3)  # 调整为3列

        print(f"[券组件-表格更新] 表格更新完成，最终行数: {self.voucher_table.rowCount()}")
    
    def _on_voucher_selected(self):
        """处理券选择"""
        current_row = self.voucher_table.currentRow()
        if 0 <= current_row < len(self.vouchers_data):
            selected_voucher = self.vouchers_data[current_row]
            self.voucher_selected.emit(selected_voucher)
    
    def get_selected_voucher(self) -> Optional[Dict[str, Any]]:
        """获取当前选中的券"""
        try:
            current_row = self.voucher_table.currentRow()
            if 0 <= current_row < len(self.vouchers_data):
                voucher = self.vouchers_data[current_row]
                if isinstance(voucher, dict):
                    return voucher
                else:
                    print(f"[券组件] 选中的券数据不是字典格式: {type(voucher)}")
                    return None
            return None
        except Exception as e:
            print(f"[券组件] 获取选中券失败: {e}")
            return None
    
    def clear_data(self):
        """清空数据"""
        self.vouchers_data = []
        self.statistics_data = {}
        self.current_account = None
        self.current_cinema_id = None
        self._show_empty_state()
