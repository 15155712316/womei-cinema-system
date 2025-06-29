#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整HAR流程复现测试
严格按照HAR文件中的请求顺序和参数执行券使用流程
"""

import requests
import json
import time
import urllib3
from typing import Dict, Any

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompleteHARFlowTester:
    """完整HAR流程测试器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.cinema_id = "9934"
        self.token = "afebc43f2b18da363fd78a6a10b01b72"
        
        # 使用curl命令中的参数
        self.seat_info = "10013:5:7:33045901#04#06|10013:5:8:33045901#04#05"
        self.schedule_id = "16696816"
        self.voucher_code = "GZJY01002948416827"
        
        # 当前订单ID
        self.current_order_id = None
        
        # 标准请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'token': self.token,
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }
    
    def step_1_create_order(self) -> Dict[str, Any]:
        """步骤1: 创建订单（对应HAR第1个请求）"""
        print("🎬 步骤1: 创建订单")
        print("=" * 50)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/ticket/"
        
        data = {
            'seatlable': self.seat_info,
            'schedule_id': self.schedule_id
        }
        
        print(f"📤 请求URL: {url}")
        print(f"📤 请求参数: {data}")
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    order_id = result.get('data', {}).get('order_id')
                    if order_id:
                        self.current_order_id = order_id
                        print(f"✅ 订单创建成功: {order_id}")
                        return {'success': True, 'order_id': order_id, 'data': result}
                    else:
                        print(f"❌ 未获取到订单ID")
                        return {'success': False, 'error': '未获取到订单ID'}
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"❌ 订单创建失败: {error_msg}")
                    return {'success': False, 'error': error_msg}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def step_2_get_voucher_list(self) -> Dict[str, Any]:
        """步骤2: 获取券列表（对应HAR中的券查询请求）"""
        print("\n🎫 步骤2: 获取券列表")
        print("=" * 50)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/user/voucher/list/"
        
        print(f"📤 请求URL: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                if result.get('ret') == 0:
                    vouchers = result.get('data', {}).get('unused', [])
                    print(f"✅ 获取到 {len(vouchers)} 张可用券")
                    
                    # 查找目标券码
                    target_voucher = None
                    for voucher in vouchers:
                        if voucher.get('voucher_code') == self.voucher_code:
                            target_voucher = voucher
                            break
                    
                    if target_voucher:
                        print(f"✅ 找到目标券码: {self.voucher_code}")
                        print(f"   券名称: {target_voucher.get('voucher_name', 'N/A')}")
                        print(f"   有效期: {target_voucher.get('expire_time_string', 'N/A')}")
                        return {'success': True, 'voucher': target_voucher, 'data': result}
                    else:
                        print(f"❌ 未找到目标券码: {self.voucher_code}")
                        return {'success': False, 'error': f'未找到券码 {self.voucher_code}'}
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"❌ 获取券列表失败: {error_msg}")
                    return {'success': False, 'error': error_msg}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def step_3_calculate_voucher_price(self) -> Dict[str, Any]:
        """步骤3: 计算券价格（对应HAR第19个请求）"""
        print("\n🧮 步骤3: 计算券价格")
        print("=" * 50)
        
        if not self.current_order_id:
            return {'success': False, 'error': '没有有效的订单ID'}
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/voucher/price/"
        
        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.current_order_id
        }
        
        print(f"📤 请求URL: {url}")
        print(f"📤 请求参数: {data}")
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                print(f"🔍 响应分析:")
                print(f"   ret: {result.get('ret')}")
                print(f"   sub: {result.get('sub')}")
                print(f"   msg: {result.get('msg')}")
                
                data_section = result.get('data', {})
                if data_section:
                    print(f"   手续费: {data_section.get('surcharge_price', 'N/A')}")
                    print(f"   支付金额: {data_section.get('pay_price', 'N/A')}")
                    print(f"   手续费说明: {data_section.get('surcharge_msg', 'N/A')}")
                
                return {'success': result.get('ret') == 0, 'data': result}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}
    
    def step_4_bind_voucher_to_order(self) -> Dict[str, Any]:
        """步骤4: 绑定券到订单（对应HAR第22个请求）"""
        print("\n🔄 步骤4: 绑定券到订单")
        print("=" * 50)
        
        if not self.current_order_id:
            return {'success': False, 'error': '没有有效的订单ID'}
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/"
        
        # 使用HAR中第22个请求的完整参数
        data = {
            'order_id': self.current_order_id,
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
        
        print(f"📤 请求URL: {url}")
        print(f"📤 请求参数: {data}")
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                print(f"\n🔍 详细响应分析:")
                print(f"   ret: {result.get('ret')} ({'成功' if result.get('ret') == 0 else '失败'})")
                print(f"   sub: {result.get('sub')}")
                print(f"   msg: {result.get('msg')}")
                
                data_section = result.get('data', {})
                if data_section:
                    print(f"\n💰 价格信息:")
                    price_fields = [
                        'order_total_price', 'order_payment_price', 'order_unfee_total_price',
                        'ticket_total_price', 'ticket_payment_total_price'
                    ]
                    for field in price_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")
                    
                    print(f"\n🎫 券使用信息:")
                    voucher_fields = ['voucher_use', 'voucher_discounts', 'voucher_use_goods']
                    for field in voucher_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")
                else:
                    print(f"   data字段为空")
                
                return {'success': result.get('ret') == 0, 'data': result}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}

    def step_5_verify_order_status(self) -> Dict[str, Any]:
        """步骤5: 验证订单状态"""
        print("\n📋 步骤5: 验证订单状态")
        print("=" * 50)

        if not self.current_order_id:
            return {'success': False, 'error': '没有有效的订单ID'}

        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/info/"

        params = {
            'order_id': self.current_order_id
        }

        print(f"📤 请求URL: {url}")
        print(f"📤 请求参数: {params}")

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10, verify=False)

            print(f"📥 响应状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"📥 完整响应: {json.dumps(result, ensure_ascii=False, indent=2)}")

                if result.get('ret') == 0:
                    order_data = result.get('data', {})
                    print(f"\n📊 订单状态信息:")
                    print(f"   订单ID: {order_data.get('order_id', 'N/A')}")
                    print(f"   订单状态: {order_data.get('order_status', 'N/A')}")
                    print(f"   支付状态: {order_data.get('pay_status', 'N/A')}")
                    print(f"   订单总价: {order_data.get('order_total_price', 'N/A')}")
                    print(f"   支付金额: {order_data.get('order_payment_price', 'N/A')}")

                    return {'success': True, 'data': result}
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    print(f"❌ 获取订单信息失败: {error_msg}")
                    return {'success': False, 'error': error_msg}
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return {'success': False, 'error': str(e)}

    def run_complete_flow(self):
        """运行完整流程"""
        print("🎬 沃美券使用完整HAR流程复现测试")
        print("🎯 严格按照HAR文件记录的请求顺序执行")
        print("=" * 60)

        print(f"🔧 测试配置:")
        print(f"   影院ID: {self.cinema_id}")
        print(f"   券码: {self.voucher_code}")
        print(f"   座位信息: {self.seat_info}")
        print(f"   场次ID: {self.schedule_id}")
        print(f"   Token: {self.token[:20]}...")
        print()

        results = {}

        try:
            # 步骤1: 创建订单
            step1_result = self.step_1_create_order()
            results['step1_create_order'] = step1_result

            if not step1_result['success']:
                print(f"❌ 步骤1失败，无法继续: {step1_result['error']}")
                return results

            # 等待一下，模拟真实用户操作间隔
            time.sleep(1)

            # 步骤2: 获取券列表
            step2_result = self.step_2_get_voucher_list()
            results['step2_voucher_list'] = step2_result

            # 等待一下
            time.sleep(1)

            # 步骤3: 计算券价格
            step3_result = self.step_3_calculate_voucher_price()
            results['step3_price_calculation'] = step3_result

            # 等待一下，模拟用户查看价格的时间
            time.sleep(2)

            # 步骤4: 绑定券到订单
            step4_result = self.step_4_bind_voucher_to_order()
            results['step4_voucher_binding'] = step4_result

            # 等待一下
            time.sleep(1)

            # 步骤5: 验证订单状态
            step5_result = self.step_5_verify_order_status()
            results['step5_order_verification'] = step5_result

            # 生成最终报告
            self.generate_final_report(results)

            return results

        except Exception as e:
            print(f"❌ 流程执行失败: {e}")
            import traceback
            traceback.print_exc()
            return results

    def generate_final_report(self, results: Dict[str, Any]):
        """生成最终报告"""
        print("\n📋 完整HAR流程测试报告")
        print("=" * 60)

        # 测试概况
        step1_success = results.get('step1_create_order', {}).get('success', False)
        step2_success = results.get('step2_voucher_list', {}).get('success', False)
        step3_success = results.get('step3_price_calculation', {}).get('success', False)
        step4_success = results.get('step4_voucher_binding', {}).get('success', False)
        step5_success = results.get('step5_order_verification', {}).get('success', False)

        print(f"🎯 各步骤执行结果:")
        print(f"   步骤1 - 创建订单: {'✅ 成功' if step1_success else '❌ 失败'}")
        print(f"   步骤2 - 获取券列表: {'✅ 成功' if step2_success else '❌ 失败'}")
        print(f"   步骤3 - 计算券价格: {'✅ 成功' if step3_success else '❌ 失败'}")
        print(f"   步骤4 - 绑定券到订单: {'✅ 成功' if step4_success else '❌ 失败'}")
        print(f"   步骤5 - 验证订单状态: {'✅ 成功' if step5_success else '❌ 失败'}")

        # 关键发现
        print(f"\n🔍 关键发现:")

        if step4_success:
            step4_data = results['step4_voucher_binding']['data']['data']
            has_price_info = 'order_payment_price' in step4_data
            has_voucher_info = 'voucher_use' in step4_data

            print(f"   ✅ POST /order/change/ 接口完全可行")
            print(f"   ✅ 包含完整价格信息: {'是' if has_price_info else '否'}")
            print(f"   ✅ 包含券使用详情: {'是' if has_voucher_info else '否'}")
            print(f"   ✅ 单接口模式技术验证成功")

            if has_price_info and has_voucher_info:
                print(f"\n🎯 结论: 可以将HAR分析报告中的状态更新为:")
                print(f"   '修改订单绑定券 → POST /order/change/ (✅ 完全实现)'")
        else:
            step4_error = results.get('step4_voucher_binding', {}).get('data', {})
            print(f"   ❌ 券绑定失败")
            print(f"   错误信息: {step4_error.get('msg', 'Unknown error')}")
            print(f"   错误代码: {step4_error.get('sub', 'N/A')}")

        # 保存测试结果
        with open('complete_har_flow_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 完整测试结果已保存到: complete_har_flow_results.json")

def main():
    """主函数"""
    tester = CompleteHARFlowTester()
    tester.run_complete_flow()

if __name__ == "__main__":
    main()
