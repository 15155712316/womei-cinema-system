#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证服务模块
提供登录验证、机器码绑定、积分管理等功能
"""

import hashlib
import uuid
import platform
import subprocess
import json
import requests
import time
import re
from typing import Dict, Optional, Tuple

class AuthService:
    """用户认证服务类"""
    
    def __init__(self):
        # 云函数API地址（后续替换为实际地址）
        self.api_base_url = "https://your-cloud-function-url"
        self.local_token = None
        self.current_user = None
        
    def get_machine_code(self) -> str:
        """
        获取机器码（基于硬件信息生成唯一标识）
        :return: 机器码字符串
        """
        try:
            # 获取主板序列号
            if platform.system() == "Windows":
                # Windows系统获取主板序列号
                result = subprocess.run(
                    ['wmic', 'baseboard', 'get', 'serialnumber'], 
                    capture_output=True, 
                    text=True
                )
                board_serial = result.stdout.strip().split('\n')[-1].strip()
                
                # 获取CPU序列号
                result = subprocess.run(
                    ['wmic', 'cpu', 'get', 'processorid'], 
                    capture_output=True, 
                    text=True
                )
                cpu_serial = result.stdout.strip().split('\n')[-1].strip()
                
                # 获取硬盘序列号
                result = subprocess.run(
                    ['wmic', 'diskdrive', 'get', 'serialnumber'], 
                    capture_output=True, 
                    text=True
                )
                disk_serial = result.stdout.strip().split('\n')[-1].strip()
                
                # 组合生成机器码
                machine_info = f"{board_serial}-{cpu_serial}-{disk_serial}-{platform.node()}"
                
            else:
                # Linux/Mac系统的实现（备用方案）
                machine_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
            
            # 生成MD5哈希作为机器码
            machine_code = hashlib.md5(machine_info.encode()).hexdigest()
            print(f"[机器码] 生成的机器码: {machine_code}")
            return machine_code
            
        except Exception as e:
            print(f"[机器码] 获取机器码失败: {e}")
            # 备用方案：使用计算机名称生成
            fallback_info = f"{platform.node()}-{platform.system()}"
            return hashlib.md5(fallback_info.encode()).hexdigest()
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        验证手机号格式
        :param phone: 手机号
        :return: 是否有效
        """
        # 中国手机号格式验证 (11位数字，以1开头)
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    def login(self, phone: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        用户登录验证（手机号+机器码）
        :param phone: 手机号
        :return: (是否成功, 消息, 用户信息)
        """
        try:
            # 验证手机号格式
            if not self.validate_phone_number(phone):
                return False, "请输入正确的手机号码", None
            
            # 获取当前机器码
            machine_code = self.get_machine_code()
            
            # 构建登录请求
            login_data = {
                "phone": phone,
                "machine_code": machine_code,
                "timestamp": int(time.time())
            }
            
            print(f"[登录验证] 手机号: {phone}, 机器码: {machine_code}")
            
            # 发送登录请求到云函数
            response = self._call_api("login", login_data)
            
            if response.get("success"):
                user_info = response.get("data", {})
                self.current_user = user_info
                self.local_token = user_info.get("token")
                
                print(f"[登录验证] 登录成功，用户状态: {user_info.get('status')}, 积分: {user_info.get('points')}")
                return True, "登录成功", user_info
            else:
                error_msg = response.get("message", "登录失败")
                print(f"[登录验证] 登录失败: {error_msg}")
                return False, error_msg, None
                
        except Exception as e:
            print(f"[登录验证] 登录异常: {e}")
            return False, f"登录异常: {str(e)}", None
    
    def check_auth(self) -> Tuple[bool, str, Optional[Dict]]:
        """
        检查用户认证状态和权限
        :return: (是否有效, 消息, 用户信息)
        """
        if not self.local_token or not self.current_user:
            return False, "未登录", None
        
        try:
            # 验证token和用户状态
            auth_data = {
                "token": self.local_token,
                "user_id": self.current_user.get("id"),
                "timestamp": int(time.time())
            }
            
            response = self._call_api("check_auth", auth_data)
            
            if response.get("success"):
                user_info = response.get("data", {})
                
                # 检查账号状态
                if user_info.get("status") != 1:
                    return False, "账号已被禁用", None
                
                # 更新本地用户信息
                self.current_user = user_info
                return True, "认证有效", user_info
            else:
                # 认证失败，清除本地信息
                self.logout()
                return False, response.get("message", "认证失败"), None
                
        except Exception as e:
            print(f"[权限验证] 验证异常: {e}")
            return False, f"验证异常: {str(e)}", None
    
    def use_points(self, operation: str, points: int) -> Tuple[bool, str]:
        """
        使用积分（扣除积分）
        :param operation: 操作描述
        :param points: 要扣除的积分数
        :return: (是否成功, 消息)
        """
        if not self.local_token or not self.current_user:
            return False, "未登录"
        
        try:
            points_data = {
                "token": self.local_token,
                "user_id": self.current_user.get("id"),
                "operation": operation,
                "points": points,
                "timestamp": int(time.time())
            }
            
            response = self._call_api("use_points", points_data)
            
            if response.get("success"):
                # 更新本地积分信息
                new_points = response.get("data", {}).get("remaining_points", 0)
                self.current_user["points"] = new_points
                
                print(f"[积分扣除] 操作: {operation}, 扣除: {points}, 剩余: {new_points}")
                return True, f"扣除成功，剩余积分: {new_points}"
            else:
                error_msg = response.get("message", "积分扣除失败")
                return False, error_msg
                
        except Exception as e:
            print(f"[积分扣除] 扣除异常: {e}")
            return False, f"积分扣除异常: {str(e)}"
    
    def get_user_info(self) -> Optional[Dict]:
        """
        获取当前用户信息
        :return: 用户信息字典或None
        """
        return self.current_user
    
    def logout(self):
        """用户登出"""
        self.local_token = None
        self.current_user = None
        print("[用户认证] 已登出")
    
    def _call_api(self, endpoint: str, data: Dict) -> Dict:
        """
        调用云函数API
        :param endpoint: API端点
        :param data: 请求数据
        :return: 响应数据
        """
        # 临时方案：使用本地模拟数据
        # 正式版本会调用真实的云函数API
        return self._mock_api_response(endpoint, data)
    
    def _mock_api_response(self, endpoint: str, data: Dict) -> Dict:
        """
        模拟API响应（开发阶段使用）
        正式版本会替换为真实的云函数调用
        """
        print(f"[模拟API] 调用端点: {endpoint}, 数据: {data}")
        
        if endpoint == "login":
            phone = data.get("phone")
            machine_code = data.get("machine_code")
            
            # 模拟用户数据（正式版本从数据库读取）
            mock_users = {
                "13800138000": {
                    "id": "user_001",
                    "phone": "13800138000", 
                    "username": "管理员",
                    "machine_code": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 100
                },
                "13900139000": {
                    "id": "user_002", 
                    "phone": "13900139000",
                    "username": "测试用户",
                    "machine_code": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 50
                },
                "13700137000": {
                    "id": "user_003", 
                    "phone": "13700137000",
                    "username": "普通用户",
                    "machine_code": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 30
                }
            }
            
            user = mock_users.get(phone)
            if not user:
                return {"success": False, "message": "手机号未注册，请联系管理员"}
            
            if user["machine_code"] != machine_code:
                return {"success": False, "message": "此手机号已绑定其他设备，请联系管理员"}
            
            if user["status"] != 1:
                return {"success": False, "message": "账号已被禁用，请联系管理员"}
            
            # 生成token
            token = hashlib.md5(f"{phone}{machine_code}{time.time()}".encode()).hexdigest()
            
            return {
                "success": True,
                "message": "登录成功",
                "data": {
                    "id": user["id"],
                    "phone": user["phone"],
                    "username": user["username"],
                    "status": user["status"],
                    "points": user["points"],
                    "token": token
                }
            }
        
        elif endpoint == "check_auth":
            # 模拟权限检查
            token = data.get("token")
            if token:
                # 简单验证（正式版本需要验证token有效性）
                return {
                    "success": True,
                    "message": "认证有效",
                    "data": {
                        "id": "user_001",
                        "phone": "13800138000",
                        "username": "管理员",
                        "status": 1,
                        "points": 95  # 模拟积分变化
                    }
                }
            else:
                return {"success": False, "message": "Token无效"}
        
        elif endpoint == "use_points":
            points = data.get("points", 0)
            operation = data.get("operation", "")
            
            # 模拟积分扣除
            current_points = 95  # 从当前用户信息获取
            if current_points >= points:
                new_points = current_points - points
                return {
                    "success": True,
                    "message": "积分扣除成功",
                    "data": {
                        "remaining_points": new_points,
                        "operation": operation
                    }
                }
            else:
                return {"success": False, "message": "积分不足"}
        
        return {"success": False, "message": "未知API端点"}

# 全局认证服务实例
auth_service = AuthService() 