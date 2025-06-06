#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付策略模式 - 统一支付处理逻辑
自动生成，用于第三阶段C设计模式应用
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.data_utils import DataUtils
from utils.error_handler import handle_exceptions, ErrorHandler

class PaymentStrategy(ABC):
    """支付策略抽象基类"""

    @abstractmethod
    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """验证支付数据"""
        pass

    @abstractmethod
    def execute_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行支付"""
        pass

    @abstractmethod
    def get_payment_type(self) -> str:
        """获取支付类型"""
        pass

class MemberCardPaymentStrategy(PaymentStrategy):
    """会员卡支付策略"""

    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """验证会员卡支付数据"""
        required_fields = ['user_id', 'card_no', 'amount']
        is_valid, missing = DataUtils.validate_required_fields(payment_data, required_fields)

        if not is_valid:
            ErrorHandler.show_warning_message("数据验证", f"缺少必需字段: {', '.join(missing)}")
            return False

        # 验证金额
        amount = DataUtils.safe_get(payment_data, 'amount', 0, required_type=float)
        if amount <= 0:
            ErrorHandler.show_warning_message("数据验证", "支付金额必须大于0")
            return False

        return True

    @handle_exceptions(show_message=True, default_return=None)
    def execute_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行会员卡支付"""
        if not self.validate_payment_data(payment_data):
            return None

        # 模拟会员卡支付API调用
        print(f"执行会员卡支付: {payment_data}")

        # 这里应该调用实际的会员卡支付API
        result = {
            'success': True,
            'payment_id': f"member_{payment_data.get('user_id')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'amount': payment_data.get('amount'),
            'payment_type': 'member_card'
        }

        return result

    def get_payment_type(self) -> str:
        return "member_card"

class CouponPaymentStrategy(PaymentStrategy):
    """优惠券支付策略"""

    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """验证优惠券支付数据"""
        required_fields = ['user_id', 'coupon_codes', 'original_amount']
        is_valid, missing = DataUtils.validate_required_fields(payment_data, required_fields)

        if not is_valid:
            ErrorHandler.show_warning_message("数据验证", f"缺少必需字段: {', '.join(missing)}")
            return False

        # 验证优惠券
        coupon_codes = DataUtils.safe_get(payment_data, 'coupon_codes', '')
        if not coupon_codes:
            ErrorHandler.show_warning_message("数据验证", "请选择优惠券")
            return False

        return True

    @handle_exceptions(show_message=True, default_return=None)
    def execute_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行优惠券支付"""
        if not self.validate_payment_data(payment_data):
            return None

        # 模拟优惠券支付API调用
        print(f"执行优惠券支付: {payment_data}")

        result = {
            'success': True,
            'payment_id': f"coupon_{payment_data.get('user_id')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'original_amount': payment_data.get('original_amount'),
            'discount_amount': payment_data.get('discount_amount', 0),
            'final_amount': payment_data.get('final_amount', 0),
            'payment_type': 'coupon'
        }

        return result

    def get_payment_type(self) -> str:
        return "coupon"

class MixedPaymentStrategy(PaymentStrategy):
    """混合支付策略（优惠券+会员卡）"""

    def __init__(self):
        self.coupon_strategy = CouponPaymentStrategy()
        self.member_strategy = MemberCardPaymentStrategy()

    def validate_payment_data(self, payment_data: Dict[str, Any]) -> bool:
        """验证混合支付数据"""
        required_fields = ['user_id', 'coupon_codes', 'card_no', 'final_amount']
        is_valid, missing = DataUtils.validate_required_fields(payment_data, required_fields)

        if not is_valid:
            ErrorHandler.show_warning_message("数据验证", f"缺少必需字段: {', '.join(missing)}")
            return False

        return True

    @handle_exceptions(show_message=True, default_return=None)
    def execute_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行混合支付"""
        if not self.validate_payment_data(payment_data):
            return None

        # 模拟混合支付API调用
        print(f"执行混合支付: {payment_data}")

        result = {
            'success': True,
            'payment_id': f"mixed_{payment_data.get('user_id')}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'coupon_discount': payment_data.get('coupon_discount', 0),
            'member_payment': payment_data.get('final_amount', 0),
            'total_saved': payment_data.get('total_saved', 0),
            'payment_type': 'mixed'
        }

        return result

    def get_payment_type(self) -> str:
        return "mixed"

class PaymentContext:
    """支付上下文类"""

    def __init__(self):
        self.strategy = None
        self.strategies = {
            'member_card': MemberCardPaymentStrategy(),
            'coupon': CouponPaymentStrategy(),
            'mixed': MixedPaymentStrategy()
        }

    def set_strategy(self, payment_type: str):
        """设置支付策略"""
        if payment_type in self.strategies:
            self.strategy = self.strategies[payment_type]
        else:
            raise ValueError(f"不支持的支付类型: {payment_type}")

    def execute_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行支付"""
        if not self.strategy:
            ErrorHandler.show_error_message("支付错误", "未设置支付策略")
            return None

        return self.strategy.execute_payment(payment_data)

    def get_available_strategies(self) -> list:
        """获取可用的支付策略"""
        return list(self.strategies.keys())

# 全局支付上下文实例
payment_context = PaymentContext()

def get_payment_context() -> PaymentContext:
    """获取支付上下文实例"""
    return payment_context
