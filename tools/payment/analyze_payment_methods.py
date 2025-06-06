#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAR文件支付方式分析脚本
分析两个HAR抓包文件，提取支付方式和API接口信息
"""

import json
import base64
import urllib.parse
from typing import Dict, List, Any

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

def analyze_payment_apis(har_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """分析支付相关的API"""
    payment_apis = []
    
    if not har_data or 'log' not in har_data:
        return payment_apis
    
    entries = har_data['log']['entries']
    
    for entry in entries:
        request = entry.get('request', {})
        response = entry.get('response', {})
        
        url = request.get('url', '')
        method = request.get('method', '')
        
        # 识别支付相关的API
        if any(keyword in url.lower() for keyword in ['pay', 'order', 'coupon', 'member']):
            api_info = {
                'url': url,
                'method': method,
                'endpoint': url.split('/')[-1].split('?')[0],
                'query_params': {},
                'post_data': {},
                'response_data': {}
            }
            
            # 解析查询参数
            if '?' in url:
                query_string = url.split('?')[1]
                api_info['query_params'] = dict(urllib.parse.parse_qsl(query_string))
            
            # 解析POST数据
            post_data = request.get('postData', {})
            if post_data and 'text' in post_data:
                if post_data.get('encoding') == 'base64':
                    decoded_data = decode_base64_content(post_data['text'])
                    api_info['post_data'] = dict(urllib.parse.parse_qsl(decoded_data))
                else:
                    api_info['post_data'] = dict(urllib.parse.parse_qsl(post_data['text']))
            
            # 解析响应数据
            response_content = response.get('content', {})
            if response_content and 'text' in response_content:
                if response_content.get('encoding') == 'base64':
                    decoded_response = decode_base64_content(response_content['text'])
                    try:
                        api_info['response_data'] = json.loads(decoded_response)
                    except:
                        api_info['response_data'] = decoded_response
                else:
                    try:
                        api_info['response_data'] = json.loads(response_content['text'])
                    except:
                        api_info['response_data'] = response_content['text']
            
            payment_apis.append(api_info)
    
    return payment_apis

def identify_payment_methods(apis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """识别支付方式"""
    payment_methods = {
        'coupon_payment': [],      # 券支付
        'member_card_payment': [], # 会员卡支付
        'mixed_payment': [],       # 混合支付
        'prepay_validation': [],   # 预支付验证
        'order_creation': [],      # 订单创建
        'member_info': []          # 会员信息
    }
    
    for api in apis:
        endpoint = api['endpoint']
        url = api['url']
        
        if 'memcardPay' in endpoint:
            payment_methods['member_card_payment'].append(api)
        elif 'ordercouponPrepay' in endpoint:
            payment_methods['prepay_validation'].append(api)
        elif 'createOrder' in endpoint:
            payment_methods['order_creation'].append(api)
        elif 'getMemberInfo' in endpoint:
            payment_methods['member_info'].append(api)
        elif 'getCouponByOrder' in endpoint:
            payment_methods['coupon_payment'].append(api)
        elif any(keyword in url.lower() for keyword in ['pay', 'payment']):
            payment_methods['mixed_payment'].append(api)
    
    return payment_methods

def analyze_payment_flow(payment_methods: Dict[str, Any]) -> Dict[str, Any]:
    """分析支付流程"""
    flow_analysis = {}
    
    # 分析会员卡支付
    if payment_methods['member_card_payment']:
        memcard_api = payment_methods['member_card_payment'][0]
        post_data = memcard_api.get('post_data', {})
        
        flow_analysis['member_card_payment'] = {
            'endpoint': '/MiniTicket/index.php/MiniPay/memcardPay',
            'method': 'POST',
            'required_params': {
                'totalprice': post_data.get('totalprice', ''),
                'memberinfo': post_data.get('memberinfo', ''),
                'mempass': post_data.get('mempass', ''),
                'orderno': post_data.get('orderno', ''),
                'couponcodes': post_data.get('couponcodes', ''),
                'price': post_data.get('price', ''),
                'discountprice': post_data.get('discountprice', ''),
                'filmname': post_data.get('filmname', ''),
                'featureno': post_data.get('featureno', ''),
                'ticketcount': post_data.get('ticketcount', ''),
                'cinemaname': post_data.get('cinemaname', ''),
                'cinemaid': post_data.get('cinemaid', ''),
                'userid': post_data.get('userid', ''),
                'openid': post_data.get('openid', ''),
                'token': post_data.get('token', ''),
                'source': post_data.get('source', '')
            },
            'description': '会员卡支付接口，支持券+会员卡混合支付'
        }
    
    # 分析预支付验证
    if payment_methods['prepay_validation']:
        prepay_api = payment_methods['prepay_validation'][0]
        query_params = prepay_api.get('query_params', {})
        response_data = prepay_api.get('response_data', {})
        
        flow_analysis['prepay_validation'] = {
            'endpoint': '/MiniTicket/index.php/MiniOrder/ordercouponPrepay',
            'method': 'GET',
            'required_params': {
                'orderno': query_params.get('orderno', ''),
                'couponcode': query_params.get('couponcode', ''),
                'cinemaid': query_params.get('cinemaid', ''),
                'userid': query_params.get('userid', ''),
                'openid': query_params.get('openid', ''),
                'token': query_params.get('token', ''),
                'source': query_params.get('source', '')
            },
            'response_fields': {
                'paymentAmount': '实付金额（分）',
                'mempaymentAmount': '会员实付金额（分）',
                'discountprice': '券抵扣金额（分）',
                'discountmemprice': '会员券抵扣金额（分）',
                'totalprice': '总价（分）',
                'totalmemprice': '会员总价（分）',
                'couponcodes': '使用的券码',
                'bindType': '绑定类型'
            },
            'description': '预支付验证接口，计算券抵扣后的实付金额'
        }
    
    return flow_analysis

def generate_integration_code(flow_analysis: Dict[str, Any]) -> str:
    """生成集成代码"""
    code = '''
# PyQt5电影票务管理系统 - 新增支付方式集成代码

class PaymentMethodManager:
    """支付方式管理器"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def validate_coupon_prepay(self, order_no: str, coupon_codes: str) -> Dict[str, Any]:
        """验证券预支付"""
        params = {
            'orderno': order_no,
            'couponcode': coupon_codes,
            'cinemaid': self.api_client.cinema_id,
            'userid': self.api_client.user_id,
            'openid': self.api_client.openid,
            'token': self.api_client.token,
            'source': '2'
        }
        
        response = self.api_client.get('/MiniTicket/index.php/MiniOrder/ordercouponPrepay', params)
        
        if response.get('resultCode') == '0':
            result_data = response.get('resultData', {})
            return {
                'success': True,
                'payment_amount': int(result_data.get('paymentAmount', '0')),  # 分
                'member_payment_amount': int(result_data.get('mempaymentAmount', '0')),  # 分
                'discount_price': int(result_data.get('discountprice', '0')),  # 分
                'discount_member_price': int(result_data.get('discountmemprice', '0')),  # 分
                'total_price': int(result_data.get('totalprice', '0')),  # 分
                'total_member_price': int(result_data.get('totalmemprice', '0')),  # 分
                'coupon_codes': result_data.get('couponcodes', ''),
                'bind_type': result_data.get('bindType', 0)
            }
        else:
            return {'success': False, 'error': response.get('resultDesc', '验证失败')}
    
    def process_member_card_payment(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理会员卡支付"""
        # 构建支付参数
        payment_params = {
            'totalprice': str(order_data.get('total_price', 0)),  # 分
            'memberinfo': json.dumps({
                'cardno': order_data.get('member_card_no', ''),
                'mobile': order_data.get('mobile', ''),
                'memberId': order_data.get('member_id', ''),
                'cardtype': '0',
                'cardcinemaid': self.api_client.cinema_id,
                'balance': order_data.get('balance', 0)
            }),
            'mempass': order_data.get('member_password', ''),
            'orderno': order_data.get('order_no', ''),
            'couponcodes': order_data.get('coupon_codes', ''),
            'price': str(order_data.get('original_price', 0)),  # 分
            'discountprice': str(order_data.get('discount_price', 0)),  # 分
            'filmname': order_data.get('film_name', ''),
            'featureno': order_data.get('feature_no', ''),
            'ticketcount': str(order_data.get('ticket_count', 1)),
            'cinemaname': order_data.get('cinema_name', ''),
            'cinemaid': self.api_client.cinema_id,
            'userid': self.api_client.user_id,
            'openid': self.api_client.openid,
            'token': self.api_client.token,
            'source': '2'
        }
        
        response = self.api_client.post('/MiniTicket/index.php/MiniPay/memcardPay', payment_params)
        
        if response.get('resultCode') == '0':
            return {'success': True, 'message': '会员卡支付成功'}
        else:
            return {'success': False, 'error': response.get('resultDesc', '支付失败')}

# 在main_modular.py中集成新的支付方式
class EnhancedPaymentSystem:
    """增强的支付系统"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.payment_manager = PaymentMethodManager(main_window.api_client)
    
    def show_payment_options(self, order_data: Dict[str, Any]):
        """显示支付选项"""
        # 创建支付方式选择对话框
        payment_dialog = PaymentMethodDialog(self.main_window)
        payment_dialog.set_order_data(order_data)
        
        if payment_dialog.exec_() == QDialog.Accepted:
            payment_method = payment_dialog.get_selected_payment_method()
            self.process_payment(order_data, payment_method)
    
    def process_payment(self, order_data: Dict[str, Any], payment_method: str):
        """处理支付"""
        if payment_method == 'coupon_only':
            # 现有的纯券支付逻辑
            self.main_window._process_coupon_payment(order_data)
        
        elif payment_method == 'member_card':
            # 新增：会员卡支付
            self._process_member_card_payment(order_data)
        
        elif payment_method == 'mixed':
            # 新增：混合支付（券+会员卡）
            self._process_mixed_payment(order_data)
    
    def _process_member_card_payment(self, order_data: Dict[str, Any]):
        """处理会员卡支付"""
        # 1. 验证会员信息
        member_info = self.main_window.member_info
        if not member_info or not member_info.get('is_member'):
            QMessageBox.warning(self.main_window, "提示", "请先登录会员账户")
            return
        
        # 2. 检查余额
        balance = member_info.get('balance', 0)
        total_amount = order_data.get('amount', 0) * 100  # 转换为分
        
        if balance < total_amount:
            QMessageBox.warning(self.main_window, "提示", f"会员卡余额不足\\n余额: ¥{balance/100:.2f}\\n需要: ¥{total_amount/100:.2f}")
            return
        
        # 3. 执行支付
        payment_data = {
            'total_price': total_amount,
            'member_card_no': member_info.get('cardno', ''),
            'mobile': member_info.get('mobile', ''),
            'member_id': member_info.get('memberId', ''),
            'balance': balance,
            'member_password': self._get_member_password(),
            'order_no': order_data.get('orderno', ''),
            'original_price': total_amount,
            'discount_price': 0,
            'film_name': order_data.get('movie', ''),
            'feature_no': order_data.get('featureno', ''),
            'ticket_count': len(order_data.get('seats', [])),
            'cinema_name': order_data.get('cinema', '')
        }
        
        result = self.payment_manager.process_member_card_payment(payment_data)
        
        if result['success']:
            QMessageBox.information(self.main_window, "支付成功", "会员卡支付成功！")
            self.main_window._get_ticket_code_after_payment(order_data.get('orderno', ''))
        else:
            QMessageBox.warning(self.main_window, "支付失败", result.get('error', '支付失败'))
    
    def _process_mixed_payment(self, order_data: Dict[str, Any]):
        """处理混合支付（券+会员卡）"""
        # 1. 先验证券抵扣
        selected_coupons = self.main_window.selected_coupons
        if not selected_coupons:
            QMessageBox.warning(self.main_window, "提示", "请先选择优惠券")
            return
        
        coupon_codes = ','.join([c.get('couponcode', '') for c in selected_coupons])
        
        # 2. 验证预支付
        prepay_result = self.payment_manager.validate_coupon_prepay(
            order_data.get('orderno', ''), 
            coupon_codes
        )
        
        if not prepay_result['success']:
            QMessageBox.warning(self.main_window, "验证失败", prepay_result.get('error', '券验证失败'))
            return
        
        # 3. 计算会员卡需要支付的金额
        member_payment_amount = prepay_result.get('member_payment_amount', 0)
        
        if member_payment_amount > 0:
            # 需要会员卡支付剩余金额
            member_info = self.main_window.member_info
            if not member_info or member_info.get('balance', 0) < member_payment_amount:
                QMessageBox.warning(self.main_window, "提示", "会员卡余额不足支付剩余金额")
                return
        
        # 4. 执行混合支付
        payment_data = {
            'total_price': prepay_result.get('total_member_price', 0),
            'member_card_no': member_info.get('cardno', ''),
            'mobile': member_info.get('mobile', ''),
            'member_id': member_info.get('memberId', ''),
            'balance': member_info.get('balance', 0),
            'member_password': self._get_member_password(),
            'order_no': order_data.get('orderno', ''),
            'coupon_codes': coupon_codes,
            'original_price': prepay_result.get('total_price', 0),
            'discount_price': prepay_result.get('discount_member_price', 0),
            'film_name': order_data.get('movie', ''),
            'feature_no': order_data.get('featureno', ''),
            'ticket_count': len(order_data.get('seats', [])),
            'cinema_name': order_data.get('cinema', '')
        }
        
        result = self.payment_manager.process_member_card_payment(payment_data)
        
        if result['success']:
            QMessageBox.information(self.main_window, "支付成功", "混合支付成功！")
            self.main_window._get_ticket_code_after_payment(order_data.get('orderno', ''))
        else:
            QMessageBox.warning(self.main_window, "支付失败", result.get('error', '支付失败'))
    
    def _get_member_password(self) -> str:
        """获取会员密码"""
        password, ok = QInputDialog.getText(
            self.main_window, 
            "会员密码", 
            "请输入会员卡密码:", 
            QLineEdit.Password
        )
        return password if ok else ""
'''
    
    return code

def main():
    """主函数"""
    print("🎬 PyQt5电影票务管理系统 - HAR文件支付方式分析")
    print("=" * 80)
    
    # 分析两个HAR文件
    har_files = [
        "大都荟混合下单_05_30_10_58_38.har",
        "大都荟下单2025_05_25_17_58_35.har"
    ]
    
    all_payment_methods = {}
    all_apis = []
    
    for har_file in har_files:
        print(f"\n🔍 分析文件: {har_file}")
        har_data = parse_har_file(har_file)
        
        if har_data:
            apis = analyze_payment_apis(har_data)
            payment_methods = identify_payment_methods(apis)
            
            all_apis.extend(apis)
            
            print(f"\n📋 发现的支付相关API:")
            for category, api_list in payment_methods.items():
                if api_list:
                    print(f"  {category}: {len(api_list)} 个API")
                    for api in api_list:
                        print(f"    - {api['method']} {api['endpoint']}")
            
            # 合并支付方式
            for category, api_list in payment_methods.items():
                if category not in all_payment_methods:
                    all_payment_methods[category] = []
                all_payment_methods[category].extend(api_list)
    
    print("\n" + "=" * 80)
    print("📊 支付方式分析总结")
    print("=" * 80)
    
    # 分析支付流程
    flow_analysis = analyze_payment_flow(all_payment_methods)
    
    print("\n🎯 识别的支付方式:")
    
    if all_payment_methods['member_card_payment']:
        print("\n1. 💳 会员卡支付 (Member Card Payment)")
        print("   - 接口: /MiniTicket/index.php/MiniPay/memcardPay")
        print("   - 方法: POST")
        print("   - 描述: 使用会员卡余额支付，支持券+会员卡混合支付")
        print("   - 特点: 需要会员密码验证，支持余额扣减")
    
    if all_payment_methods['prepay_validation']:
        print("\n2. 🎫 券预支付验证 (Coupon Prepay Validation)")
        print("   - 接口: /MiniTicket/index.php/MiniOrder/ordercouponPrepay")
        print("   - 方法: GET")
        print("   - 描述: 验证券的有效性并计算抵扣后的实付金额")
        print("   - 特点: 支持多张券组合使用，返回详细的价格计算")
    
    if all_payment_methods['coupon_payment']:
        print("\n3. 🎟️ 纯券支付 (Coupon Only Payment)")
        print("   - 接口: /MiniTicket/index.php/MiniCoupon/getCouponByOrder")
        print("   - 方法: GET")
        print("   - 描述: 获取可用券列表，支持纯券支付")
        print("   - 特点: 现有系统已支持")
    
    print("\n🔄 支付流程分析:")
    print("1. 创建订单 → 2. 获取可用券 → 3. 验证券抵扣 → 4. 执行支付 → 5. 获取取票码")
    
    print("\n💡 新增支付方式建议:")
    print("✅ 会员卡支付 - 使用会员卡余额直接支付")
    print("✅ 混合支付 - 券抵扣 + 会员卡余额支付剩余金额")
    print("✅ 预支付验证 - 实时计算券抵扣和实付金额")
    
    print("\n🛠️ 集成到现有系统的建议:")
    print("1. 在支付界面添加支付方式选择")
    print("2. 集成会员信息验证和余额查询")
    print("3. 实现券+会员卡的混合支付逻辑")
    print("4. 添加会员密码输入和验证")
    print("5. 优化支付成功后的取票码显示")
    
    # 生成集成代码
    integration_code = generate_integration_code(flow_analysis)
    
    # 保存集成代码到文件
    with open('payment_integration_code.py', 'w', encoding='utf-8') as f:
        f.write(integration_code)
    
    print(f"\n📝 集成代码已生成: payment_integration_code.py")
    print("🎉 分析完成！")

if __name__ == "__main__":
    main()
