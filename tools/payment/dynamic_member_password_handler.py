
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
                    f"请输入会员卡密码\n({validation_result['policy_description']}):", 
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
