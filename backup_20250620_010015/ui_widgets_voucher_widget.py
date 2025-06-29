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
                self.data_loaded.emit(result['data'])
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
        
        # 统计信息区
        self._create_statistics_area(layout)
        
        # 券列表表格
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
    
    def _create_statistics_area(self, parent_layout):
        """创建简化的券信息区域"""
        info_group = ClassicGroupBox("券信息")
        info_layout = QHBoxLayout(info_group)

        # 只显示有效券数量
        self.voucher_count_label = ClassicLabel("有效券: 0张")
        self.voucher_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.voucher_count_label)

        info_layout.addStretch()
        parent_layout.addWidget(info_group)
    
    def _create_voucher_table(self, parent_layout):
        """创建券列表表格"""
        table_group = ClassicGroupBox("券列表")
        table_layout = QVBoxLayout(table_group)
        
        # 创建表格
        self.voucher_table = ClassicTableWidget()
        self.voucher_table.setColumnCount(4)
        self.voucher_table.setHorizontalHeaderLabels([
            "券名称", "券号", "有效期", "状态"
        ])
        
        # 设置列宽
        header = self.voucher_table.horizontalHeader()
        header.resizeSection(0, 200)  # 券名称
        header.resizeSection(1, 150)  # 券号
        header.resizeSection(2, 120)  # 有效期
        header.resizeSection(3, 80)   # 状态
        
        # 设置表格属性
        from PyQt5.QtWidgets import QAbstractItemView
        self.voucher_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.voucher_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.voucher_table.setAlternatingRowColors(True)
        
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
        self.voucher_table.setSpan(0, 0, 1, 4)
    
    def _show_loading_state(self):
        """显示加载状态"""
        self.voucher_table.setRowCount(1)
        loading_item = QTableWidgetItem("正在加载券数据，请稍候...")
        loading_item.setBackground(QColor('#e3f2fd'))
        self.voucher_table.setItem(0, 0, loading_item)
        self.voucher_table.setSpan(0, 0, 1, 4)
        
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
        self.voucher_table.setSpan(0, 0, 1, 4)
        
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
        
        # 创建并启动加载线程（始终只显示有效券）
        self.load_thread = VoucherLoadThread(self.current_cinema_id, token, only_valid=True)
        self.load_thread.data_loaded.connect(self._on_data_loaded)
        self.load_thread.error_occurred.connect(self._on_error_occurred)
        self.load_thread.progress_updated.connect(self._on_progress_updated)
        self.load_thread.start()
    
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

            # 确保券数据是字典列表格式
            self.vouchers_data = []
            for i, voucher in enumerate(vouchers_raw):
                print(f"[券组件] 处理第{i+1}个券，类型: {type(voucher)}")

                if isinstance(voucher, dict):
                    # 如果已经是字典，直接使用
                    print(f"[券组件] 券{i+1}是字典，券名: {voucher.get('voucher_name', '未知')}")
                    self.vouchers_data.append(voucher)
                else:
                    # 如果是对象，调用to_dict方法
                    try:
                        if hasattr(voucher, 'to_dict'):
                            voucher_dict = voucher.to_dict()
                            print(f"[券组件] 券{i+1}转换为字典，券名: {voucher_dict.get('voucher_name', '未知')}")
                            self.vouchers_data.append(voucher_dict)
                        else:
                            # 如果没有to_dict方法，尝试转换为字典
                            voucher_dict = {
                                'voucher_name': getattr(voucher, 'voucher_name', '未知券'),
                                'voucher_code_mask': getattr(voucher, 'voucher_code_mask', '无券号'),
                                'expire_time_string': getattr(voucher, 'expire_time_string', '未知'),
                                'is_valid': getattr(voucher, 'is_valid', lambda: False)() if callable(getattr(voucher, 'is_valid', None)) else False
                            }
                            print(f"[券组件] 券{i+1}手动转换，券名: {voucher_dict.get('voucher_name', '未知')}")
                            self.vouchers_data.append(voucher_dict)
                    except Exception as convert_error:
                        print(f"[券组件] 转换券数据失败: {convert_error}")
                        continue

            print(f"[券组件] 最终券数据数量: {len(self.vouchers_data)}")

            # 更新UI显示
            print(f"[券组件] 开始更新UI...")
            self._update_voucher_table()
            self._update_statistics()

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
    
    # 移除切换功能，始终只显示有效券
    
    def _update_statistics(self):
        """更新简化的券信息显示"""
        # 直接使用券数据的长度，因为我们只显示有效券
        count = len(self.vouchers_data)
        self.voucher_count_label.setText(f"有效券: {count}张")

        # 根据券数量设置颜色
        if count == 0:
            self.voucher_count_label.setStyleSheet("color: #666; font-weight: bold; font-size: 14px;")
        else:
            self.voucher_count_label.setStyleSheet("color: #4CAF50; font-weight: bold; font-size: 14px;")
    
    def _update_voucher_table(self):
        """更新券列表表格"""
        if not self.vouchers_data:
            self._show_empty_state()
            return

        # 清空表格
        self.voucher_table.setRowCount(0)
        self.voucher_table.clearSpans()

        # 设置行数
        self.voucher_table.setRowCount(len(self.vouchers_data))

        # 填充数据
        for row, voucher in enumerate(self.vouchers_data):
            try:
                # 安全地获取券数据
                if isinstance(voucher, dict):
                    # 券名称
                    name = voucher.get('voucher_name', '未知券')
                    name_item = QTableWidgetItem(str(name))
                    self.voucher_table.setItem(row, 0, name_item)

                    # 券号（掩码）
                    code_mask = voucher.get('voucher_code_mask', '无券号')
                    code_item = QTableWidgetItem(str(code_mask))
                    self.voucher_table.setItem(row, 1, code_item)

                    # 有效期
                    expire_str = voucher.get('expire_time_string', '未知')
                    expire_item = QTableWidgetItem(str(expire_str))
                    self.voucher_table.setItem(row, 2, expire_item)

                    # 状态（由于只显示有效券，所以都是有效的）
                    is_valid = voucher.get('is_valid', True)  # 默认为有效
                    status_text = "有效"
                    status_item = QTableWidgetItem(status_text)
                    status_item.setBackground(QColor('#d4edda'))  # 绿色
                    self.voucher_table.setItem(row, 3, status_item)
                else:
                    # 如果不是字典，显示错误信息
                    error_item = QTableWidgetItem("数据格式错误")
                    error_item.setBackground(QColor('#f8d7da'))  # 红色
                    self.voucher_table.setItem(row, 0, error_item)
                    self.voucher_table.setSpan(row, 0, 1, 4)

            except Exception as e:
                print(f"[券组件] 填充第{row}行数据失败: {e}")
                # 显示错误行
                error_item = QTableWidgetItem(f"第{row+1}行数据错误")
                error_item.setBackground(QColor('#f8d7da'))
                self.voucher_table.setItem(row, 0, error_item)
                self.voucher_table.setSpan(row, 0, 1, 4)
    
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
        self._update_statistics()
