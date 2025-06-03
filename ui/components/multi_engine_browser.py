#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多引擎浏览器管理器
支持QWebEngine、Selenium、系统浏览器等多种方案
"""

import json
import os
import time
import threading
from typing import Dict, List, Callable, Optional
from urllib.parse import urlparse

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import QTimer, pyqtSignal, QThread, QObject

# 检查可用的浏览器引擎
WEBENGINE_AVAILABLE = False
SELENIUM_AVAILABLE = False

try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
    from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
    WEBENGINE_AVAILABLE = True
    print("[浏览器] ✅ QWebEngine 可用")
except ImportError:
    print("[浏览器] ❌ QWebEngine 不可用")

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
    print("[浏览器] ✅ Selenium 可用")
except ImportError:
    print("[浏览器] ❌ Selenium 不可用")


class NetworkRequest:
    """网络请求数据结构"""
    def __init__(self, url: str, method: str = "GET", headers: Dict = None, data: str = ""):
        self.url = url
        self.method = method
        self.headers = headers or {}
        self.data = data
        self.timestamp = time.time()


class ParameterExtractor:
    """参数提取器"""
    
    @staticmethod
    def extract_from_request(request: NetworkRequest) -> Dict[str, str]:
        """从网络请求中提取参数"""
        params = {}
        
        try:
            # 1. 提取API域名
            parsed_url = urlparse(request.url)
            if parsed_url.scheme and parsed_url.netloc:
                params['base_url'] = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # 2. 检查是否为影院相关API
            if not ParameterExtractor.is_cinema_api(request.url):
                return params
            
            # 3. 提取影院ID
            cinema_id = ParameterExtractor.extract_cinema_id(request.url)
            if cinema_id:
                params['cinema_id'] = cinema_id
            
            # 4. 提取认证信息
            auth_params = ParameterExtractor.extract_auth_params(request)
            params.update(auth_params)
            
        except Exception as e:
            print(f"[参数提取] 提取参数错误: {e}")
        
        return params
    
    @staticmethod
    def is_cinema_api(url: str) -> bool:
        """判断是否为影院API"""
        cinema_keywords = [
            'cinema', 'movie', 'film', 'ticket', 'seat', 'order',
            'miniticket', 'wechat', 'api', 'service', 'booking'
        ]
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in cinema_keywords)
    
    @staticmethod
    def extract_cinema_id(url: str) -> Optional[str]:
        """提取影院ID"""
        import re
        patterns = [
            r'cinemaid[=:]([a-zA-Z0-9]+)',
            r'cinema_id[=:]([a-zA-Z0-9]+)',
            r'cinemaId[=:]([a-zA-Z0-9]+)',
            r'/cinema/([a-zA-Z0-9]+)',
            r'cid[=:]([a-zA-Z0-9]+)',
            r'[?&]id=([a-zA-Z0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                cinema_id = match.group(1)
                if len(cinema_id) >= 3 and cinema_id.isalnum():
                    return cinema_id
        return None
    
    @staticmethod
    def extract_auth_params(request: NetworkRequest) -> Dict[str, str]:
        """提取认证参数"""
        auth_params = {}
        
        # 从URL参数中提取
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(request.url)
        query_params = parse_qs(parsed.query)
        
        auth_fields = ['openid', 'token', 'userid', 'access_token', 'sessionid']
        
        for field in auth_fields:
            if field in query_params:
                value = query_params[field][0]
                if value and len(value) > 10:
                    auth_params[field] = value
        
        # 从请求头中提取
        for key, value in request.headers.items():
            key_lower = key.lower()
            if 'authorization' in key_lower and 'bearer' in value.lower():
                token = value.replace('Bearer ', '').replace('bearer ', '')
                if len(token) > 10:
                    auth_params['token'] = token
            elif 'openid' in key_lower:
                if len(value) > 10:
                    auth_params['openid'] = value
        
        return auth_params


class WebEngineInterceptor(QWebEngineUrlRequestInterceptor):
    """QWebEngine网络拦截器"""
    
    def __init__(self, callback: Callable[[NetworkRequest], None]):
        super().__init__()
        self.callback = callback
    
    def interceptRequest(self, info):
        """拦截网络请求"""
        try:
            url = info.requestUrl().toString()
            method = info.requestMethod().data().decode()
            
            # 创建请求对象
            request = NetworkRequest(url, method)
            
            # 调用回调函数
            if self.callback:
                self.callback(request)
                
        except Exception as e:
            print(f"[WebEngine拦截] 错误: {e}")


class SeleniumBrowser(QThread):
    """Selenium浏览器线程"""
    
    request_captured = pyqtSignal(object)  # NetworkRequest
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.is_monitoring = False
        self.target_url = ""
    
    def setup_driver(self):
        """设置Chrome驱动"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--disable-features=VizDisplayCompositor')
            chrome_options.add_argument('--disable-extensions')
            
            # 模拟微信浏览器
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/88.0.4324.181 Mobile Safari/537.36 MicroMessenger/8.0.1')
            
            # 启用网络日志
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--log-level=0')
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            
            # 使用webdriver-manager自动管理ChromeDriver
            driver_path = ChromeDriverManager().install()
            self.driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
            
            print("[Selenium] ✅ Chrome驱动设置成功")
            return True
            
        except Exception as e:
            print(f"[Selenium] ❌ Chrome驱动设置失败: {e}")
            return False
    
    def start_monitoring(self, url: str):
        """开始监听"""
        self.target_url = url
        self.is_monitoring = True
        self.start()
    
    def stop_monitoring(self):
        """停止监听"""
        self.is_monitoring = False
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def run(self):
        """运行浏览器监听"""
        if not self.setup_driver():
            return
        
        try:
            # 导航到目标URL
            self.driver.get(self.target_url)
            
            # 监听网络请求
            while self.is_monitoring:
                try:
                    # 获取性能日志
                    logs = self.driver.get_log('performance')
                    
                    for log in logs:
                        message = json.loads(log['message'])
                        
                        if message['message']['method'] == 'Network.requestWillBeSent':
                            request_data = message['message']['params']['request']
                            url = request_data['url']
                            method = request_data['method']
                            headers = request_data.get('headers', {})
                            
                            # 创建请求对象
                            request = NetworkRequest(url, method, headers)
                            
                            # 发送信号
                            self.request_captured.emit(request)
                    
                    time.sleep(0.1)  # 避免CPU占用过高
                    
                except Exception as e:
                    print(f"[Selenium监听] 错误: {e}")
                    time.sleep(1)
        
        except Exception as e:
            print(f"[Selenium] 运行错误: {e}")
        
        finally:
            if self.driver:
                self.driver.quit()


