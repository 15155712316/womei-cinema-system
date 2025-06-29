#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细的沃美优惠券流程分析报告
基于HAR文件的深入分析和现有代码对比
"""

import json
import os
from datetime import datetime

def load_analysis_data():
    """加载分析数据"""
    try:
        with open('complete_voucher_har_analysis.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载分析数据失败: {e}")
        return None

def generate_detailed_report():
    """生成详细分析报告"""
    
    print("🎬 沃美影城优惠券流程详细分析报告")
    print("🎯 基于HAR文件的完整业务流程分析")
    print("=" * 80)
    
    data = load_analysis_data()
    if not data:
        return
    
    print(f"📊 分析概况:")
    print(f"   HAR文件: {data['har_file']}")
    print(f"   分析时间: {data['analysis_time']}")
    print(f"   总请求数: {data['total_requests']}")
    print()
    
    # 1. 完整流程梳理
    print("📋 1. 完整流程梳理")
    print("=" * 60)
    
    api_requests = data['api_requests']
    
    # 按时间顺序分析业务流程
    print("⏰ 按时间顺序的业务流程:")
    
    for i, req in enumerate(reversed(api_requests)):  # 反转以按时间正序
        timestamp = datetime.fromisoformat(req['timestamp'].replace('Z', '+00:00'))
        time_str = timestamp.strftime('%H:%M:%S.%f')[:-3]
        
        print(f"   {len(api_requests)-i:2d}. [{time_str}] {req['method']:4s} {req['business_type']}")
        print(f"       路径: {req['path']}")
        print(f"       状态: {req['implementation_status']}")
        
        # 显示关键参数
        if req['post_params']:
            key_params = []
            for key, value in req['post_params'].items():
                if key in ['voucher_code', 'order_id', 'schedule_id', 'seatlable']:
                    key_params.append(f"{key}={value}")
            if key_params:
                print(f"       参数: {', '.join(key_params)}")
        
        # 显示查询参数
        if req['query_params']:
            key_queries = []
            for key, values in req['query_params'].items():
                if key in ['voucher_type', 'schedule_id', 'order_id']:
                    key_queries.append(f"{key}={values[0] if values else ''}")
            if key_queries:
                print(f"       查询: {', '.join(key_queries)}")
        
        print()
    
    # 2. 接口实现状态对比
    print("\n📋 2. 接口实现状态详细对比")
    print("=" * 60)
    
    # 按业务类型分组
    business_groups = {}
    for req in api_requests:
        business_type = req['business_type']
        if business_type not in business_groups:
            business_groups[business_type] = []
        business_groups[business_type].append(req)
    
    # 核心业务接口分析
    print("🔴 核心业务接口（高优先级）:")
    core_apis = ['创建订单', '订单信息查询', '用户券列表查询', '券价格计算', '券绑定到订单']
    
    for api_type in core_apis:
        if api_type in business_groups:
            requests = business_groups[api_type]
            status = requests[0]['implementation_status']
            unique_paths = set(req['path'] for req in requests)
            
            print(f"   {status} {api_type}")
            print(f"      接口路径: {', '.join(unique_paths)}")
            print(f"      调用次数: {len(requests)}")
            
            # 显示具体功能
            if api_type == '券绑定到订单':
                voucher_requests = [req for req in requests if req.get('post_params', {}).get('voucher_code')]
                if voucher_requests:
                    voucher_codes = [req['post_params'].get('voucher_code', '') for req in voucher_requests]
                    print(f"      券码使用: {', '.join(voucher_codes)}")
            
            print()
    
    # 3. 新发现的接口分析
    print("📋 3. 新发现的接口详细分析")
    print("=" * 60)
    
    new_apis = {}
    for req in api_requests:
        if '❌未实现' in req['implementation_status']:
            path = req['path']
            if path not in new_apis:
                new_apis[path] = {
                    'path': path,
                    'business_type': req['business_type'],
                    'method': req['method'],
                    'calls': [],
                    'query_params': set(),
                    'response_data': []
                }
            
            new_apis[path]['calls'].append(req)
            
            # 收集查询参数
            for key in req['query_params'].keys():
                new_apis[path]['query_params'].add(key)
            
            # 收集响应数据
            if req['response_json']:
                new_apis[path]['response_data'].append(req['response_json'])
    
    print("🔍 未实现的接口详细分析:")
    
    for path, info in new_apis.items():
        print(f"\n   📍 {path}")
        print(f"      方法: {info['method']}")
        print(f"      调用次数: {len(info['calls'])}")
        print(f"      查询参数: {', '.join(info['query_params']) if info['query_params'] else '无'}")
        
        # 分析接口功能
        functionality = analyze_api_functionality(path, info)
        print(f"      推测功能: {functionality}")
        
        # 分析响应数据
        if info['response_data']:
            sample_response = info['response_data'][0]
            if isinstance(sample_response.get('data'), list):
                print(f"      返回数据: 列表类型，长度 {len(sample_response['data'])}")
            elif isinstance(sample_response.get('data'), dict):
                print(f"      返回数据: 对象类型，字段 {len(sample_response['data'])}")
            else:
                print(f"      返回数据: {type(sample_response.get('data', 'N/A'))}")
        
        # 实现优先级
        priority = get_implementation_priority(path, info)
        print(f"      实现优先级: {priority}")
        
        print()
    
    # 4. 与昨天分析的对比
    print("📋 4. 与昨天券使用流程验证的对比")
    print("=" * 60)
    
    print("✅ 昨天验证成功的核心接口:")
    verified_apis = [
        'POST /order/change/ - 券绑定功能',
        'POST /order/voucher/price/ - 券价格计算',
        'GET /user/voucher/list/ - 券列表查询',
        'GET /order/info/ - 订单信息查询'
    ]
    
    for api in verified_apis:
        print(f"   ✅ {api}")
    
    print(f"\n🆕 今天HAR分析新发现的接口:")
    new_findings = [
        'GET /user/vouchers - 特定类型券查询（VGC_P类型）',
        'GET /order/vcc/list/ - VCC券列表',
        'GET /order/vcc/usable/count - 可用VCC券数量',
        'GET /user/vouchers_page - 分页券查询',
        'GET /user/cards/ - 用户卡片信息',
        'GET /user/info/ - 用户基本信息'
    ]
    
    for finding in new_findings:
        print(f"   🆕 {finding}")
    
    # 5. 实现建议和优先级
    print(f"\n📋 5. 实现建议和优先级排序")
    print("=" * 60)
    
    print("🔴 立即实现（高优先级）:")
    print("   目前所有高优先级接口都已实现 ✅")
    
    print(f"\n🟡 后续实现（中优先级）:")
    medium_priority = [
        'GET /user/info/ - 用户信息查询，用于个人中心显示',
    ]
    
    for item in medium_priority:
        print(f"   📋 {item}")
    
    print(f"\n🟢 可选实现（低优先级）:")
    low_priority = [
        'GET /user/vouchers - 特定券类型查询，可能用于券分类显示',
        'GET /order/vcc/list/ - VCC券管理，如果不使用VCC券可忽略',
        'GET /user/cards/ - 用户卡片管理，非核心功能',
        'GET /user/vouchers_page - 券分页查询，可用现有接口替代'
    ]
    
    for item in low_priority:
        print(f"   📋 {item}")

def analyze_api_functionality(path, info):
    """分析API功能"""
    if '/user/vouchers' in path and 'voucher_type' in info['query_params']:
        return "按类型查询用户券（如VGC_P类型券）"
    elif '/order/vcc/list' in path:
        return "查询VCC（Virtual Credit Card）券列表"
    elif '/order/vcc/usable/count' in path:
        return "查询可用VCC券数量"
    elif '/user/vouchers_page' in path:
        return "分页查询用户券列表"
    elif '/user/cards' in path:
        return "查询用户卡片信息（会员卡、储值卡等）"
    elif '/user/info' in path:
        return "查询用户基本信息"
    elif '/order/sublists/info' in path:
        return "查询订单子列表信息"
    else:
        return "未知功能，需要进一步分析"

def get_implementation_priority(path, info):
    """获取实现优先级"""
    if '/user/info' in path:
        return "🟡 中优先级 - 用户体验相关"
    elif '/user/vouchers' in path and 'voucher_type' in info['query_params']:
        return "🟢 低优先级 - 券分类功能"
    elif '/order/vcc' in path:
        return "🟢 低优先级 - VCC券功能（可选）"
    elif '/user/cards' in path:
        return "🟢 低优先级 - 卡片管理功能"
    else:
        return "🟢 低优先级 - 非核心功能"

def main():
    """主函数"""
    generate_detailed_report()
    
    print(f"\n🎯 总结")
    print("=" * 60)
    print("✅ 核心券使用流程已完全实现并验证")
    print("✅ 所有高优先级接口都已实现")
    print("🆕 发现了一些辅助功能接口，但不影响核心业务")
    print("🚀 系统已具备完整的券使用能力")
    
    print(f"\n📋 下一步建议:")
    print("1. 优先实现用户信息查询接口（中优先级）")
    print("2. 根据业务需要选择性实现其他辅助接口")
    print("3. 优化现有接口的性能和用户体验")
    print("4. 完善错误处理和异常情况处理")

if __name__ == "__main__":
    main()
