
# PyQt5电影票务管理系统 - 支付流程优化实施代码

import json
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit

class MemberInfoService:
    """会员信息服务"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def get_member_info(self) -> Dict[str, Any]:
        """获取会员信息 - 替换本地JSON数据为API实时获取"""
        try:
            # 调用会员信息API
            response = self.api_client.get('/MiniTicket/index.php/MiniMember/getMemberInfo', {
                'groupid': '',
                'cinemaid': self.api_client.cinema_id,
                'cardno': '',
                'userid': self.api_client.user_id,
                'openid': self.api_client.openid,
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.api_client.token,
                'source': '2'
            })
            
            if response.get('resultCode') == '0':
                member_data = response.get('resultData', {})
                return {
                    'success': True,
                    'is_member': True,
                    'cardno': member_data.get('cardno', ''),
                    'mobile': member_data.get('mobile', ''),
                    'memberId': member_data.get('memberId', ''),
                    'cardtype': member_data.get('cardtype', '0'),
                    'cardcinemaid': member_data.get('cardcinemaid', ''),
                    'balance': int(float(member_data.get('balance', 0)) * 100)  # 转换为分
                }
            else:
                return {
                    'success': False,
                    'is_member': False,
                    'error': response.get('resultDesc', '获取会员信息失败')
                }
                
        except Exception as e:
            print(f"[会员信息] API调用失败: {e}")
            return {
                'success': False,
                'is_member': False,
                'error': f'网络错误: {str(e)}'
            }

class CouponPrePayService:
    """券预支付验证服务"""
    
    def __init__(self, api_client):
        self.api_client = api_client
    
    def validate_coupon_prepay(self, order_no: str, coupon_codes: str) -> Dict[str, Any]:
        """验证券预支付"""
        try:
            response = self.api_client.get('/MiniTicket/index.php/MiniOrder/ordercouponPrepay', {
                'orderno': order_no,
                'couponcode': coupon_codes,
                'cinemaid': self.api_client.cinema_id,
                'userid': self.api_client.user_id,
                'openid': self.api_client.openid,
                'token': self.api_client.token,
                'source': '2'
            })
            
            if response.get('resultCode') == '0':
                result_data = response.get('resultData', {})
                return {
                    'success': True,
                    'payment_amount': int(result_data.get('paymentAmount', '0')),
                    'member_payment_amount': int(result_data.get('mempaymentAmount', '0')),
                    'discount_price': int(result_data.get('discountprice', '0')),
                    'discount_member_price': int(result_data.get('discountmemprice', '0')),
                    'total_price': int(result_data.get('totalprice', '0')),
                    'total_member_price': int(result_data.get('totalmemprice', '0')),
                    'coupon_codes': result_data.get('couponcodes', ''),
                    'bind_type': result_data.get('bindType', 0)
                }
            else:
                return {
                    'success': False,
                    'error': response.get('resultDesc', '券验证失败')
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

class DynamicPasswordPolicyManager:
    """动态密码策略管理器"""
    
    def __init__(self, api_client):
        self.api_client = api_client
        # 基于分析结果的密码策略配置
        self.password_policies = {
            'www.heibaiyingye.cn': {
                'requires_password': true,
                'enable_mempassword': '1',
                'description': '黑白影业 - 需要会员卡密码'
            },
            'zcxzs7.cityfilms.cn': {
                'requires_password': false,
                'enable_mempassword': '0',
                'description': '城市影院 - 不需要会员卡密码'
            }
        }
    
    def get_password_policy_from_order_detail(self, order_no: str) -> Dict[str, Any]:
        """从订单详情获取密码策略"""
        try:
            response = self.api_client.get('/MiniTicket/index.php/MiniOrder/getUnpaidOrderDetail', {
                'orderno': order_no,
                'groupid': '',
                'cinemaid': self.api_client.cinema_id,
                'cardno': '',
                'userid': self.api_client.user_id,
                'openid': self.api_client.openid,
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': self.api_client.token,
                'source': '2'
            })
            
            if response.get('resultCode') == '0':
                order_data = response.get('resultData', {})
                enable_mempassword = order_data.get('enable_mempassword', '0')
                
                return {
                    'success': True,
                    'requires_password': enable_mempassword == '1',
                    'enable_mempassword': enable_mempassword,
                    'mem_pay_only': order_data.get('memPayONLY', '0'),
                    'source': 'order_detail_api'
                }
            else:
                return {'success': False, 'error': response.get('resultDesc', '获取订单详情失败')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_password_policy(self, base_url: str = None, order_no: str = None) -> Dict[str, Any]:
        """获取密码策略"""
        # 优先从订单详情API获取实时策略
        if order_no:
            api_policy = self.get_password_policy_from_order_detail(order_no)
            if api_policy.get('success'):
                return api_policy
        
        # 降级到基于域名的策略
        if base_url:
            domain = self._extract_domain(base_url)
            for policy_domain, policy in self.password_policies.items():
                if policy_domain in domain:
                    policy['source'] = 'domain_config'
                    return policy
        
        # 默认策略
        return {
            'requires_password': True,
            'enable_mempassword': '1',
            'description': '默认策略 - 需要会员卡密码',
            'source': 'default'
        }
    
    def _extract_domain(self, url: str) -> str:
        """提取域名"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url

