#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理API服务模块
提供管理后台相关的API功能，包括修改用户机器码
"""

import requests
import json
from typing import Dict, Optional, Tuple

class AdminAPIService:
    """管理API服务类"""
    
    def __init__(self):
        # API服务器地址
        self.api_base_url = "http://43.142.19.28:5000"
        
    def update_user_machine_code(self, phone: str, new_machine_code: str) -> Tuple[bool, str]:
        """
        更新用户的机器码
        :param phone: 用户手机号
        :param new_machine_code: 新的机器码
        :return: (是否成功, 消息)
        """
        try:
            # 构建更新机器码的请求
            update_data = {
                "phone": phone,
                "machineCode": new_machine_code,
                "timestamp": int(__import__('time').time())
            }
            
            url = f"{self.api_base_url}/update_machine_code"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LeYing-Admin-Client/1.0'
            }
            
            print(f"[管理API] 更新机器码请求: {phone} -> {new_machine_code}")
            
            response = requests.post(url, json=update_data, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                return True, result.get("message", "机器码更新成功")
            else:
                return False, result.get("message", "机器码更新失败")
                
        except requests.exceptions.RequestException as e:
            print(f"[管理API] 网络异常: {e}")
            return False, f"网络连接失败: {str(e)}"
        except Exception as e:
            print(f"[管理API] 异常: {e}")
            return False, f"更新异常: {str(e)}"
    
    def get_user_list(self) -> Tuple[bool, str, Optional[list]]:
        """
        获取用户列表
        :return: (是否成功, 消息, 用户列表)
        """
        try:
            url = f"{self.api_base_url}/admin/users"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LeYing-Admin-Client/1.0'
            }
            
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                return True, "获取成功", result.get("data", [])
            else:
                return False, result.get("message", "获取失败"), None
                
        except requests.exceptions.RequestException as e:
            print(f"[管理API] 网络异常: {e}")
            return False, f"网络连接失败: {str(e)}", None
        except Exception as e:
            print(f"[管理API] 异常: {e}")
            return False, f"获取异常: {str(e)}", None
    
    def update_user_status(self, phone: str, status: int) -> Tuple[bool, str]:
        """
        更新用户状态
        :param phone: 用户手机号
        :param status: 新状态 (1=启用, 0=禁用)
        :return: (是否成功, 消息)
        """
        try:
            update_data = {
                "phone": phone,
                "status": status,
                "timestamp": int(__import__('time').time())
            }
            
            url = f"{self.api_base_url}/update_user_status"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LeYing-Admin-Client/1.0'
            }
            
            response = requests.post(url, json=update_data, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                status_text = "启用" if status == 1 else "禁用"
                return True, f"用户状态已更新为{status_text}"
            else:
                return False, result.get("message", "状态更新失败")
                
        except requests.exceptions.RequestException as e:
            print(f"[管理API] 网络异常: {e}")
            return False, f"网络连接失败: {str(e)}"
        except Exception as e:
            print(f"[管理API] 异常: {e}")
            return False, f"更新异常: {str(e)}"
    
    def update_user_points(self, phone: str, points: int) -> Tuple[bool, str]:
        """
        更新用户积分
        :param phone: 用户手机号
        :param points: 新积分数量
        :return: (是否成功, 消息)
        """
        try:
            update_data = {
                "phone": phone,
                "points": points,
                "timestamp": int(__import__('time').time())
            }
            
            url = f"{self.api_base_url}/update_user_points"
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LeYing-Admin-Client/1.0'
            }
            
            response = requests.post(url, json=update_data, headers=headers, timeout=10, verify=False)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                return True, f"用户积分已更新为{points}"
            else:
                return False, result.get("message", "积分更新失败")
                
        except requests.exceptions.RequestException as e:
            print(f"[管理API] 网络异常: {e}")
            return False, f"网络连接失败: {str(e)}"
        except Exception as e:
            print(f"[管理API] 异常: {e}")
            return False, f"更新异常: {str(e)}"

# 全局管理API服务实例
admin_api_service = AdminAPIService() 