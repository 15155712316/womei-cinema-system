#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI工具类 - 提供统一的消息管理和UI辅助功能
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Any
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

class MessageManager:
    """消息管理器 - 支持自动关闭和居中显示"""
    
    @staticmethod
    def _create_message_box(parent, title, message, icon_type):
        """创建居中的消息框"""
        msg_box = QMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_type)
        
        # 设置字体
        font = QFont("Microsoft YaHei", 10)
        msg_box.setFont(font)
        
        # 设置窗口标志，确保居中显示
        msg_box.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        
        # 居中显示
        if parent:
            # 相对于父窗口居中
            parent_rect = parent.geometry()
            msg_box.move(
                parent_rect.x() + (parent_rect.width() - 400) // 2,
                parent_rect.y() + (parent_rect.height() - 200) // 2
            )
        else:
            # 屏幕居中
            from PyQt5.QtWidgets import QDesktopWidget
            screen = QDesktopWidget().screenGeometry()
            msg_box.move(
                (screen.width() - 400) // 2,
                (screen.height() - 200) // 2
            )
        
        return msg_box
    
    @staticmethod
    def show_success(parent, title, message, auto_close=True):
        """显示成功消息 - 默认1秒后自动关闭"""
        msg_box = MessageManager._create_message_box(parent, title, message, QMessageBox.Information)
        
        if auto_close:
            # 1秒后自动关闭
            timer = QTimer()
            timer.timeout.connect(msg_box.accept)
            timer.start(1000)  # 1秒
            msg_box.exec_()
            timer.stop()
        else:
            msg_box.exec_()
    
    @staticmethod
    def show_error(parent, title, message, auto_close=False):
        """显示错误消息 - 默认需要手动确认"""
        msg_box = MessageManager._create_message_box(parent, title, message, QMessageBox.Critical)
        
        if auto_close:
            # 1秒后自动关闭
            timer = QTimer()
            timer.timeout.connect(msg_box.accept)
            timer.start(1000)  # 1秒
            msg_box.exec_()
            timer.stop()
        else:
            msg_box.exec_()
    
    @staticmethod
    def show_warning(parent, title, message, auto_close=False):
        """显示警告消息 - 默认需要手动确认"""
        msg_box = MessageManager._create_message_box(parent, title, message, QMessageBox.Warning)
        
        if auto_close:
            # 1秒后自动关闭
            timer = QTimer()
            timer.timeout.connect(msg_box.accept)
            timer.start(1000)  # 1秒
            msg_box.exec_()
            timer.stop()
        else:
            msg_box.exec_()
    
    @staticmethod
    def show_info(parent, title, message, auto_close=True):
        """显示信息消息 - 默认1秒后自动关闭"""
        msg_box = MessageManager._create_message_box(parent, title, message, QMessageBox.Information)
        
        if auto_close:
            # 1秒后自动关闭
            timer = QTimer()
            timer.timeout.connect(msg_box.accept)
            timer.start(1000)  # 1秒
            msg_box.exec_()
            timer.stop()
        else:
            msg_box.exec_()

class CouponManager:
    """优惠券状态管理器"""
    
    @staticmethod
    def should_show_coupons(ui_state: str) -> bool:
        """
        判断是否应该显示优惠券列表
        
        Args:
            ui_state: UI状态 ('initial', 'ordering', 'order_submitted', 'payment_success')
        
        Returns:
            bool: 是否应该显示优惠券
        """
        # 只在订单提交后和支付成功后显示优惠券
        return ui_state in ['order_submitted', 'payment_success']
    
    @staticmethod
    def clear_coupons_if_needed(ui_state: str, clear_callback) -> None:
        """
        根据UI状态决定是否清空优惠券列表
        
        Args:
            ui_state: 当前UI状态
            clear_callback: 清空优惠券的回调函数
        """
        if not CouponManager.should_show_coupons(ui_state):
            clear_callback()

class UIConstants:
    """UI常量和配置"""
    
    # 成功弹窗显示配置
    SUCCESS_POPUP_EVENTS = {
        'login_success': True,      # 登录成功显示弹窗
        'order_success': False,     # 下单成功不显示弹窗
        'payment_success': False,   # 支付成功不显示弹窗
        'coupon_bind_success': False,  # 绑券成功不显示弹窗
    }
    
    # UI状态定义
    UI_STATES = {
        'INITIAL': 'initial',
        'ORDERING': 'ordering', 
        'ORDER_SUBMITTED': 'order_submitted',
        'PAYMENT_SUCCESS': 'payment_success'
    }
    
    # 颜色配置
    COLORS = {
        'PRIMARY': '#2196F3',       # 主色调
        'SUCCESS': '#4CAF50',       # 成功色
        'WARNING': '#FF9800',       # 警告色
        'ERROR': '#F44336',         # 错误色
        'INFO': '#2196F3',          # 信息色
        'BACKGROUND': '#FFFFFF',    # 背景色
        'TEXT': '#333333',          # 文字色
        'BORDER': '#E0E0E0',        # 边框色
    }
    
    @staticmethod
    def should_show_success_popup(event_name: str) -> bool:
        """
        判断指定事件是否应该显示成功弹窗
        
        Args:
            event_name: 事件名称
            
        Returns:
            bool: 是否显示弹窗
        """
        return UIConstants.SUCCESS_POPUP_EVENTS.get(event_name, False)

