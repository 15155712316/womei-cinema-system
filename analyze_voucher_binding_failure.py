#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析沃美影城券绑定失败的根本原因
通过对比HAR文件中的成功案例来找出差异
"""

import sys
import os
import json
import re
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class VoucherBindingAnalyzer:
    """券绑定失败分析器"""
    
    def __init__(self):
        self.har_file = "下单用券对比ct.womovie.cn_2025_06_29_14_51_48.har"
        self.current_failure = {
            "order_id": "250629134710001936",
            "cinema_id": "400028",
            "cinema_name": "北京沃美世界城店",
            "voucher_code": "GZJY01002948416827",
            "error_code": "sub=4004",
            "error_message": "获取兑换券验券异常，请联系影院"
        }
    
    def load_har_file(self):
        """加载HAR文件"""
        print("📁 加载HAR文件分析")
        print("=" * 80)
        
        try:
            with open(self.har_file, 'r', encoding='utf-8') as f:
                har_data = json.load(f)
            
            print(f"✅ HAR文件加载成功: {self.har_file}")
            
            # 获取基本信息
            log = har_data.get('log', {})
            entries = log.get('entries', [])
            
            print(f"📊 HAR文件信息:")
            print(f"   版本: {log.get('version', 'N/A')}")
            print(f"   创建工具: {log.get('creator', {}).get('name', 'N/A')}")
            print(f"   请求总数: {len(entries)}")
            
            return har_data
            
        except FileNotFoundError:
            print(f"❌ HAR文件不存在: {self.har_file}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ HAR文件格式错误: {e}")
            return None
        except Exception as e:
            print(f"❌ 加载HAR文件失败: {e}")
            return None
    
    def extract_voucher_related_requests(self, har_data):
        """提取券相关的请求"""
        print(f"\n🔍 提取券相关的请求")
        print("=" * 80)
        
        if not har_data:
            return []
        
        entries = har_data.get('log', {}).get('entries', [])
        voucher_requests = []
        
        # 券相关的URL模式
        voucher_patterns = [
            r'/voucher/',
            r'/order/change',
            r'/order/voucher/price',
            r'/user/voucher/list'
        ]
        
        for entry in entries:
            request = entry.get('request', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            # 检查是否是券相关请求
            is_voucher_related = any(re.search(pattern, url, re.IGNORECASE) for pattern in voucher_patterns)
            
            if is_voucher_related:
                response = entry.get('response', {})
                
                voucher_request = {
                    'url': url,
                    'method': method,
                    'headers': request.get('headers', []),
                    'postData': request.get('postData', {}),
                    'response_status': response.get('status', 0),
                    'response_headers': response.get('headers', []),
                    'response_content': response.get('content', {}),
                    'timestamp': entry.get('startedDateTime', ''),
                    'time': entry.get('time', 0)
                }
                
                voucher_requests.append(voucher_request)
        
        print(f"📊 找到券相关请求: {len(voucher_requests)} 个")
        
        # 按时间排序
        voucher_requests.sort(key=lambda x: x['timestamp'])
        
        # 显示请求概览
        for i, req in enumerate(voucher_requests, 1):
            url_path = req['url'].split('/')[-2:] if '/' in req['url'] else [req['url']]
            print(f"   {i}. {req['method']} /{'/'.join(url_path)} (状态: {req['response_status']})")
        
        return voucher_requests
    
    def analyze_successful_voucher_binding(self, voucher_requests):
        """分析成功的券绑定流程"""
        print(f"\n🎯 分析成功的券绑定流程")
        print("=" * 80)
        
        successful_bindings = []
        
        for req in voucher_requests:
            # 检查是否是券绑定请求
            if '/order/change' in req['url'] and req['method'] == 'POST':
                # 尝试解析响应内容
                response_content = req['response_content']
                content_text = response_content.get('text', '')
                
                if content_text:
                    try:
                        response_data = json.loads(content_text)
                        ret = response_data.get('ret', -1)
                        sub = response_data.get('sub', -1)
                        
                        # 检查是否成功
                        if ret == 0 and sub == 0:
                            data = response_data.get('data', {})
                            voucher_use = data.get('voucher_use', {})
                            
                            # 检查是否有券使用信息
                            if voucher_use and voucher_use.get('use_codes'):
                                print(f"✅ 找到成功的券绑定:")
                                print(f"   URL: {req['url']}")
                                print(f"   时间: {req['timestamp']}")
                                print(f"   券码: {voucher_use.get('use_codes', [])}")
                                print(f"   抵扣金额: {voucher_use.get('use_total_price', 0)}")
                                
                                successful_bindings.append({
                                    'request': req,
                                    'response_data': response_data,
                                    'voucher_codes': voucher_use.get('use_codes', []),
                                    'discount_amount': voucher_use.get('use_total_price', 0)
                                })
                    
                    except json.JSONDecodeError:
                        continue
        
        print(f"\n📊 成功券绑定统计: {len(successful_bindings)} 个")
        return successful_bindings
    
    def extract_request_parameters(self, request):
        """提取请求参数"""
        params = {}
        
        # 提取POST数据
        post_data = request.get('postData', {})
        if post_data:
            text = post_data.get('text', '')
            mime_type = post_data.get('mimeType', '')
            
            if 'application/x-www-form-urlencoded' in mime_type and text:
                # 解析form数据
                import urllib.parse
                parsed = urllib.parse.parse_qs(text)
                for key, values in parsed.items():
                    params[key] = values[0] if len(values) == 1 else values
        
        return params
    
    def compare_with_current_failure(self, successful_bindings):
        """对比成功案例与当前失败案例"""
        print(f"\n📊 对比成功案例与当前失败案例")
        print("=" * 80)
        
        if not successful_bindings:
            print("❌ 未找到成功的券绑定案例进行对比")
            return
        
        # 选择最相关的成功案例
        best_match = successful_bindings[0]  # 暂时选择第一个
        
        print(f"🎯 选择对比的成功案例:")
        print(f"   券码: {best_match['voucher_codes']}")
        print(f"   抵扣金额: {best_match['discount_amount']}")
        print(f"   时间: {best_match['request']['timestamp']}")
        
        # 提取成功案例的参数
        success_params = self.extract_request_parameters(best_match['request'])
        success_headers = {h['name']: h['value'] for h in best_match['request']['headers']}
        
        print(f"\n📋 参数对比分析:")
        print(f"{'参数名称':<20} {'成功案例':<25} {'当前失败案例':<25} {'差异':<10}")
        print("-" * 90)
        
        # 当前失败案例的参数（基于我们的实现）
        current_params = {
            'order_id': self.current_failure['order_id'],
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'card_id': '',
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'use_rewards': 'Y',
            'use_limit_cards': 'N',
            'limit_cards': '[]',
            'voucher_code': self.current_failure['voucher_code'],
            'voucher_code_type': 'VGC_T',
            'ticket_pack_goods': ' '
        }
        
        # 对比参数
        all_params = set(success_params.keys()) | set(current_params.keys())
        differences = []
        
        for param in sorted(all_params):
            success_val = success_params.get(param, '缺失')
            current_val = current_params.get(param, '缺失')
            
            if success_val != current_val:
                diff_status = "❌ 不同"
                differences.append({
                    'param': param,
                    'success_value': success_val,
                    'current_value': current_val
                })
            else:
                diff_status = "✅ 相同"
            
            # 截断长值用于显示
            success_display = str(success_val)[:22] + "..." if len(str(success_val)) > 25 else str(success_val)
            current_display = str(current_val)[:22] + "..." if len(str(current_val)) > 25 else str(current_val)
            
            print(f"{param:<20} {success_display:<25} {current_display:<25} {diff_status:<10}")
        
        return differences, success_params, best_match
    
    def analyze_request_sequence(self, voucher_requests):
        """分析请求序列"""
        print(f"\n🔄 分析请求序列")
        print("=" * 80)
        
        print("📋 券相关请求时序:")
        for i, req in enumerate(voucher_requests, 1):
            timestamp = req['timestamp']
            method = req['method']
            url_parts = req['url'].split('/')
            endpoint = '/'.join(url_parts[-2:]) if len(url_parts) >= 2 else req['url']
            status = req['response_status']
            
            print(f"   {i}. {timestamp} - {method} {endpoint} (状态: {status})")
            
            # 如果是POST请求，显示关键参数
            if method == 'POST':
                params = self.extract_request_parameters(req)
                if 'voucher_code' in params:
                    print(f"      券码: {params['voucher_code']}")
                if 'order_id' in params:
                    print(f"      订单: {params['order_id']}")
        
        return voucher_requests

def main():
    """主函数"""
    print("🎬 沃美影城券绑定失败根本原因分析")
    print("🎯 通过HAR文件对比找出成功案例与失败案例的差异")
    print("=" * 80)
    
    analyzer = VoucherBindingAnalyzer()
    
    print(f"📋 当前失败案例:")
    print(f"   订单号: {analyzer.current_failure['order_id']}")
    print(f"   影院: {analyzer.current_failure['cinema_name']} (ID: {analyzer.current_failure['cinema_id']})")
    print(f"   券码: {analyzer.current_failure['voucher_code']}")
    print(f"   错误: {analyzer.current_failure['error_code']}, {analyzer.current_failure['error_message']}")
    
    # 1. 加载HAR文件
    har_data = analyzer.load_har_file()
    if not har_data:
        return False
    
    # 2. 提取券相关请求
    voucher_requests = analyzer.extract_voucher_related_requests(har_data)
    if not voucher_requests:
        print("❌ 未找到券相关请求")
        return False
    
    # 3. 分析请求序列
    analyzer.analyze_request_sequence(voucher_requests)
    
    # 4. 分析成功的券绑定
    successful_bindings = analyzer.analyze_successful_voucher_binding(voucher_requests)
    
    # 5. 对比分析
    if successful_bindings:
        differences, success_params, best_match = analyzer.compare_with_current_failure(successful_bindings)
        
        # 6. 生成分析报告
        generate_analysis_report(analyzer, differences, success_params, best_match)
    else:
        print("❌ 未找到成功的券绑定案例")
    
    return True

def generate_analysis_report(analyzer, differences, success_params, best_match):
    """生成分析报告"""
    print(f"\n📋 券绑定失败根本原因分析报告")
    print("=" * 80)
    
    print(f"🎯 关键发现:")
    
    if differences:
        print(f"   发现 {len(differences)} 个参数差异:")
        for diff in differences:
            print(f"   - {diff['param']}: 成功案例='{diff['success_value']}', 当前='{diff['current_value']}'")
    else:
        print(f"   ✅ 所有参数与成功案例一致")
    
    print(f"\n💡 可能的失败原因:")
    
    reasons = [
        {
            "原因": "券码状态问题",
            "描述": "券码可能已被使用、过期或不适用于当前影院",
            "验证方法": "检查券码在用户券列表中的状态"
        },
        {
            "原因": "订单状态问题", 
            "描述": "订单可能不在可绑定券的状态",
            "验证方法": "检查订单状态是否为PENDING"
        },
        {
            "原因": "影院特定限制",
            "描述": "券码可能不适用于北京沃美世界城店",
            "验证方法": "在其他影院测试相同券码"
        },
        {
            "原因": "时序依赖问题",
            "描述": "可能需要特定的前置步骤",
            "验证方法": "按HAR文件中的完整序列执行"
        }
    ]
    
    for i, reason in enumerate(reasons, 1):
        print(f"\n{i}. {reason['原因']}:")
        print(f"   描述: {reason['描述']}")
        print(f"   验证方法: {reason['验证方法']}")
    
    print(f"\n🔧 建议的解决方案:")
    print(f"   1. 验证券码在当前影院的可用性")
    print(f"   2. 检查订单状态是否支持券绑定")
    print(f"   3. 尝试在成功案例的影院进行测试")
    print(f"   4. 按HAR文件中的完整流程执行券绑定")

if __name__ == "__main__":
    main()
