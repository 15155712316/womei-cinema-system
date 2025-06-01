#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影院选择面板 - PyQt5版本
完全复刻tkinter版本的功能和四级联动逻辑
"""

import json
import os
from typing import Callable, Optional, Dict, List

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from services.cinema_manager import cinema_manager
from services.film_service import get_films, load_cinemas, get_plan_seat_info
from services.ui_utils import MessageManager

class CinemaSelectPanelPyQt5(QWidget):
    """影院选择面板 - PyQt5版本"""
    
    def __init__(self, parent=None, on_cinema_changed=None):
        super().__init__(parent)
        
        # 回调函数
        self.on_cinema_changed = on_cinema_changed
        
        # 主窗口引用，便于访问current_account
        self.main_window = None
        self.seat_panel = None
        
        # 数据
        self.cinemas = []
        self.films = []
        self.shows = {}
        self.film_key_map = {}
        self.films_map = {}
        self.current_film_key = None
        
        self._init_ui()
        self._load_cinemas()
    
    def _init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)
        
        # 字体设置
        combo_font = QFont("微软雅黑", 10)
        btn_font = QFont("微软雅黑", 10, QFont.Bold)
        label_font = QFont("微软雅黑", 10)
        
        # 行1: 影院下拉
        row1 = QFrame()
        row1_layout = QHBoxLayout(row1)
        row1_layout.setContentsMargins(5, 2, 5, 2)
        row1_layout.setSpacing(2)
        
        cinema_label = QLabel("影院：")
        cinema_label.setFont(label_font)
        row1_layout.addWidget(cinema_label)
        
        self.cinema_combo = QComboBox()
        self.cinema_combo.setFont(combo_font)
        self.cinema_combo.currentTextChanged.connect(self.on_cinema_select)
        self._setup_combo_style(self.cinema_combo)
        row1_layout.addWidget(self.cinema_combo, 1)
        
        layout.addWidget(row1)
        
        # 行2: 影片下拉
        row2 = QFrame()
        row2_layout = QHBoxLayout(row2)
        row2_layout.setContentsMargins(5, 2, 5, 2)
        row2_layout.setSpacing(2)
        
        movie_label = QLabel("影片：")
        movie_label.setFont(label_font)
        row2_layout.addWidget(movie_label)
        
        self.movie_combo = QComboBox()
        self.movie_combo.setFont(combo_font)
        self.movie_combo.currentTextChanged.connect(self.on_movie_select)
        self._setup_combo_style(self.movie_combo)
        row2_layout.addWidget(self.movie_combo, 1)
        
        layout.addWidget(row2)
        
        # 行3: 日期下拉
        row3 = QFrame()
        row3_layout = QHBoxLayout(row3)
        row3_layout.setContentsMargins(5, 2, 5, 2)
        row3_layout.setSpacing(2)
        
        date_label = QLabel("日期：")
        date_label.setFont(label_font)
        row3_layout.addWidget(date_label)
        
        self.date_combo = QComboBox()
        self.date_combo.setFont(combo_font)
        self.date_combo.currentTextChanged.connect(self.on_date_select)
        self._setup_combo_style(self.date_combo)
        row3_layout.addWidget(self.date_combo, 1)
        
        layout.addWidget(row3)
        
        # 行4: 场次下拉
        row4 = QFrame()
        row4_layout = QVBoxLayout(row4)
        row4_layout.setContentsMargins(5, 2, 5, 2)
        row4_layout.setSpacing(2)
        
        session_label = QLabel("场次：")
        session_label.setFont(label_font)
        row4_layout.addWidget(session_label)
        
        self.session_combo = QComboBox()
        self.session_combo.setFont(combo_font)
        self.session_combo.currentTextChanged.connect(self.on_session_select)
        self._setup_combo_style(self.session_combo)
        row4_layout.addWidget(self.session_combo)
        
        layout.addWidget(row4)
        
        # 行5: 操作按钮
        row5 = QFrame()
        row5_layout = QHBoxLayout(row5)
        row5_layout.setContentsMargins(5, 3, 5, 2)
        
        self.open_seat_btn = QPushButton("选座")
        self.open_seat_btn.setFont(btn_font)
        self.open_seat_btn.clicked.connect(self.on_open_seat_selection)
        self._setup_button_style(self.open_seat_btn)
        row5_layout.addWidget(self.open_seat_btn)
        
        layout.addWidget(row5)
        
        # 当前账号显示区
        self.current_account_label = QLabel("当前账号：-")
        self.current_account_label.setFont(QFont("微软雅黑", 11, QFont.Bold))
        self.current_account_label.setStyleSheet("QLabel { color: red; }")
        self.current_account_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.current_account_label)
        
        # 添加弹簧
        layout.addStretch()
    
    def _setup_combo_style(self, combo: QComboBox):
        """设置下拉框样式"""
        combo.setStyleSheet("""
            QComboBox {
                font: 10px "Microsoft YaHei";
                padding: 3px 5px;
                border: 1px solid #ccc;
                border-radius: 2px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox:focus {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 2px solid #999;
                border-top: none;
                border-right: none;
                width: 4px;
                height: 4px;
                margin-right: 5px;
                transform: rotate(-45deg);
            }
            QComboBox QAbstractItemView {
                font: 10px "Microsoft YaHei";
                border: 1px solid #ccc;
                background-color: white;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
    
    def _setup_button_style(self, button: QPushButton):
        """设置按钮样式"""
        button.setStyleSheet("""
            QPushButton {
                background-color: #007acc;
                color: white;
                font: bold 10px "Microsoft YaHei";
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #005a99;
            }
            QPushButton:pressed {
                background-color: #004d7a;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
    
    def _load_cinemas(self):
        """加载影院数据"""
        try:
            self.cinemas = load_cinemas()
            cinema_names = [c['name'] for c in self.cinemas]
            
            self.cinema_combo.clear()
            self.cinema_combo.addItems(cinema_names)
            
            print(f"[影院面板] 加载了 {len(self.cinemas)} 个影院")
            
        except Exception as e:
            print(f"加载影院数据失败: {e}")
            self.cinemas = []
    
    def set_main_window(self, main_window):
        """设置主窗口引用，便于访问当前账号信息"""
        self.main_window = main_window
    
    def set_seat_panel(self, seat_panel):
        """设置座位面板引用"""
        self.seat_panel = seat_panel
    
    def get_current_account(self):
        """获取当前登录的账号信息"""
        if self.main_window and hasattr(self.main_window, 'current_account'):
            account = getattr(self.main_window, 'current_account', None)
            print(f"[DEBUG] get_current_account: main_window存在={self.main_window is not None}")
            print(f"[DEBUG] get_current_account: account存在={account is not None}")
            if account:
                print(f"[DEBUG] account详情: userid={account.get('userid', 'N/A')}, cinemaid={account.get('cinemaid', 'N/A')}, balance={account.get('balance', 'N/A')}")
            else:
                print(f"[DEBUG] account为空，main_window.current_account={getattr(self.main_window, 'current_account', 'ATTR_NOT_FOUND')}")
            return account
        else:
            print(f"[DEBUG] get_current_account: main_window={self.main_window}, has_current_account={hasattr(self.main_window, 'current_account') if self.main_window else 'N/A'}")
            return None
    
    def get_selected_cinemaid(self):
        """获取当前选中的影院ID"""
        current_index = self.cinema_combo.currentIndex()
        if 0 <= current_index < len(self.cinemas):
            return self.cinemas[current_index]['cinemaid']
        return None
    
    def refresh_cinema_dropdown(self):
        """刷新影院下拉框"""
        self._load_cinemas()
    
    # ==========================================================================
    # 四级联动事件处理
    # ==========================================================================
    
    def on_cinema_select(self, cinema_name: str):
        """影院下拉框选中事件，加载对应影院的影片和场次数据"""
        if not cinema_name:
            return
        
        print(f"[DEBUG] on_cinema_select 被触发: {cinema_name}")
        
        # 清空券列表
        if hasattr(self.main_window, '_clear_coupons_impl'):
            self.main_window._clear_coupons_impl()
        
        current_index = self.cinema_combo.currentIndex()
        if current_index < 0 or current_index >= len(self.cinemas):
            print("[DEBUG] 无效的影院索引")
            return
        
        selected = self.cinemas[current_index]
        base_url = selected['base_url']
        cinemaid = selected['cinemaid']
        print(f"[DEBUG] 选中影院: {selected.get('name', '未知')}, cinemaid: {cinemaid}")
        
        # 获取当前账号
        print("[DEBUG] 正在调用 get_current_account()...")
        current_account = self.get_current_account()
        print(f"[DEBUG] get_current_account() 返回: {current_account is not None}")
        
        if not current_account:
            print("[DEBUG] current_account为空，显示登录提示")
            QMessageBox.warning(self, "登录提示", "请先登录账号后再选择影院")
            return
        
        print("[DEBUG] 账号验证通过，继续执行...")
        openid = current_account.get('openid', '')
        token = current_account.get('token', '')
        userid = current_account.get('userid', '')
        
        try:
            # 获取接口数据，直接使用原始数据（与tkinter版本保持一致）
            raw_data = get_films(base_url, cinemaid, openid, userid, token)
            self.films = raw_data['films']
            self.shows = raw_data['shows']
            
            film_names = [film['fn'] for film in self.films]
            film_keys = [film['fc'] for film in self.films]
            
            # 更新影片下拉框
            self.movie_combo.clear()
            self.movie_combo.addItems(film_names)
            
            self.film_key_map = dict(zip(film_names, film_keys))
            self.films_map = {film['fc']: film for film in self.films}
            
            # 自动联动：选中第一个影片，触发影片选择事件
            if film_names:
                self.movie_combo.setCurrentIndex(0)
                # on_movie_select 会自动被 currentTextChanged 信号触发
            
            # 触发影院变化回调
            if self.on_cinema_changed:
                self.on_cinema_changed()
                
        except Exception as e:
            print(f"加载影院数据失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载影院数据失败: {str(e)}")
    
    def on_movie_select(self, film_name: str):
        """影片下拉框选中事件，加载对应影片的日期和场次数据"""
        if not film_name:
            return
        
        print(f"[DEBUG] on_movie_select 被触发: {film_name}")
        
        # 清空券列表
        if hasattr(self.main_window, '_clear_coupons_impl'):
            self.main_window._clear_coupons_impl()
        
        film_key = self.film_key_map.get(film_name)
        if not film_key or film_key not in self.shows:
            self.date_combo.clear()
            self.session_combo.clear()
            return
        
        date_list = list(self.shows[film_key].keys())
        
        # 更新日期下拉框
        self.date_combo.clear()
        self.date_combo.addItems(date_list)
        
        # 清空场次下拉框
        self.session_combo.clear()
        self.current_film_key = film_key
        
        # 自动联动：选中第一个日期，触发日期选择事件
        if date_list:
            self.date_combo.setCurrentIndex(0)
            # on_date_select 会自动被 currentTextChanged 信号触发
    
    def on_date_select(self, date_str: str):
        """日期下拉框选中事件，加载对应日期的场次数据"""
        if not date_str or not self.current_film_key:
            return
        
        print(f"[DEBUG] on_date_select 被触发: {date_str}")
        
        # 清空券列表
        if hasattr(self.main_window, '_clear_coupons_impl'):
            self.main_window._clear_coupons_impl()
        
        if self.current_film_key not in self.shows or date_str not in self.shows[self.current_film_key]:
            self.session_combo.clear()
            return
        
        sessions = self.shows[self.current_film_key][date_str]
        session_list = []
        
        for session in sessions:
            # 使用正确的字段名，与原始tkinter版本保持一致
            start_time = session.get('q', '')  # 开始时间
            hall_name = session.get('t', '')   # 厅名
            hall_info = session.get('r', '')   # 其他信息（厅类型等）
            ticket_price = session.get('tbprice', '0')  # 票价
            
            # 构建显示格式：时间 厅名 厅信息 票价:价格
            session_display = f"{start_time} {hall_name} {hall_info} 票价:{ticket_price}"
            session_list.append(session_display)
        
        # 更新场次下拉框
        self.session_combo.clear()
        self.session_combo.addItems(session_list)
        
        # 自动选中第一个场次
        if session_list:
            self.session_combo.setCurrentIndex(0)
            # on_session_select 会自动被 currentTextChanged 信号触发
    
    def on_session_select(self, session_str: str):
        """场次下拉框选中事件，加载座位图"""
        if not session_str or not self.current_film_key:
            return
        
        print(f"[DEBUG] on_session_select 被触发: {session_str}")
        
        # 清空券列表
        if hasattr(self.main_window, '_clear_coupons_impl'):
            self.main_window._clear_coupons_impl()
        
        current_date = self.date_combo.currentText()
        if not current_date:
            return
        
        session_index = self.session_combo.currentIndex()
        if session_index < 0:
            return
        
        try:
            sessions = self.shows[self.current_film_key][current_date]
            if session_index >= len(sessions):
                return
            
            selected_session = sessions[session_index]
            
            # 更新当前账号显示
            current_account = self.get_current_account()
            if current_account:
                phone = current_account.get('phone', 'Unknown')
                self.current_account_label.setText(f"当前账号：{phone}")
            
            # 获取座位信息
            self._load_seat_info(selected_session)
            
        except Exception as e:
            print(f"场次选择处理失败: {e}")
    
    def _load_seat_info(self, session_info: Dict):
        """加载座位信息"""
        try:
            current_account = self.get_current_account()
            if not current_account:
                return
            
            current_index = self.cinema_combo.currentIndex()
            if current_index < 0 or current_index >= len(self.cinemas):
                return
            
            selected_cinema = self.cinemas[current_index]
            base_url = selected_cinema['base_url']
            cinemaid = selected_cinema['cinemaid']
            
            openid = current_account.get('openid', '')
            token = current_account.get('token', '')
            userid = current_account.get('userid', '')
            
            # 使用正确的字段名，与原始tkinter版本保持一致
            showCode = session_info.get('g', '')           # 场次唯一编码
            hallCode = session_info.get('j', '')           # 影厅编码
            filmCode = session_info.get('h', self.current_film_key)  # 影片编码
            showDate = session_info.get('k', '').split(' ')[0] if session_info.get('k') else ''  # 放映日期
            startTime = session_info.get('q', '')          # 放映开始时间
            
            # 获取影片No
            filmNo = ''
            if self.current_film_key and self.current_film_key in self.films_map:
                filmNo = self.films_map[self.current_film_key].get('fno', '')
            
            if not showCode:
                print("[DEBUG] 缺少showCode，无法获取座位信息")
                return
            
            print(f"[DEBUG] 获取座位信息参数:")
            print(f"  showCode={showCode}, hallCode={hallCode}")
            print(f"  filmCode={filmCode}, filmNo={filmNo}")
            print(f"  showDate={showDate}, startTime={startTime}")
            
            # 获取座位数据
            seat_data = get_plan_seat_info(
                base_url, showCode, hallCode, filmCode, filmNo, 
                showDate, startTime, userid, openid, token, cinemaid
            )
            
            # 检查API返回
            if isinstance(seat_data, dict):
                if seat_data.get('resultCode') == '400':
                    error_msg = seat_data.get('resultDesc', '未知错误')
                    print(f"[DEBUG] 座位API错误: {error_msg}")
                    QMessageBox.warning(self, "API错误", f"获取座位信息失败: {error_msg}\n\n这通常是因为：\n1. 账号token已过期\n2. 账号权限不足\n3. 场次信息无效")
                    return
                elif seat_data.get('resultCode') == '0' and 'resultData' in seat_data:
                    # 成功获取数据
                    result_data = seat_data['resultData']
                    print(f"[DEBUG] 成功获取座位数据")
                    
                    # 更新座位面板
                    if self.seat_panel:
                        self.seat_panel.update_seat_data(result_data)
                else:
                    print(f"[DEBUG] 未知的API响应格式: {seat_data}")
                    QMessageBox.warning(self, "数据错误", "获取到的座位数据格式异常")
            else:
                print(f"[DEBUG] API返回非字典类型数据: {type(seat_data)}")
                QMessageBox.warning(self, "响应错误", "座位API返回数据格式错误")
            
        except Exception as e:
            print(f"加载座位信息失败: {e}")
            QMessageBox.warning(self, "加载失败", f"加载座位信息失败: {str(e)}")
    
    def on_open_seat_selection(self):
        """选座按钮点击事件 - 打开或刷新座位图"""
        current_account = self.get_current_account()
        if not current_account:
            QMessageBox.warning(self, "账号提示", "请先选择账号")
            return

        if not self.session_combo.currentText():
            QMessageBox.warning(self, "场次提示", "请先选择场次")
            return

        # 重新加载当前场次的座位信息
        print(f"[影院面板] 用户点击选座按钮，刷新座位图")
        self.on_session_select(self.session_combo.currentText())

        # 不显示提示信息，直接刷新座位图
        print(f"[影院面板] 座位图已刷新")
    
    def set_current_account(self, account: Dict):
        """设置当前账号（外部调用接口）"""
        if account:
            phone = account.get('phone', 'Unknown')
            self.current_account_label.setText(f"当前账号：{phone}")
        else:
            self.current_account_label.setText("当前账号：-")
    
    def get_current_session_info(self):
        """获取当前选中的场次信息"""
        if not self.current_film_key:
            return None
        
        current_date = self.date_combo.currentText()
        session_index = self.session_combo.currentIndex()
        
        if not current_date or session_index < 0:
            return None
        
        try:
            sessions = self.shows[self.current_film_key][current_date]
            if session_index < len(sessions):
                return sessions[session_index]
        except (KeyError, IndexError):
            pass
        
        return None
    
    def get_current_film_info(self):
        """获取当前选中的影片信息"""
        if not self.current_film_key or self.current_film_key not in self.films_map:
            return None
        return self.films_map[self.current_film_key] 