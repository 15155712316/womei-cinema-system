#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一的认证错误处理服务
用于登录和定时验证的错误信息解析和处理
"""

from typing import Tuple, Optional, Dict
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import QTimer, Qt


class AuthErrorHandler:
    """统一的认证错误处理器"""
    
    @staticmethod
    def parse_error_message(error_msg: str) -> str:
        """
        解析API错误信息，返回用户友好的提示
        统一登录和验证的错误信息处理逻辑
        """
        try:
            # 转换为小写便于匹配
            error_lower = error_msg.lower()
            
            # 🔧 根据具体错误码和错误信息进行匹配
            
            # === HTTP状态码错误 ===
            if "403" in error_msg or "forbidden" in error_lower:
                # 进一步解析403错误的具体原因
                if "banned" in error_lower or "封禁" in error_msg or "disabled" in error_lower:
                    return "账号已被封禁，请联系管理员"
                elif "machine" in error_lower or "device" in error_lower or "机器码" in error_msg:
                    return "设备验证失败，请重新绑定设备"
                else:
                    return "访问权限不足，请联系管理员"
            
            elif "404" in error_msg or "not found" in error_lower:
                return "账号不存在，请检查手机号是否正确"
            
            elif "401" in error_msg or "unauthorized" in error_lower:
                return "认证信息已过期，请重新登录"
            
            elif "500" in error_msg or "internal server error" in error_lower:
                return "服务器内部错误，请稍后重试"
            
            # === 网络连接错误 ===
            elif "timeout" in error_lower or "超时" in error_msg:
                return "网络连接超时，请检查网络后重试"
            
            elif "connection" in error_lower or "连接" in error_msg:
                return "无法连接到服务器，请检查网络连接"
            
            # === 业务逻辑错误 ===
            elif "not registered" in error_lower or "未注册" in error_msg:
                return "该手机号未注册\n\n请联系管理员添加账号"
            
            elif "device not authorized" in error_lower or "设备未授权" in error_msg:
                return "设备未授权，机器码不匹配\n\n请联系管理员重新绑定设备"
            
            elif "account disabled" in error_lower or "账号已被禁用" in error_msg:
                return "账号已被禁用\n\n请联系管理员启用账号"
            
            elif "failed to bind device" in error_lower or "设备绑定失败" in error_msg:
                return "设备绑定失败\n\n请稍后重试或联系管理员"
            
            # === 输入验证错误 ===
            elif "invalid" in error_lower and ("phone" in error_lower or "手机" in error_msg):
                return "手机号格式不正确，请检查后重试"
            
            elif "invalid" in error_lower and ("machine" in error_lower or "机器码" in error_msg):
                return "设备验证失败，请重新绑定设备"
            
            # === 中文错误信息 ===
            elif "机器码" in error_msg and ("验证" in error_msg or "失败" in error_msg):
                return "设备验证失败，请重新绑定设备"
            
            elif "用户不存在" in error_msg or "账号不存在" in error_msg:
                return "账号不存在，请检查手机号是否正确"
            
            elif "密码错误" in error_msg or "密码不正确" in error_msg:
                return "密码错误，请检查后重试"
            
            elif "账号被禁用" in error_msg or "账号已封禁" in error_msg:
                return "账号已被封禁，请联系管理员"
            
            # === 数据库和服务器错误 ===
            elif "database query error" in error_lower or "数据库" in error_msg:
                return "数据库查询错误\n\n请稍后重试或联系技术支持"
            
            # === 默认处理 ===
            # 检查是否包含具体的服务器返回错误信息
            elif "message" in error_lower or "错误" in error_msg:
                # 如果错误信息本身就比较友好，直接使用
                if len(error_msg) < 100 and not any(x in error_lower for x in ["error", "exception", "failed"]):
                    return error_msg
            
            # 默认情况：显示原始错误信息，但添加友好的前缀
            return f"认证验证失败: {error_msg}\n\n如问题持续存在，请联系管理员"
            
        except Exception as e:
            print(f"[错误解析] 解析错误信息失败: {e}")
            return f"认证失败: {error_msg}"
    
    @staticmethod
    def show_login_error(parent: QWidget, error_msg: str):
        """
        显示登录错误信息
        用于登录窗口的错误提示
        """
        try:
            from services.ui_utils import MessageManager
            
            # 解析错误信息
            user_friendly_message = AuthErrorHandler.parse_error_message(error_msg)
            
            # 显示错误对话框
            MessageManager.show_error(parent, "登录失败", user_friendly_message)
            
        except Exception as e:
            print(f"[错误处理] 显示登录错误失败: {e}")
            # 备用方案
            QMessageBox.critical(parent, "登录失败", f"登录失败: {error_msg}")
    
    @staticmethod
    def show_auth_failed_dialog(parent: QWidget, error_msg: str, on_confirmed_callback=None):
        """
        显示认证失败对话框
        用于定时验证失败时的错误提示，支持回调处理
        优化：将详细错误信息直接显示在主要文本区域
        """
        try:
            # 解析错误信息
            user_friendly_message = AuthErrorHandler.parse_error_message(error_msg)

            # 🆕 创建自定义消息框，确保正确处理用户响应
            msg_box = QMessageBox(parent)
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setWindowTitle("认证失败")

            # 🔧 优化：将详细错误信息直接显示在主要文本区域，无需点击"详细信息"
            main_text = f"用户认证失败，需要重新登录\n\n"
            main_text += f"失败原因：\n{user_friendly_message}\n\n"
            main_text += f"点击确认后将自动跳转到登录页面"

            msg_box.setText(main_text)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setDefaultButton(QMessageBox.Ok)

            # 🆕 设置窗口属性，确保显示在最前面
            msg_box.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)

            # 🔧 调整对话框大小，确保能完整显示错误信息
            msg_box.setStyleSheet("""
                QMessageBox {
                    min-width: 400px;
                    min-height: 200px;
                }
                QMessageBox QLabel {
                    min-width: 350px;
                    font-size: 12px;
                    line-height: 1.4;
                }
            """)

            print(f"[错误处理] 显示认证失败对话框，错误信息: {user_friendly_message}")

            # 显示对话框并获取结果
            result = msg_box.exec_()

            # 🔧 修复：只有在用户点击确认后才执行回调
            if result == QMessageBox.Ok and on_confirmed_callback:
                print(f"[错误处理] 用户确认认证失败对话框，执行回调")
                on_confirmed_callback()

        except Exception as e:
            print(f"[错误处理] 显示认证失败对话框失败: {e}")
            # 备用方案
            user_friendly_message = AuthErrorHandler.parse_error_message(error_msg)
            QMessageBox.warning(
                parent,
                "认证失败",
                f"用户认证失败，需要重新登录\n\n失败原因：\n{user_friendly_message}\n\n点击确认后将自动跳转到登录页面"
            )
            if on_confirmed_callback:
                on_confirmed_callback()
    
    @staticmethod
    def handle_auth_success(user_info: Dict, is_silent: bool = True):
        """
        处理认证成功
        :param user_info: 用户信息
        :param is_silent: 是否静默处理（不显示提示）
        """
        try:
            phone = user_info.get('phone', 'N/A')
            points = user_info.get('points', 0)
            
            print(f"[认证成功] 用户: {phone}, 积分: {points}")
            
            # 定时验证成功时静默处理，不显示任何提示
            if is_silent:
                return
            
            # 登录成功时可以显示提示（由调用方决定）
            # 这里不做任何UI操作，由具体的窗口类处理
            
        except Exception as e:
            print(f"[认证成功] 处理认证成功失败: {e}")


class AuthResult:
    """认证结果封装类"""
    
    def __init__(self, success: bool, message: str, user_info: Optional[Dict] = None):
        self.success = success
        self.message = message
        self.user_info = user_info
        self.parsed_message = AuthErrorHandler.parse_error_message(message) if not success else message
    
    def is_success(self) -> bool:
        """是否成功"""
        return self.success
    
    def get_user_friendly_message(self) -> str:
        """获取用户友好的错误信息"""
        return self.parsed_message if not self.success else self.message
    
    def get_user_info(self) -> Optional[Dict]:
        """获取用户信息"""
        return self.user_info
    
    def __str__(self):
        status = "成功" if self.success else "失败"
        return f"AuthResult({status}: {self.get_user_friendly_message()})"


# 全局错误处理器实例
auth_error_handler = AuthErrorHandler()
