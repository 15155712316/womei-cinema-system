#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完全自动化参数采集器
实现真正的自动监听功能
"""

import json
import re
import os
import webbrowser
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QFrame, QMessageBox, QTabWidget, QWidget
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

# 导入自动浏览器组件
try:
    from ui.components.auto_browser import AutoBrowserWidget
    AUTO_BROWSER_AVAILABLE = True
except ImportError as e:
    AUTO_BROWSER_AVAILABLE = False


class ParameterExtractorHelper:
    """参数提取辅助类 - 不依赖WebEngine"""

    @staticmethod
    def extract_from_text(text):
        """从文本中提取参数"""
        extracted_params = {}

        try:
            # 1. 提取API域名
            url_patterns = [
                r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'base_url["\']?\s*[:=]\s*["\']?(https?://[^"\'>\s]+)',
                r'domain["\']?\s*[:=]\s*["\']?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]

            for pattern in url_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0].startswith('http') else f"https://{match[0]}"
                    elif not match.startswith('http'):
                        match = f"https://{match}"

                    if 'base_url' not in extracted_params:
                        extracted_params['base_url'] = match
                        break

            # 2. 提取影院ID
            cinema_patterns = [
                r'cinemaid["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]+)',
                r'cinema_id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]+)',
                r'cinemaId["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]+)',
                r'cid["\']?\s*[:=]\s*["\']?([a-zA-Z0-9]+)'
            ]

            for pattern in cinema_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    cinema_id = match.group(1)
                    if len(cinema_id) >= 3:
                        extracted_params['cinema_id'] = cinema_id
                        break

            # 3. 提取认证信息
            auth_patterns = {
                'openid': [
                    r'openid["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                    r'"openid"\s*:\s*"([^"]+)"'
                ],
                'token': [
                    r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                    r'"token"\s*:\s*"([^"]+)"',
                    r'access_token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})'
                ],
                'userid': [
                    r'userid["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)',
                    r'"userid"\s*:\s*"([^"]+)"',
                    r'user_id["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]+)'
                ]
            }

            for param_name, patterns in auth_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        value = match.group(1)
                        if len(value) > 5:  # 过滤太短的值
                            extracted_params[param_name] = value
                            break
                if param_name in extracted_params:
                    break

        except Exception as e:
            print(f"[参数提取] 文本分析错误: {e}")

        return extracted_params

    @staticmethod
    def validate_params(params):
        """验证参数有效性"""
        required = ['base_url', 'cinema_id']
        missing = [p for p in required if p not in params or not params[p]]
        return len(missing) == 0, missing


class AutoParameterExtractor(QDialog):
    """完全自动化参数采集器"""

    parameter_extracted = pyqtSignal(str, str)  # key, value

    def __init__(self, parent=None):
        super().__init__(parent)
        self.extracted_params = {}
        self.auto_mode = True  # 默认使用自动模式
        self.collection_completed = None  # 🆕 采集完成回调函数

        self.setWindowTitle("🎬 自动参数采集器")
        self.setMinimumSize(1000, 700)
        self.setModal(True)

        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # 顶部说明
        self.create_instruction_area(layout)

        # 创建Tab界面
        self.tab_widget = QTabWidget()

        # curl解析Tab
        self.curl_tab = QWidget()
        self.setup_curl_tab()
        self.tab_widget.addTab(self.curl_tab, "📋 curl解析")

        # 手动输入Tab
        self.manual_tab = QWidget()
        self.setup_manual_tab()
        self.tab_widget.addTab(self.manual_tab, "✏️ 手动输入")

        layout.addWidget(self.tab_widget)

        # 底部控制区域
        self.create_control_area(layout)

        # 连接Tab切换信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
    
    def create_instruction_area(self, layout):
        """创建说明区域"""
        instruction_frame = QFrame()
        instruction_frame.setFrameStyle(QFrame.StyledPanel)
        instruction_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        instruction_layout = QVBoxLayout(instruction_frame)

        title = QLabel("🎬 curl命令参数采集器")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")

        steps_text = """🚀 最简单的参数采集方案：

📋 curl命令解析（推荐）：
1. 使用浏览器开发者工具或抓包工具获取网络请求
2. 右键复制为curl命令
3. 粘贴到"curl解析"Tab页面
4. 系统自动提取所有API参数
5. 点击"确认采集"保存

✏️ 手动输入模式：
1. 点击"手动输入"Tab页面
2. 粘贴抓包数据或直接输入参数
3. 点击"分析参数"按钮提取参数

