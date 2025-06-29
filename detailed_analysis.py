#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细分析HAR文件中的接口
重点分析券相关和支付相关的接口
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

def analyze_detailed_purpose(method, url, request_data, response_data):
    """详细分析请求用途"""
    url_path = urlparse(url).path
    query_params = parse_qs(urlparse(url).query)
    
    # 券相关接口详细分析
    if '/user/voucher/list/' in url_path:
        return '获取用户券列表', '券查询', '获取用户所有可用券列表，包含unused、used、disabled分类'
    elif '/user/vouchers' in url_path:
        voucher_type = query_params.get('voucher_type', [''])[0]
        if voucher_type == 'VGC_T':
            return '获取票券列表', '券查询', '获取特定场次的票券(VGC_T类型)'
        elif voucher_type == 'VGC_P':
            return '获取商品券列表', '券查询', '获取商品券(VGC_P类型)'
        else:
            return '获取券列表', '券查询', f'获取券列表，类型：{voucher_type}'
    elif '/user/vouchers_page' in url_path:
        return '分页获取券列表', '券查询', '分页获取券列表，支持翻页功能'
    elif '/order/voucher/price/' in url_path:
        return '计算券价格', '券验证', '计算使用券后的订单价格和手续费'
    elif '/order/vcc/list/' in url_path:
        return '获取订单VCC券列表', '券查询', '获取订单可用的VCC券列表(EVGC_VOUCHER类型)'
    elif '/order/vcc/usable/count' in url_path:
        return '获取可用VCC券数量', '券查询', '获取订单可用的VCC券数量统计'
    
    # 订单相关接口详细分析
    elif '/order/ticket/' in url_path:
        return '创建订单', '订单创建', '创建电影票订单，包含座位信息和场次ID'
    elif '/order/info/' in url_path:
        return '获取订单详情', '订单查询', '获取订单完整信息，包含状态、价格、座位等'
    elif '/order/change/' in url_path:
        return '修改订单', '订单修改', '修改订单信息，如支付方式、会员卡、券等'
    elif '/order/sublists/info' in url_path:
        return '获取订单子列表', '订单查询', '获取订单相关的子订单信息'
    elif '/order/payment/' in url_path:
        return '订单支付', '支付流程', '处理订单支付，生成支付凭证'
    elif '/order/query/' in url_path:
        return '查询订单状态', '订单查询', '查询订单处理状态(PROCESSING/SUCCESS等)'
    elif '/order/template/' in url_path:
        return '订单模板处理', '订单处理', '处理订单相关的模板消息'
    
    # 用户相关接口详细分析
    elif '/user/info/' in url_path:
        return '获取用户信息', '用户查询', '获取用户基本信息、会员状态等'
    elif '/user/cards/' in url_path:
        return '获取用户卡片', '会员卡查询', '获取用户的会员卡信息和余额'
    
    # 其他接口
    elif '/ads/' in url_path:
        return '获取广告', '广告展示', '获取购票后的广告横幅'
    elif '/vcc/activity/gift/' in url_path:
        return '获取VCC活动礼品', '活动查询', '获取VCC相关的活动礼品信息'
    
    else:
        return '未知接口', '其他', f'路径：{url_path}'

def get_implementation_status(purpose, category):
    """判断实现状态"""
    implemented = {
        '创建订单': '✅ 已实现',
        '获取订单详情': '✅ 已实现', 
        '获取用户券列表': '✅ 已实现',
        '获取用户信息': '✅ 已实现',
        '获取用户卡片': '✅ 已实现'
    }
    
    partially_implemented = {
        '修改订单': '🔶 部分实现',
        '查询订单状态': '🔶 部分实现'
    }
    
    not_implemented = {
        '计算券价格': '❌ 未实现',
        '获取订单VCC券列表': '❌ 未实现', 
        '获取可用VCC券数量': '❌ 未实现',
        '分页获取券列表': '❌ 未实现',
        '获取票券列表': '❌ 未实现',
        '获取商品券列表': '❌ 未实现',
        '订单支付': '❌ 未实现',
        '订单模板处理': '❌ 未实现'
    }
    
    if purpose in implemented:
        return implemented[purpose]
    elif purpose in partially_implemented:
        return partially_implemented[purpose]
    elif purpose in not_implemented:
        return not_implemented[purpose]
    else:
        return '❓ 状态未知'

def main():
    """主函数"""
    try:
        # 读取HAR文件
        with open('沃美下单用券ct.womovie.cn_2025_06_24_16_59_20.har', 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        
        print("🎬 沃美电影票务系统详细接口分析报告")
        print("=" * 100)
        
        # 按时间顺序分析每个接口
        for i, entry in enumerate(entries):
            method = entry['request']['method']
            url = entry['request']['url']
            start_time = entry['startedDateTime']
            status = entry['response']['status']
            
            # 解码内容
            request_data = ''
            if 'postData' in entry['request']:
                request_data = decode_content(entry['request']['postData'])
            
            response_content = decode_content(entry['response'].get('content', {}))
            
            # 详细分析
            purpose, category, description = analyze_detailed_purpose(method, url, request_data, response_content)
            impl_status = get_implementation_status(purpose, category)
            
            print(f"\n🔗 {i+1}. [{method}] {purpose}")
            print(f"   📍 URL: {url}")
            print(f"   📋 分类: {category}")
            print(f"   📝 描述: {description}")
            print(f"   🔧 实现状态: {impl_status}")
            print(f"   ⏰ 时间: {start_time}")
            print(f"   📊 状态: {status}")
            
            if request_data and len(request_data.strip()) > 0:
                print(f"   📤 请求参数: {request_data}")
            
            if response_content and len(response_content.strip()) > 0:
                # 尝试解析JSON响应
                try:
                    resp_json = json.loads(response_content)
                    print(f"   📥 响应状态: ret={resp_json.get('ret')}, msg={resp_json.get('msg')}")
                    if 'data' in resp_json and resp_json['data']:
                        data_keys = list(resp_json['data'].keys()) if isinstance(resp_json['data'], dict) else 'array'
                        print(f"   📊 数据字段: {data_keys}")
                except:
                    print(f"   📥 响应内容: {response_content[:100]}...")
            
            print("-" * 80)
        
        print("\n" + "=" * 100)
        print("✅ 详细分析完成！")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
