#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安装浏览器依赖组件
提供多种浏览器引擎的备选方案
"""

import subprocess
import sys
import os

def install_package(package_name, description=""):
    """安装Python包"""
    try:
        print(f"正在安装 {package_name}...")
        if description:
            print(f"  用途: {description}")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", package_name
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print(f"✅ {package_name} 安装成功")
            return True
        else:
            print(f"❌ {package_name} 安装失败: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {package_name} 安装异常: {e}")
        return False

def check_webengine():
    """检查QWebEngine是否可用"""
    try:
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        print("✅ QWebEngine 已可用")
        return True
    except ImportError:
        print("❌ QWebEngine 不可用")
        return False

def install_browser_engines():
    """安装浏览器引擎依赖"""
    print("=== 浏览器引擎依赖安装 ===\n")
    
    # 方案1: 尝试安装PyQtWebEngine
    print("方案1: 安装 PyQtWebEngine")
    if install_package("PyQtWebEngine", "Qt WebEngine浏览器组件"):
        if check_webengine():
            print("🎉 PyQtWebEngine 安装成功并可用！")
            return "webengine"
    
    # 方案2: 安装selenium + webdriver
    print("\n方案2: 安装 Selenium WebDriver")
    selenium_success = install_package("selenium", "Web自动化框架")
    webdriver_success = install_package("webdriver-manager", "WebDriver管理器")
    
    if selenium_success and webdriver_success:
        print("🎉 Selenium 安装成功！")
        return "selenium"
    
    # 方案3: 安装requests + beautifulsoup (降级方案)
    print("\n方案3: 安装网络请求组件")
    requests_success = install_package("requests", "HTTP请求库")
    bs4_success = install_package("beautifulsoup4", "HTML解析库")
    
    if requests_success and bs4_success:
        print("🎉 网络请求组件安装成功！")
        return "requests"
    
    print("❌ 所有浏览器引擎安装失败")
    return None

def download_chromedriver():
    """下载ChromeDriver"""
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("正在下载 ChromeDriver...")
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver 下载成功: {driver_path}")
        return driver_path
    except Exception as e:
        print(f"❌ ChromeDriver 下载失败: {e}")
        return None

def main():
    """主函数"""
    print("🚀 开始安装浏览器依赖组件...\n")
    
    # 安装浏览器引擎
    engine_type = install_browser_engines()
    
    if engine_type == "selenium":
        # 如果使用Selenium，下载ChromeDriver
        download_chromedriver()
    
    print(f"\n=== 安装完成 ===")
    print(f"推荐的浏览器引擎: {engine_type}")
    
    # 生成配置文件
    config = {
        "browser_engine": engine_type,
        "webengine_available": engine_type == "webengine",
        "selenium_available": engine_type == "selenium",
        "requests_available": engine_type == "requests"
    }
    
    import json
    with open("browser_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    print(f"配置文件已保存: browser_config.json")

if __name__ == "__main__":
    main()
