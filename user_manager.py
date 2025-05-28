#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理工具 - 命令行版本
用于快速管理用户账号，避免直接操作数据库
"""

import sys
import getpass
from pymongo import MongoClient
from datetime import datetime
import hashlib

class UserManager:
    def __init__(self):
        # 连接MongoDB
        try:
            self.client = MongoClient("mongodb://testuser:testpass@127.0.0.1:27017/userdb")
            self.db = self.client["userdb"]
            self.users = self.db["users"]
            self.admins = self.db["admins"]
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            sys.exit(1)
    
    def hash_password(self, password):
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_admin(self, username, password):
        """创建管理员账号"""
        hashed_pw = self.hash_password(password)
        admin_doc = {
            "username": username,
            "password": hashed_pw,
            "created_at": datetime.now(),
            "role": "admin"
        }
        
        # 检查管理员是否已存在
        if self.admins.find_one({"username": username}):
            print(f"❌ 管理员 {username} 已存在")
            return False
        
        self.admins.insert_one(admin_doc)
        print(f"✅ 管理员 {username} 创建成功")
        return True
    
    def verify_admin(self, username, password):
        """验证管理员账号"""
        admin = self.admins.find_one({"username": username})
        if not admin:
            return False
        
        hashed_pw = self.hash_password(password)
        return admin["password"] == hashed_pw
    
    def add_user(self, phone, points=0, status=1):
        """添加用户"""
        # 检查用户是否已存在
        if self.users.find_one({"phone": phone}):
            print(f"❌ 用户 {phone} 已存在")
            return False
        
        user_doc = {
            "phone": phone,
            "points": points,
            "status": status,
            "created_at": datetime.now()
        }
        
        self.users.insert_one(user_doc)
        print(f"✅ 用户 {phone} 添加成功 (积分: {points}, 状态: {'启用' if status else '禁用'})")
        return True
    
    def list_users(self, limit=20):
        """列出用户"""
        users = list(self.users.find({}).limit(limit))
        if not users:
            print("📋 暂无用户")
            return
        
        print(f"\n📋 用户列表 (显示前{len(users)}个):")
        print("-" * 80)
        print(f"{'手机号':<15} {'积分':<8} {'状态':<8} {'机器码':<20} {'创建时间':<20}")
        print("-" * 80)
        
        for user in users:
            phone = user.get('phone', 'N/A')
            points = user.get('points', 0)
            status = '启用' if user.get('status', 1) == 1 else '禁用'
            machine_code = user.get('machineCode', '未绑定')[:15]
            created_at = user.get('created_at', 'N/A')
            if isinstance(created_at, datetime):
                created_at = created_at.strftime('%Y-%m-%d %H:%M')
            
            print(f"{phone:<15} {points:<8} {status:<8} {machine_code:<20} {str(created_at):<20}")
    
    def update_user_points(self, phone, points):
        """更新用户积分"""
        result = self.users.update_one(
            {"phone": phone}, 
            {"$set": {"points": points}}
        )
        if result.modified_count > 0:
            print(f"✅ 用户 {phone} 积分更新为 {points}")
            return True
        else:
            print(f"❌ 用户 {phone} 不存在")
            return False
    
    def update_user_status(self, phone, status):
        """更新用户状态"""
        result = self.users.update_one(
            {"phone": phone}, 
            {"$set": {"status": status}}
        )
        if result.modified_count > 0:
            status_text = "启用" if status == 1 else "禁用"
            print(f"✅ 用户 {phone} 状态更新为 {status_text}")
            return True
        else:
            print(f"❌ 用户 {phone} 不存在")
            return False
    
    def delete_user(self, phone):
        """删除用户"""
        result = self.users.delete_one({"phone": phone})
        if result.deleted_count > 0:
            print(f"✅ 用户 {phone} 已删除")
            return True
        else:
            print(f"❌ 用户 {phone} 不存在")
            return False
    
    def get_stats(self):
        """获取统计信息"""
        total_users = self.users.count_documents({})
        active_users = self.users.count_documents({"status": 1})
        disabled_users = self.users.count_documents({"status": 0})
        
        print(f"\n📊 系统统计:")
        print(f"总用户数: {total_users}")
        print(f"启用用户: {active_users}")
        print(f"禁用用户: {disabled_users}")

def main():
    """主程序"""
    print("=" * 50)
    print("🔐 用户管理系统")
    print("=" * 50)
    
    manager = UserManager()
    
    # 检查是否有管理员账号
    admin_count = manager.admins.count_documents({})
    if admin_count == 0:
        print("\n🚀 初次使用，请创建管理员账号:")
        username = input("管理员用户名: ").strip()
        password = getpass.getpass("管理员密码: ")
        if username and password:
            manager.create_admin(username, password)
        else:
            print("❌ 用户名和密码不能为空")
            return
    
    # 管理员登录
    print("\n🔑 请登录管理员账号:")
    username = input("用户名: ").strip()
    password = getpass.getpass("密码: ")
    
    if not manager.verify_admin(username, password):
        print("❌ 用户名或密码错误")
        return
    
    print(f"✅ 欢迎 {username}！")
    
    # 主菜单
    while True:
        print("\n" + "=" * 30)
        print("📋 管理菜单:")
        print("1. 查看用户列表")
        print("2. 添加用户")
        print("3. 更新用户积分")
        print("4. 更新用户状态")
        print("5. 删除用户")
        print("6. 系统统计")
        print("7. 创建管理员")
        print("0. 退出")
        print("=" * 30)
        
        choice = input("请选择操作 (0-7): ").strip()
        
        if choice == "1":
            manager.list_users()
        
        elif choice == "2":
            phone = input("手机号: ").strip()
            points = input("初始积分 (默认0): ").strip()
            points = int(points) if points.isdigit() else 0
            status = input("状态 (1=启用, 0=禁用, 默认1): ").strip()
            status = int(status) if status in ['0', '1'] else 1
            manager.add_user(phone, points, status)
        
        elif choice == "3":
            phone = input("手机号: ").strip()
            points = input("新积分: ").strip()
            if points.isdigit():
                manager.update_user_points(phone, int(points))
            else:
                print("❌ 积分必须是数字")
        
        elif choice == "4":
            phone = input("手机号: ").strip()
            status = input("新状态 (1=启用, 0=禁用): ").strip()
            if status in ['0', '1']:
                manager.update_user_status(phone, int(status))
            else:
                print("❌ 状态只能是 0 或 1")
        
        elif choice == "5":
            phone = input("手机号: ").strip()
            confirm = input(f"确认删除用户 {phone}? (y/N): ").strip().lower()
            if confirm == 'y':
                manager.delete_user(phone)
        
        elif choice == "6":
            manager.get_stats()
        
        elif choice == "7":
            username = input("新管理员用户名: ").strip()
            password = getpass.getpass("新管理员密码: ")
            if username and password:
                manager.create_admin(username, password)
            else:
                print("❌ 用户名和密码不能为空")
        
        elif choice == "0":
            print("👋 再见！")
            break
        
        else:
            print("❌ 无效选择，请重新输入")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {e}") 