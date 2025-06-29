#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美优惠券缺失接口实现方案
基于HAR文件分析结果，实现缺失的优惠券相关API接口
"""

import requests
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class WomeiVoucherServiceExtended:
    """
    扩展的沃美优惠券服务
    实现HAR文件中发现的缺失接口
    """
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.headers_template = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'multipart/form-data',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9'
        }
    
    def get_vouchers_by_type(self, cinema_id: str, token: str, voucher_type: str, 
                           schedule_id: str = "", goods_id: str = "") -> Dict[str, Any]:
        """
        按类型获取优惠券列表 (HAR接口1)
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            voucher_type: 券类型 (VGC_P/VGC_T)
            schedule_id: 场次ID
            goods_id: 商品ID
            
        Returns:
            Dict: 券列表结果
        """
        try:
            headers = self.headers_template.copy()
            headers['token'] = token
            
            # 构建查询参数
            params = {
                'voucher_type': voucher_type,
                'schedule_id': schedule_id,
                'goods_id': goods_id
            }
            
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/user/vouchers"
            
            print(f"[券类型查询] 🚀 查询券类型: {voucher_type}")
            print(f"[券类型查询] 📡 URL: {url}")
            print(f"[券类型查询] 📋 参数: {params}")
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            
            print(f"[券类型查询] 📥 响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"[券类型查询] ✅ 查询成功，券数量: {len(result.get('data', []))}")
                return result
            else:
                return {
                    'ret': -1,
                    'sub': response.status_code,
                    'msg': f'请求失败: HTTP {response.status_code}',
                    'data': []
                }
                
        except Exception as e:
            logger.error(f"按类型查询券失败: {e}")
            return {
                'ret': -1,
                'sub': -1,
                'msg': f'查询异常: {str(e)}',
                'data': []
            }
    
    def get_vouchers_page(self, cinema_id: str, token: str, voucher_type: str,
                         schedule_id: str = "", goods_id: str = "", page_index: int = 1) -> Dict[str, Any]:
        """
        分页获取优惠券列表 (HAR接口2)
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            voucher_type: 券类型
            schedule_id: 场次ID
            goods_id: 商品ID
            page_index: 页码
            
        Returns:
            Dict: 分页券列表结果
        """
        try:
            headers = self.headers_template.copy()
            headers['token'] = token
            
            params = {
                'voucher_type': voucher_type,
                'schedule_id': schedule_id,
                'goods_id': goods_id,
                'page_index': str(page_index)
            }
            
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/user/vouchers_page"
            
            print(f"[分页券查询] 🚀 查询第{page_index}页券列表")
            print(f"[分页券查询] 📡 URL: {url}")
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                page_info = result.get('data', {}).get('page', {})
                vouchers = result.get('data', {}).get('result', [])
                
                print(f"[分页券查询] ✅ 查询成功")
                print(f"[分页券查询] 📊 页面信息: 第{page_info.get('page_num', 0)}页，共{page_info.get('total_page', 0)}页")
                print(f"[分页券查询] 🎫 券数量: {len(vouchers)}")
                
                return result
            else:
                return {
                    'ret': -1,
                    'sub': response.status_code,
                    'msg': f'分页查询失败: HTTP {response.status_code}',
                    'data': {'page': {}, 'result': []}
                }
                
        except Exception as e:
            logger.error(f"分页查询券失败: {e}")
            return {
                'ret': -1,
                'sub': -1,
                'msg': f'分页查询异常: {str(e)}',
                'data': {'page': {}, 'result': []}
            }
    
    def get_voucher_usable_count(self, cinema_id: str, token: str, order_id: str,
                               voucher_type: str = "EVGC_VOUCHER", card_id: str = "") -> Dict[str, Any]:
        """
        获取优惠券可用数量 (HAR接口3)
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_type: 券类型
            card_id: 卡ID
            
        Returns:
            Dict: 可用数量结果
        """
        try:
            headers = self.headers_template.copy()
            headers['token'] = token
            
            params = {
                'order_id': order_id,
                'type': voucher_type,
                'card_id': card_id
            }
            
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/vcc/usable/count"
            
            print(f"[券数量统计] 🚀 查询订单{order_id}的券可用数量")
            print(f"[券数量统计] 📡 URL: {url}")
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                count = result.get('data', {}).get('count', 0)
                
                print(f"[券数量统计] ✅ 查询成功，可用券数量: {count}")
                return result
            else:
                return {
                    'ret': -1,
                    'sub': response.status_code,
                    'msg': f'数量查询失败: HTTP {response.status_code}',
                    'data': {'order_id': order_id, 'count': 0}
                }
                
        except Exception as e:
            logger.error(f"查询券可用数量失败: {e}")
            return {
                'ret': -1,
                'sub': -1,
                'msg': f'数量查询异常: {str(e)}',
                'data': {'order_id': order_id, 'count': 0}
            }
    
    def calculate_voucher_price(self, cinema_id: str, token: str, order_id: str,
                              voucher_code: str, **kwargs) -> Dict[str, Any]:
        """
        计算优惠券价格 (HAR接口4)
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_code: 券码
            **kwargs: 其他参数
            
        Returns:
            Dict: 价格计算结果
        """
        try:
            headers = self.headers_template.copy()
            headers['token'] = token
            
            # 构建POST数据
            data = {
                'order_id': order_id,
                'voucher_code': voucher_code,
                **kwargs
            }
            
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/voucher/price/"
            
            print(f"[券价格计算] 🚀 计算券{voucher_code}的价格")
            print(f"[券价格计算] 📡 URL: {url}")
            print(f"[券价格计算] 📋 订单ID: {order_id}")
            
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                price_data = result.get('data', {})
                
                print(f"[券价格计算] ✅ 计算成功")
                print(f"[券价格计算] 💰 支付价格: {price_data.get('pay_price', 0)}")
                print(f"[券价格计算] 💸 附加费用: {price_data.get('surcharge_price', 0)}")
                
                return result
            else:
                return {
                    'ret': -1,
                    'sub': response.status_code,
                    'msg': f'价格计算失败: HTTP {response.status_code}',
                    'data': {'surcharge_price': 0, 'pay_price': 0, 'surcharge_msg': ''}
                }
                
        except Exception as e:
            logger.error(f"计算券价格失败: {e}")
            return {
                'ret': -1,
                'sub': -1,
                'msg': f'价格计算异常: {str(e)}',
                'data': {'surcharge_price': 0, 'pay_price': 0, 'surcharge_msg': ''}
            }
    
    def get_order_vcc_list(self, cinema_id: str, token: str, order_id: str,
                          voucher_type: str = "EVGC_VOUCHER", card_id: str = "") -> Dict[str, Any]:
        """
        获取订单VCC券列表 (HAR接口5)
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_type: 券类型
            card_id: 卡ID
            
        Returns:
            Dict: VCC券列表结果
        """
        try:
            headers = self.headers_template.copy()
            headers['token'] = token
            
            params = {
                'order_id': order_id,
                'type': voucher_type,
                'card_id': card_id
            }
            
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/vcc/list/"
            
            print(f"[VCC券查询] 🚀 查询订单{order_id}的VCC券列表")
            print(f"[VCC券查询] 📡 URL: {url}")
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                vcc_data = result.get('data', {})
                usable_count = len(vcc_data.get('usable', []))
                disable_count = len(vcc_data.get('disable', []))
                
                print(f"[VCC券查询] ✅ 查询成功")
                print(f"[VCC券查询] 🎫 可用VCC券: {usable_count}张")
                print(f"[VCC券查询] 🚫 不可用VCC券: {disable_count}张")
                
                return result
            else:
                return {
                    'ret': -1,
                    'sub': response.status_code,
                    'msg': f'VCC券查询失败: HTTP {response.status_code}',
                    'data': {'order_id': order_id, 'usable': [], 'disable': []}
                }
                
        except Exception as e:
            logger.error(f"查询VCC券列表失败: {e}")
            return {
                'ret': -1,
                'sub': -1,
                'msg': f'VCC券查询异常: {str(e)}',
                'data': {'order_id': order_id, 'usable': [], 'disable': []}
            }
    
    def complete_voucher_workflow(self, cinema_id: str, token: str, order_id: str,
                                voucher_code: str, voucher_type: str = "VGC_T") -> Dict[str, Any]:
        """
        完整的优惠券使用工作流程
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_code: 券码
            voucher_type: 券类型
            
        Returns:
            Dict: 完整流程结果
        """
        workflow_result = {
            'success': False,
            'steps': {},
            'final_result': {},
            'error_message': ''
        }
        
        try:
            print(f"[完整券流程] 🚀 开始完整券使用流程")
            print(f"[完整券流程] 📋 订单: {order_id}, 券码: {voucher_code}")
            
            # 步骤1: 计算券价格
            print(f"[完整券流程] 1️⃣ 计算券价格...")
            price_result = self.calculate_voucher_price(cinema_id, token, order_id, voucher_code)
            workflow_result['steps']['price_calculation'] = price_result
            
            if price_result.get('ret') != 0:
                workflow_result['error_message'] = f"价格计算失败: {price_result.get('msg')}"
                return workflow_result
            
            # 步骤2: 绑定券到订单
            print(f"[完整券流程] 2️⃣ 绑定券到订单...")
            from services.womei_order_voucher_service import WomeiOrderVoucherService
            order_service = WomeiOrderVoucherService()
            
            bind_result = order_service.bind_voucher_to_order(
                cinema_id, token, order_id, voucher_code, voucher_type
            )
            workflow_result['steps']['voucher_binding'] = bind_result
            
            if bind_result.get('ret') != 0:
                workflow_result['error_message'] = f"券绑定失败: {bind_result.get('msg')}"
                return workflow_result
            
            # 步骤3: 验证结果
            print(f"[完整券流程] 3️⃣ 验证券使用结果...")
            final_price = bind_result.get('data', {}).get('order_payment_price', 0)
            voucher_use = bind_result.get('data', {}).get('voucher_use', {})
            
            workflow_result['success'] = True
            workflow_result['final_result'] = {
                'order_payment_price': final_price,
                'voucher_use': voucher_use,
                'voucher_discounts': bind_result.get('data', {}).get('voucher_discounts', [])
            }
            
            print(f"[完整券流程] ✅ 券使用流程完成")
            print(f"[完整券流程] 💰 最终支付价格: {final_price}")
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"完整券流程异常: {e}")
            workflow_result['error_message'] = f"流程异常: {str(e)}"
            return workflow_result


# 全局服务实例
_extended_voucher_service = None

def get_extended_voucher_service() -> WomeiVoucherServiceExtended:
    """获取扩展券服务实例"""
    global _extended_voucher_service
    if _extended_voucher_service is None:
        _extended_voucher_service = WomeiVoucherServiceExtended()
    return _extended_voucher_service


# 便捷函数
def get_vouchers_by_type(cinema_id: str, token: str, voucher_type: str, **kwargs) -> Dict[str, Any]:
    """按类型获取券列表的便捷函数"""
    service = get_extended_voucher_service()
    return service.get_vouchers_by_type(cinema_id, token, voucher_type, **kwargs)

def calculate_voucher_price(cinema_id: str, token: str, order_id: str, voucher_code: str) -> Dict[str, Any]:
    """计算券价格的便捷函数"""
    service = get_extended_voucher_service()
    return service.calculate_voucher_price(cinema_id, token, order_id, voucher_code)

def complete_voucher_workflow(cinema_id: str, token: str, order_id: str, voucher_code: str) -> Dict[str, Any]:
    """完整券使用流程的便捷函数"""
    service = get_extended_voucher_service()
    return service.complete_voucher_workflow(cinema_id, token, order_id, voucher_code)
