#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
影院控制器 - 处理影院相关的业务逻辑
"""

from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal
from utils.signals import event_bus, event_handler
from services.cinema_manager import CinemaManager
from services.film_service import get_films, normalize_film_data, get_plan_seat_info


class CinemaController(QObject):
    """影院控制器"""
    
    # 信号定义
    cinema_selected = pyqtSignal(dict)  # 影院选择
    cinema_list_updated = pyqtSignal(list)  # 影院列表更新
    movie_list_updated = pyqtSignal(list)  # 电影列表更新
    session_list_updated = pyqtSignal(list)  # 场次列表更新
    seat_map_loaded = pyqtSignal(dict)  # 座位图加载完成
    cinema_error = pyqtSignal(str, str)  # 影院错误 (title, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 服务实例
        self.cinema_manager = CinemaManager()
        
        # 当前状态
        self.current_cinema = None
        self.current_account = None
        self.cinema_list = []
        self.movie_list = []
        self.session_list = []
        
        # 连接事件总线
        self._connect_events()
        
        print("[影院控制器] 初始化完成")
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.account_selected.connect(self._on_account_selected)
        event_bus.user_login_success.connect(self._on_user_login_success)
    
    @event_handler("account_selected")
    def _on_account_selected(self, account_data: dict):
        """账号选择处理"""
        self.current_account = account_data
        print(f"[影院控制器] 账号已选择: {account_data.get('phone', 'N/A')}")
        
        # 如果有当前影院，重新加载电影列表
        if self.current_cinema:
            self.load_movie_list()
    
    @event_handler("user_login_success")
    def _on_user_login_success(self, user_data: dict):
        """用户登录成功处理"""
        print(f"[影院控制器] 用户登录成功: {user_data.get('phone', 'N/A')}")
        
        # 加载影院列表
        self.load_cinema_list()
    
    def load_cinema_list(self) -> List[dict]:
        """移除本地影院文件加载 - 影院通过API动态获取"""
        try:
            print("[影院控制器] 🚫 已移除本地影院文件加载")
            print("[影院控制器] 🔄 沃美系统：影院将通过城市API动态获取")

            # 不再从本地文件加载影院列表
            # 沃美系统的影院数据通过城市API获取
            self.cinema_list = []

            # 发布空的影院列表（表示需要通过API获取）
            self.cinema_list_updated.emit([])
            event_bus.cinema_list_updated.emit([])

            return []

        except Exception as e:
            print(f"[影院控制器] 初始化错误: {e}")
            self.cinema_error.emit("初始化失败", f"影院控制器初始化失败: {str(e)}")
            return []
    
    def select_cinema(self, cinema_data: dict):
        """选择影院"""
        try:
            if not cinema_data:
                return
            
            self.current_cinema = cinema_data
            cinema_name = cinema_data.get('cinemaShortName', 'N/A')
            
            print(f"[影院控制器] 影院已选择: {cinema_name}")
            
            # 发布影院选择事件
            self.cinema_selected.emit(cinema_data)
            event_bus.cinema_selected.emit(cinema_data)
            
            # 加载该影院的电影列表
            self.load_movie_list()
            
        except Exception as e:
            print(f"[影院控制器] 选择影院错误: {e}")
            self.cinema_error.emit("选择失败", f"选择影院失败: {str(e)}")
    
    def load_movie_list(self) -> List[dict]:
        """加载电影列表"""
        try:
            if not self.current_cinema or not self.current_account:
                print("[影院控制器] 影院或账号信息不完整，无法加载电影")
                return []
            
            print("[影院控制器] 开始加载电影列表")
            
            # 获取必要参数
            base_url = self.current_cinema.get('base_url', '') or self.current_cinema.get('domain', '')
            if base_url:
                base_url = base_url.replace('https://', '').replace('http://', '')
            
            cinema_id = self.current_cinema.get('cinemaid', '')
            user_id = self.current_account.get('userid', '')
            openid = self.current_account.get('openid', '')
            token = self.current_account.get('token', '')
            
            if not all([base_url, cinema_id, user_id]):
                print("[影院控制器] 参数不完整，无法加载电影")
                return []
            
            # 调用API获取电影
            raw_data = get_films(base_url, cinema_id, openid, user_id, token)
            normalized_data = normalize_film_data(raw_data)
            
            movies = normalized_data.get('films', [])
            
            if movies:
                self.movie_list = movies
                print(f"[影院控制器] 电影列表加载成功: {len(movies)} 部电影")
                
                # 发布电影列表更新事件
                self.movie_list_updated.emit(movies)
                event_bus.movie_list_updated.emit(movies)
                
                return movies
            else:
                print("[影院控制器] 没有获取到电影数据")
                self.movie_list = []
                self.movie_list_updated.emit([])
                return []
                
        except Exception as e:
            print(f"[影院控制器] 加载电影列表错误: {e}")
            self.cinema_error.emit("加载失败", f"加载电影列表失败: {str(e)}")
            
            # 如果API调用失败，使用默认电影列表
            default_movies = [
                {"name": "阿凡达：水之道", "id": "1"},
                {"name": "流浪地球2", "id": "2"},
                {"name": "满江红", "id": "3"}
            ]
            self.movie_list = default_movies
            self.movie_list_updated.emit(default_movies)
            return default_movies
    
    def select_movie(self, movie_data: dict):
        """选择电影"""
        try:
            if not movie_data:
                return
            
            movie_name = movie_data.get('name', 'N/A')
            print(f"[影院控制器] 电影已选择: {movie_name}")
            
            # 发布电影选择事件
            event_bus.movie_selected.emit(movie_data)
            
            # 加载该电影的场次列表
            self.load_session_list(movie_data)
            
        except Exception as e:
            print(f"[影院控制器] 选择电影错误: {e}")
            self.cinema_error.emit("选择失败", f"选择电影失败: {str(e)}")
    
    def load_session_list(self, movie_data: dict) -> List[dict]:
        """加载场次列表"""
        try:
            # 这里应该调用API获取场次列表
            # 目前使用模拟数据
            
            sessions = [
                {
                    "time": "10:30",
                    "hall": "1号厅",
                    "price": "35.00",
                    "session_id": "s1"
                },
                {
                    "time": "14:20",
                    "hall": "2号厅", 
                    "price": "40.00",
                    "session_id": "s2"
                },
                {
                    "time": "18:45",
                    "hall": "3号厅",
                    "price": "45.00",
                    "session_id": "s3"
                }
            ]
            
            self.session_list = sessions
            print(f"[影院控制器] 场次列表加载成功: {len(sessions)} 个场次")
            
            # 发布场次列表更新事件
            self.session_list_updated.emit(sessions)
            event_bus.session_list_updated.emit(sessions)
            
            return sessions
            
        except Exception as e:
            print(f"[影院控制器] 加载场次列表错误: {e}")
            self.cinema_error.emit("加载失败", f"加载场次列表失败: {str(e)}")
            return []
    
    def select_session(self, session_data: dict):
        """选择场次"""
        try:
            if not session_data:
                return
            
            session_time = session_data.get('time', 'N/A')
            print(f"[影院控制器] 场次已选择: {session_time}")
            
            # 发布场次选择事件
            event_bus.session_selected.emit(session_data)
            
            # 加载座位图
            self.load_seat_map(session_data)
            
        except Exception as e:
            print(f"[影院控制器] 选择场次错误: {e}")
            self.cinema_error.emit("选择失败", f"选择场次失败: {str(e)}")
    
    def load_seat_map(self, session_data: dict) -> Optional[dict]:
        """加载座位图"""
        try:
            if not all([self.current_cinema, self.current_account, session_data]):
                print("[影院控制器] 信息不完整，无法加载座位图")
                return None
            
            print("[影院控制器] 开始加载座位图")
            
            # 发布座位图加载中事件
            event_bus.seat_map_loading.emit()
            
            # 获取必要参数
            base_url = self.current_cinema.get('base_url', '') or self.current_cinema.get('domain', '')
            if base_url:
                base_url = base_url.replace('https://', '').replace('http://', '')
            
            # 构建API参数
            params = {
                'base_url': base_url,
                'showCode': session_data.get('g', ''),
                'hallCode': session_data.get('j', ''),
                'filmCode': session_data.get('h', ''),
                'filmNo': session_data.get('fno', ''),
                'showDate': session_data.get('k', '').split(' ')[0] if session_data.get('k') else '',
                'startTime': session_data.get('q', ''),
                'userid': self.current_account.get('userid', ''),
                'openid': self.current_account.get('openid', ''),
                'token': self.current_account.get('token', ''),
                'cinemaid': self.current_cinema.get('cinemaid', ''),
                'cardno': self.current_account.get('cardno', '')
            }
            
            # 验证参数完整性
            required_params = ['base_url', 'showCode', 'hallCode', 'filmCode', 'userid', 'openid', 'token', 'cinemaid']
            missing_params = [p for p in required_params if not params.get(p)]
            if missing_params:
                error_msg = f"缺少必要参数: {', '.join(missing_params)}"
                print(f"[影院控制器] {error_msg}")
                event_bus.seat_map_error.emit(error_msg)
                return None
            
            # 调用座位图API
            seat_result = get_plan_seat_info(**params)
            
            if seat_result and isinstance(seat_result, dict):
                if seat_result.get('resultCode') == '0':
                    # 成功获取座位数据
                    seat_data = seat_result.get('resultData', {})
                    
                    print("[影院控制器] 座位图加载成功")
                    
                    # 发布座位图加载完成事件
                    self.seat_map_loaded.emit(seat_data)
                    event_bus.seat_map_loaded.emit(seat_data)
                    
                    return seat_data
                else:
                    # API返回错误
                    error_msg = seat_result.get('resultDesc', '未知错误')
                    print(f"[影院控制器] 座位图API错误: {error_msg}")
                    event_bus.seat_map_error.emit(error_msg)
                    return None
            else:
                # 响应格式错误
                print("[影院控制器] 座位图API响应格式错误")
                event_bus.seat_map_error.emit("座位图数据格式错误")
                return None
                
        except Exception as e:
            print(f"[影院控制器] 加载座位图错误: {e}")
            import traceback
            traceback.print_exc()
            event_bus.seat_map_error.emit(f"加载座位图异常: {str(e)}")
            return None
    
    def get_current_cinema(self) -> Optional[dict]:
        """获取当前影院"""
        return self.current_cinema
    
    def get_cinema_list(self) -> List[dict]:
        """获取影院列表"""
        return self.cinema_list.copy()
    
    def get_movie_list(self) -> List[dict]:
        """获取电影列表"""
        return self.movie_list.copy()
    
    def get_session_list(self) -> List[dict]:
        """获取场次列表"""
        return self.session_list.copy()
    
    def find_cinema_by_name(self, cinema_name: str) -> Optional[dict]:
        """根据名称查找影院"""
        for cinema in self.cinema_list:
            if cinema.get('cinemaShortName') == cinema_name or cinema.get('name') == cinema_name:
                return cinema
        return None
