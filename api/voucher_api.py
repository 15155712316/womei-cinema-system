#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券管理API接口
提供券查询、过滤、统计等功能的API接口
"""

import json
import logging
from typing import Dict, Optional, Any
from services.voucher_service import get_voucher_service, VoucherStatus
from utils.data_utils import DataUtils

logger = logging.getLogger(__name__)

class VoucherAPI:
    """券管理API类"""
    
    def __init__(self):
        self.voucher_service = get_voucher_service()
        self.data_utils = DataUtils()
    
    def get_user_vouchers(self, cinema_id: str, token: str, 
                         only_valid: bool = False,
                         status_filter: Optional[str] = None,
                         name_filter: Optional[str] = None) -> Dict[str, Any]:
        """
        获取用户券列表
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            only_valid: 是否只返回有效券
            status_filter: 状态过滤
            name_filter: 名称过滤
            
        Returns:
            API响应格式的券数据
        """
        try:
            # 获取所有券
            vouchers, page_info = self.voucher_service.get_all_vouchers(
                cinema_id, token, only_valid=only_valid
            )

            # 安全地检查券数据
            if not isinstance(vouchers, list):
                logger.error(f"券服务返回的数据不是列表格式: {type(vouchers)}")
                return {
                    'success': False,
                    'code': 500,
                    'message': '券数据格式错误',
                    'data': None
                }

            # 应用额外过滤
            if status_filter or name_filter:
                vouchers = self.voucher_service.filter_vouchers(
                    vouchers, status_filter, name_filter
                )

            # 获取统计信息
            statistics = self.voucher_service.get_voucher_statistics(vouchers)

            # 安全地转换为字典格式
            vouchers_data = []
            for i, voucher in enumerate(vouchers):
                try:
                    if hasattr(voucher, 'to_dict'):
                        vouchers_data.append(voucher.to_dict())
                    else:
                        logger.warning(f"第{i+1}个券对象没有to_dict方法，跳过")
                        continue
                except Exception as e:
                    logger.error(f"转换第{i+1}个券对象失败: {e}")
                    continue
            
            return {
                'success': True,
                'code': 200,
                'message': '获取券列表成功',
                'data': {
                    'vouchers': vouchers_data,
                    'statistics': statistics,
                    'page_info': page_info,
                    'filters_applied': {
                        'only_valid': only_valid,
                        'status_filter': status_filter,
                        'name_filter': name_filter
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"获取用户券列表失败: {e}")
            return {
                'success': False,
                'code': 500,
                'message': f'获取券列表失败: {str(e)}',
                'data': None
            }
    
    def get_valid_vouchers_only(self, cinema_id: str, token: str) -> Dict[str, Any]:
        """
        只获取有效券列表（快捷方法）

        Args:
            cinema_id: 影院ID
            token: 用户token

        Returns:
            有效券列表
        """
        return self.get_user_vouchers(cinema_id, token, only_valid=True)

    def get_order_available_vouchers(self, cinema_id: str, token: str) -> Dict[str, Any]:
        """
        获取当前订单可用的优惠券列表（沃美新API）

        Args:
            cinema_id: 影院ID
            token: 用户token

        Returns:
            订单可用券列表
        """
        try:
            print(f"[券API] 🚀 调用沃美订单可用券API")
            print(f"[券API] 🏢 影院ID: {cinema_id}")
            print(f"[券API] 🎫 Token: {token[:20]}...")

            # 调用沃美券服务的新接口
            from services.womei_voucher_service import get_womei_voucher_service
            womei_service = get_womei_voucher_service()

            result = womei_service.get_order_available_vouchers(cinema_id, token)

            print(f"[券API] 📥 沃美服务响应: ret={result.get('ret')}, msg={result.get('msg')}")

            # 检查沃美API响应
            if result.get('ret') == 0:
                vouchers_data = result.get('data', {}).get('vouchers', [])
                total_count = result.get('data', {}).get('total_count', 0)

                print(f"[券API] ✅ 获取成功，订单可用券数量: {total_count}")

                # 转换为VoucherInfo对象格式（保持与现有API兼容）
                from services.voucher_service import VoucherInfo
                voucher_objects = []

                for voucher_data in vouchers_data:
                    try:
                        voucher_obj = VoucherInfo(voucher_data)
                        voucher_objects.append(voucher_obj)
                    except Exception as e:
                        logger.error(f"转换券对象失败: {e}")
                        continue

                # 转换为字典格式
                vouchers_dict = []
                for voucher in voucher_objects:
                    try:
                        if hasattr(voucher, 'to_dict'):
                            vouchers_dict.append(voucher.to_dict())
                        else:
                            # 如果没有to_dict方法，手动构建字典
                            vouchers_dict.append({
                                'voucher_code': voucher.voucher_code,
                                'voucher_code_mask': voucher.voucher_code_mask,
                                'voucher_name': voucher.voucher_name,
                                'expire_time': voucher.expire_time,
                                'expire_time_string': voucher.expire_time_string,
                                'status': voucher.status
                            })
                    except Exception as e:
                        logger.error(f"转换券字典失败: {e}")
                        continue

                # 生成统计信息
                statistics = {
                    'total_count': len(vouchers_dict),
                    'valid_count': len(vouchers_dict),  # 订单可用券都是有效的
                    'used_count': 0,
                    'disabled_count': 0,
                    'expired_count': 0,
                    'valid_rate': 100.0 if vouchers_dict else 0,
                    'source': 'womei_order_api'
                }

                return {
                    'success': True,
                    'code': 200,
                    'message': '获取订单可用券列表成功',
                    'data': {
                        'vouchers': vouchers_dict,
                        'statistics': statistics,
                        'page_info': {'total_page': 1, 'current_page': 1},
                        'filters_applied': {
                            'only_valid': True,
                            'order_available': True,
                            'api_source': 'womei_voucher_list'
                        }
                    }
                }
            else:
                error_msg = result.get('msg', '获取订单可用券失败')
                print(f"[券API] ❌ 沃美API错误: {error_msg}")
                return {
                    'success': False,
                    'code': 500,
                    'message': error_msg,
                    'data': None
                }

        except Exception as e:
            logger.error(f"获取订单可用券列表失败: {e}")
            print(f"[券API] ❌ 异常: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'code': 500,
                'message': f'获取订单可用券失败: {str(e)}',
                'data': None
            }
    
    def get_voucher_statistics_only(self, cinema_id: str, token: str) -> Dict[str, Any]:
        """
        只获取券统计信息
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            
        Returns:
            券统计信息
        """
        try:
            vouchers, _ = self.voucher_service.get_all_vouchers(cinema_id, token)
            statistics = self.voucher_service.get_voucher_statistics(vouchers)
            
            return {
                'success': True,
                'code': 200,
                'message': '获取券统计成功',
                'data': statistics
            }
            
        except Exception as e:
            logger.error(f"获取券统计失败: {e}")
            return {
                'success': False,
                'code': 500,
                'message': f'获取券统计失败: {str(e)}',
                'data': None
            }
    
    def search_vouchers(self, cinema_id: str, token: str, 
                       search_term: str) -> Dict[str, Any]:
        """
        搜索券
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            search_term: 搜索关键词（券号或券名）
            
        Returns:
            搜索结果
        """
        try:
            vouchers, page_info = self.voucher_service.get_all_vouchers(cinema_id, token)
            
            # 搜索匹配的券
            search_results = []
            search_term_lower = search_term.lower()
            
            for voucher in vouchers:
                if (search_term_lower in voucher.voucher_code.lower() or
                    search_term_lower in voucher.voucher_name.lower() or
                    search_term_lower in voucher.voucher_code_mask.lower()):
                    search_results.append(voucher)
            
            # 转换为字典格式
            results_data = [voucher.to_dict() for voucher in search_results]
            
            return {
                'success': True,
                'code': 200,
                'message': f'搜索完成，找到 {len(search_results)} 条结果',
                'data': {
                    'search_term': search_term,
                    'results': results_data,
                    'total_found': len(search_results),
                    'total_searched': len(vouchers)
                }
            }
            
        except Exception as e:
            logger.error(f"搜索券失败: {e}")
            return {
                'success': False,
                'code': 500,
                'message': f'搜索失败: {str(e)}',
                'data': None
            }
    
    def get_vouchers_by_status(self, cinema_id: str, token: str, 
                              status: str) -> Dict[str, Any]:
        """
        按状态获取券列表
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            status: 券状态 (UN_USE, USED, DISABLED)
            
        Returns:
            指定状态的券列表
        """
        return self.get_user_vouchers(cinema_id, token, status_filter=status)
    
    def export_vouchers_data(self, cinema_id: str, token: str, 
                           export_format: str = 'json') -> Dict[str, Any]:
        """
        导出券数据
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            export_format: 导出格式 (json, csv)
            
        Returns:
            导出结果
        """
        try:
            vouchers, page_info = self.voucher_service.get_all_vouchers(cinema_id, token)
            statistics = self.voucher_service.get_voucher_statistics(vouchers)
            
            export_data = {
                'export_time': self.data_utils.get_current_timestamp(),
                'cinema_id': cinema_id,
                'total_vouchers': len(vouchers),
                'statistics': statistics,
                'vouchers': [voucher.to_dict() for voucher in vouchers]
            }
            
            if export_format.lower() == 'json':
                # 保存为JSON文件
                filename = f"vouchers_export_{cinema_id}_{self.data_utils.get_current_timestamp()}.json"
                filepath = f"data/exports/{filename}"
                
                # 确保目录存在
                import os
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                return {
                    'success': True,
                    'code': 200,
                    'message': '导出成功',
                    'data': {
                        'filename': filename,
                        'filepath': filepath,
                        'format': 'json',
                        'total_vouchers': len(vouchers),
                        'file_size': os.path.getsize(filepath)
                    }
                }
            
            elif export_format.lower() == 'csv':
                # 保存为CSV文件
                import csv
                filename = f"vouchers_export_{cinema_id}_{self.data_utils.get_current_timestamp()}.csv"
                filepath = f"data/exports/{filename}"
                
                # 确保目录存在
                import os
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                    if vouchers:
                        writer = csv.DictWriter(f, fieldnames=vouchers[0].to_dict().keys())
                        writer.writeheader()
                        for voucher in vouchers:
                            writer.writerow(voucher.to_dict())
                
                return {
                    'success': True,
                    'code': 200,
                    'message': '导出成功',
                    'data': {
                        'filename': filename,
                        'filepath': filepath,
                        'format': 'csv',
                        'total_vouchers': len(vouchers),
                        'file_size': os.path.getsize(filepath)
                    }
                }
            
            else:
                return {
                    'success': False,
                    'code': 400,
                    'message': f'不支持的导出格式: {export_format}',
                    'data': None
                }
                
        except Exception as e:
            logger.error(f"导出券数据失败: {e}")
            return {
                'success': False,
                'code': 500,
                'message': f'导出失败: {str(e)}',
                'data': None
            }

# 全局API实例
voucher_api = VoucherAPI()

def get_voucher_api() -> VoucherAPI:
    """获取券API实例"""
    return voucher_api

# 便捷函数
def get_user_vouchers(cinema_id: str, token: str, **kwargs) -> Dict[str, Any]:
    """获取用户券列表的便捷函数"""
    return voucher_api.get_user_vouchers(cinema_id, token, **kwargs)

def get_valid_vouchers(cinema_id: str, token: str) -> Dict[str, Any]:
    """获取有效券列表的便捷函数"""
    return voucher_api.get_valid_vouchers_only(cinema_id, token)

def get_order_available_vouchers(cinema_id: str, token: str) -> Dict[str, Any]:
    """获取订单可用券列表的便捷函数（沃美新API）"""
    return voucher_api.get_order_available_vouchers(cinema_id, token)

def search_vouchers(cinema_id: str, token: str, search_term: str) -> Dict[str, Any]:
    """搜索券的便捷函数"""
    return voucher_api.search_vouchers(cinema_id, token, search_term)

def get_voucher_statistics(cinema_id: str, token: str) -> Dict[str, Any]:
    """获取券统计的便捷函数"""
    return voucher_api.get_voucher_statistics_only(cinema_id, token)

def validate_voucher_for_order(cinema_id: str, token: str, voucher_code: str) -> Dict[str, Any]:
    """
    验证券是否可用于订单

    Args:
        cinema_id: 影院ID
        token: 用户token
        voucher_code: 券号

    Returns:
        验证结果
    """
    try:
        # 获取所有券
        vouchers, _ = voucher_api.voucher_service.get_all_vouchers(cinema_id, token)

        # 查找指定券号
        target_voucher = None
        for voucher in vouchers:
            if voucher.voucher_code == voucher_code:
                target_voucher = voucher
                break

        if not target_voucher:
            return {
                'success': False,
                'code': 404,
                'message': '未找到指定券号',
                'data': {'voucher_code': voucher_code, 'valid': False}
            }

        # 检查券的有效性
        is_valid = target_voucher.is_valid()
        validation_details = {
            'voucher_code': voucher_code,
            'voucher_name': target_voucher.voucher_name,
            'status': target_voucher.status,
            'expire_time': target_voucher.expire_time,
            'expire_date': target_voucher.get_expire_date(),
            'balance': target_voucher.voucher_balance,
            'balance_str': target_voucher.voucher_balance_str,
            'valid': is_valid,
            'reasons': []
        }

        # 添加验证失败原因
        if not is_valid:
            if target_voucher.status != VoucherStatus.UN_USE:
                validation_details['reasons'].append(f"券状态为: {target_voucher.status}")
            if target_voucher.is_expired():
                validation_details['reasons'].append("券已过期")
            if target_voucher.voucher_balance <= 0:
                validation_details['reasons'].append("券余额不足")

        return {
            'success': True,
            'code': 200,
            'message': '券验证完成',
            'data': validation_details
        }

    except Exception as e:
        logger.error(f"验证券失败: {e}")
        return {
            'success': False,
            'code': 500,
            'message': f'验证券失败: {str(e)}',
            'data': None
        }
