#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券数据处理工具类
提供券数据的格式化、验证、分析等工具函数
"""

import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class VoucherDataProcessor:
    """券数据处理器"""
    
    @staticmethod
    def format_voucher_display_name(voucher_name: str, voucher_code: str) -> str:
        """
        格式化券显示名称
        
        Args:
            voucher_name: 券名称
            voucher_code: 券号
            
        Returns:
            格式化后的显示名称
        """
        # 提取券号后4位作为标识
        code_suffix = voucher_code[-4:] if len(voucher_code) >= 4 else voucher_code
        return f"{voucher_name} (***{code_suffix})"
    
    @staticmethod
    def parse_voucher_type_from_code(voucher_code: str) -> str:
        """
        从券号解析券类型
        
        Args:
            voucher_code: 券号
            
        Returns:
            券类型标识
        """
        if voucher_code.startswith('GZJY'):
            return '广州佳意券'
        elif voucher_code.startswith('CGYTJ'):
            return '天津通兑券'
        elif voucher_code.startswith('XKHY'):
            return '轩夸券'
        elif voucher_code.startswith('CATHY'):
            return '团体券'
        else:
            return '其他券'
    
    @staticmethod
    def calculate_expire_days(expire_time: int) -> int:
        """
        计算券距离过期的天数
        
        Args:
            expire_time: 过期时间戳
            
        Returns:
            剩余天数（负数表示已过期）
        """
        current_time = int(time.time())
        days_diff = (expire_time - current_time) // (24 * 3600)
        return days_diff
    
    @staticmethod
    def get_expire_status_text(expire_time: int) -> Tuple[str, str]:
        """
        获取过期状态文本和颜色
        
        Args:
            expire_time: 过期时间戳
            
        Returns:
            (状态文本, 颜色代码)
        """
        days_left = VoucherDataProcessor.calculate_expire_days(expire_time)
        
        if days_left < 0:
            return "已过期", "#ff4444"
        elif days_left == 0:
            return "今日过期", "#ff8800"
        elif days_left <= 7:
            return f"{days_left}天后过期", "#ffaa00"
        elif days_left <= 30:
            return f"{days_left}天后过期", "#4CAF50"
        else:
            return f"{days_left}天后过期", "#2196F3"
    
    @staticmethod
    def group_vouchers_by_type(vouchers: List[Any]) -> Dict[str, List[Any]]:
        """
        按类型分组券
        
        Args:
            vouchers: 券列表
            
        Returns:
            按类型分组的券字典
        """
        grouped = {}
        for voucher in vouchers:
            voucher_type = VoucherDataProcessor.parse_voucher_type_from_code(voucher.voucher_code)
            if voucher_type not in grouped:
                grouped[voucher_type] = []
            grouped[voucher_type].append(voucher)
        
        return grouped
    
    @staticmethod
    def sort_vouchers_by_priority(vouchers: List[Any]) -> List[Any]:
        """
        按优先级排序券（有效券优先，即将过期的优先）
        
        Args:
            vouchers: 券列表
            
        Returns:
            排序后的券列表
        """
        def sort_key(voucher):
            # 优先级：有效性 > 过期时间 > 绑定时间
            is_valid = voucher.is_valid()
            expire_time = voucher.expire_time
            bind_time = voucher.bind_time
            
            # 有效券排在前面，按过期时间升序
            if is_valid:
                return (0, expire_time, -bind_time)
            else:
                # 无效券排在后面，按绑定时间降序
                return (1, -bind_time, expire_time)
        
        return sorted(vouchers, key=sort_key)
    
    @staticmethod
    def filter_vouchers_by_cinema(vouchers: List[Any], cinema_id: str) -> List[Any]:
        """
        按影院过滤券（如果券有影院限制）
        
        Args:
            vouchers: 券列表
            cinema_id: 影院ID
            
        Returns:
            过滤后的券列表
        """
        # 目前沃美券API没有返回影院限制信息，暂时返回所有券
        # 后续可以根据券的scope_desc字段进行过滤
        return vouchers
    
    @staticmethod
    def validate_voucher_code_format(voucher_code: str) -> bool:
        """
        验证券号格式
        
        Args:
            voucher_code: 券号
            
        Returns:
            是否为有效格式
        """
        # 基本格式验证：字母开头，包含数字
        pattern = r'^[A-Z]{2,6}\d{8,16}$'
        return bool(re.match(pattern, voucher_code))
    
    @staticmethod
    def extract_voucher_summary(vouchers: List[Any]) -> Dict[str, Any]:
        """
        提取券摘要信息
        
        Args:
            vouchers: 券列表
            
        Returns:
            摘要信息
        """
        if not vouchers:
            return {
                'total': 0,
                'valid': 0,
                'expired': 0,
                'expiring_soon': 0,
                'types': {},
                'latest_expire_date': None,
                'earliest_expire_date': None
            }
        
        valid_count = 0
        expired_count = 0
        expiring_soon_count = 0
        type_counts = {}
        expire_times = []
        
        for voucher in vouchers:
            # 统计状态
            if voucher.is_valid():
                valid_count += 1
                expire_times.append(voucher.expire_time)
                
                # 检查是否即将过期（7天内）
                days_left = VoucherDataProcessor.calculate_expire_days(voucher.expire_time)
                if 0 <= days_left <= 7:
                    expiring_soon_count += 1
            elif voucher.is_expired():
                expired_count += 1
            
            # 统计类型
            voucher_type = VoucherDataProcessor.parse_voucher_type_from_code(voucher.voucher_code)
            type_counts[voucher_type] = type_counts.get(voucher_type, 0) + 1
        
        # 计算过期时间范围
        latest_expire = max(expire_times) if expire_times else None
        earliest_expire = min(expire_times) if expire_times else None
        
        return {
            'total': len(vouchers),
            'valid': valid_count,
            'expired': expired_count,
            'expiring_soon': expiring_soon_count,
            'types': type_counts,
            'latest_expire_date': datetime.fromtimestamp(latest_expire).strftime('%Y-%m-%d') if latest_expire else None,
            'earliest_expire_date': datetime.fromtimestamp(earliest_expire).strftime('%Y-%m-%d') if earliest_expire else None
        }

class VoucherDisplayFormatter:
    """券显示格式化器"""
    
    @staticmethod
    def format_voucher_card_text(voucher: Any) -> str:
        """
        格式化券卡片显示文本
        
        Args:
            voucher: 券对象
            
        Returns:
            格式化的显示文本
        """
        status_text, _ = VoucherDataProcessor.get_expire_status_text(voucher.expire_time)
        voucher_type = VoucherDataProcessor.parse_voucher_type_from_code(voucher.voucher_code)
        
        return f"""券名: {voucher.voucher_name}