class UIHelper:
    """UI辅助工具"""
    
    @staticmethod
    def center_window(window: tk.Toplevel, width: int = 400, height: int = 300) -> None:
        """
        将窗口居中显示
        
        Args:
            window: 要居中的窗口
            width: 窗口宽度
            height: 窗口高度
        """
        try:
            window.update_idletasks()
            
            # 获取屏幕尺寸
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            
            # 计算居中位置
            x = (screen_width - width) // 2
            y = (screen_height - height) // 2
            
            # 设置窗口位置和大小
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            print(f"[UIHelper] 窗口居中失败: {e}")
    
    @staticmethod
    def create_label_frame(parent: tk.Widget, text: str, **kwargs) -> tk.LabelFrame:
        """
        创建标准样式的LabelFrame
        
        Args:
            parent: 父组件
            text: 标题文本
            **kwargs: 其他参数
            
        Returns:
            tk.LabelFrame: 创建的LabelFrame
        """
        default_style = {
            'font': ('微软雅黑', 10),
            'foreground': UIConstants.COLORS['TEXT'],
            'relief': 'groove',
            'borderwidth': 1
        }
        default_style.update(kwargs)
        
        return tk.LabelFrame(parent, text=text, **default_style)
    
    @staticmethod
    def create_button(parent: tk.Widget, text: str, command=None, style='primary', **kwargs) -> tk.Button:
        """
        创建标准样式的按钮
        
        Args:
            parent: 父组件
            text: 按钮文本
            command: 点击回调
            style: 样式类型 ('primary', 'success', 'warning', 'error')
            **kwargs: 其他参数
            
        Returns:
            tk.Button: 创建的按钮
        """
        style_config = {
            'primary': {'bg': UIConstants.COLORS['PRIMARY'], 'fg': 'white'},
            'success': {'bg': UIConstants.COLORS['SUCCESS'], 'fg': 'white'},
            'warning': {'bg': UIConstants.COLORS['WARNING'], 'fg': 'white'},
            'error': {'bg': UIConstants.COLORS['ERROR'], 'fg': 'white'},
        }
        
        default_style = {
            'font': ('微软雅黑', 10),
            'relief': 'flat',
            'borderwidth': 0,
            'cursor': 'hand2',
            'activebackground': UIConstants.COLORS['PRIMARY'],
            'activeforeground': 'white'
        }
        
        if style in style_config:
            default_style.update(style_config[style])
        
        default_style.update(kwargs)
        
        return tk.Button(parent, text=text, command=command, **default_style)

def safe_call(func, *args, **kwargs):
    """
    安全调用函数，捕获异常并记录
    
    Args:
        func: 要调用的函数
        *args: 位置参数
        **kwargs: 关键字参数
        
    Returns:
        任何: 函数返回值，异常时返回None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        print(f"[SafeCall] 调用 {func.__name__} 失败: {e}")
        return None

# 模块级便捷函数
def show_info(parent, title, message):
    """便捷的信息提示函数"""
    MessageManager.show_info(parent, title, message)

def show_warning(parent, title, message):
    """便捷的警告提示函数"""
    MessageManager.show_warning(parent, title, message)

def show_error(parent, title, message):
    """便捷的错误提示函数"""
    MessageManager.show_error(parent, title, message)

def ask_yes_no(parent, title, message):
    """便捷的确认对话框函数"""
    return MessageManager.ask_yes_no(parent, title, message)

if __name__ == "__main__":
    # 测试UI工具类
    print("🧪 测试UI工具类...")
    
    # 测试常量
    print(f"主色调: {UIConstants.COLORS['PRIMARY']}")
    print(f"是否显示登录成功弹窗: {UIConstants.should_show_success_popup('login_success')}")
    print(f"是否显示下单成功弹窗: {UIConstants.should_show_success_popup('order_success')}")
    
    # 测试优惠券管理
    print(f"initial状态是否显示优惠券: {CouponManager.should_show_coupons('initial')}")
    print(f"order_submitted状态是否显示优惠券: {CouponManager.should_show_coupons('order_submitted')}")
    
    print("✅ UI工具类测试完成") 