#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
错误处理工具 - 统一错误处理逻辑
自动生成，用于减少错误处理的重复代码
"""

import functools
import traceback
from typing import Callable, Any, Optional
from PyQt5.QtWidgets import QMessageBox

class ErrorHandler:
    """错误处理工具类"""
    
    @staticmethod
    def show_error_message(title: str, message: str, parent=None):
        """显示错误消息"""
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def show_warning_message(title: str, message: str, parent=None):
        """显示警告消息"""
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_info_message(title: str, message: str, parent=None):
        """显示信息消息"""
        QMessageBox.information(parent, title, message)

def handle_exceptions(
    show_message: bool = True,
    message_title: str = "错误",
    default_return: Any = None,
    log_error: bool = True
):
    """异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    print(f"函数 {func.__name__} 发生异常: {e}")
                    print(f"异常详情: {traceback.format_exc()}")
                
                if show_message:
                    error_msg = f"操作失败: {str(e)}"
                    ErrorHandler.show_error_message(message_title, error_msg)
                
                return default_return
        return wrapper
    return decorator

def handle_api_errors(
    show_message: bool = True,
    default_return: Any = None
):
    """API错误处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ConnectionError as e:
                if show_message:
                    ErrorHandler.show_error_message("网络错误", f"网络连接失败: {e}")
                return default_return
            except TimeoutError as e:
                if show_message:
                    ErrorHandler.show_error_message("超时错误", f"请求超时: {e}")
                return default_return
            except Exception as e:
                if show_message:
                    ErrorHandler.show_error_message("API错误", f"API调用失败: {e}")
                return default_return
        return wrapper
    return decorator

def validate_data(required_fields: list = None):
    """数据验证装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 假设第一个参数是self，第二个是data
            if len(args) >= 2 and isinstance(args[1], dict):
                data = args[1]
                if required_fields:
                    missing_fields = [field for field in required_fields 
                                    if field not in data or data[field] is None]
                    if missing_fields:
                        error_msg = f"缺少必需字段: {', '.join(missing_fields)}"
                        ErrorHandler.show_warning_message("数据验证失败", error_msg)
                        return None
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
