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
        # 云函数API地址（需要替换为实际地址）
        self.api_base_url = "https://your-cloud-function-url"
        self.local_token = None
        self.current_user = None
        
    def get_machine_code(self) -> str:
        """
        获取机器码（基于硬件信息生成真实机器码）
        :return: 机器码字符串
        """
        try:
            # 获取硬件信息用于生成机器码 - 使用有序字典确保顺序一致
            hardware_info = {}
            
            # 1. 获取计算机名
            try:
                computer_name = platform.node()
                hardware_info["computer"] = computer_name
            except Exception as e:
                pass

            # 2. 获取处理器信息
            try:
                processor = platform.processor()
                hardware_info["processor"] = processor
            except Exception as e:
                pass

            # 3. 获取系统信息（固定格式）
            try:
                system_info = f"{platform.system()}-{platform.machine()}"  # 移除release，因为可能变化
                hardware_info["system"] = system_info
            except Exception as e:
                pass

            # 4. Windows平台特定信息
            if platform.system().lower() == 'windows':
                try:
                    # 获取主板序列号
                    result = subprocess.run(['wmic', 'baseboard', 'get', 'serialnumber'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip() and 'SerialNumber' not in line:
                                board_serial = line.strip()
                                hardware_info["board"] = board_serial
                                break
                except Exception as e:
                    pass

                try:
                    # 获取CPU序列号
                    result = subprocess.run(['wmic', 'cpu', 'get', 'processorid'], 
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip() and 'ProcessorId' not in line:
                                cpu_id = line.strip()
                                hardware_info["cpu"] = cpu_id
                                break
                except Exception as e:
                    pass

                try:
                    # 获取硬盘序列号
                    result = subprocess.run(['wmic', 'diskdrive', 'get', 'serialnumber'],
                                          capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if line.strip() and 'SerialNumber' not in line and line.strip() != '':
                                disk_serial = line.strip()
                                hardware_info["disk"] = disk_serial
                                break
                except Exception as e:
                    pass
            
            # 5. 如果没有获取到足够的硬件信息，使用MAC地址作为补充
            if len(hardware_info) < 2:
                try:
                    mac_address = hex(uuid.getnode())
                    hardware_info["mac"] = mac_address
                except Exception as e:
                    pass

            # 6. 按键名排序并组合所有硬件信息，确保顺序一致
            sorted_keys = sorted(hardware_info.keys())
            combined_parts = []
            for key in sorted_keys:
                combined_parts.append(f"{key}:{hardware_info[key]}")
            
            combined_info = "|".join(combined_parts)
            
            # 7. 生成MD5哈希并取前16位作为机器码
            machine_code = hashlib.md5(combined_info.encode('utf-8')).hexdigest()[:16].upper()
            
            return machine_code
            
        except Exception as e:
            # 如果生成失败，使用系统信息的简单哈希作为备用（不使用时间戳）
            fallback_info = f"{platform.node()}-{platform.system()}-{platform.machine()}"
            fallback_code = hashlib.md5(fallback_info.encode('utf-8')).hexdigest()[:16].upper()
            return fallback_code
    
    def validate_phone(self, phone: str) -> bool:
        """
        验证手机号格式（别名方法）
        :param phone: 手机号
        :return: 是否有效
        """
        return self.validate_phone_number(phone)
    
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
        用户登录验证（仅需手机号+机器码，无需密码）
        :param phone: 手机号
        :return: (是否成功, 消息, 用户信息)
        """
        try:
            # 验证手机号格式
            if not self.validate_phone_number(phone):
                return False, "请输入正确的手机号码", None
            
            # 获取当前机器码
            machine_code = self.get_machine_code()
            
            # 构建登录请求（匹配API服务器参数）
            login_data = {
                "phone": phone,  # API服务器使用phone字段
                "machineCode": machine_code,  # 使用驼峰命名
                "timestamp": int(time.time())
            }
            
            
            # 发送登录请求到API服务器
            response = self._call_api("login", login_data)
            
            if response.get("success"):
                user_info = response.get("data", {})
                
                # 确保用户信息包含username字段（兼容主窗口显示）
                if "username" not in user_info:
                    user_info["username"] = user_info.get("phone", phone)
                
                # 保存登录状态
                self.current_user = user_info
                self.local_token = f"token_{phone}_{int(time.time())}"  # 生成本地token
                
                print(f"[登录验证] 登录成功，用户状态: {user_info.get('status')}, 积分: {user_info.get('points')}")
                return True, "登录成功", user_info
            else:
                error_msg = response.get("message", "登录失败")
                return False, error_msg, None
                
        except Exception as e:
            return False, f"登录异常: {str(e)}", None
    
    def check_auth(self) -> Tuple[bool, str, Optional[Dict]]:
        """
        检查用户认证状态和权限 - 使用真实登录API验证
        :return: (是否有效, 消息, 用户信息)
        """
        # 检查本地登录状态
        if not self.current_user:
            return False, "未登录", None
        
        try:
            # 使用真实的登录API进行认证检查
            phone = self.current_user.get("phone") or self.current_user.get("username")
            if not phone:
                return False, "用户信息不完整", None
            
            # 获取当前机器码
            machine_code = self.get_machine_code()
            
            # 构建登录请求（与登录时相同的参数）
            login_data = {
                "phone": phone,
                "machineCode": machine_code,
                "timestamp": int(time.time())
            }
            
            
            # 调用登录API进行验证
            response = self._call_api("login", login_data)
            
            if response.get("success"):
                # 验证成功，更新用户信息
                user_info = response.get("data", {})
                
                # 确保用户信息包含username字段
                if "username" not in user_info:
                    user_info["username"] = user_info.get("phone", phone)
                
                # 更新本地用户信息
                self.current_user = user_info
                
                print(f"[认证检查] 验证成功，用户状态: {user_info.get('status')}, 积分: {user_info.get('points')}")
                return True, "认证有效", user_info
            else:
                error_msg = response.get("message", "认证失败")
                return False, error_msg, None
                
        except Exception as e:
            return False, f"验证异常: {str(e)}", None
    
    def use_points(self, operation: str, points: int) -> Tuple[bool, str]:
        """
        使用积分（扣除积分）
        :param operation: 操作描述
        :param points: 要扣除的积分数
        :return: (是否成功, 消息)
        """
        if not self.current_user:
            return False, "未登录"
        
        try:
            current_points = self.current_user.get("points", 0)
            
            # 检查积分是否足够
            if current_points < points:
                return False, f"积分不足，当前积分: {current_points}，需要: {points}"
            
            # 扣除积分（本地处理，实际应用中可调用API更新服务器积分）
            new_points = current_points - points
            self.current_user["points"] = new_points
            
            return True, f"扣除成功，剩余积分: {new_points}"
                
        except Exception as e:
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
    
    def _call_api(self, endpoint: str, data: Dict) -> Dict:
        """调用API服务器"""
        # 只处理login端点，其他端点不再调用服务器
        if endpoint != "login":
            return {"success": False, "message": f"端点 {endpoint} 暂不支持服务器调用"}
        
        # 使用真实的API服务器地址
        api_base_url = "http://43.142.19.28:5000"
        url = f"{api_base_url}/login"
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LeYing-Auth-Client/1.0'
            }


            response = requests.post(url, json=data, headers=headers, timeout=10, verify=False)

            # 🔧 修复：不要对所有HTTP错误都抛出异常，而是根据状态码处理
            if response.status_code == 200:
                # 成功响应
                result = response.json()
                return result
            elif response.status_code in [400, 401, 403, 404]:
                # 业务逻辑错误（如账号不存在、机器码不匹配等），返回服务器的错误信息
                try:
                    error_result = response.json()
                    return {
                        "success": False,
                        "message": error_result.get("message", f"HTTP {response.status_code} 错误")
                    }
                except:
                    return {"success": False, "message": f"HTTP {response.status_code} 错误"}
            else:
                # 其他HTTP错误
                return {"success": False, "message": f"服务器错误: HTTP {response.status_code}"}

        except requests.exceptions.ConnectionError as e:
            # 真正的连接错误
            return {"success": False, "message": f"无法连接到服务器: 连接被拒绝"}
        except requests.exceptions.Timeout as e:
            # 超时错误
            return {"success": False, "message": f"无法连接到服务器: 连接超时"}
        except requests.exceptions.RequestException as e:
            # 其他网络异常
            return {"success": False, "message": f"网络异常: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"请求异常: {str(e)}"}
    
    def _mock_api_response(self, endpoint: str, data: Dict) -> Dict:
        """
        模拟API响应（开发阶段使用，云函数不可用时的备用方案）
        """
        
        if endpoint == "login":
            username = data.get("username")  # 云函数参数名
            machine_code = data.get("machineCode")  # 云函数参数名
            
            # 模拟用户数据（正式版本从云数据库读取）
            mock_users = {
                "13800138000": {
                    "id": "user001",
                    "username": "13800138000",
                    "machineCode": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 100
                },
                "13900139000": {
                    "id": "user002", 
                    "username": "13900139000",
                    "machineCode": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 50
                },
                "13700137000": {
                    "id": "user003", 
                    "username": "13700137000",
                    "machineCode": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 30
                },
                "15155712316": {
                    "id": "user004", 
                    "username": "15155712316",
                    "machineCode": machine_code,  # 绑定当前机器码
                    "status": 1,
                    "points": 80
                }
            }
            
            user = mock_users.get(username)
            if not user:
                return {"success": False, "message": "手机号未注册，请联系管理员"}
            
            if user["machineCode"] != machine_code:
                return {"success": False, "message": "设备未授权，请联系管理员绑定设备"}
            
            if user["status"] != 1:
                return {"success": False, "message": "账号已被禁用，请联系管理员"}
            
            # 生成token
            token = hashlib.md5(f"{username}{machine_code}{time.time()}".encode()).hexdigest()
            
            return {
                "success": True,
                "message": "登录成功",
                "data": {
                    "id": user["id"],
                    "username": user["username"],
                    "phone": user["username"],
                    "status": user["status"],
                    "points": user["points"],
                    "token": token
                }
            }
        
        elif endpoint == "check_auth":
            # 模拟权限检查
            token = data.get("token")
            if token:
                return {
                    "success": True,
                    "message": "认证有效",
                    "data": {
                        "id": "user001",
                        "username": "13800138000",
                        "phone": "13800138000",
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
                        "remainingPoints": new_points,  # 使用驼峰命名
                        "operation": operation
                    }
                }
            else:
                return {"success": False, "message": "积分不足"}
        
        return {"success": False, "message": "未知API端点"}

# 全局认证服务实例
auth_service = AuthService() 