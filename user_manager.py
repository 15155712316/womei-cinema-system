#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理工具
用于管理乐影系统的用户账号、积分等
"""

import json
import os
import hashlib
import time
import re
from typing import Dict, List, Optional

# 添加项目根目录到路径
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import auth_service

class UserManager:
    """用户管理类"""
    
    def __init__(self):
        self.users_file = "users_data.json"
        self.users = self.load_users()
    
    def load_users(self) -> Dict:
        """加载用户数据"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载用户数据失败: {e}")
        
        # 创建默认用户数据
        machine_code = auth_service.get_machine_code()
        default_users = {
            "13800138000": {
                "id": "user_001",
                "phone": "13800138000",
                "username": "管理员",
                "machine_code": machine_code,
                "status": 1,
                "points": 100,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": ""
            },
            "13900139000": {
                "id": "user_002",
                "phone": "13900139000", 
                "username": "测试用户",
                "machine_code": machine_code,
                "status": 1,
                "points": 50,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": ""
            },
            "13700137000": {
                "id": "user_003",
                "phone": "13700137000",
                "username": "普通用户", 
                "machine_code": machine_code,
                "status": 1,
                "points": 30,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_login": ""
            }
        }
        self.save_users(default_users)
        return default_users
    
    def save_users(self, users: Dict = None):
        """保存用户数据"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users or self.users, f, ensure_ascii=False, indent=2)
            print("✅ 用户数据已保存")
        except Exception as e:
            print(f"❌ 保存用户数据失败: {e}")
    
    def list_users(self):
        """列出所有用户"""
        print("=" * 80)
        print("用户列表")
        print("=" * 80)
        print(f"{'手机号':<15} {'用户名':<10} {'状态':<6} {'积分':<8} {'机器码':<20} {'创建时间':<20}")
        print("-" * 80)
        
        for phone, user in self.users.items():
            status_str = "正常" if user.get("status") == 1 else "禁用"
            machine_code = user.get("machine_code", "")[:16] + "..."
            print(f"{phone:<15} {user.get('username', ''):<10} {status_str:<6} {user.get('points', 0):<8} {machine_code:<20} {user.get('created_at', ''):<20}")
        
        print(f"\n总计: {len(self.users)} 个用户")
    
    def add_user(self):
        """添加新用户"""
        print("=" * 50)
        print("添加新用户")
        print("=" * 50)
        
        # 输入手机号
        phone = input("请输入手机号 (11位): ").strip()
        
        # 验证手机号格式
        if not re.match(r'^1[3-9]\d{9}$', phone):
            print("❌ 手机号格式不正确")
            return
        
        # 检查是否已存在
        if phone in self.users:
            print("❌ 该手机号已存在")
            return
        
        # 输入用户名
        username = input("请输入用户名: ").strip()
        if not username:
            print("❌ 用户名不能为空")
            return
        
        # 输入机器码
        print("请输入机器码 (留空使用当前机器码):")
        machine_code = input().strip()
        if not machine_code:
            machine_code = auth_service.get_machine_code()
            print(f"使用当前机器码: {machine_code}")
        
        # 输入初始积分
        try:
            points = int(input("请输入初始积分 (默认30): ") or "30")
        except ValueError:
            points = 30
        
        # 创建用户
        user_id = f"user_{int(time.time())}"
        user_data = {
            "id": user_id,
            "phone": phone,
            "username": username,
            "machine_code": machine_code,
            "status": 1,
            "points": points,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": ""
        }
        
        self.users[phone] = user_data
        self.save_users()
        
        print(f"✅ 用户 {username} ({phone}) 已成功添加")
    
    def modify_user(self):
        """修改用户信息"""
        print("=" * 50)
        print("修改用户信息")
        print("=" * 50)
        
        phone = input("请输入要修改的用户手机号: ").strip()
        
        if phone not in self.users:
            print("❌ 用户不存在")
            return
        
        user = self.users[phone]
        print(f"\n当前用户信息:")
        print(f"手机号: {user.get('phone')}")
        print(f"用户名: {user.get('username')}")
        print(f"状态: {'正常' if user.get('status') == 1 else '禁用'}")
        print(f"积分: {user.get('points')}")
        print(f"机器码: {user.get('machine_code')}")
        
        print("\n请选择要修改的项目:")
        print("1. 用户名")
        print("2. 状态 (启用/禁用)")
        print("3. 积分")
        print("4. 机器码")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            new_username = input("请输入新用户名: ").strip()
            if new_username:
                user["username"] = new_username
                print(f"✅ 用户名已更新为: {new_username}")
        
        elif choice == "2":
            current_status = "正常" if user.get("status") == 1 else "禁用"
            print(f"当前状态: {current_status}")
            new_status = input("请输入新状态 (1=正常, 0=禁用): ").strip()
            
            if new_status in ["0", "1"]:
                user["status"] = int(new_status)
                status_str = "正常" if int(new_status) == 1 else "禁用"
                print(f"✅ 用户状态已更新为: {status_str}")
            else:
                print("❌ 无效的状态值")
                return
        
        elif choice == "3":
            current_points = user.get("points", 0)
            print(f"当前积分: {current_points}")
            
            try:
                new_points = int(input("请输入新积分值: "))
                user["points"] = new_points
                print(f"✅ 积分已更新为: {new_points}")
            except ValueError:
                print("❌ 请输入有效的数字")
                return
        
        elif choice == "4":
            print(f"当前机器码: {user.get('machine_code')}")
            new_machine_code = input("请输入新机器码 (留空使用当前机器码): ").strip()
            
            if not new_machine_code:
                new_machine_code = auth_service.get_machine_code()
                print(f"使用当前机器码: {new_machine_code}")
            
            user["machine_code"] = new_machine_code
            print(f"✅ 机器码已更新")
        
        elif choice == "0":
            return
        
        else:
            print("❌ 无效的选择")
            return
        
        self.save_users()
    
    def delete_user(self):
        """删除用户"""
        print("=" * 50)
        print("删除用户")
        print("=" * 50)
        
        phone = input("请输入要删除的用户手机号: ").strip()
        
        if phone not in self.users:
            print("❌ 用户不存在")
            return
        
        user = self.users[phone]
        print(f"\n确认删除用户:")
        print(f"手机号: {user.get('phone')}")
        print(f"用户名: {user.get('username')}")
        
        confirm = input("\n确认删除? (y/N): ").strip().lower()
        if confirm in ['y', 'yes', '是']:
            del self.users[phone]
            self.save_users()
            print(f"✅ 用户 {user.get('username')} ({phone}) 已删除")
        else:
            print("❌ 取消删除")
    
    def manage_points(self):
        """积分管理"""
        print("=" * 50)
        print("积分管理")
        print("=" * 50)
        
        phone = input("请输入用户手机号: ").strip()
        
        if phone not in self.users:
            print("❌ 用户不存在")
            return
        
        user = self.users[phone]
        current_points = user.get("points", 0)
        
        print(f"\n用户: {user.get('username')} ({phone})")
        print(f"当前积分: {current_points}")
        
        print("\n选择操作:")
        print("1. 增加积分")
        print("2. 减少积分")
        print("3. 设置积分")
        print("0. 返回")
        
        choice = input("\n请选择: ").strip()
        
        try:
            if choice == "1":
                amount = int(input("请输入增加的积分数: "))
                user["points"] = current_points + amount
                print(f"✅ 已增加 {amount} 积分，当前积分: {user['points']}")
            
            elif choice == "2":
                amount = int(input("请输入减少的积分数: "))
                new_points = max(0, current_points - amount)  # 不能为负数
                user["points"] = new_points
                print(f"✅ 已减少 {amount} 积分，当前积分: {user['points']}")
            
            elif choice == "3":
                new_points = int(input("请输入新积分值: "))
                user["points"] = max(0, new_points)  # 不能为负数
                print(f"✅ 积分已设置为: {user['points']}")
            
            elif choice == "0":
                return
            
            else:
                print("❌ 无效的选择")
                return
            
            self.save_users()
            
        except ValueError:
            print("❌ 请输入有效的数字")
    
    def export_for_cloud(self):
        """导出数据用于云端部署"""
        print("=" * 50)
        print("导出云端数据")
        print("=" * 50)
        
        # 转换为云端数据格式
        cloud_data = []
        for phone, user in self.users.items():
            cloud_user = {
                "_id": user.get("id"),
                "phone": phone,
                "username": user.get("username"),
                "machine_code": user.get("machine_code"),
                "status": user.get("status"),
                "points": user.get("points"),
                "created_at": user.get("created_at"),
                "last_login": user.get("last_login", "")
            }
            cloud_data.append(cloud_user)
        
        # 保存为云端格式
        cloud_file = "cloud_users_export.json"
        try:
            with open(cloud_file, 'w', encoding='utf-8') as f:
                json.dump(cloud_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 云端数据已导出到: {cloud_file}")
            print(f"📄 导出了 {len(cloud_data)} 个用户")
            print("\n💡 使用说明:")
            print("1. 将此文件上传到腾讯云数据库")
            print("2. 修改 auth_service.py 中的 API 地址")
            print("3. 部署云函数处理用户认证")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def run(self):
        """运行用户管理界面"""
        while True:
            print("\n" + "=" * 60)
            print("乐影用户管理系统")
            print("=" * 60)
            print("1. 查看用户列表")
            print("2. 添加新用户")
            print("3. 修改用户信息")
            print("4. 删除用户")
            print("5. 积分管理")
            print("6. 导出云端数据")
            print("0. 退出")
            
            choice = input("\n请选择操作: ").strip()
            
            try:
                if choice == "1":
                    self.list_users()
                
                elif choice == "2":
                    self.add_user()
                
                elif choice == "3":
                    self.modify_user()
                
                elif choice == "4":
                    self.delete_user()
                
                elif choice == "5":
                    self.manage_points()
                
                elif choice == "6":
                    self.export_for_cloud()
                
                elif choice == "0":
                    print("👋 退出用户管理系统")
                    break
                
                else:
                    print("❌ 无效的选择，请重新输入")
            
            except KeyboardInterrupt:
                print("\n\n👋 退出用户管理系统")
                break
            except Exception as e:
                print(f"❌ 操作失败: {e}")
                import traceback
                traceback.print_exc()

def main():
    """主函数"""
    print("🚀 启动乐影用户管理系统")
    print(f"当前机器码: {auth_service.get_machine_code()}")
    
    manager = UserManager()
    manager.run()

if __name__ == "__main__":
    main() 