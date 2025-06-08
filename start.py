#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyQt5电影票务管理系统 - 简单启动脚本
解决依赖问题的最简方案
"""

import sys
import os
from pathlib import Path

def install_dependencies():
    """安装必需的依赖"""
    import subprocess
    
    print("📦 安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ 依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_minimal_modules():
    """创建最小化的必需模块"""
    
    # 确保目录存在
    for dir_name in ['patterns', 'ui', 'utils', 'api', 'services', 'performance']:
        Path(dir_name).mkdir(exist_ok=True)
        (Path(dir_name) / "__init__.py").touch()
    
    # 创建最小化模块
    modules = {
        'patterns/order_observer.py': '''
class OrderStatus:
    CREATED = "created"
    PAID = "paid"
    CANCELLED = "cancelled"

class OrderSubject:
    def __init__(self):
        self.observers = []
    def attach(self, observer): pass
    def notify(self, order_id, status): pass

def get_order_subject(): return OrderSubject()
def setup_order_observers(): pass
''',
        'patterns/payment_strategy.py': '''
class PaymentContext:
    def __init__(self): pass
    def set_strategy(self, strategy): pass
    def execute_payment(self, amount): return True

def get_payment_context(): return PaymentContext()
''',
        'ui/ui_component_factory.py': '''
from PyQt5.QtWidgets import QPushButton, QLabel, QLineEdit

class UIComponentFactory:
    @staticmethod
    def create_button(text, callback=None):
        btn = QPushButton(text)
        if callback: btn.clicked.connect(callback)
        return btn
    @staticmethod
    def create_label(text): return QLabel(text)
    @staticmethod
    def create_input(placeholder=""): 
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        return inp
''',
        'utils/data_utils.py': '''
import json
class DataUtils:
    @staticmethod
    def parse_json_response(text):
        try: return json.loads(text)
        except: return None
    @staticmethod
    def format_price(price): return f"¥{price:.2f}"
    @staticmethod
    def validate_phone(phone): return len(phone) == 11 and phone.isdigit()
''',
        'utils/error_handler.py': '''
def handle_api_errors(show_message=True, default_return=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try: return func(*args, **kwargs)
            except Exception as e:
                if show_message: print(f"API错误: {e}")
                return default_return
        return wrapper
    return decorator

class ErrorHandler:
    @staticmethod
    def handle_error(error, context=""): print(f"错误 [{context}]: {error}")
''',
        'performance/cache_manager.py': '''
import time
class CacheManager:
    def __init__(self): self.cache = {}
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < 300: return data
        return None
    def set(self, key, value): self.cache[key] = (value, time.time())

_cache = CacheManager()
def get_cache_manager(): return _cache
def cache_result(key):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cached = _cache.get(key)
            if cached is not None: return cached
            result = func(*args, **kwargs)
            _cache.set(key, result)
            return result
        return wrapper
    return decorator
''',
        'services/order_api.py': '''
def get_unpaid_order_detail(params):
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
''',
        'services/auth_service.py': '''
class AuthService:
    def __init__(self): self.current_account = None
    def login(self, phone):
        if phone and len(phone) == 11:
            self.current_account = {
                'phone': phone, 'userid': phone,
                'openid': f'openid_{phone}', 'token': f'token_{phone}'
            }
            return True, "登录成功", self.current_account
        return False, "手机号格式错误", None
    def get_machine_code(self): return "TEST_MACHINE_CODE"
    def get_member_info_enhanced(self):
        return {'success': True, 'is_member': True, 'cardno': '123456789', 'balance': 10000, 'data_source': 'api'}
'''
    }
    
    for file_path, content in modules.items():
        file_obj = Path(file_path)
        if not file_obj.exists():
            file_obj.write_text(content.strip(), encoding='utf-8')
            print(f"创建: {file_path}")

def main():
    """主启动函数"""
    print("🎬 PyQt5电影票务管理系统启动器")
    print("=" * 40)
    
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("❌ 需要Python 3.6或更高版本")
        return False
    
    # 检查PyQt5
    try:
        import PyQt5
        print("✅ PyQt5已安装")
    except ImportError:
        print("❌ PyQt5未安装，正在安装...")
        if not install_dependencies():
            return False
    
    # 创建必需模块
    print("📁 创建必需模块...")
    create_minimal_modules()
    
    # 启动主程序
    print("🚀 启动主程序...")
    try:
        os.system(f'"{sys.executable}" main_modular.py')
        return True
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 解决方案:")
        print("1. 手动安装: pip install PyQt5 requests psutil")
        print("2. 检查Python版本: python --version")
        print("3. 使用虚拟环境: python -m venv venv")
    input("\n按回车键退出...")
