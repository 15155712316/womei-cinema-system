#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件分析工具 - 专门分析沃美影院订单相关请求
"""

import json
import re
import urllib.parse
from datetime import datetime

class HARAnalyzer:
    def __init__(self, har_file_path):
        self.har_file_path = har_file_path
        self.har_data = None
        self.order_related_requests = []
        
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
    
    def analyze_requests(self):
        """分析所有请求，查找订单相关的请求"""
        if not self.har_data:
            print("❌ HAR数据未加载")
            return
        
        entries = self.har_data.get('log', {}).get('entries', [])
        print(f"📊 总请求数量: {len(entries)}")
        
        # 订单相关关键词
        order_keywords = [
            'order', 'submit', 'create', 'book', 'ticket', 'seat', 
            'pay', 'confirm', 'reserve', 'purchase', 'buy',
            '订单', '提交', '创建', '预订', '购买', '支付', '确认'
        ]
        
        for i, entry in enumerate(entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            url = request.get('url', '')
            method = request.get('method', '')
            
            # 检查URL是否包含订单相关关键词
            is_order_related = any(keyword.lower() in url.lower() for keyword in order_keywords)
            
            # 检查POST请求（通常用于提交订单）
            is_post_request = method.upper() == 'POST'
            
            # 检查请求体是否包含订单相关信息
            post_data = request.get('postData', {})
            post_text = post_data.get('text', '')
            has_order_data = any(keyword.lower() in post_text.lower() for keyword in order_keywords)
            
            if is_order_related or (is_post_request and has_order_data):
                self.order_related_requests.append({
                    'index': i,
                    'url': url,
                    'method': method,
                    'request': request,
                    'response': response,
                    'timestamp': entry.get('startedDateTime', ''),
                    'time': entry.get('time', 0)
                })
        
        print(f"🎯 找到 {len(self.order_related_requests)} 个可能与订单相关的请求")
    
    def print_request_details(self, req_data):
        """打印请求详细信息"""
        print(f"\n{'='*80}")
        print(f"📋 请求 #{req_data['index']} - {req_data['method']} {req_data['url']}")
        print(f"⏰ 时间: {req_data['timestamp']}")
        print(f"⏱️  耗时: {req_data['time']}ms")
        
        request = req_data['request']
        response = req_data['response']
        
        # 请求头
        print(f"\n📤 请求头:")
        headers = request.get('headers', [])
        for header in headers:
            print(f"  {header['name']}: {header['value']}")
        
        # 查询参数
        query_params = request.get('queryString', [])
        if query_params:
            print(f"\n🔍 查询参数:")
            for param in query_params:
                print(f"  {param['name']}: {param['value']}")
        
        # 请求体
        post_data = request.get('postData', {})
        if post_data:
            print(f"\n📝 请求体:")
            print(f"  Content-Type: {post_data.get('mimeType', 'N/A')}")
            post_text = post_data.get('text', '')
            if post_text:
                # 尝试格式化JSON
                try:
                    if post_data.get('mimeType', '').startswith('application/json'):
                        json_data = json.loads(post_text)
                        print(f"  内容: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                    else:
                        print(f"  内容: {post_text}")
                except:
                    print(f"  内容: {post_text}")
        
        # 响应信息
        print(f"\n📥 响应:")
        print(f"  状态码: {response.get('status', 'N/A')} {response.get('statusText', '')}")
        
        # 响应头
        response_headers = response.get('headers', [])
        if response_headers:
            print(f"  响应头:")
            for header in response_headers[:5]:  # 只显示前5个
                print(f"    {header['name']}: {header['value']}")
        
        # 响应内容
        content = response.get('content', {})
        if content:
            response_text = content.get('text', '')
            if response_text:
                print(f"  响应内容 (前500字符):")
                try:
                    if content.get('mimeType', '').startswith('application/json'):
                        json_data = json.loads(response_text)
                        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                        print(f"    {formatted_json[:500]}...")
                    else:
                        print(f"    {response_text[:500]}...")
                except:
                    print(f"    {response_text[:500]}...")
    
    def analyze_order_requests(self):
        """详细分析订单相关请求"""
        if not self.order_related_requests:
            print("❌ 没有找到订单相关请求")
            return
        
        print(f"\n🔍 详细分析 {len(self.order_related_requests)} 个订单相关请求:")
        
        for req_data in self.order_related_requests:
            self.print_request_details(req_data)
    
    def search_specific_patterns(self):
        """搜索特定的订单模式"""
        print(f"\n🎯 搜索特定订单模式:")
        
        patterns = {
            '座位选择': r'seat|座位|选座',
            '订单创建': r'order.*create|create.*order|订单.*创建',
            '支付相关': r'pay|payment|支付|付款',
            '确认订单': r'confirm|确认|submit.*order',
            '票务相关': r'ticket|票|cinema|影院'
        }
        
        all_entries = self.har_data.get('log', {}).get('entries', [])
        
        for pattern_name, pattern in patterns.items():
            print(f"\n📋 {pattern_name} 相关请求:")
            found_count = 0
            
            for i, entry in enumerate(all_entries):
                request = entry.get('request', {})
                url = request.get('url', '')
                post_data = request.get('postData', {}).get('text', '')
                
                if re.search(pattern, url + post_data, re.IGNORECASE):
                    found_count += 1
                    print(f"  #{i}: {request.get('method', '')} {url}")
                    if found_count >= 5:  # 限制显示数量
                        break
            
            if found_count == 0:
                print(f"  未找到相关请求")

def main():
    """主函数"""
    har_file = "沃美res.vistachina.cn_2025_06_15_15_22_27.har"
    
    print("🔍 沃美影院HAR文件分析工具")
    print("=" * 60)
    
    analyzer = HARAnalyzer(har_file)
    
    # 加载HAR文件
    if not analyzer.load_har_file():
        return
    
    # 分析请求
    analyzer.analyze_requests()
    
    # 详细分析订单相关请求
    analyzer.analyze_order_requests()
    
    # 搜索特定模式
    analyzer.search_specific_patterns()
    
    print(f"\n✅ 分析完成！")
    print(f"💡 如果没有找到订单相关请求，可能的原因：")
    print(f"   1. HAR文件记录的时间段内没有进行订单操作")
    print(f"   2. 订单API使用了不同的关键词或路径")
    print(f"   3. 需要查看更多的请求详情")

if __name__ == "__main__":
    main()
