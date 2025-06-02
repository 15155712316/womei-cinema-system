#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
事件总线系统 - 用于组件间通信
重构版本：提供更强大的事件管理和组件解耦能力
"""

from PyQt5.QtCore import QObject, pyqtSignal
from typing import Dict, Any, Callable, List, Optional
import weakref
import threading
import time


class EventBus(QObject):
    """全局事件总线 - 重构版本"""

    # ===== 用户认证事件 =====
    user_login_success = pyqtSignal(dict)  # 用户登录成功
    user_logout = pyqtSignal()  # 用户登出
    user_auth_failed = pyqtSignal(str)  # 用户认证失败

    # ===== 账号管理事件 =====
    account_selected = pyqtSignal(dict)  # 账号选择
    account_changed = pyqtSignal(dict)  # 账号变更
    account_login_success = pyqtSignal(dict)  # 账号登录成功
    account_login_failed = pyqtSignal(str)  # 账号登录失败
    account_added = pyqtSignal(dict)  # 账号添加
    account_removed = pyqtSignal(str)  # 账号删除
    account_list_updated = pyqtSignal(list)  # 账号列表更新

    # ===== 影院管理事件 =====
    cinema_selected = pyqtSignal(dict)  # 影院选择
    cinema_changed = pyqtSignal(dict)  # 影院变更
    cinema_list_updated = pyqtSignal(list)  # 影院列表更新

    # ===== 电影和场次事件 =====
    movie_selected = pyqtSignal(dict)  # 电影选择
    movie_list_updated = pyqtSignal(list)  # 电影列表更新
    session_selected = pyqtSignal(dict)  # 场次选择
    session_list_updated = pyqtSignal(list)  # 场次列表更新

    # ===== 座位管理事件 =====
    seat_selected = pyqtSignal(list)  # 座位选择
    seat_map_loaded = pyqtSignal(dict)  # 座位图加载完成
    seat_map_loading = pyqtSignal()  # 座位图加载中
    seat_map_error = pyqtSignal(str)  # 座位图加载错误

    # ===== 订单管理事件 =====
    order_created = pyqtSignal(dict)  # 订单创建
    order_submitted = pyqtSignal(dict)  # 订单提交
    order_paid = pyqtSignal(str)  # 订单支付成功
    order_cancelled = pyqtSignal(str)  # 订单取消
    order_list_updated = pyqtSignal(list)  # 订单列表更新
    order_detail_updated = pyqtSignal(dict)  # 订单详情更新
    show_qrcode = pyqtSignal(object)  # 显示二维码 (二维码数据字典或文本信息)

    # ===== 券管理事件 =====
    coupon_bound = pyqtSignal(dict)  # 券绑定
    coupon_selected = pyqtSignal(list)  # 券选择
    coupon_exchanged = pyqtSignal(dict)  # 券兑换
    coupon_list_updated = pyqtSignal(list)  # 券列表更新

    # ===== 系统事件 =====
    error_occurred = pyqtSignal(str, str)  # 错误发生 (title, message)
    message_show = pyqtSignal(str, str, str)  # 显示消息 (type, title, message)
    loading_started = pyqtSignal(str)  # 开始加载 (message)
    loading_finished = pyqtSignal()  # 加载完成

    # ===== UI状态事件 =====
    ui_state_changed = pyqtSignal(str)  # UI状态变更
    component_ready = pyqtSignal(str)  # 组件就绪

    def __init__(self):
        super().__init__()
        self._subscribers = {}  # 事件订阅者
        self._event_history = []  # 事件历史记录
        self._max_history = 100  # 最大历史记录数
        self._lock = threading.Lock()  # 线程锁

    def subscribe(self, event_name: str, callback: Callable):
        """订阅事件"""
        with self._lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []

            # 使用弱引用避免内存泄漏
            self._subscribers[event_name].append(weakref.ref(callback))
            print(f"[事件总线] 订阅事件: {event_name}")

    def unsubscribe(self, event_name: str, callback: Callable):
        """取消订阅事件"""
        with self._lock:
            if event_name in self._subscribers:
                self._subscribers[event_name] = [
                    ref for ref in self._subscribers[event_name]
                    if ref() is not None and ref() != callback
                ]
                print(f"[事件总线] 取消订阅事件: {event_name}")

    def emit_custom(self, event_name: str, data: Any = None):
        """发送自定义事件"""
        with self._lock:
            # 记录事件历史
            self._record_event(event_name, data)

            if event_name in self._subscribers:
                # 清理失效的弱引用
                valid_refs = []
                for ref in self._subscribers[event_name]:
                    callback = ref()
                    if callback is not None:
                        try:
                            if data is not None:
                                callback(data)
                            else:
                                callback()
                            valid_refs.append(ref)
                        except Exception as e:
                            print(f"[事件总线] 回调执行错误: {e}")
                            import traceback
                            traceback.print_exc()

                self._subscribers[event_name] = valid_refs

    def _record_event(self, event_name: str, data: Any):
        """记录事件历史"""
        event_record = {
            'name': event_name,
            'data': data,
            'timestamp': time.time()
        }

        self._event_history.append(event_record)

        # 限制历史记录数量
        if len(self._event_history) > self._max_history:
            self._event_history = self._event_history[-self._max_history:]

    def get_event_history(self, event_name: Optional[str] = None) -> List[Dict]:
        """获取事件历史记录"""
        with self._lock:
            if event_name:
                return [e for e in self._event_history if e['name'] == event_name]
            return self._event_history.copy()

    def clear_history(self):
        """清空事件历史"""
        with self._lock:
            self._event_history.clear()

    def get_subscribers_count(self, event_name: str) -> int:
        """获取事件订阅者数量"""
        with self._lock:
            if event_name in self._subscribers:
                # 清理失效的弱引用
                valid_refs = [ref for ref in self._subscribers[event_name] if ref() is not None]
                self._subscribers[event_name] = valid_refs
                return len(valid_refs)
            return 0


# 全局事件总线实例
event_bus = EventBus()


# ===== 便捷装饰器 =====

def event_handler(event_name: str):
    """事件处理装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                event_bus.error_occurred.emit("事件处理错误", f"处理事件 {event_name} 时发生错误: {str(e)}")
                print(f"[事件处理] {event_name} 处理错误: {e}")
                import traceback
                traceback.print_exc()
        return wrapper
    return decorator


