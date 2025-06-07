"""
智能级联选择管理器

功能：
1. 影院→影片→场次→座位的智能级联选择
2. 异步数据加载和UI更新
3. 选择状态管理和回滚机制
4. 用户交互优化和进度反馈
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

from services.smart_recognition import OrderInfo, MatchResult
from services.enhanced_matching_engine import EnhancedMatchingEngine


@dataclass
class SelectionStep:
    """选择步骤"""
    name: str
    status: str  # 'pending', 'loading', 'success', 'failed', 'skipped'
    data: Any = None
    error: str = ""
    progress: float = 0.0


@dataclass
class CascadeState:
    """级联选择状态"""
    cinema_step: SelectionStep
    movie_step: SelectionStep
    session_step: SelectionStep
    seat_step: SelectionStep
    overall_progress: float = 0.0
    is_running: bool = False
    can_rollback: bool = False


class CascadeSelectionManager(QObject):
    """智能级联选择管理器"""
    
    # 信号定义
    step_started = pyqtSignal(str)  # 步骤开始
    step_completed = pyqtSignal(str, bool, str)  # 步骤完成(步骤名, 成功, 消息)
    progress_updated = pyqtSignal(float)  # 进度更新
    selection_completed = pyqtSignal(bool, dict)  # 选择完成(成功, 结果)
    user_confirmation_needed = pyqtSignal(str, list)  # 需要用户确认(步骤名, 候选项)
    
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.enhanced_engine = EnhancedMatchingEngine(main_window)
        self.state = self._init_state()
        self.selection_callbacks = {}
        self.rollback_data = {}
        
    def _init_state(self) -> CascadeState:
        """初始化状态"""
        return CascadeState(
            cinema_step=SelectionStep("影院选择", "pending"),
            movie_step=SelectionStep("影片选择", "pending"),
            session_step=SelectionStep("场次选择", "pending"),
            seat_step=SelectionStep("座位选择", "pending")
        )
    
    async def start_cascade_selection(self, order_info: OrderInfo, auto_mode: bool = True) -> bool:
        """开始级联选择"""
        try:
            if self.state.is_running:
                print("[级联选择] 级联选择正在进行中")
                return False
            
            print(f"[级联选择] 开始智能级联选择 (自动模式: {auto_mode})")
            
            # 重置状态
            self.state = self._init_state()
            self.state.is_running = True
            self.rollback_data.clear()
            
            # 保存原始状态用于回滚
            self._save_rollback_data()
            
            success = True
            
            try:
                # 步骤1：影院选择
                success &= await self._select_cinema(order_info, auto_mode)
                if not success and not auto_mode:
                    return False
                
                # 步骤2：影片选择
                if success and self.state.cinema_step.status == 'success':
                    success &= await self._select_movie(order_info, auto_mode)
                
                # 步骤3：场次选择
                if success and self.state.movie_step.status == 'success':
                    success &= await self._select_session(order_info, auto_mode)
                
                # 步骤4：座位选择
                if success and self.state.session_step.status == 'success':
                    success &= await self._select_seats(order_info, auto_mode)
                
                # 完成选择
                self._finalize_selection(success)
                
                return success
                
            except Exception as e:
                print(f"[级联选择] 级联选择过程异常: {e}")
                self._finalize_selection(False)
                return False
            
        except Exception as e:
            print(f"[级联选择] 启动级联选择失败: {e}")
            return False
    
    async def _select_cinema(self, order_info: OrderInfo, auto_mode: bool) -> bool:
        """选择影院"""
        try:
            self.state.cinema_step.status = 'loading'
            self.step_started.emit("影院选择")
            self._update_progress(10)
            
            # 获取影院数据
            cinemas_data = self._get_cinemas_data()
            if not cinemas_data:
                self.state.cinema_step.status = 'failed'
                self.state.cinema_step.error = "无法获取影院数据"
                self.step_completed.emit("影院选择", False, "无法获取影院数据")
                return False
            
            self._update_progress(20)
            
            # 使用增强匹配引擎查找影院
            cinema_match = await self.enhanced_engine.enhanced_cinema_match(order_info, cinemas_data)
            
            if cinema_match:
                # 自动选择影院
                success = await self._apply_cinema_selection(cinema_match)
                if success:
                    self.state.cinema_step.status = 'success'
                    self.state.cinema_step.data = cinema_match
                    self.step_completed.emit("影院选择", True, f"已选择: {cinema_match.get('cinemaShortName')}")
                    self._update_progress(25)
                    return True
                else:
                    self.state.cinema_step.status = 'failed'
                    self.state.cinema_step.error = "影院选择应用失败"
                    self.step_completed.emit("影院选择", False, "影院选择应用失败")
                    return False
            else:
                # 未找到匹配的影院
                if auto_mode:
                    self.state.cinema_step.status = 'failed'
                    self.state.cinema_step.error = f"未找到匹配的影院: {order_info.cinema_name}"
                    self.step_completed.emit("影院选择", False, f"未找到匹配的影院: {order_info.cinema_name}")
                    return False
                else:
                    # 手动模式：提供候选项让用户选择
                    candidates = self.enhanced_engine.find_cinema_candidates(order_info.cinema_name, cinemas_data)
                    if candidates:
                        self.user_confirmation_needed.emit("影院选择", [c.data for c in candidates[:5]])
                        return False  # 等待用户选择
                    else:
                        self.state.cinema_step.status = 'failed'
                        self.state.cinema_step.error = "未找到任何候选影院"
                        self.step_completed.emit("影院选择", False, "未找到任何候选影院")
                        return False
            
        except Exception as e:
            print(f"[级联选择] 影院选择失败: {e}")
            self.state.cinema_step.status = 'failed'
            self.state.cinema_step.error = str(e)
            self.step_completed.emit("影院选择", False, f"影院选择失败: {e}")
            return False
    
    async def _select_movie(self, order_info: OrderInfo, auto_mode: bool) -> bool:
        """选择影片"""
        try:
            self.state.movie_step.status = 'loading'
            self.step_started.emit("影片选择")
            self._update_progress(35)
            
            # 等待影片数据加载
            await asyncio.sleep(0.5)  # 给UI时间更新
            
            # 获取影片数据
            movies_data = self._get_movies_data()
            if not movies_data:
                self.state.movie_step.status = 'failed'
                self.state.movie_step.error = "无法获取影片数据"
                self.step_completed.emit("影片选择", False, "无法获取影片数据")
                return False
            
            self._update_progress(45)
            
            # 查找匹配的影片
            movie_match = self._find_movie_match(order_info, movies_data)
            
            if movie_match:
                # 自动选择影片
                success = await self._apply_movie_selection(movie_match)
                if success:
                    self.state.movie_step.status = 'success'
                    self.state.movie_step.data = movie_match
                    self.step_completed.emit("影片选择", True, f"已选择: {movie_match.get('name', movie_match.get('filmName'))}")
                    self._update_progress(50)
                    return True
                else:
                    self.state.movie_step.status = 'failed'
                    self.state.movie_step.error = "影片选择应用失败"
                    self.step_completed.emit("影片选择", False, "影片选择应用失败")
                    return False
            else:
                # 未找到匹配的影片
                self.state.movie_step.status = 'failed'
                self.state.movie_step.error = f"未找到匹配的影片: {order_info.movie_name}"
                self.step_completed.emit("影片选择", False, f"未找到匹配的影片: {order_info.movie_name}")
                return False
            
        except Exception as e:
            print(f"[级联选择] 影片选择失败: {e}")
            self.state.movie_step.status = 'failed'
            self.state.movie_step.error = str(e)
            self.step_completed.emit("影片选择", False, f"影片选择失败: {e}")
            return False
    
    async def _select_session(self, order_info: OrderInfo, auto_mode: bool) -> bool:
        """选择场次"""
        try:
            self.state.session_step.status = 'loading'
            self.step_started.emit("场次选择")
            self._update_progress(60)
            
            # 等待场次数据加载
            await asyncio.sleep(0.5)
            
            # 获取场次数据
            sessions_data = self._get_sessions_data()
            if not sessions_data:
                self.state.session_step.status = 'failed'
                self.state.session_step.error = "无法获取场次数据"
                self.step_completed.emit("场次选择", False, "无法获取场次数据")
                return False
            
            self._update_progress(70)
            
            # 查找匹配的场次
            session_match = self._find_session_match(order_info, sessions_data)
            
            if session_match:
                # 自动选择场次
                success = await self._apply_session_selection(session_match)
                if success:
                    self.state.session_step.status = 'success'
                    self.state.session_step.data = session_match
                    self.step_completed.emit("场次选择", True, f"已选择: {session_match.get('time', session_match.get('showTime'))}")
                    self._update_progress(75)
                    return True
                else:
                    self.state.session_step.status = 'failed'
                    self.state.session_step.error = "场次选择应用失败"
                    self.step_completed.emit("场次选择", False, "场次选择应用失败")
                    return False
            else:
                # 未找到匹配的场次
                self.state.session_step.status = 'failed'
                self.state.session_step.error = f"未找到匹配的场次: {order_info.session_time}"
                self.step_completed.emit("场次选择", False, f"未找到匹配的场次: {order_info.session_time}")
                return False
            
        except Exception as e:
            print(f"[级联选择] 场次选择失败: {e}")
            self.state.session_step.status = 'failed'
            self.state.session_step.error = str(e)
            self.step_completed.emit("场次选择", False, f"场次选择失败: {e}")
            return False
    
    async def _select_seats(self, order_info: OrderInfo, auto_mode: bool) -> bool:
        """选择座位"""
        try:
            self.state.seat_step.status = 'loading'
            self.step_started.emit("座位选择")
            self._update_progress(85)
            
            # 等待座位图加载
            await asyncio.sleep(1.0)
            
            # 解析座位信息
            seat_matches = self._parse_seat_info(order_info)
            if not seat_matches:
                self.state.seat_step.status = 'failed'
                self.state.seat_step.error = "无法解析座位信息"
                self.step_completed.emit("座位选择", False, "无法解析座位信息")
                return False
            
            self._update_progress(90)
            
            # 应用座位选择
            success = await self._apply_seat_selection(seat_matches)
            if success:
                self.state.seat_step.status = 'success'
                self.state.seat_step.data = seat_matches
                seat_str = ", ".join([f"{s['row']}排{s['col']}座" for s in seat_matches])
                self.step_completed.emit("座位选择", True, f"已选择: {seat_str}")
                self._update_progress(100)
                return True
            else:
                self.state.seat_step.status = 'failed'
                self.state.seat_step.error = "座位选择应用失败"
                self.step_completed.emit("座位选择", False, "座位选择应用失败")
                return False
            
        except Exception as e:
            print(f"[级联选择] 座位选择失败: {e}")
            self.state.seat_step.status = 'failed'
            self.state.seat_step.error = str(e)
            self.step_completed.emit("座位选择", False, f"座位选择失败: {e}")
            return False
    
    def _get_cinemas_data(self) -> List[Dict]:
        """获取影院数据"""
        try:
            if hasattr(self.main_window, 'tab_manager_widget') and hasattr(self.main_window.tab_manager_widget, 'cinemas_data'):
                return self.main_window.tab_manager_widget.cinemas_data or []
            return []
        except:
            return []
    
    def _get_movies_data(self) -> List[Dict]:
        """获取影片数据"""
        try:
            # 这里需要根据实际的数据获取方式实现
            # 暂时返回空列表
            return []
        except:
            return []
    
    def _get_sessions_data(self) -> List[Dict]:
        """获取场次数据"""
        try:
            # 这里需要根据实际的数据获取方式实现
            # 暂时返回空列表
            return []
        except:
            return []
    
    def _find_movie_match(self, order_info: OrderInfo, movies_data: List[Dict]) -> Optional[Dict]:
        """查找影片匹配"""
        # 使用现有的影片匹配逻辑
        # 这里可以集成增强匹配引擎的影片匹配功能
        return None
    
    def _find_session_match(self, order_info: OrderInfo, sessions_data: List[Dict]) -> Optional[Dict]:
        """查找场次匹配"""
        # 使用现有的场次匹配逻辑
        return None
    
    def _parse_seat_info(self, order_info: OrderInfo) -> List[Dict]:
        """解析座位信息"""
        try:
            seat_matches = []
            for seat_str in order_info.seats:
                import re
                match = re.match(r'(\d+)排(\d+)座', seat_str)
                if match:
                    row = int(match.group(1))
                    col = int(match.group(2))
                    seat_matches.append({
                        'row': row,
                        'col': col,
                        'seat_str': seat_str
                    })
            return seat_matches
        except:
            return []
    
    async def _apply_cinema_selection(self, cinema_data: Dict) -> bool:
        """应用影院选择"""
        try:
            # 这里需要调用实际的影院选择逻辑
            # 例如：触发影院选择事件，更新UI等
            print(f"[级联选择] 应用影院选择: {cinema_data.get('cinemaShortName')}")
            return True
        except:
            return False
    
    async def _apply_movie_selection(self, movie_data: Dict) -> bool:
        """应用影片选择"""
        try:
            print(f"[级联选择] 应用影片选择: {movie_data.get('name', movie_data.get('filmName'))}")
            return True
        except:
            return False
    
    async def _apply_session_selection(self, session_data: Dict) -> bool:
        """应用场次选择"""
        try:
            print(f"[级联选择] 应用场次选择: {session_data.get('time', session_data.get('showTime'))}")
            return True
        except:
            return False
    
    async def _apply_seat_selection(self, seat_matches: List[Dict]) -> bool:
        """应用座位选择"""
        try:
            print(f"[级联选择] 应用座位选择: {len(seat_matches)}个座位")
            return True
        except:
            return False
    
    def _update_progress(self, progress: float):
        """更新进度"""
        self.state.overall_progress = progress
        self.progress_updated.emit(progress)
    
    def _save_rollback_data(self):
        """保存回滚数据"""
        try:
            # 保存当前选择状态，用于回滚
            self.rollback_data = {
                'cinema': None,  # 当前选择的影院
                'movie': None,   # 当前选择的影片
                'session': None, # 当前选择的场次
                'seats': []      # 当前选择的座位
            }
            self.state.can_rollback = True
        except:
            pass
    
    def _finalize_selection(self, success: bool):
        """完成选择"""
        try:
            self.state.is_running = False
            
            if success:
                result = {
                    'cinema': self.state.cinema_step.data,
                    'movie': self.state.movie_step.data,
                    'session': self.state.session_step.data,
                    'seats': self.state.seat_step.data
                }
                self.selection_completed.emit(True, result)
                print("[级联选择] 智能级联选择完成")
            else:
                self.selection_completed.emit(False, {})
                print("[级联选择] 智能级联选择失败")
            
        except Exception as e:
            print(f"[级联选择] 完成选择处理失败: {e}")
    
    def rollback_selection(self):
        """回滚选择"""
        try:
            if not self.state.can_rollback:
                return False
            
            print("[级联选择] 执行选择回滚")
            
            # 恢复之前的选择状态
            # 这里需要根据实际的UI组件实现回滚逻辑
            
            # 重置状态
            self.state = self._init_state()
            
            return True
            
        except Exception as e:
            print(f"[级联选择] 回滚选择失败: {e}")
            return False
    
    def get_selection_state(self) -> CascadeState:
        """获取选择状态"""
        return self.state
