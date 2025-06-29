#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美影城订单券绑定服务
基于优化测试结果实现的单接口模式券绑定功能
"""

import requests
import json
import urllib3
from typing import Dict, Optional, Any

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WomeiOrderVoucherService:
    """沃美订单券绑定服务"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        
        # 标准请求头模板
        self.headers_template = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
    
    def decode_unicode_message(self, response_text: str) -> Optional[Dict]:
        """解码响应中的Unicode字符"""
        try:
            response_data = json.loads(response_text)
            
            # 递归解码Unicode字符
            def decode_unicode_recursive(obj):
                if isinstance(obj, dict):
                    return {k: decode_unicode_recursive(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [decode_unicode_recursive(item) for item in obj]
                elif isinstance(obj, str):
                    try:
                        # 🔧 修复Unicode解码逻辑
                        if '\\u' in obj:
                            # 使用codecs.decode处理Unicode转义
                            import codecs
                            decoded = codecs.decode(obj, 'unicode_escape')
                            return decoded
                        else:
                            return obj
                    except Exception:
                        return obj
                else:
                    return obj
            
            return decode_unicode_recursive(response_data)
            
        except Exception as e:
            print(f"[沃美券绑定] Unicode解码失败: {e}")
            return None



    def calculate_voucher_price(self, cinema_id: str, token: str, order_id: str,
                              voucher_code: str, voucher_type: str = 'VGC_T') -> Dict[str, Any]:
        """
        🧮 计算优惠券价格 (HAR接口实现)
        调用 POST /order/voucher/price/ 接口计算使用券后的价格

        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_code: 券码
            voucher_type: 券类型，默认VGC_T

        Returns:
            Dict: 价格计算结果，包含 pay_price, surcharge_price 等信息
        """
        try:
            print(f"[沃美券价格] 🧮 开始计算券价格")
            print(f"[沃美券价格] 📋 订单ID: {order_id}")
            print(f"[沃美券价格] 🎫 券码: {voucher_code}")
            print(f"[沃美券价格] 🏢 影院ID: {cinema_id}")
            print(f"[沃美券价格] 🔑 Token: {token[:20]}...")

            # 构建请求头 (修复Content-Type)
            headers = self.headers_template.copy()
            headers['token'] = token
            headers['Content-Type'] = 'application/x-www-form-urlencoded'  # 🆕 修复Content-Type

            # 构建请求URL
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/voucher/price/"

            # 🆕 构建POST数据 (基于HAR文件分析，只保留核心参数)
            data = {
                'voucher_code': voucher_code,  # 券码
                'order_id': order_id          # 订单ID
            }

            print(f"[沃美券价格] 📡 请求URL: {url}")
            print(f"[沃美券价格] 📋 请求参数 (HAR格式): {data}")
            print(f"[沃美券价格] 📋 Content-Type: application/x-www-form-urlencoded")

            # 🆕 发送POST请求 (使用正确的Content-Type)
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)

            print(f"[沃美券价格] 📥 响应状态: {response.status_code}")
            print(f"[沃美券价格] 📥 原始响应: {response.text}")

            if response.status_code == 200:
                # 解码Unicode字符
                decoded_data = self.decode_unicode_message(response.text)

                if decoded_data:
                    print(f"[沃美券价格] 📋 解码后完整响应:")
                    print(json.dumps(decoded_data, ensure_ascii=False, indent=2))

                    # 提取价格信息
                    data_section = decoded_data.get('data', {})
                    price_info = {
                        'pay_price': data_section.get('pay_price', 0),
                        'surcharge_price': data_section.get('surcharge_price', 0),
                        'surcharge_msg': data_section.get('surcharge_msg', '')
                    }

                    print(f"[沃美券价格] 💰 价格计算结果:")
                    print(f"[沃美券价格] 💰 支付价格: {price_info['pay_price']}")
                    print(f"[沃美券价格] 💸 附加费用: {price_info['surcharge_price']}")
                    print(f"[沃美券价格] 📝 附加说明: {price_info['surcharge_msg']}")

                    return {
                        'success': True,
                        'ret': decoded_data.get('ret', 0),
                        'sub': decoded_data.get('sub', 0),
                        'msg': decoded_data.get('msg', ''),
                        'data': decoded_data.get('data', {}),
                        'price_info': price_info
                    }
                else:
                    return {
                        'success': False,
                        'ret': -1,
                        'sub': -1,
                        'msg': '响应解析失败',
                        'data': {},
                        'error': 'decode_failed'
                    }
            else:
                return {
                    'success': False,
                    'ret': -1,
                    'sub': response.status_code,
                    'msg': f'价格计算失败: HTTP {response.status_code}',
                    'data': {},
                    'error': 'http_error'
                }

        except Exception as e:
            print(f"[沃美券价格] ❌ 价格计算异常: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'ret': -1,
                'sub': -1,
                'msg': f'价格计算异常: {str(e)}',
                'data': {},
                'error': 'exception'
            }

    def bind_voucher_to_order(self, cinema_id: str, token: str, order_id: str,
                             voucher_code: str, voucher_type: str = 'VGC_T') -> Dict[str, Any]:
        """
        🚀 单接口券绑定
        直接调用券绑定API，实现券抵扣功能（已优化简化）

        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_code: 券码
            voucher_type: 券类型，默认VGC_T

        Returns:
            Dict: 券绑定结果，包含价格信息和券使用详情
        """
        try:
            print(f"[沃美券绑定] 🚀 开始单接口券绑定")
            print(f"[沃美券绑定] 📋 订单ID: {order_id}")
            print(f"[沃美券绑定] 🎫 券码: {voucher_code}")
            print(f"[沃美券绑定] 🏢 影院ID: {cinema_id}")
            print(f"[沃美券绑定] 🔑 Token: {token[:20]}...")

            # 构建请求头 (修复Content-Type)
            headers = self.headers_template.copy()
            headers['token'] = token
            headers['Content-Type'] = 'application/x-www-form-urlencoded'  # 🆕 修复Content-Type

            # 构建请求URL
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"

            # 🎉 单接口模式参数（顺序匹配目标curl命令）
            data = {
                'order_id': order_id,
                'discount_id': '0',
                'discount_type': 'TP_VOUCHER',  # 🎉 关键参数：确保券抵扣生效
                'card_id': '',
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'use_rewards': 'Y',
                'use_limit_cards': 'N',
                'limit_cards': '[]',
                'voucher_code': voucher_code,
                'voucher_code_type': voucher_type,
                'ticket_pack_goods': ' ',
            }
            
            print(f"[沃美券绑定] 📡 请求URL: {url}")
            print(f"[沃美券绑定] 📤 请求参数: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 发送POST请求
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            
            print(f"[沃美券绑定] 📥 HTTP状态码: {response.status_code}")
            print(f"[沃美券绑定] 📥 原始响应: {response.text[:500]}...")
            
            if response.status_code == 200:
                # 解码Unicode字符
                decoded_data = self.decode_unicode_message(response.text)
                
                if decoded_data:
                    print(f"[沃美券绑定] 📋 解码后响应: {json.dumps(decoded_data, ensure_ascii=False, indent=2)}")
                    
                    # 分析响应结果
                    ret = decoded_data.get('ret', -1)
                    sub = decoded_data.get('sub', -1)
                    msg = decoded_data.get('msg', '未知错误')
                    data_section = decoded_data.get('data', {})
                    
                    print(f"[沃美券绑定] 🔍 响应分析: ret={ret}, sub={sub}, msg={msg}")
                    
                    # 检查数据完整性
                    has_price_info = any(field in data_section for field in [
                        'order_total_price', 'order_payment_price', 'ticket_total_price'
                    ])
                    has_voucher_info = any(field in data_section for field in [
                        'voucher_use', 'voucher_discounts', 'voucher_use_goods'
                    ])
                    
                    print(f"[沃美券绑定] 📊 数据完整性: 价格信息={has_price_info}, 券信息={has_voucher_info}")
                    
                    # 🔧 修复：正确处理Token超时问题
                    is_token_timeout = (ret == 0 and sub == 408)
                    is_success = (ret == 0 and sub == 0)

                    # 🔧 用户友好的错误处理
                    user_friendly_msg = msg
                    error_type = 'unknown'

                    if not is_success:
                        if sub == 4004:
                            error_type = 'voucher_cinema_restriction'
                            user_friendly_msg = "该券码不适用于当前影院，请尝试其他券码或联系影院客服"
                        elif sub == 1000:
                            error_type = 'parameter_error'
                            user_friendly_msg = "券码参数错误，请检查券码是否正确"
                        elif is_token_timeout:
                            error_type = 'token_timeout'
                            user_friendly_msg = "登录已过期，请重新登录"
                        else:
                            error_type = 'api_failed'

                    # 构建标准化返回结果
                    result = {
                        'success': is_success,
                        'ret': ret,
                        'sub': sub,
                        'msg': user_friendly_msg,
                        'original_msg': msg,  # 保留原始消息用于调试
                        'data': data_section,
                        'has_price_calculation': has_price_info,
                        'has_voucher_details': has_voucher_info,
                        'single_interface_mode': True,  # 标记为单接口模式
                        'voucher_code': voucher_code,
                        'order_id': order_id,
                        'is_token_timeout': is_token_timeout,  # 🆕 标记Token超时
                        'error': error_type  # 🆕 错误类型
                    }
                    
                    # 如果成功，提取关键信息
                    if result['success'] and data_section:
                        # 提取价格信息
                        price_info = {
                            'order_total_price': data_section.get('order_total_price', 0),
                            'order_payment_price': data_section.get('order_payment_price', 0),
                            'ticket_total_price': data_section.get('ticket_total_price', 0),
                            'ticket_payment_total_price': data_section.get('ticket_payment_total_price', 0)
                        }
                        result['price_info'] = price_info
                        
                        # 提取券使用信息
                        voucher_use = data_section.get('voucher_use', {})
                        if voucher_use:
                            voucher_info = {
                                'use_codes': voucher_use.get('use_codes', []),
                                'use_total_price': voucher_use.get('use_total_price', 0),
                                'use_detail': voucher_use.get('use_detail', [])
                            }
                            result['voucher_info'] = voucher_info
                            
                            # 计算节省金额
                            original_price = price_info.get('order_total_price', 0)
                            payment_price = price_info.get('order_payment_price', 0)
                            savings = original_price - payment_price
                            result['savings'] = savings
                            
                            print(f"[沃美券绑定] 💰 价格计算: 原价={original_price}, 支付={payment_price}, 节省={savings}")
                    
                    return result
                else:
                    return {
                        'success': False,
                        'ret': -1,
                        'sub': -1,
                        'msg': '响应解析失败',
                        'data': {},
                        'error': 'decode_failed'
                    }
            else:
                return {
                    'success': False,
                    'ret': -1,
                    'sub': -1,
                    'msg': f'HTTP请求失败: {response.status_code}',
                    'data': {},
                    'error': 'http_error'
                }
                
        except Exception as e:
            print(f"[沃美券绑定] ❌ 券绑定异常: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'ret': -1,
                'sub': -1,
                'msg': f'请求异常: {str(e)}',
                'data': {},
                'error': 'exception'
            }

    def complete_voucher_workflow(self, cinema_id: str, token: str, order_id: str,
                                voucher_code: str, voucher_type: str = 'VGC_T') -> Dict[str, Any]:
        """
        🔄 完整的两步式券使用工作流程
        1. 先调用价格计算接口获取价格信息
        2. 再调用券绑定接口完成券使用

        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            voucher_code: 券码
            voucher_type: 券类型，默认VGC_T

        Returns:
            Dict: 完整流程结果，包含两个步骤的详细信息
        """
        workflow_result = {
            'success': False,
            'steps': {},
            'final_result': {},
            'error_message': '',
            'price_calculation': {},
            'voucher_binding': {}
        }

        try:
            print(f"[沃美券流程] 🔄 开始完整券使用流程")
            print(f"[沃美券流程] 📋 订单: {order_id}, 券码: {voucher_code}")
            print(f"[沃美券流程] 🏢 影院: {cinema_id}, 券类型: {voucher_type}")

            # 步骤1: 计算券价格
            print(f"[沃美券流程] 1️⃣ 第一步：计算券价格...")
            price_result = self.calculate_voucher_price(cinema_id, token, order_id, voucher_code, voucher_type)
            workflow_result['steps']['price_calculation'] = price_result
            workflow_result['price_calculation'] = price_result

            if not price_result.get('success', False) or price_result.get('ret') != 0:
                error_msg = price_result.get('msg', '价格计算失败')
                workflow_result['error_message'] = f"价格计算失败: {error_msg}"
                print(f"[沃美券流程] ❌ 价格计算失败: {error_msg}")
                return workflow_result

            print(f"[沃美券流程] ✅ 价格计算成功")

            # 步骤2: 绑定券到订单
            print(f"[沃美券流程] 2️⃣ 第二步：绑定券到订单...")
            bind_result = self.bind_voucher_to_order(cinema_id, token, order_id, voucher_code, voucher_type)
            workflow_result['steps']['voucher_binding'] = bind_result
            workflow_result['voucher_binding'] = bind_result

            if not bind_result.get('success', False) or bind_result.get('ret') != 0:
                error_msg = bind_result.get('msg', '券绑定失败')
                workflow_result['error_message'] = f"券绑定失败: {error_msg}"
                print(f"[沃美券流程] ❌ 券绑定失败: {error_msg}")
                return workflow_result

            print(f"[沃美券流程] ✅ 券绑定成功")

            # 步骤3: 整合最终结果
            print(f"[沃美券流程] 3️⃣ 第三步：整合结果...")

            # 从绑定结果中提取最终价格信息
            bind_data = bind_result.get('data', {})
            final_price = bind_data.get('order_payment_price', 0)
            voucher_use = bind_data.get('voucher_use', {})
            voucher_discounts = bind_data.get('voucher_discounts', [])

            # 从价格计算结果中提取预计价格
            price_data = price_result.get('data', {})
            calculated_price = price_data.get('pay_price', 0)
            surcharge_price = price_data.get('surcharge_price', 0)

            workflow_result['success'] = True
            workflow_result['final_result'] = {
                'order_payment_price': final_price,
                'calculated_pay_price': calculated_price,
                'surcharge_price': surcharge_price,
                'voucher_use': voucher_use,
                'voucher_discounts': voucher_discounts,
                'price_match': abs(final_price - calculated_price) < 0.01  # 价格是否匹配
            }

            print(f"[沃美券流程] ✅ 完整券使用流程成功完成")
            print(f"[沃美券流程] 💰 预计支付价格: {calculated_price}")
            print(f"[沃美券流程] 💰 实际支付价格: {final_price}")
            print(f"[沃美券流程] 💸 附加费用: {surcharge_price}")
            print(f"[沃美券流程] 🎫 券使用详情: {len(voucher_use.get('use_codes', []))}张券")

            return workflow_result

        except Exception as e:
            print(f"[沃美券流程] ❌ 完整流程异常: {e}")
            import traceback
            traceback.print_exc()
            workflow_result['error_message'] = f"流程异常: {str(e)}"
            return workflow_result
    
    def get_updated_order_info(self, cinema_id: str, token: str, order_id: str) -> Dict[str, Any]:
        """
        获取更新后的订单信息
        用于券绑定成功后同步订单详情
        
        Args:
            cinema_id: 影院ID
            token: 用户token
            order_id: 订单ID
            
        Returns:
            Dict: 订单详情
        """
        try:
            print(f"[沃美券绑定] 🔄 获取更新后的订单信息")
            
            # 构建请求头
            headers = self.headers_template.copy()
            headers['token'] = token
            
            # 构建请求URL
            url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/info/?version=tp_version&order_id={order_id}"
            
            print(f"[沃美券绑定] 📡 订单查询URL: {url}")
            
            # 发送GET请求
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            
            print(f"[沃美券绑定] 📥 订单查询状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解码Unicode字符
                decoded_data = self.decode_unicode_message(response.text)
                
                if decoded_data and decoded_data.get('ret') == 0:
                    order_data = decoded_data.get('data', {})
                    print(f"[沃美券绑定] ✅ 订单信息更新成功")
                    
                    return {
                        'success': True,
                        'data': order_data,
                        'ret': decoded_data.get('ret'),
                        'sub': decoded_data.get('sub'),
                        'msg': decoded_data.get('msg')
                    }
                else:
                    print(f"[沃美券绑定] ❌ 订单信息查询失败: {decoded_data}")
                    return {
                        'success': False,
                        'data': {},
                        'error': 'query_failed'
                    }
            else:
                return {
                    'success': False,
                    'data': {},
                    'error': 'http_error'
                }
                
        except Exception as e:
            print(f"[沃美券绑定] ❌ 订单信息查询异常: {e}")
            return {
                'success': False,
                'data': {},
                'error': 'exception'
            }


# 全局服务实例
_womei_order_voucher_service = None

def get_womei_order_voucher_service() -> WomeiOrderVoucherService:
    """获取沃美订单券绑定服务实例"""
    global _womei_order_voucher_service
    if _womei_order_voucher_service is None:
        _womei_order_voucher_service = WomeiOrderVoucherService()
    return _womei_order_voucher_service


# 便捷函数
def calculate_voucher_price(cinema_id: str, token: str, order_id: str, voucher_code: str, voucher_type: str = 'VGC_T') -> Dict[str, Any]:
    """
    计算优惠券价格的便捷函数

    Args:
        cinema_id: 影院ID
        token: 用户token
        order_id: 订单ID
        voucher_code: 券码
        voucher_type: 券类型，默认VGC_T

    Returns:
        Dict: 价格计算结果
    """
    service = get_womei_order_voucher_service()
    return service.calculate_voucher_price(cinema_id, token, order_id, voucher_code, voucher_type)


def bind_voucher_to_order(cinema_id: str, token: str, order_id: str, voucher_code: str, voucher_type: str = 'VGC_T') -> Dict[str, Any]:
    """
    绑定券到订单的便捷函数

    Args:
        cinema_id: 影院ID
        token: 用户token
        order_id: 订单ID
        voucher_code: 券码
        voucher_type: 券类型，默认VGC_T

    Returns:
        Dict: 券绑定结果
    """
    service = get_womei_order_voucher_service()
    return service.bind_voucher_to_order(cinema_id, token, order_id, voucher_code, voucher_type)


def complete_voucher_workflow(cinema_id: str, token: str, order_id: str, voucher_code: str, voucher_type: str = 'VGC_T') -> Dict[str, Any]:
    """
    完整券使用流程的便捷函数

    Args:
        cinema_id: 影院ID
        token: 用户token
        order_id: 订单ID
        voucher_code: 券码
        voucher_type: 券类型，默认VGC_T

    Returns:
        Dict: 完整流程结果
    """
    service = get_womei_order_voucher_service()
    return service.complete_voucher_workflow(cinema_id, token, order_id, voucher_code, voucher_type)