⚡ 超简单操作：只需复制粘贴curl命令，一键提取所有参数！
✅ 高准确率：直接从真实API请求中提取，100%准确！"""

        steps = QLabel(steps_text)
        steps.setStyleSheet("color: #666; line-height: 1.5; font-size: 12px;")
        steps.setWordWrap(True)

        instruction_layout.addWidget(title)
        instruction_layout.addWidget(steps)
        layout.addWidget(instruction_frame)

    def setup_curl_tab(self):
        """设置curl解析Tab"""
        layout = QVBoxLayout(self.curl_tab)

        # curl输入区域
        curl_label = QLabel("📋 粘贴curl命令:")
        curl_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")

        self.curl_input = QTextEdit()
        self.curl_input.setMinimumHeight(200)
        self.curl_input.setPlaceholderText("""请粘贴完整的curl命令，例如：

curl -X GET 'https://www.heibaiyingye.cn/MiniTicket/index.php/MiniCommonSystem/getCinemaSettings?sortType=1&groupid&cinemaid=35fec8259e74&cardno&userid=15155712316&openid=oAOCp7VbeeoqMM4yC8e2i3G3lxI8&CVersion=3.9.12&OS=Windows&token=3a30b9e980892714&source=2' -H 'User-Agent: Mozilla/5.0...' -H 'Accept: application/json'

获取curl命令的方法：
1. 浏览器开发者工具 → Network → 右键请求 → Copy as cURL
2. Fiddler → 右键请求 → Copy → Copy as cURL
3. Charles → 右键请求 → Copy cURL Request

系统会自动从curl命令中提取：
• API域名 (base_url)
• 影院ID (cinema_id)
• 用户认证信息 (openid, token, user_id)
• 其他必要参数""")

        # 解析结果显示区域
        result_label = QLabel("🔍 解析结果:")
        result_label.setStyleSheet("font-weight: bold; margin-top: 10px; margin-bottom: 5px;")

        self.curl_result = QTextEdit()
        self.curl_result.setMaximumHeight(150)
        self.curl_result.setPlaceholderText("curl命令解析结果将显示在这里...")
        self.curl_result.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 3px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)

        # 组装布局
        layout.addWidget(curl_label)
        layout.addWidget(self.curl_input)
        layout.addWidget(result_label)
        layout.addWidget(self.curl_result)


    def setup_manual_tab(self):
        """设置手动输入Tab"""
        layout = QVBoxLayout(self.manual_tab)

        # 文本输入区域
        text_label = QLabel("📝 粘贴抓包数据或网络请求内容:")
        text_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")

        self.text_input = QTextEdit()
        self.text_input.setMinimumHeight(200)
        self.text_input.setPlaceholderText("""请粘贴包含影院API参数的文本内容，例如：

1. 网络请求URL：
   https://api.example.com/cinema/12345?openid=xxx&token=yyy

2. JSON响应数据：
   {"cinemaid": "12345", "base_url": "https://api.example.com", "openid": "xxx"}

3. 抓包工具的请求详情...

支持多种格式，工具会自动识别和提取参数。""")

        # 手动输入区域
        manual_label = QLabel("✏️ 或手动输入参数:")
        manual_label.setStyleSheet("font-weight: bold; margin-top: 10px; margin-bottom: 5px;")

        manual_layout = QHBoxLayout()

        # API域名输入
        api_layout = QVBoxLayout()
        api_layout.addWidget(QLabel("API域名 (必填):"))
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("https://api.example.com")
        api_layout.addWidget(self.api_input)

        # 影院ID输入
        cinema_layout = QVBoxLayout()
        cinema_layout.addWidget(QLabel("影院ID (必填):"))
        self.cinema_input = QLineEdit()
        self.cinema_input.setPlaceholderText("12345")
        cinema_layout.addWidget(self.cinema_input)

        manual_layout.addLayout(api_layout)
        manual_layout.addLayout(cinema_layout)

        # 认证信息输入
        auth_layout = QHBoxLayout()

        openid_layout = QVBoxLayout()
        openid_layout.addWidget(QLabel("OpenID (可选):"))
        self.openid_input = QLineEdit()
        self.openid_input.setPlaceholderText("用户OpenID")
        openid_layout.addWidget(self.openid_input)

        token_layout = QVBoxLayout()
        token_layout.addWidget(QLabel("Token (可选):"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("访问Token")
        token_layout.addWidget(self.token_input)

        auth_layout.addLayout(openid_layout)
        auth_layout.addLayout(token_layout)

        # 组装布局
        layout.addWidget(text_label)
        layout.addWidget(self.text_input)
        layout.addWidget(manual_label)
        layout.addLayout(manual_layout)
        layout.addLayout(auth_layout)

    def on_tab_changed(self, index):
        """Tab切换事件处理"""
        tab_text = self.tab_widget.tabText(index)
        self.auto_mode = (tab_text == "📋 curl解析")

        if self.auto_mode:
            print("[参数采集] 切换到curl解析模式")
        else:
            print("[参数采集] 切换到手动输入模式")

        # 更新按钮可见性
        self.update_button_visibility()

    def on_parameter_extracted(self, key: str, value: str):
        """处理提取到的参数"""
        if key and value:
            self.extracted_params[key] = value

    def on_status_changed(self, status: str):
        """处理状态变化"""
        print(f"[参数采集] 状态更新: {status}")



    def create_input_area(self, layout):
        """创建输入区域"""
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.StyledPanel)
        input_layout = QVBoxLayout(input_frame)

        # 文本输入区域
        text_label = QLabel("📝 粘贴抓包数据或网络请求内容:")
        text_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")

        self.text_input = QTextEdit()
        self.text_input.setMinimumHeight(200)
        self.text_input.setPlaceholderText("""请粘贴包含影院API参数的文本内容，例如：

