#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户刷新时间定时验证服务
实现定时检查用户登录状态，记录刷新时间，失败时跳转登录页面
版本: 1.0
"""

import time
import requests
import sys
import os
from typing import Optional, Dict, Tuple
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtWidgets import QMessageBox, QApplication

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from services.auth_service import auth_service
    from services.auth_error_handler import auth_error_handler, AuthResult
except ImportError:
    # 如果导入失败，创建一个简单的占位符
    auth_service = None
    auth_error_handler = None


class RefreshTimerService(QObject):
    """用户刷新时间定时验证服务"""
    
    # 信号定义
    auth_failed = pyqtSignal(str)  # 认证失败信号，传递错误信息
    auth_success = pyqtSignal(dict)  # 认证成功信号，传递用户信息
    
    def __init__(self):
        super().__init__()

        # 配置参数
        self.check_interval = 10 * 60 * 1000  # 10分钟检查一次（毫秒）
        self.api_base_url = "http://43.142.19.28:5000"  # API服务器地址
        self.request_timeout = 10  # 请求超时时间（秒）

        # 状态变量
        self.current_user = None
        self.is_running = False

        # 创建定时器
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_user_auth)

        print("[刷新验证服务] 🚀 初始化完成")
        print(f"[刷新验证服务] 📋 配置信息:")
        print(f"[刷新验证服务]   - 检查间隔: {self.check_interval // 1000 // 60} 分钟")
        print(f"[刷新验证服务]   - API地址: {self.api_base_url}")
        print(f"[刷新验证服务]   - 超时时间: {self.request_timeout} 秒")
    
    def start_monitoring(self, user_info: Dict):
        """开始监控用户认证状态"""
        try:
            print(f"[刷新验证服务] 🎯 收到启动监控请求")
            print(f"[刷新验证服务] 📋 用户信息: {user_info}")

            self.current_user = user_info
            phone = user_info.get('phone', '')

            if not phone:
                print("[刷新验证服务] ❌ 用户信息不完整，无法启动监控 - 缺少phone字段")
                return False

            print(f"[刷新验证服务] ✅ 开始监控用户: {phone}")
            print(f"[刷新验证服务] ⏰ 检查间隔: {self.check_interval // 1000 // 60} 分钟")
            print(f"[刷新验证服务] 🔄 定时器状态: {'已运行' if self.timer.isActive() else '未运行'}")

            # 启动定时器
            self.timer.start(self.check_interval)
            self.is_running = True

            print(f"[刷新验证服务] 🚀 定时器已启动，状态: {'活跃' if self.timer.isActive() else '非活跃'}")

            # 立即执行一次检查
            print(f"[刷新验证服务] 🔍 立即执行首次验证检查...")
            self._check_user_auth()

            return True

        except Exception as e:
            print(f"[刷新验证服务] ❌ 启动监控失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def stop_monitoring(self):
        """停止监控"""
        try:
            if self.timer.isActive():
                self.timer.stop()
            
            self.is_running = False
            self.current_user = None
            
            print("[刷新验证服务] 已停止监控")
            
        except Exception as e:
            print(f"[刷新验证服务] 停止监控失败: {e}")
    
    def _check_user_auth(self):
        """检查用户认证状态"""
        try:
            if not self.current_user:
                print("[刷新验证服务] 没有当前用户信息，停止检查")
                self.stop_monitoring()
                return
            
            phone = self.current_user.get('phone', '')
            print(f"[刷新验证服务] 开始检查用户认证状态: {phone}")
            
            # 调用刷新时间更新API
            success, message, updated_user_info = self._update_refresh_time(phone)
            
            if success:
                print(f"[刷新验证服务] 认证检查成功: {message}")
                
                # 更新本地用户信息
                if updated_user_info:
                    self.current_user.update(updated_user_info)
                
                # 发出认证成功信号
                self.auth_success.emit(self.current_user)
                
            else:
                print(f"[刷新验证服务] 认证检查失败: {message}")
                
                # 停止监控
                self.stop_monitoring()
                
                # 发出认证失败信号
                self.auth_failed.emit(message)
                
        except Exception as e:
            print(f"[刷新验证服务] 认证检查异常: {e}")
            
            # 发出认证失败信号
            self.auth_failed.emit(f"认证检查异常: {str(e)}")
    
    def _update_refresh_time(self, phone: str) -> Tuple[bool, str, Optional[Dict]]:
        """更新用户刷新时间 - 使用与登录相同的验证逻辑"""
        try:
            print(f"[刷新验证服务] 🔄 开始验证用户: {phone}")

            # 🆕 使用与登录窗口完全相同的验证逻辑
            if auth_service:
                success, message, user_info = auth_service.login(phone)

                if success:
                    print(f"[刷新验证服务] ✅ 验证成功 - 用户: {user_info.get('phone', 'N/A')}, 积分: {user_info.get('points', 0)}")

                    # 🆕 使用统一的认证成功处理（静默模式）
                    if auth_error_handler:
                        auth_error_handler.handle_auth_success(user_info, is_silent=True)

                    return True, "验证成功", user_info
                else:
                    print(f"[刷新验证服务] ❌ 验证失败: {message}")
                    return False, message, None
            else:
                # 备用方案：直接调用API（如果auth_service不可用）
                return self._fallback_api_call(phone)

        except Exception as e:
            error_msg = f"验证异常: {str(e)}"
            print(f"[刷新验证服务] ❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg, None

    def _fallback_api_call(self, phone: str) -> Tuple[bool, str, Optional[Dict]]:
        """备用API调用方案（当auth_service不可用时）"""
        try:
            url = f"{self.api_base_url}/login"

            data = {
                "phone": phone,
                "machineCode": self._get_machine_code(),
                "timestamp": int(time.time())
            }

            print(f"[刷新验证服务] 🔄 备用API调用: {url}")
            print(f"[刷新验证服务] 📋 请求数据: {data}")

            response = requests.post(
                url,
                json=data,
                timeout=self.request_timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'LeYing-Auth-Client/1.0'
                }
            )

            print(f"[刷新验证服务] 📡 API响应状态: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"[刷新验证服务] 📄 API响应内容: {result}")

                if result.get("success"):
                    user_data = result.get("data", {})
                    print(f"[刷新验证服务] ✅ 验证成功 - 用户: {user_data.get('phone', 'N/A')}, 积分: {user_data.get('points', 0)}")
                    return True, "验证成功", user_data
                else:
                    error_msg = result.get("message", "验证失败")
                    print(f"[刷新验证服务] ❌ 验证失败: {error_msg}")
                    return False, error_msg, None
            else:
                try:
                    error_response = response.json()
                    error_msg = error_response.get("message", f"HTTP {response.status_code}")
                except:
                    error_msg = f"HTTP {response.status_code}"

                print(f"[刷新验证服务] ❌ 服务器错误: {error_msg}")
                return False, error_msg, None

        except requests.exceptions.ConnectionError:
            error_msg = "无法连接到服务器，请检查网络连接"
            print(f"[刷新验证服务] ❌ {error_msg}")
            return False, error_msg, None
        except requests.exceptions.Timeout:
            error_msg = "连接超时，请稍后重试"
            print(f"[刷新验证服务] ❌ {error_msg}")
            return False, error_msg, None
        except Exception as e:
            error_msg = f"验证异常: {str(e)}"
            print(f"[刷新验证服务] ❌ {error_msg}")
            return False, error_msg, None

    def _get_machine_code(self) -> str:
        """获取机器码 - 与auth_service保持一致"""
        try:
            # 导入auth_service获取机器码
            if auth_service:
                return auth_service.get_machine_code()
            else:
                # 备用方案：简单的机器码生成
                import platform
                import hashlib
                machine_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
                return hashlib.md5(machine_info.encode('utf-8')).hexdigest()[:16].upper()
        except Exception as e:
            print(f"[刷新验证服务] ⚠️ 获取机器码失败: {e}")
            return "DEFAULT_MACHINE_CODE"
    
    def set_check_interval(self, minutes: int):
        """设置检查间隔（分钟）"""
        try:
            if minutes < 1:
                minutes = 1
            elif minutes > 60:
                minutes = 60
            
            self.check_interval = minutes * 60 * 1000
            
            # 如果定时器正在运行，重新启动以应用新间隔
            if self.is_running and self.timer.isActive():
                self.timer.stop()
                self.timer.start(self.check_interval)
            
            print(f"[刷新验证服务] 检查间隔已设置为: {minutes} 分钟")
            
        except Exception as e:
            print(f"[刷新验证服务] 设置检查间隔失败: {e}")
    
    def get_status(self) -> Dict:
        """获取服务状态"""
        return {
            "is_running": self.is_running,
            "current_user": self.current_user.get('phone', '') if self.current_user else '',
            "check_interval_minutes": self.check_interval // 1000 // 60,
            "timer_active": self.timer.isActive() if hasattr(self, 'timer') else False
        }


# 创建全局实例
refresh_timer_service = RefreshTimerService()


def main():
    """测试刷新验证服务"""
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 模拟用户信息
    test_user = {
        'phone': '13800138000',
        'username': '测试用户',
        'points': 100
    }
    
    def on_auth_success(user_info):
        print(f"认证成功: {user_info}")
    
    def on_auth_failed(error_msg):
        print(f"认证失败: {error_msg}")
        app.quit()
    
    # 连接信号
    refresh_timer_service.auth_success.connect(on_auth_success)
    refresh_timer_service.auth_failed.connect(on_auth_failed)
    
    # 设置较短的检查间隔用于测试（1分钟）
    refresh_timer_service.set_check_interval(1)
    
    # 开始监控
    refresh_timer_service.start_monitoring(test_user)
    
    print("刷新验证服务测试启动...")
    print("按 Ctrl+C 退出")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()



