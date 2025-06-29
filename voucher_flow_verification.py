#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券使用流程验证测试
使用HAR文件中的真实参数验证接口能力
"""

import requests
import json
import time
from typing import Dict, Any
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class VoucherFlowVerifier:
    """券使用流程验证器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.cinema_id = "9647"  # 从HAR中提取
        self.token = "afebc43f2b18da363fd78a6a10b01b72"  # 从HAR中提取
        self.order_id = "250624153810000654"  # 从HAR中提取
        self.voucher_code = "GZJY01002948425042"  # 从HAR中提取
        
        # 从HAR中提取的请求头
        self.headers = {
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'content-type': 'application/x-www-form-urlencoded',
            'token': self.token,
            'accept': '*/*'
        }
    
    def test_voucher_price_calculation(self) -> Dict[str, Any]:
        """测试券价格计算接口"""
        print("🧮 测试券价格计算接口")
        print("-" * 50)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/voucher/price/"
        
        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.order_id
        }
        
        try:
            print(f"📤 请求URL: {url}")
            print(f"📤 请求参数: {data}")
            
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    data_info = result.get('data', {})
                    print(f"✅ 券价格计算成功:")
                    print(f"   手续费: {data_info.get('surcharge_price', 'N/A')}")
                    print(f"   支付金额: {data_info.get('pay_price', 'N/A')}")
                    print(f"   手续费说明: {data_info.get('surcharge_msg', 'N/A')}")
                    return {'success': True, 'data': result}
                else:
                    print(f"❌ 券价格计算失败: {result.get('msg', 'Unknown error')}")
                    return {'success': False, 'error': result.get('msg', 'Unknown error')}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求异常: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return {'success': False, 'error': f'JSON decode error: {e}'}
    
    def test_order_change_with_voucher(self) -> Dict[str, Any]:
        """测试订单修改接口的券绑定能力"""
        print("\n🔄 测试订单修改接口的券绑定能力")
        print("-" * 50)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/"
        
        # 使用HAR中第22个请求的完整参数
        data = {
            'order_id': self.order_id,
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'card_id': '',
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'use_rewards': 'Y',
            'use_limit_cards': 'N',
            'limit_cards': '[]',
            'voucher_code': self.voucher_code,
            'voucher_code_type': 'VGC_T',
            'ticket_pack_goods': ' '
        }
        
        try:
            print(f"📤 请求URL: {url}")
            print(f"📤 请求参数: {data}")
            
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    data_info = result.get('data', {})
                    print(f"✅ 券绑定成功:")
                    print(f"   订单总价: {data_info.get('order_total_price', 'N/A')}")
                    print(f"   支付金额: {data_info.get('order_payment_price', 'N/A')}")
                    print(f"   券折扣: {data_info.get('voucher_discounts', 'N/A')}")
                    print(f"   券使用详情: {data_info.get('voucher_use', 'N/A')}")
                    return {'success': True, 'data': result}
                else:
                    print(f"❌ 券绑定失败: {result.get('msg', 'Unknown error')}")
                    return {'success': False, 'error': result.get('msg', 'Unknown error')}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求异常: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return {'success': False, 'error': f'JSON decode error: {e}'}
    
    def test_order_change_without_voucher(self) -> Dict[str, Any]:
        """测试订单修改接口不绑定券的情况"""
        print("\n🔄 测试订单修改接口不绑定券的情况")
        print("-" * 50)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/"
        
        # 使用HAR中第18个请求的参数（无券）
        data = {
            'order_id': self.order_id,
            'discount_id': '0',
            'discount_type': '',
            'card_id': '',
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'use_rewards': 'Y',
            'use_limit_cards': 'N',
            'limit_cards': '[]',
            'voucher_code': '',
            'voucher_code_type': '',
            'ticket_pack_goods': ''
        }
        
        try:
            print(f"📤 请求URL: {url}")
            print(f"📤 请求参数: {data}")
            
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    data_info = result.get('data', {})
                    print(f"✅ 订单修改成功（无券）:")
                    print(f"   订单总价: {data_info.get('order_total_price', 'N/A')}")
                    print(f"   支付金额: {data_info.get('order_payment_price', 'N/A')}")
                    print(f"   券折扣: {data_info.get('voucher_discounts', 'N/A')}")
                    return {'success': True, 'data': result}
                else:
                    print(f"❌ 订单修改失败: {result.get('msg', 'Unknown error')}")
                    return {'success': False, 'error': result.get('msg', 'Unknown error')}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求异常: {e}")
            return {'success': False, 'error': str(e)}
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return {'success': False, 'error': f'JSON decode error: {e}'}
    
    def test_invalid_voucher_scenarios(self) -> Dict[str, Any]:
        """测试无效券码场景"""
        print("\n❌ 测试无效券码场景")
        print("-" * 50)
        
        invalid_scenarios = [
            {'code': 'INVALID123456789', 'desc': '无效券码'},
            {'code': 'EXPIRED123456789', 'desc': '过期券码'},
            {'code': '', 'desc': '空券码'}
        ]
        
        results = []
        
        for scenario in invalid_scenarios:
            print(f"\n🧪 测试场景: {scenario['desc']}")
            
            url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/"
            
            data = {
                'order_id': self.order_id,
                'discount_id': '0',
                'discount_type': 'TP_VOUCHER',
                'card_id': '',
                'pay_type': 'WECHAT',
                'rewards': '[]',
                'use_rewards': 'Y',
                'use_limit_cards': 'N',
                'limit_cards': '[]',
                'voucher_code': scenario['code'],
                'voucher_code_type': 'VGC_T',
                'ticket_pack_goods': ' '
            }
            
            try:
                response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"📥 响应: ret={result.get('ret')}, msg={result.get('msg')}")
                    
                    results.append({
                        'scenario': scenario['desc'],
                        'code': scenario['code'],
                        'success': result.get('ret') == 0,
                        'message': result.get('msg', ''),
                        'response': result
                    })
                else:
                    print(f"❌ HTTP请求失败: {response.status_code}")
                    results.append({
                        'scenario': scenario['desc'],
                        'code': scenario['code'],
                        'success': False,
                        'message': f'HTTP {response.status_code}',
                        'response': None
                    })
                    
            except Exception as e:
                print(f"❌ 请求异常: {e}")
                results.append({
                    'scenario': scenario['desc'],
                    'code': scenario['code'],
                    'success': False,
                    'message': str(e),
                    'response': None
                })
        
        return {'results': results}
    
    def compare_two_approaches(self):
        """对比两种方法的结果"""
        print("\n🔍 对比两种券使用方法")
        print("=" * 60)
        
        # 方法1: 先计算价格，再绑定券
        print("📋 方法1: 双接口模式（先计算价格，再绑定券）")
        price_result = self.test_voucher_price_calculation()
        
        if price_result['success']:
            print("⏱️  等待2秒后进行券绑定...")
            time.sleep(2)
            bind_result = self.test_order_change_with_voucher()
        else:
            bind_result = {'success': False, 'error': '价格计算失败，跳过绑定'}
        
        # 方法2: 直接绑定券（单接口模式）
        print("\n📋 方法2: 单接口模式（直接绑定券）")
        direct_result = self.test_order_change_with_voucher()
        
        # 对比结果
        print("\n📊 结果对比:")
        print("-" * 40)
        print(f"双接口模式:")
        print(f"  价格计算: {'✅ 成功' if price_result['success'] else '❌ 失败'}")
        print(f"  券绑定: {'✅ 成功' if bind_result['success'] else '❌ 失败'}")
        
        print(f"单接口模式:")
        print(f"  直接绑定: {'✅ 成功' if direct_result['success'] else '❌ 失败'}")
        
        return {
            'dual_mode': {'price': price_result, 'bind': bind_result},
            'single_mode': direct_result
        }

