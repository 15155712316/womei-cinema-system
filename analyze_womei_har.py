#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析沃美HAR文件，提取API调用链路
"""

import json
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import pandas as pd

def analyze_har_file(har_file_path):
    """分析HAR文件，提取API调用信息"""
    
    print(f"正在分析HAR文件: {har_file_path}")
    
    try:
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except Exception as e:
        print(f"读取HAR文件失败: {e}")
        return None
    
    # 提取entries
    entries = har_data.get('log', {}).get('entries', [])
    print(f"找到 {len(entries)} 个HTTP请求")
    
    # 分析每个请求
    api_calls = []
    
    for i, entry in enumerate(entries):
        request = entry.get('request', {})
        response = entry.get('response', {})
        
        # 基本信息
        method = request.get('method', '')
        url = request.get('url', '')
        status = response.get('status', 0)
        
        # 解析URL
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # 请求头
        headers = {h['name']: h['value'] for h in request.get('headers', [])}
        
        # 请求体
        post_data = request.get('postData', {})
        request_body = post_data.get('text', '') if post_data else ''
        
        # 响应内容
        response_content = response.get('content', {})
        response_text = response_content.get('text', '')
        
        # 时间信息
        started_time = entry.get('startedDateTime', '')
        
        # 判断是否为API调用（过滤静态资源）
        is_api = is_api_call(url, method, headers)
        
        api_call = {
            'index': i + 1,
            'time': started_time,
            'method': method,
            'url': url,
            'domain': domain,
            'path': path,
            'query_params': query_params,
            'headers': headers,
            'request_body': request_body,
            'status': status,
            'response_text': response_text[:1000] if response_text else '',  # 限制长度
            'is_api': is_api
        }
        
        api_calls.append(api_call)
    
    return api_calls

def is_api_call(url, method, headers):
    """判断是否为API调用"""
    
    # 静态资源扩展名
    static_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.ico', '.svg', '.woff', '.ttf']
    
    # 检查URL是否包含静态资源扩展名
    for ext in static_extensions:
        if url.lower().endswith(ext):
            return False
    
    # 检查是否包含API相关路径
    api_patterns = [
        r'/ticket/',
        r'/api/',
        r'/citys/',
        r'/cinemas/',
        r'/movies/',
        r'/sessions/',
        r'/order/',
        r'/seats/',
        r'/login',
        r'/user/',
        r'/member/',
        r'/coupon/'
    ]
    
    for pattern in api_patterns:
        if re.search(pattern, url, re.IGNORECASE):
            return True
    
    # 检查Content-Type
    content_type = headers.get('content-type', '').lower()
    if 'application/json' in content_type or 'multipart/form-data' in content_type:
        return True
    
    return False

def analyze_business_flow(api_calls):
    """分析业务流程"""
    
    print("\n=== 业务流程分析 ===")
    
    # 过滤API调用
    api_only = [call for call in api_calls if call['is_api']]
    
    print(f"API调用总数: {len(api_only)}")
    
    # 按业务分类
    business_categories = {
        '城市选择': [r'/citys/', r'/city'],
        '影院选择': [r'/cinemas/', r'/cinema'],
        '电影选择': [r'/movies/', r'/movie', r'/films/', r'/film'],
        '场次选择': [r'/sessions/', r'/session', r'/shows/', r'/show'],
        '座位选择': [r'/seats/', r'/seat'],
        '订单创建': [r'/order/', r'/orders/'],
        '用户认证': [r'/login', r'/user/', r'/auth'],
        '会员信息': [r'/member/', r'/vip'],
        '优惠券': [r'/coupon/', r'/discount']
    }
    
    categorized_calls = {}
    
    for category, patterns in business_categories.items():
        categorized_calls[category] = []
        for call in api_only:
            for pattern in patterns:
                if re.search(pattern, call['url'], re.IGNORECASE):
                    categorized_calls[category].append(call)
                    break
    
    # 输出分类结果
    for category, calls in categorized_calls.items():
        if calls:
            print(f"\n{category} ({len(calls)}个调用):")
            for call in calls:
                print(f"  {call['method']} {call['path']}")
    
    return categorized_calls

def extract_api_details(api_calls):
    """提取API详细信息"""
    
    print("\n=== API详细信息 ===")
    
    api_details = []
    
    for call in api_calls:
        if not call['is_api']:
            continue
            
        detail = {
            'method': call['method'],
            'url': call['url'],
            'path': call['path'],
            'domain': call['domain'],
            'headers': {},
            'params': {},
            'body': call['request_body'],
            'response': call['response_text']
        }
        
        # 提取关键请求头
        important_headers = [
            'content-type', 'token', 'tenant-short', 'x-channel-id', 
            'client-version', 'user-agent', 'referer'
        ]
        
        for header in important_headers:
            if header in call['headers']:
                detail['headers'][header] = call['headers'][header]
        
        # 提取查询参数
        detail['params'] = call['query_params']
        
        api_details.append(detail)
    
    return api_details

def compare_with_existing_code(api_details):
    """与现有代码对比分析"""
    
    print("\n=== 与现有代码对比 ===")
    
    # 分析域名
    domains = set()
    for detail in api_details:
        domains.add(detail['domain'])
    
    print(f"发现的域名: {list(domains)}")
    
    # 分析API端点
    endpoints = set()
    for detail in api_details:
        path = detail['path']
        # 提取端点模式
        if '/ticket/' in path:
            endpoint = path.split('/ticket/')[1].split('/')[1] if len(path.split('/ticket/')) > 1 else ''
            if endpoint:
                endpoints.add(endpoint)
    
    print(f"发现的API端点: {list(endpoints)}")
    
    # 分析请求头模式
    header_patterns = {}
    for detail in api_details:
        for header, value in detail['headers'].items():
            if header not in header_patterns:
                header_patterns[header] = set()
            header_patterns[header].add(value)
    
    print("\n关键请求头:")
    for header, values in header_patterns.items():
        print(f"  {header}: {list(values)}")

def generate_adaptation_plan(api_details, categorized_calls):
    """生成适配方案"""
    
    print("\n=== 适配方案 ===")
    
    print("1. 需要修改的文件:")
    files_to_modify = [
        "cinema_api_adapter.py - 已有沃美配置，需验证",
        "services/film_service.py - 电影数据获取逻辑",
        "services/cinema_manager.py - 影院管理逻辑", 
        "services/order_api.py - 订单API调用",
        "main_modular.py - 主窗口业务逻辑"
    ]
    
    for file in files_to_modify:
        print(f"  - {file}")
    
    print("\n2. 关键差异点:")
    differences = [
        "域名: 需要确认实际使用的域名",
        "请求头: 验证token、tenant-short等参数",
        "API端点: 确认路径格式是否一致",
        "数据格式: 分析响应数据结构差异"
    ]
    
    for diff in differences:
        print(f"  - {diff}")
    
    print("\n3. 实施步骤:")
    steps = [
        "验证HAR文件中的API调用是否完整",
        "测试现有cinema_api_adapter.py的沃美配置",
        "分析响应数据格式，制作字段映射表",
        "修改数据解析逻辑",
        "更新业务流程代码",
        "全面测试验证"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"  {i}. {step}")

def main():
    """主函数"""
    
    har_file = "沃美res.vistachina.cn_2025_06_15_15_22_27.har"
    
    # 分析HAR文件
    api_calls = analyze_har_file(har_file)
    
    if not api_calls:
        print("HAR文件分析失败")
        return
    
    # 分析业务流程
    categorized_calls = analyze_business_flow(api_calls)
    
    # 提取API详细信息
    api_details = extract_api_details(api_calls)
    
    # 与现有代码对比
    compare_with_existing_code(api_details)
    
    # 生成适配方案
    generate_adaptation_plan(api_details, categorized_calls)
    
    # 保存分析结果
    output_file = "womei_har_analysis.json"
    analysis_result = {
        'total_requests': len(api_calls),
        'api_requests': len([c for c in api_calls if c['is_api']]),
        'categorized_calls': categorized_calls,
        'api_details': api_details
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
