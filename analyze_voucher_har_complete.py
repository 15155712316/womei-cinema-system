#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美电影院系统优惠券使用流程完整性分析工具
基于HAR文件分析优惠券相关API调用序列，对比项目实现情况
"""

import json
import base64
import urllib.parse
from typing import Dict, List, Any
import os

class VoucherHARAnalyzer:
    def __init__(self, har_file_path: str):
        self.har_file_path = har_file_path
        self.har_data = None
        self.voucher_apis = []
        self.api_sequence = []
        
    def load_har_file(self):
        """加载HAR文件"""
        try:
            with open(self.har_file_path, 'r', encoding='utf-8') as f:
                self.har_data = json.load(f)
            print(f"✅ 成功加载HAR文件: {self.har_file_path}")
            return True
        except Exception as e:
            print(f"❌ 加载HAR文件失败: {e}")
            return False
    
    def decode_base64_content(self, content_text: str) -> str:
        """解码base64内容"""
        try:
            decoded_bytes = base64.b64decode(content_text)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            print(f"⚠️ Base64解码失败: {e}")
            return content_text
    
    def extract_voucher_related_apis(self):
        """提取优惠券相关的API调用"""
        if not self.har_data:
            return
        
        entries = self.har_data.get('log', {}).get('entries', [])
        
        for entry in entries:
            request = entry.get('request', {})
            response = entry.get('response', {})
            url = request.get('url', '')
            method = request.get('method', '')
            
            # 识别优惠券相关的API
            if self.is_voucher_related_api(url):
                api_info = {
                    'url': url,
                    'method': method,
                    'headers': request.get('headers', []),
                    'query_params': request.get('queryString', []),
                    'post_data': request.get('postData', {}),
                    'response_status': response.get('status', 0),
                    'response_content': self.extract_response_content(response),
                    'timestamp': entry.get('startedDateTime', ''),
                    'time': entry.get('time', 0)
                }
                self.voucher_apis.append(api_info)
                
        print(f"✅ 提取到 {len(self.voucher_apis)} 个优惠券相关API调用")
    
    def is_voucher_related_api(self, url: str) -> bool:
        """判断是否为优惠券相关API"""
        voucher_keywords = [
            'voucher', 'vouchers', 'vcc', 'coupon', 'discount',
            'user/vouchers', 'order/voucher', 'order/change',
            'usable/count', 'price'
        ]
        
        url_lower = url.lower()
        return any(keyword in url_lower for keyword in voucher_keywords)
    
    def extract_response_content(self, response: Dict) -> Dict:
        """提取响应内容"""
        content = response.get('content', {})
        content_text = content.get('text', '')
        encoding = content.get('encoding', '')
        
        if encoding == 'base64' and content_text:
            decoded_content = self.decode_base64_content(content_text)
            try:
                return json.loads(decoded_content)
            except:
                return {'raw_content': decoded_content}
        elif content_text:
            try:
                return json.loads(content_text)
            except:
                return {'raw_content': content_text}
        
        return {}
    
    def analyze_api_sequence(self):
        """分析API调用序列"""
        print("\n📋 优惠券相关API调用序列分析:")
        print("=" * 80)
        
        for i, api in enumerate(self.voucher_apis, 1):
            url_path = urllib.parse.urlparse(api['url']).path
            query_params = {param['name']: param['value'] for param in api['query_params']}
            
            print(f"\n{i}. {api['method']} {url_path}")
            print(f"   时间戳: {api['timestamp']}")
            print(f"   响应状态: {api['response_status']}")
            
            if query_params:
                print(f"   查询参数: {query_params}")
            
            # 分析响应内容
            response_content = api['response_content']
            if isinstance(response_content, dict):
                if 'ret' in response_content:
                    print(f"   响应结果: ret={response_content.get('ret')}, sub={response_content.get('sub')}")
                    print(f"   响应消息: {response_content.get('msg', 'N/A')}")
                
                if 'data' in response_content:
                    data = response_content['data']
                    if isinstance(data, list):
                        print(f"   数据条数: {len(data)}")
                        if data and isinstance(data[0], dict):
                            # 显示第一条数据的关键字段
                            first_item = data[0]
                            key_fields = ['voucher_code', 'voucher_name', 'status', 'voucher_balance']
                            for field in key_fields:
                                if field in first_item:
                                    print(f"   {field}: {first_item[field]}")
                    else:
                        print(f"   数据内容: {data}")
            
            print("-" * 60)
    
    def categorize_apis(self) -> Dict[str, List]:
        """对API进行分类"""
        categories = {
            'voucher_list': [],      # 优惠券列表
            'voucher_count': [],     # 优惠券数量统计
            'voucher_price': [],     # 优惠券价格计算
            'voucher_bind': [],      # 优惠券绑定/使用
            'order_change': [],      # 订单修改
            'other': []              # 其他
        }
        
        for api in self.voucher_apis:
            url = api['url'].lower()
            
            if 'user/vouchers' in url:
                categories['voucher_list'].append(api)
            elif 'usable/count' in url:
                categories['voucher_count'].append(api)
            elif 'voucher/price' in url:
                categories['voucher_price'].append(api)
            elif 'order/change' in url:
                categories['order_change'].append(api)
            elif 'voucher' in url and ('bind' in url or 'use' in url):
                categories['voucher_bind'].append(api)
            else:
                categories['other'].append(api)
        
        return categories
    
    def generate_analysis_report(self):
        """生成分析报告"""
        categories = self.categorize_apis()
        
        print("\n📊 API分类统计:")
        print("=" * 80)
        
        for category, apis in categories.items():
            if apis:
                print(f"\n{category.upper()} ({len(apis)}个):")
                for api in apis:
                    url_path = urllib.parse.urlparse(api['url']).path
                    print(f"  - {api['method']} {url_path}")
        
        # 分析完整的优惠券使用流程
        print("\n🔄 优惠券使用流程分析:")
        print("=" * 80)
        
        workflow_steps = [
            "1. 获取可用优惠券列表 (user/vouchers)",
            "2. 查询优惠券可用数量 (usable/count)", 
            "3. 计算优惠券价格/折扣 (voucher/price)",
            "4. 绑定/使用优惠券 (order/change)",
            "5. 确认订单变更结果"
        ]
        
        for step in workflow_steps:
            print(f"  {step}")
        
        # 检查流程完整性
        print("\n✅ 流程完整性检查:")
        print("=" * 80)
        
        has_voucher_list = len(categories['voucher_list']) > 0
        has_voucher_count = len(categories['voucher_count']) > 0
        has_voucher_price = len(categories['voucher_price']) > 0
        has_order_change = len(categories['order_change']) > 0
        
        print(f"  优惠券列表获取: {'✅' if has_voucher_list else '❌'}")
        print(f"  优惠券数量统计: {'✅' if has_voucher_count else '❌'}")
        print(f"  优惠券价格计算: {'✅' if has_voucher_price else '❌'}")
        print(f"  订单变更处理: {'✅' if has_order_change else '❌'}")
        
        completeness_score = sum([has_voucher_list, has_voucher_count, has_voucher_price, has_order_change])
        print(f"\n  流程完整性评分: {completeness_score}/4 ({completeness_score/4*100:.1f}%)")
        
        return categories

def main():
    """主函数"""
    har_file = "沃美下单以后选优惠券ct.womovie.cn_2025_06_25_15_20_11.har"
    
    if not os.path.exists(har_file):
        print(f"❌ HAR文件不存在: {har_file}")
        return
    
    analyzer = VoucherHARAnalyzer(har_file)
    
    # 加载HAR文件
    if not analyzer.load_har_file():
        return
    
    # 提取优惠券相关API
    analyzer.extract_voucher_related_apis()
    
    # 分析API调用序列
    analyzer.analyze_api_sequence()
    
    # 生成分析报告
    categories = analyzer.generate_analysis_report()
    
    # 保存分析结果
    output_file = "voucher_har_analysis_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_apis': len(analyzer.voucher_apis),
            'categories': {k: len(v) for k, v in categories.items()},
            'api_details': analyzer.voucher_apis
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 分析结果已保存到: {output_file}")

if __name__ == "__main__":
    main()
