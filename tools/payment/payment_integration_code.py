
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
            QMessageBox.warning(self.main_window, "提示", f"会员卡余额不足\n余额: ¥{balance/100:.2f}\n需要: ¥{total_amount/100:.2f}")
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
