#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据处理工具类 - 统一数据处理逻辑
自动生成，用于减少数据处理的重复代码
"""

import json
from typing import Any, Dict, List, Optional, Union

class DataUtils:
    """数据处理工具类"""
    
    @staticmethod
    def safe_get(data: Dict, key: str, default: Any = None, required_type: type = None) -> Any:
        """安全获取字典数据"""
        if not isinstance(data, dict) or key not in data:
            return default
        
        value = data[key]
        if value is None:
            return default
        
        if required_type and not isinstance(value, required_type):
            try:
                # 尝试类型转换
                if required_type == int:
                    return int(value)
                elif required_type == float:
                    return float(value)
                elif required_type == str:
                    return str(value)
                elif required_type == bool:
                    return bool(value)
                else:
                    return default
            except (ValueError, TypeError):
                return default
        
        return value
    
    @staticmethod
    def safe_get_nested(data: Dict, keys: List[str], default: Any = None) -> Any:
        """安全获取嵌套字典数据"""
        current = data
        for key in keys:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current
    
    @staticmethod
    def parse_json_response(response_text: str, success_key: str = 'success') -> Optional[Dict]:
        """解析JSON响应"""
        try:
            result = json.loads(response_text)
            if isinstance(result, dict) and result.get(success_key):
                return result
            return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> tuple[bool, List[str]]:
        """验证必需字段"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                missing_fields.append(field)
        return len(missing_fields) == 0, missing_fields
    
    @staticmethod
    def clean_dict(data: Dict, remove_none: bool = True, remove_empty: bool = True) -> Dict:
        """清理字典数据"""
        cleaned = {}
        for key, value in data.items():
            if remove_none and value is None:
                continue
            if remove_empty and value == '':
                continue
            cleaned[key] = value
        return cleaned
    
    @staticmethod
    def merge_dicts(*dicts: Dict) -> Dict:
        """合并多个字典"""
        result = {}
        for d in dicts:
            if isinstance(d, dict):
                result.update(d)
        return result
    
    @staticmethod
    def format_price(price: Union[int, float, str], currency: str = '¥') -> str:
        """格式化价格显示"""
        try:
            if isinstance(price, str):
                price = float(price)
            return f"{currency}{price:.2f}"
        except (ValueError, TypeError):
            return f"{currency}0.00"
    
    @staticmethod
    def safe_int(value: Any, default: int = 0) -> int:
        """安全转换为整数"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def safe_float(value: Any, default: float = 0.0) -> float:
        """安全转换为浮点数"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
