#!/usr/bin/env python3
"""
UI工具类 - 提供统一的消息管理和UI辅助功能
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Any

class MessageManager:
    """统一消息管理器 - 处理各种弹窗和提示"""
    
    @staticmethod
    def show_info(parent: Optional[tk.Widget], title: str, message: str) -> None:
        """显示信息提示"""
        try:
            if parent:
                # 将消息框居中到父窗口
                parent.update_idletasks()
                x = parent.winfo_x() + parent.winfo_width() // 2 - 150
                y = parent.winfo_y() + parent.winfo_height() // 2 - 50
                root = parent.winfo_toplevel()
                root.geometry(f"+{x}+{y}")
            
            messagebox.showinfo(title, message)
        except Exception as e:
            print(f"[MessageManager] 显示信息弹窗失败: {e}")
            print(f"[MessageManager] 消息内容: {title} - {message}")
    
    @staticmethod
    def show_warning(parent: Optional[tk.Widget], title: str, message: str) -> None:
        """显示警告提示"""
        try:
            if parent:
                parent.update_idletasks()
                x = parent.winfo_x() + parent.winfo_width() // 2 - 150
                y = parent.winfo_y() + parent.winfo_height() // 2 - 50
                root = parent.winfo_toplevel()
                root.geometry(f"+{x}+{y}")
            
            messagebox.showwarning(title, message)
        except Exception as e:
            print(f"[MessageManager] 显示警告弹窗失败: {e}")
            print(f"[MessageManager] 警告内容: {title} - {message}")
    
    @staticmethod
    def show_error(parent: Optional[tk.Widget], title: str, message: str) -> None:
        """显示错误提示"""
        try:
            if parent:
                parent.update_idletasks()
                x = parent.winfo_x() + parent.winfo_width() // 2 - 150
                y = parent.winfo_y() + parent.winfo_height() // 2 - 50
                root = parent.winfo_toplevel()
                root.geometry(f"+{x}+{y}")
            
            messagebox.showerror(title, message)
        except Exception as e:
            print(f"[MessageManager] 显示错误弹窗失败: {e}")
            print(f"[MessageManager] 错误内容: {title} - {message}")
    
    @staticmethod
    def ask_yes_no(parent: Optional[tk.Widget], title: str, message: str) -> bool:
        """显示确认对话框"""
        try:
            if parent:
                parent.update_idletasks()
                x = parent.winfo_x() + parent.winfo_width() // 2 - 150
                y = parent.winfo_y() + parent.winfo_height() // 2 - 50
                root = parent.winfo_toplevel()
                root.geometry(f"+{x}+{y}")
            
            return messagebox.askyesno(title, message)
        except Exception as e:
            print(f"[MessageManager] 显示确认对话框失败: {e}")
            print(f"[MessageManager] 确认内容: {title} - {message}")
            return False

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