券号: {voucher.voucher_code_mask}
类型: {voucher_type}
状态: {status_text}
余额: {voucher.voucher_balance_str}
过期: {voucher.expire_time_string}"""
    
    @staticmethod
    def format_voucher_list_item(voucher: Any) -> str:
        """
        格式化券列表项显示文本
        
        Args:
            voucher: 券对象
            
        Returns:
            格式化的列表项文本
        """
        status_icon = "✅" if voucher.is_valid() else "❌"
        days_left = VoucherDataProcessor.calculate_expire_days(voucher.expire_time)
        
        if voucher.is_valid():
            if days_left <= 7:
                urgency = "🔥"
            elif days_left <= 30:
                urgency = "⚠️"
            else:
                urgency = "✨"
        else:
            urgency = "💀"
        
        return f"{status_icon} {urgency} {voucher.voucher_name} ({voucher.voucher_code_mask}) - {voucher.voucher_balance_str}"
    
    @staticmethod
    def format_statistics_text(statistics: Dict[str, Any]) -> str:
        """
        格式化统计信息文本
        
        Args:
            statistics: 统计信息
            
        Returns:
            格式化的统计文本
        """
        total = statistics.get('total_count', 0)
        valid = statistics.get('valid_count', 0)
        expired = statistics.get('expired_count', 0)
        disabled = statistics.get('disabled_count', 0)
        
        return f"""券统计信息:
总数: {total} 张
有效: {valid} 张
过期: {expired} 张
作废: {disabled} 张
有效率: {statistics.get('valid_rate', 0):.1f}%"""

# 全局实例
voucher_processor = VoucherDataProcessor()
voucher_formatter = VoucherDisplayFormatter()

def get_voucher_processor() -> VoucherDataProcessor:
    """获取券数据处理器实例"""
    return voucher_processor

def get_voucher_formatter() -> VoucherDisplayFormatter:
    """获取券显示格式化器实例"""
    return voucher_formatter
