#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
插件接口系统
定义基础的插件接口和通信协议
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QObject, pyqtSignal


class IPluginInterface:
    """插件接口基类"""
    
    def get_name(self) -> str:
        """返回插件名称"""
        raise NotImplementedError("子类必须实现get_name方法")
    
    def get_version(self) -> str:
        """返回插件版本"""
        raise NotImplementedError("子类必须实现get_version方法")
    
    def load(self, parent: QWidget) -> QWidget:
        """加载插件并返回主界面组件"""
        raise NotImplementedError("子类必须实现load方法")
    
    def unload(self) -> bool:
        """卸载插件"""
        raise NotImplementedError("子类必须实现unload方法")
    
    def get_config(self) -> Dict[str, Any]:
        """获取插件配置"""
        raise NotImplementedError("子类必须实现get_config方法")
    
    def set_config(self, config: Dict[str, Any]) -> bool:
        """设置插件配置"""
        raise NotImplementedError("子类必须实现set_config方法")


class IWidgetInterface:
    """UI组件接口基类"""
    
    def initialize(self) -> None:
        """初始化组件"""
        raise NotImplementedError("子类必须实现initialize方法")
    
    def cleanup(self) -> None:
        """清理组件资源"""
        raise NotImplementedError("子类必须实现cleanup方法")
    
    def get_widget(self) -> QWidget:
        """获取Qt组件"""
        raise NotImplementedError("子类必须实现get_widget方法")


class IServiceInterface:
    """业务服务接口基类"""
    
    def start_service(self) -> bool:
        """启动服务"""
        raise NotImplementedError("子类必须实现start_service方法")
    
    def stop_service(self) -> bool:
        """停止服务"""
        raise NotImplementedError("子类必须实现stop_service方法")
    
    def is_running(self) -> bool:
        """检查服务是否运行中"""
        raise NotImplementedError("子类必须实现is_running方法")


class EventBus(QObject):
    """事件总线 - 实现跨模块通信"""
    
    # 定义全局事件信号
    user_login_success = pyqtSignal(dict)  # 用户登录成功
    user_logout = pyqtSignal()  # 用户登出
    account_changed = pyqtSignal(dict)  # 账号切换
    cinema_selected = pyqtSignal(dict)  # 🆕 影院选择 - 修改为dict类型支持完整影院数据
    order_created = pyqtSignal(dict)  # 订单创建
    order_paid = pyqtSignal(str)  # 订单支付
    coupon_bound = pyqtSignal(dict)  # 券绑定
    data_updated = pyqtSignal(str, dict)  # 数据更新 (数据类型, 数据)
    
    def __init__(self):
        super().__init__()
        self._subscribers = {}
    
    def subscribe(self, event_name: str, callback):
        """订阅事件"""
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)
    
    def unsubscribe(self, event_name: str, callback):
        """取消订阅事件"""
        if event_name in self._subscribers:
            self._subscribers[event_name].remove(callback)
    
    def emit_event(self, event_name: str, data: Any = None):
        """发布事件"""
        if event_name in self._subscribers:
            for callback in self._subscribers[event_name]:
                try:
                    if data is not None:
                        callback(data)
                    else:
                        callback()
                except Exception as e:
                    print(f"[EventBus] 事件处理错误: {event_name}, {e}")


# 全局事件总线实例
event_bus = EventBus()


class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self._plugins = {}
        self._active_plugins = {}
    
    def register_plugin(self, plugin_id: str, plugin: IPluginInterface):
        """注册插件"""
        self._plugins[plugin_id] = plugin
        print(f"[PluginManager] 注册插件: {plugin_id} - {plugin.get_name()}")
    
    def load_plugin(self, plugin_id: str, parent: QWidget) -> Optional[QWidget]:
        """加载插件"""
        if plugin_id in self._plugins:
            try:
                widget = self._plugins[plugin_id].load(parent)
                self._active_plugins[plugin_id] = widget
                print(f"[PluginManager] 加载插件成功: {plugin_id}")
                return widget
            except Exception as e:
                print(f"[PluginManager] 加载插件失败: {plugin_id}, {e}")
        return None
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """卸载插件"""
        if plugin_id in self._active_plugins:
            try:
                success = self._plugins[plugin_id].unload()
                if success:
                    del self._active_plugins[plugin_id]
                    print(f"[PluginManager] 卸载插件成功: {plugin_id}")
                return success
            except Exception as e:
                print(f"[PluginManager] 卸载插件失败: {plugin_id}, {e}")
        return False
    
    def get_active_plugins(self) -> Dict[str, QWidget]:
        """获取所有激活的插件"""
        return self._active_plugins.copy()


# 全局插件管理器实例
plugin_manager = PluginManager() 