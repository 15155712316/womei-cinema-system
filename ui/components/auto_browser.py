#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动监听浏览器组件
实现真正的网络请求自动拦截和参数提取
"""

import json
import re
from urllib.parse import urlparse, parse_qs
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt5.QtCore import pyqtSignal, QUrl

# 导入WebEngine组件
try:
    # 确保在导入WebEngine之前已经设置了Qt属性
    from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
    from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
    WEBENGINE_AVAILABLE = True
except ImportError as e:
    WEBENGINE_AVAILABLE = False
    QWebEngineView = None
    QWebEnginePage = None
    QWebEngineProfile = None
    QWebEngineUrlRequestInterceptor = None
except Exception as e:
    WEBENGINE_AVAILABLE = False
    QWebEngineView = None
    QWebEnginePage = None
    QWebEngineProfile = None
    QWebEngineUrlRequestInterceptor = None
    print(f"[自动浏览器] ❌ QWebEngine 初始化失败: {e}")


# 只有在WebEngine可用时才定义NetworkInterceptor
if WEBENGINE_AVAILABLE and QWebEngineUrlRequestInterceptor:
    class NetworkInterceptor(QWebEngineUrlRequestInterceptor):
        """网络请求拦截器"""

        def __init__(self, callback):
            super().__init__()
            self.callback = callback
            self.request_count = 0

        def interceptRequest(self, info):
            """拦截网络请求"""
            try:
                self.request_count += 1
                url = info.requestUrl().toString()
                method = info.requestMethod().data().decode()

                # 调用回调函数处理请求
                if self.callback:
                    self.callback(url, method, self.request_count)

            except Exception as e:
                print(f"[网络拦截] 错误: {e}")
else:
    # WebEngine不可用时的占位符类
    class NetworkInterceptor:
        def __init__(self, callback):
            self.callback = callback
            self.request_count = 0
            print("[网络拦截] ⚠️ WebEngine不可用，使用占位符拦截器")


class ParameterExtractor:
    """智能参数提取器"""
    
    @staticmethod
    def is_cinema_api(url):
        """判断是否为影院相关API"""
        cinema_keywords = [
            'cinema', 'movie', 'film', 'ticket', 'seat', 'order', 'booking',
            'miniticket', 'wechat', 'api', 'service', 'show', 'hall'
        ]
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in cinema_keywords)
    
    @staticmethod
    def extract_cinema_id(url):
        """提取影院ID"""
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
    def extract_auth_params(url):
        """提取认证参数"""
        auth_params = {}
        
        # 解析URL参数
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        auth_fields = ['openid', 'token', 'userid', 'access_token', 'sessionid']
        
        for field in auth_fields:
            if field in query_params:
                value = query_params[field][0]
                if value and len(value) > 10:
                    auth_params[field] = value
        
        return auth_params
    
    @staticmethod
    def extract_base_url(url):
        """提取API基础域名"""
        try:
            parsed = urlparse(url)
            if parsed.scheme and parsed.netloc:
                return f"{parsed.scheme}://{parsed.netloc}"
        except:
            pass
        return None
    
    @staticmethod
    def extract_all_params(url):
        """提取所有参数"""
        params = {}
        
        # 检查是否为影院API
        if not ParameterExtractor.is_cinema_api(url):
            return params
        
        # 提取基础URL
        base_url = ParameterExtractor.extract_base_url(url)
        if base_url:
            params['base_url'] = base_url
        
        # 提取影院ID
        cinema_id = ParameterExtractor.extract_cinema_id(url)
        if cinema_id:
            params['cinema_id'] = cinema_id
        
        # 提取认证参数
        auth_params = ParameterExtractor.extract_auth_params(url)
        params.update(auth_params)
        
        return params


class AutoBrowserWidget(QWidget):
    """自动监听浏览器组件"""
    
    parameter_extracted = pyqtSignal(str, str)  # key, value
    status_changed = pyqtSignal(str)  # status message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.extracted_params = {}
        self.request_count = 0
        self.is_monitoring = False
        
        self.setup_ui()
        self.setup_browser()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        self.start_button = QPushButton("🎯 开始监听")
        self.start_button.clicked.connect(self.start_monitoring)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.stop_button = QPushButton("⏹️ 停止监听")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.clicked.connect(self.clear_params)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)
        
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.clear_button)
        control_layout.addStretch()
        
        # 状态显示
        self.status_label = QLabel("准备就绪 - 点击'开始监听'启动自动参数采集")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        
        # 浏览器区域
        if WEBENGINE_AVAILABLE and QWebEngineView:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(400)
            layout.addLayout(control_layout)
            layout.addWidget(self.status_label)
            layout.addWidget(self.web_view)
        else:
            error_label = QLabel("❌ QWebEngine 不可用\n\n可能的解决方案：\n1. 安装 PyQtWebEngine: pip install PyQtWebEngine\n2. 重启应用程序\n3. 检查Qt版本兼容性")
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px; text-align: center;")
            layout.addLayout(control_layout)
            layout.addWidget(self.status_label)
            layout.addWidget(error_label)
        
        # 参数显示区域
        self.params_display = QTextEdit()
        self.params_display.setMaximumHeight(120)
        self.params_display.setPlaceholderText("提取到的参数将显示在这里...")
        self.params_display.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.params_display)
    
    def setup_browser(self):
        """设置浏览器和网络拦截"""
        if not WEBENGINE_AVAILABLE or not QWebEngineProfile:
            print("[自动浏览器] ⚠️ WebEngine不可用，跳过浏览器设置")
            return

        try:
            # 创建自定义Profile
            self.profile = QWebEngineProfile()

            # 设置网络拦截器
            self.interceptor = NetworkInterceptor(self.on_request_intercepted)
            self.profile.setRequestInterceptor(self.interceptor)

            # 创建自定义页面
            if hasattr(self, 'web_view') and QWebEnginePage:
                self.page = QWebEnginePage(self.profile)
                self.web_view.setPage(self.page)


        except Exception as e:
            print(f"[自动浏览器] ❌ 设置失败: {e}")
    
    def start_monitoring(self):
        """开始监听"""
        if not WEBENGINE_AVAILABLE or not hasattr(self, 'web_view'):
            self.status_changed.emit("❌ QWebEngine 不可用，无法启动监听")
            self.status_label.setText("❌ QWebEngine 不可用，请安装 PyQtWebEngine")
            return

        self.is_monitoring = True
        self.request_count = 0
        self.extracted_params.clear()

        # 更新按钮状态
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # 加载指导页面
        try:
            # 创建一个指导页面HTML
            guide_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>微信小程序参数采集指南</title>
                <style>
                    body { font-family: 'Microsoft YaHei', sans-serif; padding: 20px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2196F3; text-align: center; }
                    .method { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; border-left: 4px solid #2196F3; }
                    .step { margin: 10px 0; padding: 10px; background: white; border-radius: 5px; }
                    .highlight { color: #e74c3c; font-weight: bold; }
                    .success { color: #27ae60; font-weight: bold; }
                    .url-box { background: #e8f4fd; padding: 15px; border-radius: 5px; font-family: monospace; word-break: break-all; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🎬 微信小程序参数采集指南</h1>

                    <div class="method">
                        <h3>📱 方法一：手机 + 电脑抓包（推荐）</h3>
                        <div class="step">1. 下载并启动 <span class="highlight">Fiddler</span> 抓包工具</div>
                        <div class="step">2. 设置手机WiFi代理为：<span class="highlight">电脑IP:8888</span></div>
                        <div class="step">3. 在手机微信中正常操作影院小程序</div>
                        <div class="step">4. 在Fiddler中查看并复制API请求</div>
                        <div class="step">5. 将请求数据粘贴到"手动输入"Tab中</div>
                    </div>

                    <div class="method">
                        <h3>💻 方法二：微信开发者工具</h3>
                        <div class="step">1. 下载微信开发者工具</div>
                        <div class="url-box">https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html</div>
                        <div class="step">2. 在开发者工具中打开影院小程序</div>
                        <div class="step">3. 在Network面板中查看API请求</div>
                        <div class="step">4. 复制相关请求数据</div>
                    </div>

                    <div class="method">
                        <h3>🌐 方法三：影院官网（如果有）</h3>
                        <div class="step">1. 搜索影院官方网站</div>
                        <div class="step">2. 查看是否有在线购票系统</div>
                        <div class="step">3. 在此浏览器中访问官网</div>
                        <div class="step">4. 系统自动监听API请求</div>
                    </div>

                    <div style="background: #fff3cd; padding: 15px; border-radius: 5px; margin-top: 20px;">
                        <strong>💡 提示：</strong>微信小程序只能在微信环境中运行，无法直接在普通浏览器中访问。
                        建议使用上述方法获取API参数后，切换到"手动输入"Tab进行参数分析。
                    </div>

                    <div style="background: #d1ecf1; padding: 15px; border-radius: 5px; margin-top: 20px;">
                        <strong class="success">✅ 网络监听已启动</strong><br>
                        如果您访问的是影院官网（非小程序），系统会自动捕获API请求。
                    </div>
                </div>
            </body>
            </html>
            """

            # 将HTML内容加载到浏览器
            self.web_view.setHtml(guide_html)

            self.status_changed.emit("🎯 监听已启动 - 请参考指南获取小程序参数")
            self.status_label.setText("🎯 网络监听已启动 - 请参考浏览器中的指南操作")

        except Exception as e:
            print(f"[自动浏览器] ❌ 启动监听失败: {e}")
            self.status_changed.emit(f"❌ 启动监听失败: {str(e)}")
            self.stop_monitoring()
    
    def stop_monitoring(self):
        """停止监听"""
        self.is_monitoring = False
        
        # 更新按钮状态
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        # 检查提取结果
        param_count = len(self.extracted_params)
        if param_count > 0:
            self.status_changed.emit(f"✅ 监听完成 - 成功提取 {param_count} 个参数")
            self.status_label.setText(f"✅ 监听完成 - 已提取 {param_count} 个参数，共监听 {self.request_count} 个请求")
        else:
            self.status_changed.emit("⚠️ 监听完成 - 未提取到影院参数")
            self.status_label.setText(f"⚠️ 监听完成 - 未提取到影院参数，共监听 {self.request_count} 个请求")
        
        print(f"[自动浏览器] ⏹️ 停止监听，共处理 {self.request_count} 个请求")
    
    def on_request_intercepted(self, url, method, count):
        """处理拦截到的网络请求"""
        if not self.is_monitoring:
            return
        
        try:
            # 更新请求计数
            self.request_count = count
            
            # 提取参数
            params = ParameterExtractor.extract_all_params(url)
            
            if params:
                # 更新提取的参数
                self.extracted_params.update(params)
                
                # 更新显示
                self.update_params_display()
                
                # 发送信号
                for key, value in params.items():
                    self.parameter_extracted.emit(key, value)
                
            
            # 更新状态（每10个请求更新一次，避免频繁更新）
            if count % 10 == 0:
                param_count = len(self.extracted_params)
                self.status_label.setText(f"🎯 正在监听... 已处理 {count} 个请求，提取到 {param_count} 个参数")
                
        except Exception as e:
            print(f"[请求处理] 错误: {e}")
    
    def update_params_display(self):
        """更新参数显示"""
        if not self.extracted_params:
            return
        
        display_text = "🎉 提取到的参数:\n\n"
        
        for key, value in self.extracted_params.items():
            # 对敏感信息进行部分隐藏
            if key in ['token', 'openid'] and len(value) > 12:
                display_value = value[:8] + "..." + value[-4:]
            else:
                display_value = value
            
            display_text += f"✅ {key}: {display_value}\n"
        
        self.params_display.clear()
        self.params_display.append(display_text)
    
    def clear_params(self):
        """清空参数"""
        self.extracted_params.clear()
        self.request_count = 0
        self.params_display.clear()
        self.status_label.setText("准备就绪 - 点击'开始监听'启动自动参数采集")
    
    def get_extracted_params(self):
        """获取提取的参数"""
        return self.extracted_params.copy()
    
    def load_url(self, url):
        """加载指定URL"""
        if WEBENGINE_AVAILABLE and hasattr(self, 'web_view') and QUrl:
            try:
                self.web_view.load(QUrl(url))
                print(f"[自动浏览器] 加载URL: {url}")
            except Exception as e:
                print(f"[自动浏览器] 加载URL失败: {e}")
        else:
            print(f"[自动浏览器] ⚠️ WebEngine不可用，无法加载URL: {url}")