class MultiBrowserWidget(QWidget):
    """多引擎浏览器组件"""
    
    parameter_extracted = pyqtSignal(str, str)  # key, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.extracted_params = {}
        self.request_count = 0
        
        # 选择可用的浏览器引擎
        self.engine_type = self.detect_browser_engine()
        
        self.setup_ui()
        self.setup_browser()
    
    def detect_browser_engine(self) -> str:
        """检测可用的浏览器引擎"""
        if WEBENGINE_AVAILABLE:
            return "webengine"
        elif SELENIUM_AVAILABLE:
            return "selenium"
        else:
            return "fallback"
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 状态显示
        self.status_label = QLabel(f"浏览器引擎: {self.engine_type}")
        layout.addWidget(self.status_label)
        
        # 浏览器容器
        self.browser_container = QWidget()
        self.browser_layout = QVBoxLayout(self.browser_container)
        layout.addWidget(self.browser_container)
        
        # 参数显示
        self.params_display = QTextEdit()
        self.params_display.setMaximumHeight(100)
        self.params_display.setPlaceholderText("提取到的参数将显示在这里...")
        layout.addWidget(self.params_display)
    
    def setup_browser(self):
        """设置浏览器"""
        if self.engine_type == "webengine":
            self.setup_webengine()
        elif self.engine_type == "selenium":
            self.setup_selenium()
        else:
            self.setup_fallback()
    
    def setup_webengine(self):
        """设置QWebEngine"""
        try:
            # 创建WebEngine视图
            self.web_view = QWebEngineView()
            self.browser_layout.addWidget(self.web_view)
            
            # 设置网络拦截器
            self.profile = QWebEngineProfile()
            self.interceptor = WebEngineInterceptor(self.on_request_captured)
            self.profile.setRequestInterceptor(self.interceptor)
            
            # 创建页面
            page = QWebEnginePage(self.profile)
            self.web_view.setPage(page)
            
            print("[多引擎浏览器] ✅ QWebEngine 设置完成")
            
        except Exception as e:
            print(f"[多引擎浏览器] ❌ QWebEngine 设置失败: {e}")
            self.setup_fallback()
    
    def setup_selenium(self):
        """设置Selenium"""
        try:
            # 创建Selenium浏览器线程
            self.selenium_browser = SeleniumBrowser()
            self.selenium_browser.request_captured.connect(self.on_request_captured)
            
            # 添加控制按钮
            control_layout = QHBoxLayout()
            
            self.start_btn = QPushButton("启动浏览器")
            self.start_btn.clicked.connect(self.start_selenium)
            control_layout.addWidget(self.start_btn)
            
            self.stop_btn = QPushButton("停止监听")
            self.stop_btn.clicked.connect(self.stop_selenium)
            self.stop_btn.setEnabled(False)
            control_layout.addWidget(self.stop_btn)
            
            self.browser_layout.addLayout(control_layout)
            
            print("[多引擎浏览器] ✅ Selenium 设置完成")
            
        except Exception as e:
            print(f"[多引擎浏览器] ❌ Selenium 设置失败: {e}")
            self.setup_fallback()
    
    def setup_fallback(self):
        """设置降级方案"""
        fallback_label = QLabel("⚠️ 浏览器引擎不可用\n\n请手动使用浏览器访问小程序，然后使用抓包工具获取参数")
        fallback_label.setStyleSheet("color: #ff6b6b; padding: 20px; text-align: center;")
        self.browser_layout.addWidget(fallback_label)
    
    def start_selenium(self):
        """启动Selenium浏览器"""
        try:
            # 这里可以让用户输入URL，或使用默认的微信小程序URL
            default_url = "https://servicewechat.com/"  # 微信小程序容器
            
            self.selenium_browser.start_monitoring(default_url)
            
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("🎯 正在监听网络请求...")
            
        except Exception as e:
            print(f"[Selenium启动] 错误: {e}")
    
    def stop_selenium(self):
        """停止Selenium浏览器"""
        try:
            self.selenium_browser.stop_monitoring()
            
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.status_label.setText("监听已停止")
            
        except Exception as e:
            print(f"[Selenium停止] 错误: {e}")
    
    def load_url(self, url: str):
        """加载URL"""
        if self.engine_type == "webengine" and hasattr(self, 'web_view'):
            self.web_view.load(url)
        elif self.engine_type == "selenium":
            self.start_selenium()
    
    def on_request_captured(self, request: NetworkRequest):
        """处理捕获的网络请求"""
        try:
            self.request_count += 1
            
            # 提取参数
            params = ParameterExtractor.extract_from_request(request)
            
            if params:
                # 更新提取的参数
                self.extracted_params.update(params)
                
                # 更新显示
                self.update_params_display()
                
                # 发送信号
                for key, value in params.items():
                    self.parameter_extracted.emit(key, value)
                
                print(f"[参数提取] 从请求中提取到参数: {params}")
            
            # 更新状态
            self.status_label.setText(f"已监听 {self.request_count} 个请求，提取到 {len(self.extracted_params)} 个参数")
            
        except Exception as e:
            print(f"[请求处理] 错误: {e}")
    
    def update_params_display(self):
        """更新参数显示"""
        if not self.extracted_params:
            return
        
        display_text = "提取到的参数:\n\n"
        
        for key, value in self.extracted_params.items():
            # 对敏感信息进行部分隐藏
            if key in ['token', 'openid'] and len(value) > 12:
                display_value = value[:8] + "..." + value[-4:]
            else:
                display_value = value
            
            display_text += f"{key}: {display_value}\n"
        
        self.params_display.clear()
        self.params_display.append(display_text)
    
    def get_extracted_params(self) -> Dict[str, str]:
        """获取提取的参数"""
        return self.extracted_params.copy()
    
    def clear_params(self):
        """清空参数"""
        self.extracted_params.clear()
        self.request_count = 0
        self.params_display.clear()
        self.status_label.setText(f"浏览器引擎: {self.engine_type}")
