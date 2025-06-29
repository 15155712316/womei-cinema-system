#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析沃美下单以后选优惠券的完整HAR文件
从选座下单到优惠券使用的完整业务流程分析
"""

import json
import base64
from urllib.parse import unquote, parse_qs, urlparse
from datetime import datetime
import os

class CompleteVoucherHARAnalyzer:
    """完整优惠券流程HAR分析器"""
    
    def __init__(self):
        self.har_file = "沃美下单以后选优惠券ct.womovie.cn_2025_06_25_15_20_11.har"
        self.har_data = None
        self.api_requests = []
        self.business_flow = []
        
        # 已实现的接口（基于现有代码分析）
        self.implemented_apis = {
            # 基础接口
            '/cities/': '✅已实现',
            '/cinemas/': '✅已实现', 
            '/movies/': '✅已实现',
            '/seats/': '✅已实现',
            '/order/ticket/': '✅已实现',
            '/order/info/': '✅已实现',
            
            # 券相关接口（昨天验证过）
            '/user/voucher/list/': '✅已实现',
            '/order/voucher/price/': '✅已实现',
            '/order/change/': '✅已实现',
            
            # 其他接口
            '/tenant/info/': '✅已实现',
        }
    
    def load_har_data(self):
        """加载HAR数据"""
        try:
            if not os.path.exists(self.har_file):
                print(f"❌ HAR文件不存在: {self.har_file}")
                return False
            
            with open(self.har_file, 'r', encoding='utf-8') as f:
                self.har_data = json.load(f)
            
            print(f"✅ HAR文件加载成功: {self.har_file}")
            return True
        except Exception as e:
            print(f"❌ HAR文件加载失败: {e}")
            return False
    
    def decode_content(self, content_data):
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
    
    def parse_form_data(self, form_data):
        """解析表单数据"""
        if not form_data:
            return {}
        
        try:
            decoded_data = unquote(form_data)
            pairs = decoded_data.split('&')
            result = {}
            for pair in pairs:
                if '=' in pair:
                    key, value = pair.split('=', 1)
                    result[key] = value
            return result
        except Exception as e:
            return {}
    
    def identify_business_type(self, url, method, params=None):
        """识别业务类型"""
        if '/cities/' in url:
            return "城市列表查询"
        elif '/cinemas/' in url:
            return "影院列表查询"
        elif '/movies/' in url:
            return "电影和场次查询"
        elif '/seats/' in url:
            return "座位信息查询"
        elif '/order/ticket/' in url:
            return "创建订单"
        elif '/order/info/' in url:
            return "订单信息查询"
        elif '/user/voucher/list/' in url:
            return "用户券列表查询"
        elif '/order/voucher/price/' in url:
            return "券价格计算"
        elif '/order/change/' in url:
            if params and params.get('voucher_code'):
                return "券绑定到订单"
            else:
                return "订单修改"
        elif '/tenant/info/' in url:
            return "租户信息查询"
        elif '/user/info/' in url:
            return "用户信息查询"
        elif '/user/balance/' in url:
            return "用户余额查询"
        elif '/order/pay/' in url:
            return "订单支付"
        elif '/order/cancel/' in url:
            return "订单取消"
        elif '/order/refund/' in url:
            return "订单退款"
        elif '/marketing/' in url:
            return "营销活动查询"
        elif '/coupon/' in url:
            return "优惠券相关"
        elif '/rewards/' in url:
            return "积分相关"
        elif '/member/' in url:
            return "会员相关"
        else:
            return "其他接口"
    
    def extract_api_requests(self):
        """提取API请求"""
        if not self.har_data:
            return
        
        entries = self.har_data['log']['entries']
        
        for i, entry in enumerate(entries):
            request = entry['request']
            response = entry['response']
            
            # 只分析沃美相关的API请求
            if 'womovie.cn' not in request['url']:
                continue
            
            # 解析URL
            parsed_url = urlparse(request['url'])
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # 解析POST数据
            post_params = {}
            if request['method'] == 'POST' and 'postData' in request:
                post_data = self.decode_content(request.get('postData', {}))
                post_params = self.parse_form_data(post_data)
            
            # 解析响应
            response_content = self.decode_content(response.get('content', {}))
            response_json = None
            try:
                if response_content:
                    response_json = json.loads(response_content)
            except:
                pass
            
            # 识别业务类型
            business_type = self.identify_business_type(request['url'], request['method'], post_params)
            
            # 判断实现状态
            implementation_status = self.get_implementation_status(path)
            
            api_info = {
                'index': i + 1,
                'timestamp': entry['startedDateTime'],
                'method': request['method'],
                'url': request['url'],
                'path': path,
                'query_params': query_params,
                'post_params': post_params,
                'business_type': business_type,
                'implementation_status': implementation_status,
                'response_status': response['status'],
                'response_json': response_json,
                'headers': {h['name']: h['value'] for h in request['headers']},
                'response_size': response.get('bodySize', 0)
            }
            
            self.api_requests.append(api_info)
    
    def get_implementation_status(self, path):
        """获取接口实现状态"""
        for api_pattern, status in self.implemented_apis.items():
            if api_pattern in path:
                return status
        return '❌未实现'
    
    def analyze_business_flow(self):
        """分析业务流程"""
        if not self.api_requests:
            return
        
        print("\n🎬 沃美影城完整业务流程分析")
        print("🎯 从选座下单到优惠券使用的完整流程")
        print("=" * 80)
        
        current_phase = ""
        phase_requests = []
        
        for req in self.api_requests:
            # 识别业务阶段
            new_phase = self.identify_business_phase(req['business_type'])
            
            if new_phase != current_phase:
                if phase_requests:
                    self.print_phase_summary(current_phase, phase_requests)
                    phase_requests = []
                current_phase = new_phase
                print(f"\n📋 {current_phase}")
                print("-" * 60)
            
            phase_requests.append(req)
            
            # 打印请求详情
            self.print_request_detail(req)
        
        # 打印最后一个阶段
        if phase_requests:
            self.print_phase_summary(current_phase, phase_requests)
    
    def identify_business_phase(self, business_type):
        """识别业务阶段"""
        if business_type in ["城市列表查询", "影院列表查询", "电影和场次查询"]:
            return "阶段1: 选择影院和场次"
        elif business_type in ["座位信息查询"]:
            return "阶段2: 选择座位"
        elif business_type in ["创建订单", "订单信息查询"]:
            return "阶段3: 创建订单"
        elif business_type in ["用户券列表查询", "券价格计算", "券绑定到订单"]:
            return "阶段4: 优惠券使用"
        elif business_type in ["订单支付"]:
            return "阶段5: 订单支付"
        elif business_type in ["用户信息查询", "租户信息查询"]:
            return "阶段0: 初始化和认证"
        else:
            return "其他业务"
    
    def print_request_detail(self, req):
        """打印请求详情"""
        timestamp = datetime.fromisoformat(req['timestamp'].replace('Z', '+00:00'))
        time_str = timestamp.strftime('%H:%M:%S.%f')[:-3]
        
        print(f"   {req['index']:2d}. [{time_str}] {req['method']:4s} {req['business_type']}")
        print(f"       URL: {req['path']}")
        print(f"       状态: {req['implementation_status']}")
        print(f"       响应: {req['response_status']}")
        
        # 显示关键参数
        if req['post_params']:
            key_params = self.extract_key_params(req['post_params'], req['business_type'])
            if key_params:
                print(f"       参数: {key_params}")
        
        # 显示关键响应数据
        if req['response_json']:
            key_response = self.extract_key_response(req['response_json'], req['business_type'])
            if key_response:
                print(f"       响应: {key_response}")
        
        print()
    
    def extract_key_params(self, params, business_type):
        """提取关键参数"""
        if business_type == "创建订单":
            return f"座位: {params.get('seatlable', 'N/A')}, 场次: {params.get('schedule_id', 'N/A')}"
        elif business_type == "券价格计算":
            return f"券码: {params.get('voucher_code', 'N/A')}, 订单: {params.get('order_id', 'N/A')}"
        elif business_type == "券绑定到订单":
            return f"券码: {params.get('voucher_code', 'N/A')}, 类型: {params.get('discount_type', 'N/A')}"
        return ""
    
    def extract_key_response(self, response, business_type):
        """提取关键响应数据"""
        if not isinstance(response, dict):
            return ""
        
        ret = response.get('ret', 'N/A')
        sub = response.get('sub', 'N/A')
        msg = response.get('msg', 'N/A')
        
        base_info = f"ret={ret}, sub={sub}"
        
        if business_type == "创建订单":
            data = response.get('data', {})
            order_id = data.get('order_id', 'N/A') if isinstance(data, dict) else 'N/A'
            return f"{base_info}, 订单ID: {order_id}"
        elif business_type in ["券价格计算", "券绑定到订单"]:
            return f"{base_info}, msg: {msg}"
        elif business_type == "用户券列表查询":
            data = response.get('data', {})
            if isinstance(data, dict):
                unused = len(data.get('unused', []))
                return f"{base_info}, 可用券: {unused}张"
        
        return base_info
    
    def print_phase_summary(self, phase, requests):
        """打印阶段总结"""
        print(f"\n   📊 {phase} 总结:")
        print(f"      请求数量: {len(requests)}")
        
        implemented = sum(1 for req in requests if '✅' in req['implementation_status'])
        not_implemented = sum(1 for req in requests if '❌' in req['implementation_status'])
        partial = sum(1 for req in requests if '🔶' in req['implementation_status'])
        
        print(f"      实现状态: ✅{implemented} / 🔶{partial} / ❌{not_implemented}")
        
        if not_implemented > 0:
            missing_apis = [req['business_type'] for req in requests if '❌' in req['implementation_status']]
            print(f"      缺失接口: {', '.join(set(missing_apis))}")
    
    def generate_implementation_report(self):
        """生成实现状态报告"""
        print(f"\n📋 接口实现状态详细报告")
        print("=" * 80)
        
        # 按业务类型分组
        business_groups = {}
        for req in self.api_requests:
            business_type = req['business_type']
            if business_type not in business_groups:
                business_groups[business_type] = []
            business_groups[business_type].append(req)
        
        # 统计实现状态
        total_apis = len(self.api_requests)
        implemented = sum(1 for req in self.api_requests if '✅' in req['implementation_status'])
        not_implemented = sum(1 for req in self.api_requests if '❌' in req['implementation_status'])
        partial = sum(1 for req in self.api_requests if '🔶' in req['implementation_status'])
        
        print(f"📊 总体实现状态:")
        print(f"   总接口数: {total_apis}")
        print(f"   ✅ 已实现: {implemented} ({implemented/total_apis*100:.1f}%)")
        print(f"   🔶 部分实现: {partial} ({partial/total_apis*100:.1f}%)")
        print(f"   ❌ 未实现: {not_implemented} ({not_implemented/total_apis*100:.1f}%)")
        
        print(f"\n📋 按业务类型分类:")
        for business_type, requests in sorted(business_groups.items()):
            unique_paths = set(req['path'] for req in requests)
            status = requests[0]['implementation_status']  # 同类型接口状态应该相同
            
            print(f"   {status} {business_type}")
            print(f"      调用次数: {len(requests)}")
            print(f"      接口路径: {', '.join(unique_paths)}")
            
            # 显示优先级
            priority = self.get_api_priority(business_type)
            print(f"      优先级: {priority}")
            print()
    
    def get_api_priority(self, business_type):
        """获取API优先级"""
        high_priority = [
            "创建订单", "订单信息查询", "座位信息查询",
            "用户券列表查询", "券价格计算", "券绑定到订单"
        ]
        
        medium_priority = [
            "城市列表查询", "影院列表查询", "电影和场次查询",
            "订单支付", "用户信息查询"
        ]
        
        if business_type in high_priority:
            return "🔴 高优先级"
        elif business_type in medium_priority:
            return "🟡 中优先级"
        else:
            return "🟢 低优先级"

    def compare_with_existing_code(self):
        """对比现有代码实现"""
        print(f"\n🔍 与现有代码实现对比分析")
        print("=" * 80)

        # 检查主要服务文件
        service_files = [
            'services/womei_cinema_service.py',
            'services/womei_film_service.py',
            'services/womei_order_service.py',
            'services/womei_voucher_service.py',
            'main_modular.py'
        ]

        print(f"📁 检查现有服务文件:")
        for file_path in service_files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path}")
            else:
                print(f"   ❌ {file_path} (不存在)")

        print(f"\n🎯 基于昨天券使用流程验证的更新:")
        print(f"   ✅ POST /order/change/ 接口已完全验证")
        print(f"   ✅ 券价格计算接口已验证")
        print(f"   ✅ 券列表查询接口已验证")
        print(f"   ✅ 订单信息查询接口已验证")

        # 分析未实现的关键接口
        missing_critical = []
        for req in self.api_requests:
            if '❌' in req['implementation_status'] and '高优先级' in self.get_api_priority(req['business_type']):
                missing_critical.append(req)

        if missing_critical:
            print(f"\n🚨 缺失的高优先级接口:")
            for req in missing_critical:
                print(f"   ❌ {req['business_type']} - {req['path']}")
        else:
            print(f"\n✅ 所有高优先级接口都已实现")

    def generate_implementation_suggestions(self):
        """生成实现建议"""
        print(f"\n💡 实现建议和优先级排序")
        print("=" * 80)

        # 按优先级分组未实现的接口
        high_priority_missing = []
        medium_priority_missing = []
        low_priority_missing = []

        for req in self.api_requests:
            if '❌' in req['implementation_status']:
                priority = self.get_api_priority(req['business_type'])
                if '🔴' in priority:
                    high_priority_missing.append(req)
                elif '🟡' in priority:
                    medium_priority_missing.append(req)
                else:
                    low_priority_missing.append(req)

        if high_priority_missing:
            print(f"🔴 高优先级实现建议:")
            for req in high_priority_missing:
                print(f"   1. {req['business_type']}")
                print(f"      路径: {req['path']}")
                print(f"      建议: 立即实现，影响核心业务流程")
                print()

        if medium_priority_missing:
            print(f"🟡 中优先级实现建议:")
            for req in medium_priority_missing:
                print(f"   2. {req['business_type']}")
                print(f"      路径: {req['path']}")
                print(f"      建议: 后续版本实现，提升用户体验")
                print()

        if low_priority_missing:
            print(f"🟢 低优先级实现建议:")
            for req in low_priority_missing:
                print(f"   3. {req['business_type']}")
                print(f"      路径: {req['path']}")
                print(f"      建议: 可选实现，非核心功能")
                print()

        # 优化建议
        print(f"🚀 优化建议:")
        print(f"   1. 接口合并机会: 分析是否可以合并相似功能的接口")
        print(f"   2. 缓存策略: 对频繁调用的接口实现缓存")
        print(f"   3. 错误处理: 统一错误处理和重试机制")
        print(f"   4. 性能优化: 减少不必要的API调用")

    def save_analysis_report(self):
        """保存分析报告"""
        report_data = {
            'analysis_time': datetime.now().isoformat(),
            'har_file': self.har_file,
            'total_requests': len(self.api_requests),
            'business_flow': self.business_flow,
            'api_requests': self.api_requests,
            'implementation_summary': {
                'total': len(self.api_requests),
                'implemented': sum(1 for req in self.api_requests if '✅' in req['implementation_status']),
                'partial': sum(1 for req in self.api_requests if '🔶' in req['implementation_status']),
                'not_implemented': sum(1 for req in self.api_requests if '❌' in req['implementation_status'])
            }
        }

        with open('complete_voucher_har_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 分析报告已保存到: complete_voucher_har_analysis.json")

    def run_analysis(self):
        """运行完整分析"""
        print("🎬 沃美影城完整业务流程HAR分析")
        print("🎯 从选座下单到优惠券使用的完整流程分析")
        print("=" * 80)

        # 加载HAR数据
        if not self.load_har_data():
            return

        # 提取API请求
        self.extract_api_requests()

        if not self.api_requests:
            print("❌ 未找到有效的API请求")
            return

        print(f"✅ 成功提取 {len(self.api_requests)} 个API请求")

        # 分析业务流程
        self.analyze_business_flow()

        # 生成实现状态报告
        self.generate_implementation_report()

        # 对比现有代码
        self.compare_with_existing_code()

        # 生成实现建议
        self.generate_implementation_suggestions()

        # 保存分析报告
        self.save_analysis_report()

def main():
    """主函数"""
    analyzer = CompleteVoucherHARAnalyzer()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()