1. 网络请求URL：
   https://api.example.com/cinema/12345?openid=xxx&token=yyy

2. JSON响应数据：
   {"cinemaid": "12345", "base_url": "https://api.example.com", "openid": "xxx"}

3. 抓包工具的请求详情...

支持多种格式，工具会自动识别和提取参数。""")

        # 手动输入区域
        manual_label = QLabel("✏️ 或手动输入参数:")
        manual_label.setStyleSheet("font-weight: bold; margin-top: 10px; margin-bottom: 5px;")

        manual_layout = QHBoxLayout()

        # API域名输入
        api_layout = QVBoxLayout()
        api_layout.addWidget(QLabel("API域名 (必填):"))
        self.api_input = QLineEdit()
        self.api_input.setPlaceholderText("https://api.example.com")
        api_layout.addWidget(self.api_input)

        # 影院ID输入
        cinema_layout = QVBoxLayout()
        cinema_layout.addWidget(QLabel("影院ID (必填):"))
        self.cinema_input = QLineEdit()
        self.cinema_input.setPlaceholderText("12345")
        cinema_layout.addWidget(self.cinema_input)

        manual_layout.addLayout(api_layout)
        manual_layout.addLayout(cinema_layout)

        # 认证信息输入
        auth_layout = QHBoxLayout()

        openid_layout = QVBoxLayout()
        openid_layout.addWidget(QLabel("OpenID (可选):"))
        self.openid_input = QLineEdit()
        self.openid_input.setPlaceholderText("用户OpenID")
        openid_layout.addWidget(self.openid_input)

        token_layout = QVBoxLayout()
        token_layout.addWidget(QLabel("Token (可选):"))
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("访问Token")
        token_layout.addWidget(self.token_input)

        auth_layout.addLayout(openid_layout)
        auth_layout.addLayout(token_layout)

        # 组装布局
        input_layout.addWidget(text_label)
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(manual_label)
        input_layout.addLayout(manual_layout)
        input_layout.addLayout(auth_layout)

        layout.addWidget(input_frame)
    
    def create_control_area(self, layout):
        """创建控制区域"""
        control_frame = QFrame()
        control_layout = QVBoxLayout(control_frame)

        # 参数显示区域
        params_label = QLabel("📋 提取结果:")
        params_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")

        self.params_display = QTextEdit()
        self.params_display.setMaximumHeight(100)
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

        # 按钮区域
        button_layout = QHBoxLayout()

        self.analyze_button = QPushButton("🔍 分析参数")
        self.analyze_button.clicked.connect(self.analyze_parameters)
        self.analyze_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        self.clear_button = QPushButton("🗑️ 清空")
        self.clear_button.clicked.connect(self.clear_inputs)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
        """)

        self.ok_button = QPushButton("✅ 确认采集")
        self.ok_button.clicked.connect(self.execute_curl_collection)
        self.ok_button.setEnabled(False)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)

        self.cancel_button = QPushButton("❌ 取消")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)

        # 添加示例数据按钮
        self.example_button = QPushButton("📝 填充示例")
        self.example_button.clicked.connect(self.fill_example_data)
        self.example_button.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)

        # 添加获取帮助按钮
        self.help_button = QPushButton("📖 获取帮助")
        self.help_button.clicked.connect(self.show_help)
        self.help_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)

        # 添加curl解析按钮
        self.parse_curl_button = QPushButton("🔍 解析curl命令")
        self.parse_curl_button.clicked.connect(self.parse_curl_command)
        self.parse_curl_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)

        # 添加所有按钮到布局
        button_layout.addWidget(self.parse_curl_button)
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(self.example_button)
        button_layout.addWidget(self.help_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        # 初始化按钮可见性
        self.update_button_visibility()

        # 状态标签
        self.status_label = QLabel("请输入参数或粘贴抓包数据")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; margin-top: 5px;")

        # 组装布局
        control_layout.addWidget(params_label)
        control_layout.addWidget(self.params_display)
        control_layout.addLayout(button_layout)
        control_layout.addWidget(self.status_label)

        layout.addWidget(control_frame)

    def analyze_parameters(self):
        """分析参数"""
        try:
            self.status_label.setText("🔍 正在分析参数...")
            self.extracted_params.clear()

            # 从文本输入中提取参数
            text_content = self.text_input.toPlainText().strip()
            if text_content:
                extracted = ParameterExtractorHelper.extract_from_text(text_content)
                self.extracted_params.update(extracted)

            # 从手动输入中获取参数
            manual_params = self.get_manual_params()
            self.extracted_params.update(manual_params)

            # 更新显示
            self.update_params_display()

            # 验证参数
            is_valid, missing = ParameterExtractorHelper.validate_params(self.extracted_params)

            if is_valid:
                self.status_label.setText("✅ 参数分析完成，可以确认采集")
                self.ok_button.setEnabled(True)
            else:
                self.status_label.setText(f"⚠️ 缺少必要参数: {', '.join(missing)}")
                self.ok_button.setEnabled(False)

        except Exception as e:
            self.status_label.setText(f"❌ 分析失败: {str(e)}")
            print(f"[参数采集] 分析参数错误: {e}")

    def get_manual_params(self):
        """获取手动输入的参数"""
        params = {}

        # API域名
        api_url = self.api_input.text().strip()
        if api_url:
            if not api_url.startswith(('http://', 'https://')):
                api_url = 'https://' + api_url
            params['base_url'] = api_url

        # 影院ID
        cinema_id = self.cinema_input.text().strip()
        if cinema_id:
            params['cinema_id'] = cinema_id

        # OpenID
        openid = self.openid_input.text().strip()
        if openid:
            params['openid'] = openid

        # Token
        token = self.token_input.text().strip()
        if token:
            params['token'] = token

        return params

    def update_params_display(self):
        """更新参数显示"""
        if not self.extracted_params:
            self.params_display.clear()
            self.params_display.setPlaceholderText("提取到的参数将显示在这里...")
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

    def clear_inputs(self):
        """清空输入"""
        self.text_input.clear()
        self.api_input.clear()
        self.cinema_input.clear()
        self.openid_input.clear()
        self.token_input.clear()
        self.params_display.clear()
        self.extracted_params.clear()

        self.status_label.setText("请输入参数或粘贴抓包数据")
        self.ok_button.setEnabled(False)

    def fill_example_data(self):
        """填充示例数据"""
        example_text = """示例抓包数据：

1. 网络请求URL示例：
https://miniticket.example.com/api/cinema/12345?openid=ox1234567890abcdef1234567890abcdef&token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9

2. JSON响应数据示例：
{
    "resultCode": "0",
    "resultData": {
        "cinemaid": "12345",
        "base_url": "https://miniticket.example.com",
        "openid": "ox1234567890abcdef1234567890abcdef",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc123"
    }
}

3. 请求头示例：
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
X-Cinema-ID: 12345
X-OpenID: ox1234567890abcdef1234567890abcdef

请将您的实际抓包数据替换上述示例内容。"""

        self.text_input.setPlainText(example_text)
        self.status_label.setText("已填充示例数据，请替换为您的实际数据后点击'分析参数'")

    def show_help(self):
        """显示帮助信息"""
        help_text = """🔧 详细的抓包教程和技术支持

📱 微信小程序抓包方法：

方法一：使用Fiddler（推荐）
1. 下载并安装Fiddler Classic
2. 启用HTTPS解密：Tools → Options → HTTPS → 勾选"Decrypt HTTPS traffic"
3. 设置手机代理：手机WiFi设置中配置代理为电脑IP:8888
4. 在手机上访问影院小程序，Fiddler会显示所有网络请求
5. 找到包含cinema、movie、ticket等关键词的API请求
6. 复制请求URL和响应内容，粘贴到本工具中

方法二：使用Charles
1. 下载并安装Charles
2. 启用SSL代理：Proxy → SSL Proxying Settings
3. 设置手机代理连接Charles
4. 操作小程序，查看网络请求
5. 导出相关API数据

方法三：浏览器开发者工具
1. 在电脑浏览器中打开微信开发者工具
2. 加载小程序项目
3. 打开Network面板
4. 操作小程序，查看网络请求

🔍 需要提取的关键信息：
- API域名（base_url）：如 https://api.example.com
- 影院ID（cinema_id）：如 12345
- 用户认证信息（openid、token）：用于API访问

📞 技术支持：
如果您在抓包过程中遇到困难，可以：
1. 查看在线教程和视频指导
2. 联系技术人员远程协助
3. 提供影院小程序信息，由技术人员代为获取参数

💡 提示：
- 不同影院的小程序API结构可能不同
- 某些小程序可能有反抓包机制
- 建议在WiFi环境下进行抓包操作"""

        # 显示帮助对话框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("📖 抓包教程和技术支持")
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)

        # 添加打开在线教程按钮
        online_help_button = msg_box.addButton("🌐 打开在线教程", QMessageBox.ActionRole)
        online_help_button.clicked.connect(self.open_online_help)

        msg_box.exec_()

    def open_online_help(self):
        """打开在线教程"""
        try:
            # 这里可以替换为实际的在线教程URL
            tutorial_url = "https://www.bilibili.com/video/BV1234567890"  # 示例URL
            webbrowser.open(tutorial_url)
            print(f"[帮助] 已打开在线教程: {tutorial_url}")
        except Exception as e:
            print(f"[帮助] 打开在线教程失败: {e}")
            QMessageBox.warning(self, "提示", "无法打开在线教程，请手动搜索'微信小程序抓包教程'")

    def update_button_visibility(self):
        """根据当前模式更新按钮可见性"""
        if self.auto_mode:
            # curl解析模式：显示curl解析按钮，隐藏手动按钮
            self.parse_curl_button.setVisible(True)
            self.analyze_button.setVisible(False)
            self.example_button.setVisible(False)
        else:
            # 手动模式：显示手动按钮，隐藏curl解析按钮
            self.parse_curl_button.setVisible(False)
            self.analyze_button.setVisible(True)
            self.example_button.setVisible(True)

    def parse_curl_command(self):
        """解析curl命令 - 重构为只解析和验证参数"""
        try:
            # 导入curl解析器
            from ui.components.curl_parser import CurlParser

            # 获取curl命令
            curl_command = self.curl_input.toPlainText().strip()

            if not curl_command:
                self.curl_result.setText("⚠️ 请先粘贴curl命令")
                self.status_label.setText("请粘贴curl命令后再点击解析")
                return

            # 解析curl命令
            params, report = CurlParser.analyze_curl_example(curl_command)

            # 显示解析结果
            self.curl_result.clear()
            self.curl_result.append(report)

            if params:
                # 更新提取的参数
                self.extracted_params.update(params)

                # 🆕 更新参数显示
                self.update_params_display()

                # 🆕 分离影院参数和账号参数
                cinema_params = self._extract_cinema_params(params)
                account_params = self._extract_account_params(params)

                # 验证参数完整性
                cinema_valid = self._validate_cinema_params(cinema_params)
                account_valid = self._validate_account_params(account_params)

                if cinema_valid and account_valid:
                    self.status_label.setText("✅ curl命令解析成功，影院和账号参数完整，可以确认采集")
                    self.ok_button.setEnabled(True)
                elif cinema_valid:
                    self.status_label.setText("✅ 影院参数完整，账号参数不完整，可以只添加影院")
                    self.ok_button.setEnabled(True)
                else:
                    missing_cinema = self._get_missing_cinema_params(cinema_params)
                    self.status_label.setText(f"❌ 缺少必要的影院参数: {', '.join(missing_cinema)}")
                    self.ok_button.setEnabled(False)


            else:
                self.status_label.setText("❌ curl命令解析失败，请检查命令格式")
                self.ok_button.setEnabled(False)

        except ImportError:
            self.curl_result.setText("❌ curl解析器不可用")
            self.status_label.setText("curl解析器组件加载失败")

        except Exception as e:
            error_msg = f"❌ curl解析错误: {str(e)}"
            self.curl_result.setText(error_msg)
            self.status_label.setText("curl解析过程中发生错误")
            print(f"[curl解析] 错误: {e}")

    def get_auto_params(self):
        """获取自动监听的参数"""
        try:
            if hasattr(self, 'auto_browser') and AUTO_BROWSER_AVAILABLE:
                # 从自动浏览器获取参数
                auto_params = self.auto_browser.get_extracted_params()

                if auto_params:
                    # 更新提取的参数
                    self.extracted_params.update(auto_params)

                    # 更新显示
                    self.update_params_display()

                    # 验证参数
                    is_valid, missing = ParameterExtractorHelper.validate_params(self.extracted_params)

                    if is_valid:
                        self.status_label.setText("✅ 自动监听参数获取成功，可以确认采集")
                        self.ok_button.setEnabled(True)
                    else:
                        self.status_label.setText(f"⚠️ 参数不完整，缺少: {', '.join(missing)}")
                        self.ok_button.setEnabled(False)


                else:
                    self.status_label.setText("⚠️ 自动监听未提取到任何参数")
                    self.ok_button.setEnabled(False)

            else:
                self.status_label.setText("❌ 自动浏览器不可用")

        except Exception as e:
            print(f"[参数采集] 获取自动参数失败: {e}")
            self.status_label.setText(f"❌ 获取自动参数失败: {str(e)}")

    def update_params_display(self):
        """更新参数显示"""
        if not self.extracted_params:
            if hasattr(self, 'params_display'):
                self.params_display.clear()
                self.params_display.setPlaceholderText("提取到的参数将显示在这里...")
            return

        display_text = "🎉 提取到的参数:\n\n"

        for key, value in self.extracted_params.items():
            # 🔧 临时显示完整参数用于调试
            # 对敏感信息进行部分隐藏
            if key in ['token', 'openid'] and len(value) > 12:
                display_value = value[:8] + "..." + value[-4:] + f" (长度:{len(value)})"
            else:
                display_value = value

            display_text += f"✅ {key}: {display_value}\n"

        if hasattr(self, 'params_display'):
            self.params_display.clear()
            self.params_display.append(display_text)

    def _extract_cinema_params(self, params: dict) -> dict:
        """提取影院相关参数"""
        cinema_params = {}

        # 必要的影院参数
        if 'base_url' in params:
            cinema_params['base_url'] = params['base_url']
        if 'cinema_id' in params:
            cinema_params['cinema_id'] = params['cinema_id']

        return cinema_params

    def _extract_account_params(self, params: dict) -> dict:
        """提取账号相关参数"""
        account_params = {}

        # 账号认证参数
        if 'user_id' in params:
            account_params['user_id'] = params['user_id']
        if 'openid' in params:
            account_params['openid'] = params['openid']
        if 'token' in params:
            account_params['token'] = params['token']
        if 'cinema_id' in params:
            account_params['cinema_id'] = params['cinema_id']

        return account_params

    def _validate_cinema_params(self, cinema_params: dict) -> bool:
        """验证影院参数是否完整"""
        required = ['base_url', 'cinema_id']
        return all(param in cinema_params and cinema_params[param] for param in required)

    def _validate_account_params(self, account_params: dict) -> bool:
        """验证账号参数是否完整"""
        required = ['user_id', 'openid', 'token', 'cinema_id']
        return all(param in account_params and account_params[param] for param in required)

    def _get_missing_cinema_params(self, cinema_params: dict) -> list:
        """获取缺失的影院参数"""
        required = ['base_url', 'cinema_id']
        return [param for param in required if param not in cinema_params or not cinema_params[param]]

    def execute_curl_collection(self):
        """执行curl采集的两步式流程"""
        try:
            if not self.extracted_params:
                QMessageBox.warning(self, "参数错误", "请先解析curl命令提取参数")
                return

            # 分离参数
            cinema_params = self._extract_cinema_params(self.extracted_params)
            account_params = self._extract_account_params(self.extracted_params)

            # 验证参数
            cinema_valid = self._validate_cinema_params(cinema_params)
            account_valid = self._validate_account_params(account_params)

            if not cinema_valid:
                missing = self._get_missing_cinema_params(cinema_params)
                QMessageBox.warning(self, "参数不完整", f"缺少必要的影院参数: {', '.join(missing)}")
                return

            # 更新状态
            self.status_label.setText("🚀 开始执行curl采集流程...")
            self.ok_button.setEnabled(False)

            # 步骤1：添加影院
            cinema_success = self._execute_cinema_addition(cinema_params)

            if cinema_success and account_valid:
                # 步骤2：添加账号
                account_success = self._execute_account_addition(account_params)

                if account_success:
                    self.status_label.setText("🎉 curl采集完成：影院和账号都已成功添加")
                    success_message = "✅ 影院已添加\n✅ 账号已添加\n\n所有数据已保存并刷新界面。"

                    # 🆕 调用回调函数
                    if self.collection_completed:
                        self.collection_completed(True, success_message)
                    else:
                        QMessageBox.information(self, "采集成功", f"curl采集完成！\n\n{success_message}")
                else:
                    self.status_label.setText("⚠️ 影院添加成功，账号添加失败")
                    partial_message = "影院添加成功，但账号添加失败。\n\n请手动在账号Tab页面添加账号。"

                    # 🆕 调用回调函数
                    if self.collection_completed:
                        self.collection_completed(True, partial_message)  # 部分成功也算成功
                    else:
                        QMessageBox.warning(self, "部分成功", partial_message)
            elif cinema_success:
                self.status_label.setText("✅ 影院添加成功（无账号参数）")
                cinema_only_message = "影院添加成功！\n\n由于curl命令中缺少账号参数，\n请手动在账号Tab页面添加账号。"

                # 🆕 调用回调函数
                if self.collection_completed:
                    self.collection_completed(True, cinema_only_message)
                else:
                    QMessageBox.information(self, "影院添加成功", cinema_only_message)
            else:
                self.status_label.setText("❌ 影院添加失败")
                error_message = "影院添加失败，请检查curl命令格式或网络连接。"

                # 🆕 调用回调函数
                if self.collection_completed:
                    self.collection_completed(False, error_message)
                return

            # 成功后关闭对话框
            self.accept()

        except Exception as e:
            print(f"[curl采集] 执行错误: {e}")
            self.status_label.setText(f"❌ 采集失败: {str(e)}")
            error_message = f"curl采集过程中发生错误：\n{str(e)}"

            # 🆕 调用回调函数
            if self.collection_completed:
                self.collection_completed(False, error_message)
            else:
                QMessageBox.critical(self, "采集失败", error_message)
            self.ok_button.setEnabled(True)

    def _execute_cinema_addition(self, cinema_params: dict) -> bool:
        """执行影院添加步骤"""
        try:
            self.status_label.setText("🏢 正在添加影院...")

            base_url = cinema_params['base_url']
            cinema_id = cinema_params['cinema_id']


            # 🆕 智能重复检测
            if self._check_cinema_exists(cinema_id):
                print(f"[curl采集] 影院 {cinema_id} 已存在，跳过添加")
                self.status_label.setText("ℹ️ 影院已存在，跳过添加步骤")
                return True

            # 🆕 调用现有的影院添加逻辑
            from services.cinema_info_api import get_cinema_info, format_cinema_data
            from services.cinema_manager import cinema_manager

            # 🔧 增强调试信息
            print(f"  - base_url: '{base_url}' (类型: {type(base_url)}, 长度: {len(base_url)})")
            print(f"  - cinema_id: '{cinema_id}' (类型: {type(cinema_id)}, 长度: {len(cinema_id)})")

            # 🔧 检查base_url格式
            if base_url.startswith('https://'):
                clean_base_url = base_url.replace('https://', '')
            elif base_url.startswith('http://'):
                clean_base_url = base_url.replace('http://', '')
            else:
                clean_base_url = base_url

            # API验证和信息获取

            cinema_info = get_cinema_info(clean_base_url, cinema_id)

            if cinema_info:
                pass
            else:
                print(f"[curl采集] ❌ API响应为空或失败")

            if not cinema_info:
                print(f"[curl采集] 影院验证失败: {clean_base_url}, {cinema_id}")
                self.status_label.setText("❌ 影院API验证失败")
                return False

            # 格式化影院数据
            cinema_data = format_cinema_data(cinema_info, clean_base_url, cinema_id)

            # 保存影院数据
            cinemas = cinema_manager.load_cinema_list()
            cinemas.append(cinema_data)

            if cinema_manager.save_cinema_list(cinemas):
                print(f"[curl采集] 影院添加成功: {cinema_data.get('cinemaShortName')}")
                self.status_label.setText(f"✅ 影院添加成功: {cinema_data.get('cinemaShortName')}")

                # 🆕 触发界面刷新（复用现有逻辑）
                self._trigger_cinema_list_refresh()

                return True
            else:
                print(f"[curl采集] 影院保存失败")
                self.status_label.setText("❌ 影院保存失败")
                return False

        except Exception as e:
            print(f"[curl采集] 影院添加错误: {e}")
            self.status_label.setText(f"❌ 影院添加错误: {str(e)}")
            return False

    def _execute_account_addition(self, account_params: dict) -> bool:
        """执行账号添加步骤"""
        try:
            self.status_label.setText("👤 正在添加账号...")

            user_id = account_params['user_id']
            cinema_id = account_params['cinema_id']
            openid = account_params['openid']
            token = account_params['token']


            # 🆕 智能重复检测
            if self._check_account_exists(user_id, cinema_id):
                reply = QMessageBox.question(
                    self,
                    "账号已存在",
                    f"账号 {user_id} 在影院 {cinema_id} 中已存在。\n\n是否更新账号信息？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )

                if reply != QMessageBox.Yes:
                    print(f"[curl采集] 用户选择不更新账号")
                    self.status_label.setText("ℹ️ 账号已存在，用户选择不更新")
                    return True

            # 🆕 构建标准账号数据结构
            account_data = {
                'userid': user_id,
                'cinemaid': cinema_id,
                'openid': openid,
                'token': token,
                'balance': 0,  # 默认余额
                'score': 0,    # 默认积分
                'is_main': False,  # 默认非主账号
                'auto_added': True,  # 标记为自动添加
                'add_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source': 'curl_collection'  # 标记来源
            }

            # 🆕 保存账号数据（复用现有逻辑）
            if self._save_account_data(account_data):
                print(f"[curl采集] 账号添加成功: {user_id}")
                self.status_label.setText(f"✅ 账号添加成功: {user_id}")
                return True
            else:
                print(f"[curl采集] 账号保存失败")
                self.status_label.setText("❌ 账号保存失败")
                return False

        except Exception as e:
            print(f"[curl采集] 账号添加错误: {e}")
            self.status_label.setText(f"❌ 账号添加错误: {str(e)}")
            return False

    def _check_cinema_exists(self, cinema_id: str) -> bool:
        """检查影院是否已存在"""
        try:
            from services.cinema_manager import cinema_manager
            cinemas = cinema_manager.load_cinema_list()

            for cinema in cinemas:
                if cinema.get('cinemaid') == cinema_id:
                    return True
            return False

        except Exception as e:
            print(f"[curl采集] 检查影院存在性错误: {e}")
            return False

    def _check_account_exists(self, user_id: str, cinema_id: str) -> bool:
        """检查账号是否已存在"""
        try:
            import json
            import os

            accounts_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'accounts.json')

            if not os.path.exists(accounts_file):
                return False

            with open(accounts_file, "r", encoding="utf-8") as f:
                accounts = json.load(f)

            for account in accounts:
                if (account.get('userid') == user_id and
                    account.get('cinemaid') == cinema_id):
                    return True
            return False

        except Exception as e:
            print(f"[curl采集] 检查账号存在性错误: {e}")
            return False

    def _trigger_cinema_list_refresh(self):
        """触发影院列表刷新"""
        try:
            from utils.signals import event_bus
            from services.cinema_manager import cinema_manager

            # 获取最新的影院列表并发送事件
            updated_cinemas = cinema_manager.load_cinema_list()
            event_bus.cinema_list_updated.emit(updated_cinemas)

            print(f"[curl采集] 已触发影院列表刷新事件")

        except Exception as e:
            print(f"[curl采集] 触发刷新事件错误: {e}")

    def _save_account_data(self, account_data: dict) -> bool:
        """保存账号数据"""
        try:
            import json
            import os
            from datetime import datetime

            accounts_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'accounts.json')

            # 确保目录存在
            os.makedirs(os.path.dirname(accounts_file), exist_ok=True)

            # 加载现有账号
            accounts = []
            if os.path.exists(accounts_file):
                with open(accounts_file, "r", encoding="utf-8") as f:
                    accounts = json.load(f)

            # 检查是否需要更新现有账号
            user_id = account_data['userid']
            cinema_id = account_data['cinemaid']

            updated = False
            for i, account in enumerate(accounts):
                if (account.get('userid') == user_id and
                    account.get('cinemaid') == cinema_id):
                    # 更新现有账号
                    accounts[i] = account_data
                    updated = True
                    print(f"[curl采集] 更新现有账号: {user_id}")
                    break

            if not updated:
                # 添加新账号
                accounts.append(account_data)
                print(f"[curl采集] 添加新账号: {user_id}")

            # 保存账号数据
            with open(accounts_file, "w", encoding="utf-8") as f:
                json.dump(accounts, f, ensure_ascii=False, indent=2)

            # 🆕 触发账号列表刷新
            self._trigger_account_list_refresh()

            return True

        except Exception as e:
            print(f"[curl采集] 保存账号数据错误: {e}")
            return False

    def _trigger_account_list_refresh(self):
        """触发账号列表刷新"""
        try:
            from utils.signals import event_bus

            # 🆕 发送账号列表更新事件 - 修复账号组件不刷新的问题
            event_bus.account_list_updated.emit([])  # 发送空列表，让组件自己重新加载

        except Exception as e:
            print(f"[curl采集] 触发账号刷新事件错误: {e}")

    def get_extracted_params(self):
        """获取提取的参数"""
        return self.extracted_params.copy()
