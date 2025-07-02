#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美订单服务 - 专门处理沃美系统的订单相关功能
集成自订单列表.py，提供统一的订单管理接口
"""

import requests
import json
from typing import Dict, List, Optional, Any
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WomeiOrderService:
    """沃美订单服务类 - 集成到系统架构中"""
    
    def __init__(self, token: str = None):
        """
        初始化沃美订单服务
        
        Args:
            token: 用户认证token（可选，后续可通过set_token设置）
        """
        self.base_url = "https://ct.womovie.cn/ticket/wmyc/user/orders/"
        self.token = token
        self.headers_template = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'content-type': 'multipart/form-data',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i',
        }
    
    def set_token(self, token: str):
        """设置认证token"""
        self.token = token

    def get_order_detail(self, order_id: str, cinema_id: str, token: str = None) -> Dict[str, Any]:
        """
        获取订单详情

        Args:
            order_id: 订单ID
            cinema_id: 影院ID
            token: 用户token（如果不提供则使用实例的token）

        Returns:
            Dict: 包含订单详情数据和状态信息的字典
        """
        try:
            # 使用传入的token或实例的token
            use_token = token or self.token
            if not use_token:
                return {
                    'success': False,
                    'error': 'Token未提供',
                    'order_detail': {}
                }

            if not order_id:
                return {
                    'success': False,
                    'error': '订单ID未提供',
                    'order_detail': {}
                }

            if not cinema_id:
                return {
                    'success': False,
                    'error': '影院ID未提供',
                    'order_detail': {}
                }

            # 调试打印已移除

            # 🔧 修正：使用正确的沃美订单详情API URL格式
            detail_url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/info/"

            # 构建请求头
            headers = self.headers_template.copy()
            headers['token'] = use_token

            # 🔧 修正：通过参数传递order_id
            params = {
                'order_id': order_id,
                'version': 'tp_version'  # 根据现有代码添加版本参数
            }

            # 发送请求
            response = requests.get(
                detail_url,
                params=params,
                headers=headers,
                verify=False,
                timeout=10
            )

            # 调试打印已移除

            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP错误: {response.status_code}',
                    'order_detail': {},
                    'raw_response': response.text
                }

            # 解析JSON响应
            try:
                response_data = response.json()
                # 调试打印已移除

                # 检查API返回状态
                if response_data.get('ret') == 0 and response_data.get('sub') == 0:
                    # 提取订单详情数据
                    detail_data = response_data.get('data', {})

                    # 调试打印已移除
                    # 调试打印已移除
                    # 调试打印已移除
                    # 调试打印已移除
                    # 调试打印已移除

                    # 格式化订单详情数据
                    formatted_detail = self.format_order_detail(detail_data)

                    return {
                        'success': True,
                        'order_detail': formatted_detail,
                        'raw_response': response_data
                    }
                else:
                    error_msg = response_data.get('msg', '未知错误')
                    print(f"[沃美订单服务] ❌ API返回错误: {error_msg}")
                    return {
                        'success': False,
                        'error': f'API错误: {error_msg}',
                        'order_detail': {},
                        'raw_response': response_data
                    }

            except json.JSONDecodeError as e:
                print(f"[沃美订单服务] ❌ JSON解析失败: {e}")
                # 调试打印已移除
                return {
                    'success': False,
                    'error': f'JSON解析失败: {str(e)}',
                    'order_detail': {},
                    'raw_response': response.text
                }

        except requests.exceptions.Timeout:
            # 调试打印已移除
            return {
                'success': False,
                'error': '请求超时',
                'order_detail': {}
            }
        except requests.exceptions.RequestException as e:
            print(f"[沃美订单服务] ❌ 网络请求失败: {e}")
            return {
                'success': False,
                'error': f'网络请求失败: {str(e)}',
                'order_detail': {}
            }
        except Exception as e:
            print(f"[沃美订单服务] ❌ 未知错误: {e}")
            return {
                'success': False,
                'error': f'未知错误: {str(e)}',
                'order_detail': {}
            }
    
    def get_orders(self, token: str = None, offset: int = 0) -> Dict[str, Any]:
        """
        获取订单列表
        
        Args:
            token: 用户token（如果不提供则使用实例的token）
            offset: 分页偏移量，默认为0
            
        Returns:
            Dict: 包含订单数据和状态信息的字典
        """
        try:
            # 使用传入的token或实例的token
            use_token = token or self.token
            if not use_token:
                return {
                    'success': False,
                    'error': 'Token未提供',
                    'orders': []
                }
            
            # 调试打印已移除
            # 调试打印已移除
            
            # 构建请求头
            headers = self.headers_template.copy()
            headers['token'] = use_token
            
            # 构建请求参数
            params = {
                'offset': str(offset),
            }
            
            # 发送请求
            response = requests.get(
                self.base_url, 
                params=params, 
                headers=headers, 
                verify=False,
                timeout=10
            )
            
            # 调试打印已移除
            
            if response.status_code != 200:
                return {
                    'success': False,
                    'error': f'HTTP错误: {response.status_code}',
                    'orders': [],
                    'raw_response': response.text
                }
            
            # 解析JSON响应
            try:
                response_data = response.json()

                # 检查API返回状态
                if response_data.get('ret') == 0 and response_data.get('sub') == 0:
                    # 提取订单数据
                    data = response_data.get('data', {})
                    orders_list = data.get('orders', [])
                    next_offset = data.get('next_offset', 0)
                    
                    # 格式化订单数据
                    formatted_orders = self.format_orders_list(orders_list)
                    
                    return {
                        'success': True,
                        'orders': formatted_orders,
                        'next_offset': next_offset,
                        'total_count': len(formatted_orders),
                        'raw_response': response_data
                    }
                else:
                    error_msg = response_data.get('msg', '未知错误')
                    print(f"[沃美订单服务] ❌ API返回错误: {error_msg}")
                    return {
                        'success': False,
                        'error': f'API错误: {error_msg}',
                        'orders': [],
                        'raw_response': response_data
                    }
                    
            except json.JSONDecodeError as e:
                print(f"[沃美订单服务] ❌ JSON解析失败: {e}")
                # 调试打印已移除
                return {
                    'success': False,
                    'error': f'JSON解析失败: {str(e)}',
                    'orders': [],
                    'raw_response': response.text
                }
                
        except requests.exceptions.Timeout:
            # 调试打印已移除
            return {
                'success': False,
                'error': '请求超时',
                'orders': []
            }
        except requests.exceptions.RequestException as e:
            print(f"[沃美订单服务] ❌ 网络请求失败: {e}")
            return {
                'success': False,
                'error': f'网络请求失败: {str(e)}',
                'orders': []
            }
        except Exception as e:
            print(f"[沃美订单服务] ❌ 未知错误: {e}")
            return {
                'success': False,
                'error': f'未知错误: {str(e)}',
                'orders': []
            }
    
    def decode_unicode_message(self, text: str) -> str:
        """解码Unicode编码的中文字符"""
        try:
            if not text or not isinstance(text, str):
                return text
            
            # 检查是否包含Unicode编码
            if '\\u' in text:
                # 方法1：直接使用json.loads解析
                try:
                    unicode_str = f'"{text}"'
                    decoded = json.loads(unicode_str)
                    return decoded
                except:
                    # 方法2：手动替换Unicode编码
                    import codecs
                    return codecs.decode(text, 'unicode_escape')
            
            return text
            
        except Exception as e:
            print(f"[沃美订单服务] Unicode解码失败: {e}, 原文: {text}")
            return text
    
    def extract_order_fields(self, order_data: Dict) -> Dict[str, str]:
        """
        从订单数据中提取4个关键字段
        
        Args:
            order_data: 单个订单的原始数据
            
        Returns:
            Dict: 包含4个关键字段的字典
        """
        try:
            # 提取影片名称
            movie_name = order_data.get('movie_name', '未知影片')
            if not movie_name or movie_name.strip() == '':
                movie_name = '未知影片'
            
            # 提取订单状态
            status_desc = order_data.get('status_desc', '未知状态')
            if not status_desc or status_desc.strip() == '':
                # 如果status_desc为空，尝试使用status字段
                status = order_data.get('status', '')
                status_desc = status if status else '未知状态'
            
            # 提取影院名称
            cinema_name = order_data.get('cinema_name', '未知影院')
            if not cinema_name or cinema_name.strip() == '':
                cinema_name = '未知影院'
            
            # 提取订单号
            order_id = order_data.get('order_id', '未知订单号')
            if not order_id or str(order_id).strip() == '':
                order_id = '未知订单号'
            else:
                order_id = str(order_id)
            
            return {
                'movie_name': movie_name.strip(),
                'status_desc': status_desc.strip(),
                'cinema_name': cinema_name.strip(),
                'order_id': order_id.strip()
            }
            
        except Exception as e:
            print(f"[沃美订单服务] ❌ 字段提取失败: {e}")
            return {
                'movie_name': '未知影片',
                'status_desc': '未知状态',
                'cinema_name': '未知影院',
                'order_id': '未知订单号'
            }

    def format_order_detail(self, detail_data: Dict) -> Dict[str, Any]:
        """
        格式化订单详情数据，兼容现有双击事件处理逻辑

        Args:
            detail_data: 订单详情原始数据

        Returns:
            Dict: 格式化后的订单详情数据，兼容现有UI显示逻辑
        """
        try:
            # 提取基本订单信息
            order_id = detail_data.get('order_id', '')
            movie_name = detail_data.get('movie_name', '')
            cinema_name = detail_data.get('cinema_name', '')
            status_desc = detail_data.get('status_desc', '')
            show_date = detail_data.get('show_date', '')

            # 提取取票码信息
            ticket_code = detail_data.get('ticket_code', '')
            ticket_code_arr = detail_data.get('ticket_code_arr', [])

            # 提取座位和影厅信息
            ticket_items = detail_data.get('ticket_items', {})
            seat_info = ticket_items.get('seat_info', '')
            hall_name = ticket_items.get('hall_name', '')

            # 处理取票码数组，提取序列号和验证码
            qr_code = ticket_code  # 主取票码
            ds_code = ''  # 验证码

            if ticket_code_arr and isinstance(ticket_code_arr, list):
                for code_item in ticket_code_arr:
                    if isinstance(code_item, dict):
                        name = code_item.get('name', '').lower()
                        code = code_item.get('code', '')
                        if '序列号' in name or 'serial' in name:
                            qr_code = code
                        elif '验证码' in name or 'verify' in name or 'validation' in name:
                            ds_code = code

            # 调试打印已移除

            # 🔧 构建兼容现有UI逻辑的数据结构（按照字段映射要求）
            formatted_detail = {
                # 🎯 UI期望的字段名（映射后）
                'order_no': order_id,  # order_id → order_no
                'ticket_code': qr_code,  # 使用主取票码
                'film_name': movie_name,  # movie_name → film_name
                'cinema_name': cinema_name,  # 保持不变
                'show_time': show_date,  # show_date → show_time
                'hall_name': hall_name,  # 保持不变
                'seat_info': seat_info,  # 保持不变
                'status_desc': status_desc,  # 状态描述

                # 🎯 显示类型设置（使用generated_qrcode类型）
                'display_type': 'generated_qrcode',

                # 🔧 保留原始字段名（向后兼容）
                'order_id': order_id,
                'movie_name': movie_name,
                'show_date': show_date,
                'qrCode': qr_code,  # 主取票码
                'ticketCode': ticket_code,  # 原始取票码
                'dsValidateCode': ds_code,  # 验证码

                # 显示用的格式化字段
                'display': {
                    'title': movie_name,
                    'subtitle': f"{cinema_name} | {status_desc}",
                    'order_no': order_id,
                    'summary': f"{movie_name} - {status_desc}",
                    'ticket_info': f"{hall_name} {seat_info}" if hall_name and seat_info else (hall_name or seat_info or ''),
                    'show_time': show_date
                },

                # 🎯 二维码生成所需的订单信息
                'order_info': {
                    'filmName': movie_name,  # 二维码生成器期望的字段名
                    'cinemaName': cinema_name,
                    'showTime': show_date,
                    'hallName': hall_name,
                    'seatInfo': seat_info,
                    'orderNo': order_id,
                    'ticketCode': qr_code
                },

                # 原始数据（用于调试和扩展）
                'raw_data': detail_data
            }

            return formatted_detail

        except Exception as e:
            print(f"[沃美订单服务] ❌ 订单详情格式化失败: {e}")
            return {
                'order_id': detail_data.get('order_id', '未知订单号'),
                'movie_name': '格式化失败',
                'cinema_name': '未知影院',
                'status_desc': '未知状态',
                'show_date': '',
                'seat_info': '',
                'hall_name': '',
                'qrCode': '',
                'ticketCode': '',
                'dsValidateCode': '',
                'display': {
                    'title': '格式化失败',
                    'subtitle': '未知影院 | 未知状态',
                    'order_no': detail_data.get('order_id', '未知订单号'),
                    'summary': '格式化失败',
                    'ticket_info': '',
                    'show_time': ''
                },
                'raw_data': detail_data
            }

    def format_single_order(self, order_data: Dict) -> Dict[str, Any]:
        """
        格式化单个订单数据

        Args:
            order_data: 单个订单的原始数据

        Returns:
            Dict: 格式化后的订单数据
        """
        try:
            # 提取4个关键字段
            key_fields = self.extract_order_fields(order_data)

            # 提取其他有用字段
            show_date = order_data.get('show_date', '')
            ticket_num = order_data.get('ticket_num', 0)
            hall_name = order_data.get('hall_name', '')
            seat_info = order_data.get('seat_info', '')

            # 构建格式化后的订单数据
            formatted_order = {
                # 4个关键字段
                'movie_name': key_fields['movie_name'],
                'status_desc': key_fields['status_desc'],
                'cinema_name': key_fields['cinema_name'],
                'order_id': key_fields['order_id'],

                # 其他字段
                'show_date': show_date,
                'ticket_num': ticket_num,
                'hall_name': hall_name,
                'seat_info': seat_info,

                # 显示用的格式化字段
                'display': {
                    'title': key_fields['movie_name'],
                    'subtitle': f"{key_fields['cinema_name']} | {key_fields['status_desc']}",
                    'order_no': key_fields['order_id'],
                    'summary': f"{key_fields['movie_name']} - {key_fields['status_desc']}"
                },

                # 原始数据（用于调试）
                'raw_data': order_data
            }

            return formatted_order

        except Exception as e:
            print(f"[沃美订单服务] ❌ 单个订单格式化失败: {e}")
            return {
                'movie_name': '未知影片',
                'status_desc': '未知状态',
                'cinema_name': '未知影院',
                'order_id': '未知订单号',
                'show_date': '',
                'ticket_num': 0,
                'hall_name': '',
                'seat_info': '',
                'display': {
                    'title': '未知影片',
                    'subtitle': '未知影院 | 未知状态',
                    'order_no': '未知订单号',
                    'summary': '未知影片 - 未知状态'
                },
                'raw_data': order_data
            }

    def format_orders_list(self, orders_data: List[Dict]) -> List[Dict[str, Any]]:
        """
        格式化订单列表

        Args:
            orders_data: 订单列表原始数据

        Returns:
            List: 格式化后的订单列表
        """
        try:
            if not isinstance(orders_data, list):
                print(f"[沃美订单服务] ❌ 订单列表数据类型错误: {type(orders_data)}")
                return []

            formatted_orders = []

            for i, order in enumerate(orders_data):
                formatted_order = self.format_single_order(order)
                formatted_orders.append(formatted_order)

            return formatted_orders

        except Exception as e:
            print(f"[沃美订单服务] ❌ 订单列表格式化失败: {e}")
            return []


# 全局服务实例
_womei_order_service = None

def get_womei_order_service(token: str = None) -> WomeiOrderService:
    """获取沃美订单服务实例"""
    global _womei_order_service
    if _womei_order_service is None:
        _womei_order_service = WomeiOrderService(token)
    elif token:
        _womei_order_service.set_token(token)
    return _womei_order_service


def get_user_orders(token: str, offset: int = 0) -> Dict[str, Any]:
    """
    便捷函数：获取用户订单列表

    Args:
        token: 用户token
        offset: 分页偏移量，默认为0

    Returns:
        Dict: 包含订单数据和状态信息的字典
    """
    service = get_womei_order_service()
    return service.get_orders(token, offset)


def get_order_detail(order_id: str, cinema_id: str, token: str) -> Dict[str, Any]:
    """
    便捷函数：获取订单详情

    Args:
        order_id: 订单ID
        cinema_id: 影院ID
        token: 用户token

    Returns:
        Dict: 包含订单详情数据和状态信息的字典
    """
    service = get_womei_order_service()
    return service.get_order_detail(order_id, cinema_id, token)


def extract_key_fields_from_orders(orders_data: List[Dict]) -> List[Dict[str, str]]:
    """
    便捷函数：从订单列表中提取关键字段

    Args:
        orders_data: 订单列表原始数据

    Returns:
        List: 包含关键字段的订单列表
    """
    service = get_womei_order_service()
    key_fields_list = []

    for order in orders_data:
        key_fields = service.extract_order_fields(order)
        key_fields_list.append(key_fields)

    return key_fields_list