class EnhancedPaymentProcessor:
    """增强的支付处理器"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.member_service = MemberInfoService(main_window.api_client)
        self.coupon_service = CouponPrePayService(main_window.api_client)
        self.password_manager = DynamicPasswordPolicyManager(main_window.api_client)
    
    def process_member_card_payment(self, order_data: Dict[str, Any]):
        """处理会员卡支付 - 支持动态密码策略"""
        try:
            # 1. 获取实时会员信息
            member_result = self.member_service.get_member_info()
            if not member_result.get('success') or not member_result.get('is_member'):
                QMessageBox.warning(self.main_window, "提示", 
                                  member_result.get('error', '请先登录会员账户'))
                return
            
            member_info = member_result
            
            # 2. 检查余额
            balance = member_info.get('balance', 0)
            total_amount = int(order_data.get('amount', 0) * 100)
            
            if balance < total_amount:
                QMessageBox.warning(self.main_window, "余额不足", 
                                  f"会员卡余额不足\n余额: ¥{balance/100:.2f}\n需要: ¥{total_amount/100:.2f}")
                return
            
            # 3. 获取密码策略
            current_account = self.main_window.current_account
            base_url = current_account.get('base_url', '') if current_account else ''
            order_no = order_data.get('orderno', '')
            
            password_policy = self.password_manager.get_password_policy(base_url, order_no)
            
            # 4. 根据策略决定是否需要密码
            member_password = None
            if password_policy.get('requires_password', True):
                password, ok = QInputDialog.getText(
                    self.main_window, 
                    "会员密码", 
                    f"请输入会员卡密码\n({password_policy.get('description', '需要密码验证')}):", 
                    QLineEdit.Password
                )
                if not ok or not password:
                    return
                member_password = password
            
            # 5. 构建支付参数
            payment_params = {
                'totalprice': str(total_amount),
                'memberinfo': json.dumps({
                    'cardno': member_info.get('cardno', ''),
                    'mobile': member_info.get('mobile', ''),
                    'memberId': member_info.get('memberId', ''),
                    'cardtype': '0',
                    'cardcinemaid': member_info.get('cardcinemaid', ''),
                    'balance': member_info.get('balance', 0) / 100
                }),
                'orderno': order_no,
                'couponcodes': '',
                'price': str(total_amount),
                'discountprice': '0',
                'filmname': order_data.get('movie', ''),
                'featureno': order_data.get('featureno', ''),
                'ticketcount': str(len(order_data.get('seats', []))),
                'cinemaname': order_data.get('cinema', ''),
                'cinemaid': self.main_window.api_client.cinema_id,
                'userid': self.main_window.api_client.user_id,
                'openid': self.main_window.api_client.openid,
                'token': self.main_window.api_client.token,
                'source': '2'
            }
            
            # 根据策略添加密码字段
            if password_policy.get('requires_password', True) and member_password:
                payment_params['mempass'] = member_password
            
            # 6. 执行支付
            response = self.main_window.api_client.post('/MiniTicket/index.php/MiniPay/memcardPay', payment_params)
            
            if response.get('resultCode') == '0':
                QMessageBox.information(self.main_window, "支付成功", "会员卡支付成功！")
                self.main_window._get_ticket_code_after_payment(order_no)
            else:
                QMessageBox.warning(self.main_window, "支付失败", response.get('resultDesc', '支付失败'))
                
        except Exception as e:
            print(f"[会员卡支付] 错误: {e}")
            QMessageBox.warning(self.main_window, "支付错误", f"会员卡支付失败: {str(e)}")

# 在main_modular.py中的集成示例
def integrate_enhanced_payment_system(main_window):
    """集成增强支付系统到主窗口"""
    
    # 初始化增强支付处理器
    main_window.enhanced_payment = EnhancedPaymentProcessor(main_window)
    
    # 替换现有的会员信息获取方法
    def refresh_member_info_enhanced():
        """增强的会员信息刷新"""
        try:
            member_result = main_window.enhanced_payment.member_service.get_member_info()
            main_window.member_info = member_result
            
            if member_result.get('is_member'):
                balance = member_result.get('balance', 0) / 100
                print(f"[会员信息] 卡号: {member_result.get('cardno')}, 余额: ¥{balance:.2f}")
            else:
                print(f"[会员信息] {member_result.get('error', '未登录会员')}")
                
        except Exception as e:
            print(f"[会员信息] 获取失败: {e}")
            main_window.member_info = {'is_member': False}
    
    # 绑定新的会员信息刷新方法
    main_window.refresh_member_info = refresh_member_info_enhanced
    
    # 替换现有的会员卡支付方法
    main_window._process_member_card_payment = main_window.enhanced_payment.process_member_card_payment
    
    print("[集成完成] 增强支付系统已集成到主窗口")