# ===== 事件管理器 =====

class EventManager:
    """事件管理器 - 提供高级事件管理功能"""

    def __init__(self):
        self.bus = event_bus
        self._component_states = {}  # 组件状态跟踪

    def register_component(self, component_name: str, component_instance):
        """注册组件"""
        self._component_states[component_name] = {
            'instance': weakref.ref(component_instance),
            'ready': False,
            'last_update': time.time()
        }
        print(f"[事件管理器] 注册组件: {component_name}")

    def mark_component_ready(self, component_name: str):
        """标记组件就绪"""
        if component_name in self._component_states:
            self._component_states[component_name]['ready'] = True
            self._component_states[component_name]['last_update'] = time.time()
            self.bus.component_ready.emit(component_name)
            print(f"[事件管理器] 组件就绪: {component_name}")

    def is_component_ready(self, component_name: str) -> bool:
        """检查组件是否就绪"""
        return self._component_states.get(component_name, {}).get('ready', False)

    def wait_for_component(self, component_name: str, timeout: float = 5.0) -> bool:
        """等待组件就绪"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_component_ready(component_name):
                return True
            time.sleep(0.1)
        return False

    def get_component_status(self) -> Dict[str, Dict]:
        """获取所有组件状态"""
        status = {}
        for name, state in self._component_states.items():
            instance = state['instance']()
            status[name] = {
                'ready': state['ready'],
                'alive': instance is not None,
                'last_update': state['last_update']
            }
        return status


# 全局事件管理器实例
event_manager = EventManager()