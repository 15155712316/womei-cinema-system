#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件分析工具
分析沃美电影票务系统的网络请求流程
"""

import json
import base64
from urllib.parse import unquote, parse_qs, urlparse
from datetime import datetime

def decode_content(content_data):
    """解码内容"""
    if not content_data or 'text' not in content_data:
        return ''
    
    try:
        if content_data.get('encoding') == 'base64':
            return base64.b64decode(content_data['text']).decode('utf-8')
        else:
            return content_data['text']
    except Exception as e:
        return f'解码失败: {e}'

def analyze_request_purpose(method, url, request_data, response_data):
    """分析请求用途"""
    url_path = urlparse(url).path
    
    # 订单相关
    if '/order/ticket/' in url_path:
        return '创建订单', '订单创建'
    elif '/order/info/' in url_path:
        return '获取订单详情', '订单查询'
    elif '/order/change/' in url_path:
        return '修改订单', '订单修改'
    elif '/order/sublists/info' in url_path:
        return '获取订单子列表', '订单查询'
    
    # 券相关
    elif '/user/voucher/list/' in url_path:
        return '获取用户券列表', '券查询'
    elif '/voucher/bind/' in url_path:
        return '绑定券', '券使用'
    elif '/voucher/check/' in url_path:
        return '验证券', '券验证'
    
    # 用户相关
    elif '/user/info/' in url_path:
        return '获取用户信息', '用户查询'
    elif '/user/cards/' in url_path:
        return '获取用户卡片', '会员卡查询'
    
    # 支付相关
    elif '/pay/' in url_path or '/payment/' in url_path:
        return '支付处理', '支付流程'
    elif '/wxpay/' in url_path:
        return '微信支付', '支付流程'
    
    # 其他
    else:
        return '未知接口', '其他'

def main():
    """主函数"""
    try:
        # 读取HAR文件
        with open('沃美下单用券ct.womovie.cn_2025_06_24_16_59_20.har', 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        # 提取所有请求条目
        entries = har_data['log']['entries']
        
        print("🎬 沃美电影票务系统网络请求流程分析")
        print("=" * 80)
        print(f"📊 总共记录了 {len(entries)} 个网络请求")
        print("=" * 80)
        
        # 按功能分类统计
        categories = {}
        
        for i, entry in enumerate(entries):
            # 提取基本信息
            method = entry['request']['method']
            url = entry['request']['url']
            start_time = entry['startedDateTime']
            status = entry['response']['status']
            
            # 解码内容
            request_data = ''
            if 'postData' in entry['request']:
                request_data = decode_content(entry['request']['postData'])
            
            response_content = decode_content(entry['response'].get('content', {}))
            
            # 分析用途
            purpose, category = analyze_request_purpose(method, url, request_data, response_content)
            
            # 统计分类
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'index': i + 1,
                'method': method,
                'url': url,
                'purpose': purpose,
                'status': status,
                'time': start_time,
                'request_data': request_data,
                'response_content': response_content
            })
            
            # 输出详细信息
            print(f"\n🔗 {i+1}. [{method}] {purpose}")
            print(f"   📍 URL: {url}")
            print(f"   ⏰ 时间: {start_time}")
            print(f"   📊 状态: {status}")
            
            if request_data and len(request_data.strip()) > 0:
                print(f"   📤 请求数据: {request_data[:150]}{'...' if len(request_data) > 150 else ''}")
            
            if response_content and len(response_content.strip()) > 0:
                print(f"   📥 响应内容: {response_content[:150]}{'...' if len(response_content) > 150 else ''}")
            
            print("-" * 60)
        
        # 输出分类统计
        print("\n📋 接口分类统计:")
        print("=" * 80)
        for category, requests in categories.items():
            print(f"\n🏷️  {category} ({len(requests)} 个请求):")
            for req in requests:
                print(f"   {req['index']}. [{req['method']}] {req['purpose']} - 状态:{req['status']}")
        
        print("\n" + "=" * 80)
        print("✅ 分析完成！")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
