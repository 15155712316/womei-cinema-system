#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单状态观察者模式 - 状态变化通知机制
自动生成，用于第三阶段C设计模式应用
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum

class OrderStatus(Enum):
    """订单状态枚举"""
    CREATED = "created"
    PAID = "paid"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class OrderObserver(ABC):
    """订单观察者抽象基类"""

    @abstractmethod
    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus, order_data: Dict[str, Any]):
        """订单状态更新通知"""
        pass

class UIUpdateObserver(OrderObserver):
    """UI更新观察者"""

    def __init__(self, main_window):
        self.main_window = main_window

    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus, order_data: Dict[str, Any]):
        """更新UI显示"""
        print(f"UI更新: 订单{order_id}状态从{old_status.value}变为{new_status.value}")

        # 更新订单状态显示
        if hasattr(self.main_window, 'update_order_status_ui'):
            self.main_window.update_order_status_ui(order_id, new_status, order_data)

        # 根据状态更新按钮状态
        if new_status == OrderStatus.PAID:
            if hasattr(self.main_window, 'enable_ticket_generation'):
                self.main_window.enable_ticket_generation(order_id)
        elif new_status == OrderStatus.CANCELLED:
            if hasattr(self.main_window, 'disable_order_actions'):
                self.main_window.disable_order_actions(order_id)

class NotificationObserver(OrderObserver):
    """通知观察者"""

    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus, order_data: Dict[str, Any]):
        """发送通知"""
        print(f"通知: 订单{order_id}状态更新为{new_status.value}")

        # 根据状态发送不同通知
        if new_status == OrderStatus.PAID:
            self._send_payment_success_notification(order_id, order_data)
        elif new_status == OrderStatus.CONFIRMED:
            self._send_order_confirmed_notification(order_id, order_data)
        elif new_status == OrderStatus.CANCELLED:
            self._send_order_cancelled_notification(order_id, order_data)

    def _send_payment_success_notification(self, order_id: str, order_data: Dict[str, Any]):
        """发送支付成功通知"""
        print(f"发送支付成功通知: 订单{order_id}")

    def _send_order_confirmed_notification(self, order_id: str, order_data: Dict[str, Any]):
        """发送订单确认通知"""
        print(f"发送订单确认通知: 订单{order_id}")

    def _send_order_cancelled_notification(self, order_id: str, order_data: Dict[str, Any]):
        """发送订单取消通知"""
        print(f"发送订单取消通知: 订单{order_id}")

class LoggingObserver(OrderObserver):
    """日志记录观察者"""

    def update(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus, order_data: Dict[str, Any]):
        """记录状态变化日志"""
        log_message = f"订单状态变化: {order_id} {old_status.value} -> {new_status.value}"
        print(f"日志: {log_message}")

        # 这里可以写入日志文件或发送到日志服务
        self._write_to_log(log_message, order_data)

    def _write_to_log(self, message: str, order_data: Dict[str, Any]):
        """写入日志"""
        # 实际实现中可以写入文件或数据库
        pass

class OrderSubject:
    """订单主题类（被观察者）"""

    def __init__(self):
        self._observers: List[OrderObserver] = []
        self._orders: Dict[str, Dict[str, Any]] = {}

    def add_observer(self, observer: OrderObserver):
        """添加观察者"""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: OrderObserver):
        """移除观察者"""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, order_id: str, old_status: OrderStatus, new_status: OrderStatus):
        """通知所有观察者"""
        order_data = self._orders.get(order_id, {})
        for observer in self._observers:
            observer.update(order_id, old_status, new_status, order_data)

    def update_order_status(self, order_id: str, new_status: OrderStatus, order_data: Dict[str, Any] = None):
        """更新订单状态"""
        # 获取旧状态
        old_order = self._orders.get(order_id, {})
        old_status = OrderStatus(old_order.get('status', OrderStatus.CREATED.value))

        # 更新订单数据
        if order_data:
            self._orders[order_id] = order_data
        else:
            self._orders.setdefault(order_id, {})

        self._orders[order_id]['status'] = new_status.value

        # 通知观察者
        self.notify_observers(order_id, old_status, new_status)

    def get_order_status(self, order_id: str) -> OrderStatus:
        """获取订单状态"""
        order = self._orders.get(order_id, {})
        status_value = order.get('status', OrderStatus.CREATED.value)
        return OrderStatus(status_value)

    def get_order_data(self, order_id: str) -> Dict[str, Any]:
        """获取订单数据"""
        return self._orders.get(order_id, {})

# 全局订单主题实例
order_subject = OrderSubject()

def get_order_subject() -> OrderSubject:
    """获取订单主题实例"""
    return order_subject

def setup_order_observers(main_window):
    """设置订单观察者"""
    subject = get_order_subject()

    # 添加UI更新观察者
    ui_observer = UIUpdateObserver(main_window)
    subject.add_observer(ui_observer)

    # 添加通知观察者
    notification_observer = NotificationObserver()
    subject.add_observer(notification_observer)

    # 添加日志观察者
    logging_observer = LoggingObserver()
    subject.add_observer(logging_observer)

    return subject
