#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试参数提取器功能
"""

import sys
from PyQt5.QtWidgets import QApplication
from ui.dialogs.auto_parameter_extractor import AutoParameterExtractor, ParameterExtractorHelper

def test_parameter_extraction():
    """测试参数提取功能"""
    
    # 测试数据
    test_data = """
    {
        "base_url": "https://miniticket.example.com",
        "cinemaid": "12345",
        "openid": "ox1234567890abcdef1234567890abcdef",
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    }
    
    URL: https://miniticket.example.com/api/cinema/12345?openid=ox1234567890abcdef1234567890abcdef&token=abc123
    """
    
    print("测试参数提取功能...")
    
    # 测试文本提取
    extracted = ParameterExtractorHelper.extract_from_text(test_data)
    print(f"提取结果: {extracted}")
    
    # 测试参数验证
    is_valid, missing = ParameterExtractorHelper.validate_params(extracted)
    print(f"参数有效性: {is_valid}, 缺少参数: {missing}")

def test_dialog():
    """测试对话框"""
    app = QApplication(sys.argv)
    
    dialog = AutoParameterExtractor()
    
    # 预填充一些测试数据
    test_text = """
    API请求示例:
    https://miniticket.example.com/api/cinema/12345?openid=ox1234567890abcdef&token=abc123def456
    
    JSON数据:
    {"cinemaid": "12345", "base_url": "https://miniticket.example.com"}
    """
    
    dialog.text_input.setPlainText(test_text)
    
    result = dialog.exec_()
    
    if result == dialog.Accepted:
        params = dialog.get_extracted_params()
        print(f"用户确认的参数: {params}")
    else:
        print("用户取消了操作")

if __name__ == "__main__":
    print("=== 测试参数提取功能 ===")
    test_parameter_extraction()
    
    print("\n=== 测试对话框 ===")
    test_dialog()
