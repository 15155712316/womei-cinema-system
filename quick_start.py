#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 快速启动脚本
解决依赖问题，提供简化的启动方式
"""

import sys
import os
import subprocess
from pathlib import Path

def check_and_install_dependencies():
    """检查并安装必需的依赖"""
    required_packages = [
        'PyQt5',
        'requests',
        'psutil',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
            print(f"✅ {package} 已安装")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} 未安装")
    
    if missing_packages:
        print(f"\n需要安装以下包: {', '.join(missing_packages)}")
        print("正在安装...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安装失败")
                return False
    
    return True

def create_missing_modules():
    """创建缺失的模块文件"""
    
    # 创建必需的目录
    directories = [
        'patterns',
        'performance',
        'ui',
        'utils',
        'api',
        'services'
    ]
    
    for dir_name in directories:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            dir_path.mkdir(parents=True)
            print(f"创建目录: {dir_name}")
        
        # 创建__init__.py文件
        init_file = dir_path / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Auto-generated __init__.py\n")
            print(f"创建文件: {init_file}")
    
    # 创建缺失的模块文件
    modules_to_create = {
        'patterns/order_observer.py': '''
# 订单观察者模式 - 简化版本
class OrderStatus:
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"

class OrderSubject:
    def __init__(self):
        self.observers = []
    
    def attach(self, observer):
        self.observers.append(observer)
    
    def notify(self, order_id, status):
        for observer in self.observers:
            observer.update(order_id, status)

_order_subject = OrderSubject()

def get_order_subject():
    return _order_subject

def setup_order_observers():
    pass
''',
        
        'patterns/payment_strategy.py': '''
# 支付策略模式 - 简化版本
class PaymentContext:
    def __init__(self):
        self.strategy = None
    
    def set_strategy(self, strategy):
        self.strategy = strategy
    
    def execute_payment(self, amount):
        if self.strategy:
            return self.strategy.pay(amount)
        return False

_payment_context = PaymentContext()

def get_payment_context():
    return _payment_context
''',
        
        'ui/ui_component_factory.py': '''
# UI组件工厂 - 简化版本
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit

class UIComponentFactory:
    @staticmethod
    def create_button(text, callback=None):
        button = QPushButton(text)
        if callback:
            button.clicked.connect(callback)
        return button
    
    @staticmethod
    def create_label(text):
        return QLabel(text)
    
    @staticmethod
    def create_input(placeholder=""):
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        return input_field
''',
        
        'utils/data_utils.py': '''
# 数据工具类 - 简化版本
import json

class DataUtils:
    @staticmethod
    def parse_json_response(response_text):
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def format_price(price):
        return f"¥{price:.2f}"
    
    @staticmethod
    def validate_phone(phone):
        return len(phone) == 11 and phone.isdigit()
''',
        
        'utils/error_handler.py': '''
# 错误处理 - 简化版本
def handle_api_errors(show_message=True, default_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if show_message:
                    print(f"API错误: {e}")
                return default_return
        return wrapper
    return decorator

class ErrorHandler:
    @staticmethod
    def handle_error(error, context=""):
        print(f"错误 [{context}]: {error}")
''',
        
        'performance/cache_manager.py': '''
# 缓存管理 - 简化版本
import time

class CacheManager:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < 300:  # 5分钟缓存
                return data
        return None
    
    def set(self, key, value):
        self.cache[key] = (value, time.time())

_cache_manager = CacheManager()

def get_cache_manager():
    return _cache_manager

def cache_result(key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cached = _cache_manager.get(key)
            if cached is not None:
                return cached
            result = func(*args, **kwargs)
            _cache_manager.set(key, result)
            return result
        return wrapper
    return decorator
''',
        
        'services/order_api.py': '''
# 订单API服务 - 简化版本
import requests

def get_unpaid_order_detail(params):
    """获取未支付订单详情"""
    try:
        # 这里应该是实际的API调用
        # 现在返回模拟数据
        return {
            'success': True,
            'data': {
                'orderno': params.get('orderno', ''),
                'totalprice': '3000',
                'mem_totalprice': '3000',
                'ticketcount': '1',
                'filmname': '测试电影',
                'cinemaname': '测试影院'
            }
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}
''',
        
        'services/auth_service.py': '''
# 认证服务 - 简化版本
class AuthService:
    def __init__(self):
        self.current_account = None
    
    def login(self, phone):
        # 简化的登录逻辑
        if phone and len(phone) == 11:
            self.current_account = {
                'phone': phone,
                'userid': phone,
                'openid': f'openid_{phone}',
                'token': f'token_{phone}'
            }
            return True, "登录成功", self.current_account
        return False, "手机号格式错误", None
    
    def get_machine_code(self):
        return "TEST_MACHINE_CODE"
    
    def get_member_info_enhanced(self):
        return {
            'success': True,
            'is_member': True,
            'cardno': '123456789',
            'balance': 10000,
            'data_source': 'api'
        }
'''
    }
    
    for file_path, content in modules_to_create.items():
        file_obj = Path(file_path)
        if not file_obj.exists():
            file_obj.parent.mkdir(parents=True, exist_ok=True)
            file_obj.write_text(content.strip(), encoding='utf-8')
            print(f"创建模块: {file_path}")

def main():
    """主函数"""
    print("🚀 PyQt5电影票务管理系统 - 快速启动")
    print("=" * 50)
    
    # 1. 检查并安装依赖
    print("\n📦 检查依赖包...")
    if not check_and_install_dependencies():
        print("❌ 依赖安装失败，请手动安装")
        return False
    
    # 2. 创建缺失的模块
    print("\n📁 创建缺失的模块...")
    create_missing_modules()
    
    # 3. 尝试启动主程序
    print("\n🎬 启动主程序...")
    try:
        # 导入并启动主程序
        import main_modular
        print("✅ 主程序启动成功！")
        return True
    except Exception as e:
        print(f"❌ 主程序启动失败: {e}")
        print("\n🔧 可能的解决方案:")
        print("1. 检查Python版本 (需要Python 3.6+)")
        print("2. 手动安装PyQt5: pip install PyQt5")
        print("3. 检查文件路径是否正确")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 系统启动成功！")
    else:
        print("\n💡 如需帮助，请查看错误信息或联系技术支持")
    
    input("\n按回车键退出...")
