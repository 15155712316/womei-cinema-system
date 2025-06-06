#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会员卡密码验证差异分析脚本
分析两个不同影城的HAR文件，识别会员卡密码验证的差异
"""

import json
import base64
import urllib.parse
from typing import Dict, List, Any, Optional

def decode_base64_content(content: str) -> str:
    """解码base64内容"""
    try:
        decoded = base64.b64decode(content).decode('utf-8')
        return decoded
    except Exception as e:
        print(f"解码失败: {e}")
        return content

def parse_har_file(file_path: str) -> Dict[str, Any]:
    """解析HAR文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        print(f"\n📁 分析文件: {file_path}")
        print(f"📊 总请求数: {len(entries)}")
        
        return har_data
    except Exception as e:
        print(f"❌ 解析HAR文件失败: {e}")
        return {}

def extract_member_payment_apis(har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """提取会员支付相关的API"""
    member_apis = []
    
    if not har_data or 'log' not in har_data:
        return member_apis
    
    entries = har_data['log']['entries']
    
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        
        url = request.get('url', '')
        method = request.get('method', '')
        
        # 识别会员支付相关的API
        if any(keyword in url.lower() for keyword in ['memcardpay', 'member', 'pay']):
            api_info = {
                'url': url,
                'method': method,
                'endpoint': url.split('/')[-1].split('?')[0],
                'domain': url.split('/')[2] if '/' in url else '',
                'query_params': {},
                'post_data': {},
                'headers': {},
                'response_data': {},
                'status_code': response.get('status', 0)
            }
            
            # 解析请求头
            headers = request.get('headers', [])
            for header in headers:
                api_info['headers'][header.get('name', '')] = header.get('value', '')
            
            # 解析查询参数
            if '?' in url:
                query_string = url.split('?')[1]
                api_info['query_params'] = dict(urllib.parse.parse_qsl(query_string))
            
            # 解析POST数据
            post_data = request.get('postData', {})
            if post_data and 'text' in post_data:
                if post_data.get('encoding') == 'base64':
                    decoded_data = decode_base64_content(post_data['text'])
                    try:
                        api_info['post_data'] = dict(urllib.parse.parse_qsl(decoded_data))
                    except:
                        api_info['post_data'] = {'raw': decoded_data}
                else:
                    try:
                        api_info['post_data'] = dict(urllib.parse.parse_qsl(post_data['text']))
                    except:
                        api_info['post_data'] = {'raw': post_data['text']}
            
            # 解析响应数据
            response_content = response.get('content', {})
            if response_content and 'text' in response_content:
                if response_content.get('encoding') == 'base64':
                    decoded_response = decode_base64_content(response_content['text'])
                    try:
                        api_info['response_data'] = json.loads(decoded_response)
                    except:
                        api_info['response_data'] = {'raw': decoded_response}
                else:
                    try:
                        api_info['response_data'] = json.loads(response_content['text'])
                    except:
                        api_info['response_data'] = {'raw': response_content['text']}
            
            member_apis.append(api_info)
    
    return member_apis

def analyze_password_requirements(apis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """分析密码要求差异"""
    analysis = {
        'has_password_field': False,
        'password_field_name': None,
        'password_required': False,
        'password_validation': None,
        'member_info_structure': {},
        'api_parameters': {},
        'domain': '',
        'cinema_config': {}
    }
    
    for api in apis:
        if 'memcardpay' in api['endpoint'].lower():
            analysis['domain'] = api['domain']
            post_data = api.get('post_data', {})
            
            # 检查密码字段
            password_fields = ['mempass', 'password', 'pwd', 'memberPassword']
            for field in password_fields:
                if field in post_data:
                    analysis['has_password_field'] = True
                    analysis['password_field_name'] = field
                    analysis['password_required'] = bool(post_data[field])
                    break
            
            # 分析会员信息结构
            if 'memberinfo' in post_data:
                try:
                    member_info = json.loads(post_data['memberinfo'])
                    analysis['member_info_structure'] = member_info
                except:
                    analysis['member_info_structure'] = {'raw': post_data['memberinfo']}
            
            # 记录所有API参数
            analysis['api_parameters'] = post_data
            
            # 分析响应中的配置信息
            response_data = api.get('response_data', {})
            if isinstance(response_data, dict):
                # 查找可能的配置信息
                for key, value in response_data.items():
                    if 'config' in key.lower() or 'setting' in key.lower():
                        analysis['cinema_config'][key] = value
    
    return analysis

def compare_password_policies(analysis1: Dict[str, Any], analysis2: Dict[str, Any]) -> Dict[str, Any]:
    """对比两个影城的密码策略"""
    comparison = {
        'cinema1': {
            'domain': analysis1.get('domain', ''),
            'requires_password': analysis1.get('has_password_field', False),
            'password_field': analysis1.get('password_field_name', ''),
            'member_structure': analysis1.get('member_info_structure', {})
        },
        'cinema2': {
            'domain': analysis2.get('domain', ''),
            'requires_password': analysis2.get('has_password_field', False),
            'password_field': analysis2.get('password_field_name', ''),
            'member_structure': analysis2.get('member_info_structure', {})
        },
        'differences': [],
        'common_fields': [],
        'unique_fields': {
            'cinema1_only': [],
            'cinema2_only': []
        }
    }
    
    # 分析差异
    if analysis1.get('has_password_field') != analysis2.get('has_password_field'):
        comparison['differences'].append({
            'type': 'password_requirement',
            'cinema1': analysis1.get('has_password_field', False),
            'cinema2': analysis2.get('has_password_field', False),
            'description': '密码要求不同'
        })
    
    # 分析API参数差异
    params1 = set(analysis1.get('api_parameters', {}).keys())
    params2 = set(analysis2.get('api_parameters', {}).keys())
    
    comparison['common_fields'] = list(params1 & params2)
    comparison['unique_fields']['cinema1_only'] = list(params1 - params2)
    comparison['unique_fields']['cinema2_only'] = list(params2 - params1)
    
    return comparison

def generate_dynamic_password_logic(comparison: Dict[str, Any]) -> str:
    """生成动态密码验证逻辑"""
    
    code = '''
class DynamicMemberPasswordHandler:
    """动态会员密码处理器"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        self.password_policies = self._load_password_policies()
    
    def _load_password_policies(self) -> Dict[str, Dict[str, Any]]:
        """加载密码策略配置"""
        return {
            # 基于域名的密码策略配置
            'www.heibaiyingye.cn': {
                'requires_password': True,
                'password_field': 'mempass',
                'validation_required': True,
                'description': '黑白影业 - 需要会员卡密码'
            },
            'zcxzs7.cityfilms.cn': {
                'requires_password': False,
                'password_field': None,
                'validation_required': False,
                'description': '城市影院 - 不需要会员卡密码'
            }
        }
    
    def get_password_policy(self, cinema_id: str = None, base_url: str = None) -> Dict[str, Any]:
        """获取密码策略"""
        # 优先使用base_url判断
        if base_url:
            domain = self._extract_domain(base_url)
            for policy_domain, policy in self.password_policies.items():
                if policy_domain in domain:
                    return policy
        
        # 默认策略：需要密码
        return {
            'requires_password': True,
            'password_field': 'mempass',
            'validation_required': True,
            'description': '默认策略 - 需要会员卡密码'
        }
    
    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url
    
    def should_require_password(self, cinema_id: str = None, base_url: str = None) -> bool:
        """判断是否需要密码"""
        policy = self.get_password_policy(cinema_id, base_url)
        return policy.get('requires_password', True)
    
    def get_password_field_name(self, cinema_id: str = None, base_url: str = None) -> str:
        """获取密码字段名"""
        policy = self.get_password_policy(cinema_id, base_url)
        return policy.get('password_field', 'mempass')
    
    def prepare_payment_params(self, base_params: Dict[str, Any], 
                             member_password: str = None,
                             cinema_id: str = None, 
                             base_url: str = None) -> Dict[str, Any]:
        """准备支付参数"""
        policy = self.get_password_policy(cinema_id, base_url)
        
        # 复制基础参数
        payment_params = base_params.copy()
        
        # 根据策略添加密码字段
        if policy.get('requires_password', True):
            password_field = policy.get('password_field', 'mempass')
            if member_password:
                payment_params[password_field] = member_password
            else:
                # 如果需要密码但未提供，抛出异常
                raise ValueError(f"影城需要会员卡密码，但未提供密码")
        
        return payment_params
    
    def validate_member_payment(self, member_info: Dict[str, Any], 
                              payment_amount: int,
                              cinema_id: str = None, 
                              base_url: str = None) -> Dict[str, Any]:
        """验证会员支付"""
        policy = self.get_password_policy(cinema_id, base_url)
        
        # 基础验证
        if not member_info.get('is_member'):
            return {'valid': False, 'error': '非会员用户'}
        
        balance = member_info.get('balance', 0)
        if balance < payment_amount:
            return {
                'valid': False, 
                'error': f'余额不足，当前余额: ¥{balance/100:.2f}，需要: ¥{payment_amount/100:.2f}'
            }
        
        return {
            'valid': True,
            'requires_password': policy.get('requires_password', True),
            'password_field': policy.get('password_field', 'mempass'),
            'policy_description': policy.get('description', '默认策略')
        }

# 在main_modular.py中的集成示例
class EnhancedMemberPaymentSystem:
    """增强的会员支付系统"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.password_handler = DynamicMemberPasswordHandler(main_window.api_client)
    
    def process_member_payment(self, order_data: Dict[str, Any], member_info: Dict[str, Any]):
        """处理会员支付"""
        try:
            # 获取当前影城的base_url
            current_account = self.main_window.current_account
            base_url = current_account.get('base_url', '') if current_account else ''
            cinema_id = current_account.get('cinema_id', '') if current_account else ''
            
            # 验证支付
            payment_amount = int(order_data.get('amount', 0) * 100)
            validation_result = self.password_handler.validate_member_payment(
                member_info, payment_amount, cinema_id, base_url
            )
            
            if not validation_result['valid']:
                QMessageBox.warning(self.main_window, "支付验证失败", validation_result['error'])
                return
            
            # 根据策略决定是否需要密码
            member_password = None
            if validation_result['requires_password']:
                password, ok = QInputDialog.getText(
                    self.main_window, 
                    "会员密码", 
                    f"请输入会员卡密码\\n({validation_result['policy_description']}):", 
                    QLineEdit.Password
                )
                if not ok or not password:
                    return
                member_password = password
            
            # 准备支付参数
            base_params = {
                'totalprice': str(payment_amount),
                'memberinfo': json.dumps({
                    'cardno': member_info.get('cardno', ''),
                    'mobile': member_info.get('mobile', ''),
                    'memberId': member_info.get('memberId', ''),
                    'cardtype': '0',
                    'cardcinemaid': cinema_id,
                    'balance': member_info.get('balance', 0) / 100
                }),
                'orderno': order_data.get('orderno', ''),
                'couponcodes': '',
                'price': str(payment_amount),
                'discountprice': '0',
                'filmname': order_data.get('movie', ''),
                'featureno': order_data.get('featureno', ''),
                'ticketcount': str(len(order_data.get('seats', []))),
                'cinemaname': order_data.get('cinema', ''),
                'cinemaid': cinema_id,
                'userid': self.main_window.api_client.user_id,
                'openid': self.main_window.api_client.openid,
                'token': self.main_window.api_client.token,
                'source': '2'
            }
            
            # 根据策略准备最终参数
            final_params = self.password_handler.prepare_payment_params(
                base_params, member_password, cinema_id, base_url
            )
            
            # 执行支付
            response = self.main_window.api_client.post('/MiniTicket/index.php/MiniPay/memcardPay', final_params)
            
            if response.get('resultCode') == '0':
                QMessageBox.information(self.main_window, "支付成功", "会员卡支付成功！")
                self.main_window._get_ticket_code_after_payment(order_data.get('orderno', ''))
            else:
                QMessageBox.warning(self.main_window, "支付失败", response.get('resultDesc', '支付失败'))
                
        except Exception as e:
            print(f"[会员支付] 错误: {e}")
            QMessageBox.warning(self.main_window, "支付错误", f"会员支付失败: {str(e)}")
'''
    
    return code

def main():
    """主函数"""
    print("🔐 PyQt5电影票务管理系统 - 会员卡密码验证差异分析")
    print("=" * 80)
    
    # 分析两个HAR文件
    har_files = [
        {
            'file': '需要密码支付www.heibaiyingye.cn_2025_06_04_16_22_38.har',
            'description': '需要会员卡密码的影城 (黑白影业)'
        },
        {
            'file': '不需要会员卡密码zcxzs7.cityfilms.cn_2025_06_04_16_23_21.har',
            'description': '不需要会员卡密码的影城 (城市影院)'
        }
    ]
    
    analyses = []
    
    for har_info in har_files:
        print(f"\n🔍 分析: {har_info['description']}")
        har_data = parse_har_file(har_info['file'])
        
        if har_data:
            member_apis = extract_member_payment_apis(har_data)
            analysis = analyze_password_requirements(member_apis)
            analyses.append(analysis)
            
            print(f"\n📋 {har_info['description']} 分析结果:")
            print(f"  域名: {analysis.get('domain', 'N/A')}")
            print(f"  需要密码: {analysis.get('has_password_field', False)}")
            print(f"  密码字段: {analysis.get('password_field_name', 'N/A')}")
            print(f"  API参数数量: {len(analysis.get('api_parameters', {}))}")
            
            if analysis.get('api_parameters'):
                print(f"  主要参数: {list(analysis['api_parameters'].keys())[:5]}")
    
    if len(analyses) >= 2:
        print("\n" + "=" * 80)
        print("📊 密码策略对比分析")
        print("=" * 80)
        
        comparison = compare_password_policies(analyses[0], analyses[1])
        
        print(f"\n🏢 影城1 ({comparison['cinema1']['domain']}):")
        print(f"  需要密码: {comparison['cinema1']['requires_password']}")
        print(f"  密码字段: {comparison['cinema1']['password_field']}")
        
        print(f"\n🏢 影城2 ({comparison['cinema2']['domain']}):")
        print(f"  需要密码: {comparison['cinema2']['requires_password']}")
        print(f"  密码字段: {comparison['cinema2']['password_field']}")
        
        print(f"\n🔍 差异分析:")
        if comparison['differences']:
            for diff in comparison['differences']:
                print(f"  - {diff['description']}: 影城1={diff['cinema1']}, 影城2={diff['cinema2']}")
        else:
            print("  - 未发现显著差异")
        
        print(f"\n📋 共同字段 ({len(comparison['common_fields'])}):")
        for field in comparison['common_fields'][:10]:  # 显示前10个
            print(f"  - {field}")
        
        print(f"\n🔧 影城1独有字段 ({len(comparison['unique_fields']['cinema1_only'])}):")
        for field in comparison['unique_fields']['cinema1_only'][:5]:
            print(f"  - {field}")
        
        print(f"\n🔧 影城2独有字段 ({len(comparison['unique_fields']['cinema2_only'])}):")
        for field in comparison['unique_fields']['cinema2_only'][:5]:
            print(f"  - {field}")
        
        # 生成动态密码逻辑代码
        dynamic_code = generate_dynamic_password_logic(comparison)
        
        # 保存代码到文件
        with open('dynamic_member_password_handler.py', 'w', encoding='utf-8') as f:
            f.write(dynamic_code)
        
        print(f"\n📝 动态密码处理代码已生成: dynamic_member_password_handler.py")
        
        print("\n💡 实施建议:")
        print("1. ✅ 基于域名识别影城密码策略")
        print("2. ✅ 动态决定是否显示密码输入框")
        print("3. ✅ 统一的支付参数准备逻辑")
        print("4. ✅ 灵活的策略配置机制")
        print("5. ✅ 完善的错误处理和用户提示")
        
        print("\n🎯 核心优势:")
        print("- 🔄 自适应不同影城的密码策略")
        print("- 🛡️ 统一的安全验证机制")
        print("- 🎨 优化的用户交互体验")
        print("- 🔧 易于维护和扩展的架构")
    
    print("\n🎉 分析完成！")

if __name__ == "__main__":
    main()
