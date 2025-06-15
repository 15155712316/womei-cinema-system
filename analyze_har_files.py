#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件分析工具
用于对比华联和沃美下单系统的HTTP请求差异
"""

import json
import pandas as pd
from urllib.parse import urlparse, parse_qs
import re

def load_har_file(file_path):
    """加载HAR文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件 {file_path} 失败: {e}")
        return None

def extract_requests(har_data):
    """提取HAR文件中的请求信息"""
    if not har_data or 'log' not in har_data:
        return []
    
    requests = []
    entries = har_data['log'].get('entries', [])
    
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        
        # 解析URL
        url = request.get('url', '')
        parsed_url = urlparse(url)
        
        # 提取请求参数
        query_params = {}
        if parsed_url.query:
            query_params = parse_qs(parsed_url.query)
        
        # 提取POST数据
        post_data = {}
        if request.get('postData'):
            post_data_text = request['postData'].get('text', '')
            if post_data_text:
                try:
                    post_data = json.loads(post_data_text)
                except:
                    post_data = {'raw': post_data_text}
        
        # 提取请求头
        headers = {}
        for header in request.get('headers', []):
            headers[header['name']] = header['value']
        
        request_info = {
            'method': request.get('method', ''),
            'url': url,
            'domain': parsed_url.netloc,
            'path': parsed_url.path,
            'query_params': query_params,
            'post_data': post_data,
            'headers': headers,
            'status_code': response.get('status', 0),
            'response_headers': {h['name']: h['value'] for h in response.get('headers', [])},
            'mime_type': response.get('content', {}).get('mimeType', ''),
            'started_time': entry.get('startedDateTime', ''),
            'time': entry.get('time', 0)
        }
        
        requests.append(request_info)
    
    return requests

def analyze_api_requests(requests):
    """分析API请求，过滤掉静态资源"""
    api_requests = []
    
    # 定义静态资源的特征
    static_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.ico', '.svg', '.woff', '.ttf']
    static_mime_types = ['image/', 'text/css', 'application/javascript', 'font/']
    
    for req in requests:
        # 跳过静态资源
        is_static = False
        
        # 检查URL扩展名
        for ext in static_extensions:
            if req['path'].lower().endswith(ext):
                is_static = True
                break
        
        # 检查MIME类型
        if not is_static:
            for mime in static_mime_types:
                if req['mime_type'].startswith(mime):
                    is_static = True
                    break
        
        if not is_static:
            api_requests.append(req)
    
    return api_requests

def compare_requests(requests1, requests2, label1, label2):
    """对比两组请求的差异"""
    print(f"\n{'='*60}")
    print(f"API请求对比分析: {label1} vs {label2}")
    print(f"{'='*60}")
    
    # 基本统计
    print(f"\n📊 基本统计:")
    print(f"{label1}: {len(requests1)} 个API请求")
    print(f"{label2}: {len(requests2)} 个API请求")
    
    # 域名分析
    domains1 = set(req['domain'] for req in requests1)
    domains2 = set(req['domain'] for req in requests2)
    
    print(f"\n🌐 域名分析:")
    print(f"{label1} 使用的域名:")
    for domain in sorted(domains1):
        count = sum(1 for req in requests1 if req['domain'] == domain)
        print(f"  - {domain} ({count} 个请求)")
    
    print(f"\n{label2} 使用的域名:")
    for domain in sorted(domains2):
        count = sum(1 for req in requests2 if req['domain'] == domain)
        print(f"  - {domain} ({count} 个请求)")
    
    # 共同域名和独有域名
    common_domains = domains1 & domains2
    unique_domains1 = domains1 - domains2
    unique_domains2 = domains2 - domains1
    
    if common_domains:
        print(f"\n🤝 共同使用的域名: {', '.join(sorted(common_domains))}")
    if unique_domains1:
        print(f"\n🔸 {label1} 独有域名: {', '.join(sorted(unique_domains1))}")
    if unique_domains2:
        print(f"\n🔹 {label2} 独有域名: {', '.join(sorted(unique_domains2))}")
    
    # API路径分析
    print(f"\n🛣️ API路径分析:")
    paths1 = [req['path'] for req in requests1 if req['method'] in ['POST', 'PUT', 'PATCH']]
    paths2 = [req['path'] for req in requests2 if req['method'] in ['POST', 'PUT', 'PATCH']]
    
    print(f"\n{label1} 的主要API路径:")
    for path in sorted(set(paths1)):
        count = paths1.count(path)
        print(f"  - {path} ({count} 次)")
    
    print(f"\n{label2} 的主要API路径:")
    for path in sorted(set(paths2)):
        count = paths2.count(path)
        print(f"  - {path} ({count} 次)")
    
    # 请求方法分析
    methods1 = [req['method'] for req in requests1]
    methods2 = [req['method'] for req in requests2]
    
    print(f"\n📡 请求方法统计:")
    print(f"{label1}:")
    for method in sorted(set(methods1)):
        count = methods1.count(method)
        print(f"  - {method}: {count} 次")
    
    print(f"\n{label2}:")
    for method in sorted(set(methods2)):
        count = methods2.count(method)
        print(f"  - {method}: {count} 次")

def analyze_request_details(requests, label):
    """详细分析请求内容"""
    print(f"\n{'='*60}")
    print(f"详细请求分析: {label}")
    print(f"{'='*60}")
    
    # 按域名分组分析
    domain_groups = {}
    for req in requests:
        domain = req['domain']
        if domain not in domain_groups:
            domain_groups[domain] = []
        domain_groups[domain].append(req)
    
    for domain, domain_requests in domain_groups.items():
        print(f"\n🏢 域名: {domain}")
        print(f"   请求数量: {len(domain_requests)}")
        
        # 分析该域名下的API
        api_requests = [req for req in domain_requests if req['method'] in ['POST', 'PUT', 'PATCH']]
        if api_requests:
            print(f"   API请求: {len(api_requests)} 个")
            for req in api_requests:
                print(f"     - {req['method']} {req['path']}")
                if req['post_data']:
                    print(f"       POST数据: {str(req['post_data'])[:100]}...")
                if req['query_params']:
                    print(f"       查询参数: {req['query_params']}")

def main():
    """主函数"""
    # 加载HAR文件
    print("正在加载HAR文件...")
    
    huanlian_har = load_har_file('华联下单_2025_06_08_15_06_36.har')
    womei_har = load_har_file('沃美下单_2025_06_08_15_07_51.har')
    
    if not huanlian_har or not womei_har:
        print("❌ 无法加载HAR文件")
        return
    
    # 提取请求信息
    print("正在提取请求信息...")
    huanlian_requests = extract_requests(huanlian_har)
    womei_requests = extract_requests(womei_har)
    
    print(f"华联系统: 提取到 {len(huanlian_requests)} 个请求")
    print(f"沃美系统: 提取到 {len(womei_requests)} 个请求")
    
    # 过滤API请求
    huanlian_api = analyze_api_requests(huanlian_requests)
    womei_api = analyze_api_requests(womei_requests)
    
    print(f"华联系统: 过滤后 {len(huanlian_api)} 个API请求")
    print(f"沃美系统: 过滤后 {len(womei_api)} 个API请求")
    
    # 对比分析
    compare_requests(huanlian_api, womei_api, "华联系统", "沃美系统")
    
    # 详细分析
    analyze_request_details(huanlian_api, "华联系统")
    analyze_request_details(womei_api, "沃美系统")
    
    print(f"\n{'='*60}")
    print("分析完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