def main():
    """主函数"""
    print("🎬 沃美券使用流程验证测试")
    print("🎯 使用HAR文件中的真实参数进行验证")
    print("=" * 60)
    
    verifier = VoucherFlowVerifier()
    
    print(f"🔧 测试配置:")
    print(f"   影院ID: {verifier.cinema_id}")
    print(f"   订单ID: {verifier.order_id}")
    print(f"   券码: {verifier.voucher_code}")
    print(f"   Token: {verifier.token[:20]}...")
    
    # 执行验证测试
    try:
        # 对比两种方法
        comparison_result = verifier.compare_two_approaches()
        
        # 测试无效券码场景
        invalid_result = verifier.test_invalid_voucher_scenarios()
        
        # 测试无券情况
        no_voucher_result = verifier.test_order_change_without_voucher()
        
        print("\n🎯 最终结论:")
        print("=" * 60)
        
        # 分析结果并给出建议
        dual_success = (comparison_result['dual_mode']['price']['success'] and 
                       comparison_result['dual_mode']['bind']['success'])
        single_success = comparison_result['single_mode']['success']
        
        if single_success and dual_success:
            print("✅ 两种模式都可行")
            print("💡 建议: 根据用户体验需求选择")
            print("   - 需要预览价格: 使用双接口模式")
            print("   - 追求响应速度: 使用单接口模式")
        elif single_success:
            print("✅ 单接口模式可行，推荐使用")
            print("💡 优势: 减少网络请求，提高响应速度")
        elif dual_success:
            print("✅ 双接口模式可行")
            print("💡 优势: 可预先显示价格，用户体验更好")
        else:
            print("❌ 两种模式都存在问题，需要进一步调试")
        
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
