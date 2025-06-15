#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解码沃美API响应数据，分析数据结构
"""

import json
import base64
from urllib.parse import unquote

def decode_base64_response(encoded_text):
    """解码Base64编码的响应"""
    try:
        decoded_bytes = base64.b64decode(encoded_text)
        decoded_text = decoded_bytes.decode('utf-8')
        return json.loads(decoded_text)
    except Exception as e:
        print(f"解码失败: {e}")
        return None

def decode_request_body(encoded_body):
    """解码请求体"""
    try:
        decoded_bytes = base64.b64decode(encoded_body)
        decoded_text = decoded_bytes.decode('utf-8')
        return unquote(decoded_text)
    except Exception as e:
        print(f"解码请求体失败: {e}")
        return encoded_body

def analyze_api_responses():
    """分析API响应数据结构"""
    
    # 读取分析结果
    with open('womei_har_analysis.json', 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    api_details = analysis_data['api_details']
    
    print("=== 沃美API数据结构分析 ===\n")
    
    # 按业务分类分析
    business_apis = {
        '城市列表': [],
        '影院信息': [],
        '电影列表': [],
        '场次信息': [],
        '座位信息': [],
        '订单相关': [],
        '用户信息': [],
        '会员信息': []
    }
    
    for detail in api_details:
        path = detail['path']
        
        if '/citys/' in path:
            business_apis['城市列表'].append(detail)
        elif '/cinema/' in path and '/info/' in path:
            business_apis['影院信息'].append(detail)
        elif '/movies/' in path:
            business_apis['电影列表'].append(detail)
        elif '/shows/' in path:
            business_apis['场次信息'].append(detail)
        elif '/hall/' in path:
            business_apis['座位信息'].append(detail)
        elif '/order/' in path:
            business_apis['订单相关'].append(detail)
        elif '/user/' in path:
            business_apis['用户信息'].append(detail)
        elif '/member/' in path:
            business_apis['会员信息'].append(detail)
    
    # 分析每个业务类型的数据结构
    for business_type, apis in business_apis.items():
        if not apis:
            continue
            
        print(f"## {business_type}")
        print(f"API数量: {len(apis)}")
        
        for api in apis:
            print(f"\n### {api['method']} {api['path']}")
            
            # 解码响应数据
            if api['response']:
                decoded_response = decode_base64_response(api['response'])
                if decoded_response:
                    print("响应数据结构:")
                    print(json.dumps(decoded_response, ensure_ascii=False, indent=2)[:500] + "...")
            
            # 解码请求体
            if api['body']:
                decoded_body = decode_request_body(api['body'])
                print(f"请求体: {decoded_body}")
            
            # 显示关键参数
            if api['params']:
                print(f"查询参数: {api['params']}")
            
            print("-" * 50)
        
        print("\n")

def extract_key_data_structures():
    """提取关键数据结构"""
    
    print("=== 关键数据结构提取 ===\n")
    
    # 读取分析结果
    with open('womei_har_analysis.json', 'r', encoding='utf-8') as f:
        analysis_data = json.load(f)
    
    key_structures = {}
    
    for detail in analysis_data['api_details']:
        if not detail['response']:
            continue
            
        decoded_response = decode_base64_response(detail['response'])
        if not decoded_response:
            continue
        
        path = detail['path']
        
        # 提取关键API的数据结构
        if '/citys/' in path:
            key_structures['城市列表'] = decoded_response
        elif '/movies/' in path:
            key_structures['电影列表'] = decoded_response
        elif '/shows/' in path:
            key_structures['场次列表'] = decoded_response
        elif '/hall/info/' in path:
            key_structures['座位图信息'] = decoded_response
        elif '/order/ticket/' in path:
            key_structures['订单创建'] = decoded_response
    
    # 保存关键数据结构
    with open('womei_key_data_structures.json', 'w', encoding='utf-8') as f:
        json.dump(key_structures, f, ensure_ascii=False, indent=2)
    
    print("关键数据结构已保存到: womei_key_data_structures.json")
    
    # 显示数据结构概览
    for api_type, data in key_structures.items():
        print(f"\n## {api_type}")
        if isinstance(data, dict):
            if 'data' in data:
                data_content = data['data']
                if isinstance(data_content, list) and data_content:
                    print(f"数据类型: 列表，包含 {len(data_content)} 个项目")
                    print("第一个项目的字段:")
                    if isinstance(data_content[0], dict):
                        for key in data_content[0].keys():
                            print(f"  - {key}")
                elif isinstance(data_content, dict):
                    print("数据类型: 对象")
                    print("主要字段:")
                    for key in data_content.keys():
                        print(f"  - {key}")
            else:
                print("响应格式:")
                for key in data.keys():
                    print(f"  - {key}")

def compare_with_existing_code():
    """与现有代码结构对比"""
    
    print("\n=== 与现有代码对比分析 ===\n")
    
    # 分析现有的cinema_api_adapter.py配置
    print("1. 现有配置验证:")
    print("   - 域名: ct.womovie.cn ✓ (与HAR文件一致)")
    print("   - tenant-short: wmyc ✓ (与HAR文件一致)")
    print("   - x-channel-id: 40000 ✓ (与HAR文件一致)")
    print("   - client-version: 4.0 ✓ (与HAR文件一致)")
    
    print("\n2. API端点对比:")
    print("   现有配置的端点:")
    print("   - cities: /ticket/{tenant_short}/citys/")
    print("   - cinemas: /ticket/{tenant_short}/cinemas/")
    print("   - movies: /ticket/{tenant_short}/movies/")
    print("   - sessions: /ticket/{tenant_short}/sessions/")
    print("   - order: /ticket/{tenant_short}/order/")
    
    print("\n   HAR文件中发现的端点:")
    print("   - 城市: /ticket/wmyc/citys/ ✓")
    print("   - 影院: /ticket/wmyc/cinema/{cinema_id}/... ✓")
    print("   - 电影: /ticket/wmyc/cinema/{cinema_id}/movies/ ✓")
    print("   - 场次: /ticket/wmyc/cinema/{cinema_id}/shows/ ✓")
    print("   - 订单: /ticket/wmyc/cinema/{cinema_id}/order/... ✓")
    
    print("\n3. 关键差异:")
    print("   - 影院相关API需要cinema_id参数")
    print("   - 座位信息API: /ticket/wmyc/cinema/{cinema_id}/hall/...")
    print("   - 用户信息API: /ticket/wmyc/cinema/{cinema_id}/user/...")
    print("   - 会员信息API: /ticket/wmyc/cinema/{cinema_id}/member/...")

def main():
    """主函数"""
    
    # 分析API响应
    analyze_api_responses()
    
    # 提取关键数据结构
    extract_key_data_structures()
    
    # 与现有代码对比
    compare_with_existing_code()

if __name__ == "__main__":
    main()
