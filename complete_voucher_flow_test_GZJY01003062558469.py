#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的沃美影城下单到券绑定流程测试
使用券码 GZJY01003062558469 进行完整流程验证
"""

import requests
import json
import urllib3
import time
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompleteVoucherFlowTester:
    """完整券使用流程测试器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.token = "afebc43f2b18da363fd78a6a10b01b72"
        self.voucher_code = "GZJY01003062558469"
        
        # 测试参数（使用最新的有效参数）
        self.cinema_id = "9934"
        self.schedule_id = "16696845"  # 使用有效的场次ID
        self.seatlable = "10013:5:8:33045901#06#09|10013:5:9:33045901#06#08"  # 使用有效的座位
        
        # 当前订单ID
        self.current_order_id = None
        
        # 完整的请求头
        self.headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Client-Version': '4.0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Priority': 'u=1, i',
            'Referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'Tenant-Short': 'wmyc',
            'Token': self.token,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
            'X-Channel-Id': '40000',
            'X-Requested-With': 'wxapp',
            'Xweb_Xhr': '1',
        }
    
    def step_1_create_new_order(self):
        """步骤1: 创建新订单"""
        print("🎫 步骤1: 创建新订单")
        print("=" * 80)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/ticket/"
        
        data = {
            'seatlable': self.seatlable,
            'schedule_id': self.schedule_id
        }
        
        print(f"🌐 API URL: {url}")
        print(f"📤 请求方法: POST")
        print(f"📤 请求参数:")
        for key, value in data.items():
            print(f"   {key}: {value}")
        print(f"📤 券码测试: {self.voucher_code}")
        print()
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)
            
            print(f"📥 HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                print(f"\n🔍 订单创建结果分析:")
                print(f"   ret: {result.get('ret')} ({'成功' if result.get('ret') == 0 else '失败'})")
                print(f"   sub: {result.get('sub')} ({'完全成功' if result.get('sub') == 0 else '有错误码'})")
                print(f"   msg: {result.get('msg')}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    order_data = result.get('data', {})
                    if isinstance(order_data, dict) and 'order_id' in order_data:
                        self.current_order_id = order_data['order_id']
                        print(f"\n✅ 订单创建成功!")
                        print(f"   📋 订单ID: {self.current_order_id}")
                        print(f"   💰 订单总价: {order_data.get('order_total_price', 'N/A')}")
                        print(f"   🎬 电影信息: {order_data.get('movie_name', 'N/A')}")
                        print(f"   🏢 影院信息: {order_data.get('cinema_name', 'N/A')}")
                        return True, result
                    else:
                        print(f"\n❌ 未获取到有效的订单ID")
                        return False, result
                else:
                    print(f"\n❌ 订单创建失败")
                    return False, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_2_get_order_info(self):
        """步骤2: 获取订单信息"""
        print(f"\n📋 步骤2: 获取订单信息")
        print("=" * 80)
        
        if not self.current_order_id:
            print("❌ 没有有效的订单ID")
            return False, None
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/info/?version=tp_version&order_id={self.current_order_id}"
        
        print(f"🌐 API URL: {url}")
        print(f"📤 请求方法: GET")
        print(f"📤 订单ID: {self.current_order_id}")
        print()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                print(f"\n🔍 订单信息分析:")
                if result.get('ret') == 0:
                    order_data = result.get('data', {})
                    print(f"   ✅ 查询成功")
                    print(f"   📋 订单ID: {order_data.get('order_id', 'N/A')}")
                    print(f"   📊 订单状态: {order_data.get('status', 'N/A')}")
                    print(f"   💰 订单总价: {order_data.get('order_total_price', 'N/A')}")
                    print(f"   💰 支付金额: {order_data.get('order_payment_price', 'N/A')}")
                    print(f"   🎬 电影名称: {order_data.get('movie_name', 'N/A')}")
                    print(f"   ⏰ 放映时间: {order_data.get('show_date', 'N/A')}")
                    
                    ticket_items = order_data.get('ticket_items', {})
                    if ticket_items:
                        print(f"   🎫 票数: {ticket_items.get('ticket_num', 'N/A')}")
                        print(f"   🪑 座位: {ticket_items.get('seat_info', 'N/A')}")
                    
                    return True, result
                else:
                    print(f"   ❌ 查询失败: {result.get('msg')}")
                    return False, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_3_get_voucher_list(self):
        """步骤3: 获取券列表"""
        print(f"\n🎫 步骤3: 获取券列表")
        print("=" * 80)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/user/voucher/list/"
        
        print(f"🌐 API URL: {url}")
        print(f"📤 请求方法: GET")
        print(f"🎯 目标券码: {self.voucher_code}")
        print()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            print(f"📥 HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                print(f"\n🔍 券列表分析:")
                if result.get('ret') == 0:
                    data = result.get('data', {})
                    unused = data.get('unused', [])
                    used = data.get('used', [])
                    disabled = data.get('disabled', [])
                    
                    print(f"   ✅ 查询成功")
                    print(f"   📊 未使用券: {len(unused)} 张")
                    print(f"   📊 已使用券: {len(used)} 张")
                    print(f"   📊 已禁用券: {len(disabled)} 张")
                    
                    # 查找目标券码
                    target_voucher = None
                    voucher_status = "未找到"
                    
                    for voucher in unused:
                        if voucher.get('voucher_code') == self.voucher_code:
                            target_voucher = voucher
                            voucher_status = "未使用"
                            break
                    
                    if not target_voucher:
                        for voucher in used:
                            if voucher.get('voucher_code') == self.voucher_code:
                                target_voucher = voucher
                                voucher_status = "已使用"
                                break
                    
                    if not target_voucher:
                        for voucher in disabled:
                            if voucher.get('voucher_code') == self.voucher_code:
                                target_voucher = voucher
                                voucher_status = "已禁用"
                                break
                    
                    print(f"\n🎯 目标券码分析:")
                    print(f"   券码: {self.voucher_code}")
                    print(f"   状态: {voucher_status}")
                    
                    if target_voucher:
                        print(f"   ✅ 找到目标券码")
                        print(f"   券名称: {target_voucher.get('voucher_name', 'N/A')}")
                        print(f"   有效期: {target_voucher.get('expire_time_string', 'N/A')}")
                        print(f"   券数量: {target_voucher.get('voucher_num', 'N/A')}")
                        return True, result
                    else:
                        print(f"   ❌ 未找到目标券码")
                        return False, result
                else:
                    print(f"   ❌ 查询失败: {result.get('msg')}")
                    return False, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None

    def step_4_calculate_voucher_price(self):
        """步骤4: 计算券价格"""
        print(f"\n🧮 步骤4: 计算券价格")
        print("=" * 80)

        if not self.current_order_id:
            print("❌ 没有有效的订单ID")
            return False, None

        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/voucher/price/"

        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.current_order_id
        }

        print(f"🌐 API URL: {url}")
        print(f"📤 请求方法: POST")
        print(f"📤 请求参数:")
        for key, value in data.items():
            print(f"   {key}: {value}")
        print()

        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)

            print(f"📥 HTTP状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                print(f"\n📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)

                print(f"\n🔍 券价格计算分析:")
                print(f"   ret: {result.get('ret')} ({'成功' if result.get('ret') == 0 else '失败'})")
                print(f"   sub: {result.get('sub')} ({'完全成功' if result.get('sub') == 0 else '有错误码'})")
                print(f"   msg: {result.get('msg')}")

                data_section = result.get('data', {})
                if data_section:
                    print(f"\n💰 价格计算详情:")
                    for key, value in data_section.items():
                        print(f"   {key}: {value}")

                    print(f"\n🎯 关键价格信息:")
                    print(f"   手续费: {data_section.get('surcharge_price', 'N/A')}")
                    print(f"   支付金额: {data_section.get('pay_price', 'N/A')}")
                    print(f"   手续费说明: {data_section.get('surcharge_msg', 'N/A')}")
                else:
                    print(f"   📋 data字段为空")

                return result.get('ret') == 0, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False, None

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None

    def step_5_bind_voucher_to_order(self):
        """步骤5: 绑定券到订单（核心验证）"""
        print(f"\n🔄 步骤5: 绑定券到订单（核心验证）")
        print("=" * 80)

        if not self.current_order_id:
            print("❌ 没有有效的订单ID")
            return False, None

        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/change/?version=tp_version"

        data = {
            'card_id': '',
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'limit_cards': '[]',
            'order_id': self.current_order_id,
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'ticket_pack_goods': ' ',
            'use_limit_cards': 'N',
            'use_rewards': 'Y',
            'voucher_code': self.voucher_code,
            'voucher_code_type': 'VGC_T',
        }

        print(f"🌐 API URL: {url}")
        print(f"📤 请求方法: POST")
        print(f"📤 请求参数:")
        for key, value in data.items():
            print(f"   {key}: '{value}'")
        print()

        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)

            print(f"📥 HTTP状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                print(f"\n📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)

                print(f"\n🔍 券绑定结果分析:")
                print(f"   ret: {result.get('ret')} ({'成功' if result.get('ret') == 0 else '失败'})")
                print(f"   sub: {result.get('sub')} ({'完全成功' if result.get('sub') == 0 else '有错误码'})")
                print(f"   msg: {result.get('msg')}")

                data_section = result.get('data', {})
                if data_section:
                    print(f"\n💰 完整价格信息:")
                    price_fields = [
                        'order_id', 'order_total_price', 'order_unfee_total_price', 'order_payment_price',
                        'order_payment_limit_balance', 'order_payment_after_limit_balance',
                        'ticket_total_price', 'ticket_unfee_total_price', 'ticket_payment_total_price',
                        'ticket_bis_fee', 'ticket_total_fee', 'ticket_single_price', 'ticket_single_fee',
                        'ticket_num', 'fee_ticket_num'
                    ]

                    for field in price_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")

                    print(f"\n🎫 完整券使用信息:")
                    voucher_fields = [
                        'voucher_use', 'voucher_discounts', 'voucher_use_goods',
                        'marketing_use', 'marketing_discounts',
                        'coupon_use', 'coupon_discounts',
                        'rewards_use', 'rewards_discounts'
                    ]

                    for field in voucher_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")

                    print(f"\n📋 其他业务信息:")
                    other_fields = [
                        'goods', 'order_msg', 'ticket_package_goods',
                        'is_match_gift_coupon_activity', 'limit_sub_card_pay'
                    ]

                    for field in other_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")

                    print(f"\n🎯 单接口模式验证:")
                    has_price_info = any(field in data_section for field in price_fields)
                    has_voucher_info = any(field in data_section for field in voucher_fields)

                    print(f"   ✅ 接口调用成功: 是")
                    print(f"   ✅ 返回完整价格信息: {'是' if has_price_info else '否'}")
                    print(f"   ✅ 返回券使用详情: {'是' if has_voucher_info else '否'}")
                    print(f"   ✅ 数据结构完整性: {'完整' if data_section else '空'}")
                    print(f"   ✅ 支持单接口模式: {'是' if (has_price_info and has_voucher_info) else '否'}")

                    # 验证价格计算正确性
                    if has_price_info and has_voucher_info:
                        original_price = data_section.get('order_total_price', 0)
                        payment_price = data_section.get('order_payment_price', 0)
                        voucher_use = data_section.get('voucher_use', {})

                        print(f"\n💡 价格计算验证:")
                        print(f"   原始总价: {original_price}")
                        print(f"   实际支付: {payment_price}")
                        if isinstance(voucher_use, dict) and voucher_use.get('use_total_price'):
                            voucher_discount = voucher_use.get('use_total_price', 0)
                            print(f"   券抵扣金额: {voucher_discount}")
                            print(f"   计算验证: {original_price} - {voucher_discount} = {original_price - voucher_discount}")
                            print(f"   计算正确: {'✅ 是' if abs((original_price - voucher_discount) - payment_price) < 0.01 else '❌ 否'}")

                    return True, result
                else:
                    print(f"   ❌ data字段为空")
                    return False, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False, None

        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None

    def run_complete_flow_test(self):
        """运行完整的券使用流程测试"""
        print("🎬 沃美影城完整券使用流程测试")
        print(f"🎯 券码: {self.voucher_code}")
        print("🎯 验证从下单到券绑定的完整流程")
        print("=" * 80)

        print(f"🔧 测试配置:")
        print(f"   券码: {self.voucher_code}")
        print(f"   影院ID: {self.cinema_id}")
        print(f"   场次ID: {self.schedule_id}")
        print(f"   座位信息: {self.seatlable}")
        print(f"   Token: {self.token[:20]}...")
        print()

        results = {}

        # 步骤1: 创建新订单
        step1_success, step1_data = self.step_1_create_new_order()
        results['step1'] = {'success': step1_success, 'data': step1_data}

        if not step1_success:
            print(f"\n❌ 步骤1失败，无法继续后续测试")
            return results

        # 等待间隔
        time.sleep(1)

        # 步骤2: 获取订单信息
        step2_success, step2_data = self.step_2_get_order_info()
        results['step2'] = {'success': step2_success, 'data': step2_data}

        # 等待间隔
        time.sleep(1)

        # 步骤3: 获取券列表
        step3_success, step3_data = self.step_3_get_voucher_list()
        results['step3'] = {'success': step3_success, 'data': step3_data}

        if not step3_success:
            print(f"\n❌ 步骤3失败，券码可能不可用，但继续测试...")

        # 等待间隔
        time.sleep(1)

        # 步骤4: 计算券价格
        step4_success, step4_data = self.step_4_calculate_voucher_price()
        results['step4'] = {'success': step4_success, 'data': step4_data}

        # 等待间隔（模拟用户查看价格的时间）
        time.sleep(2)

        # 步骤5: 绑定券到订单（核心验证）
        step5_success, step5_data = self.step_5_bind_voucher_to_order()
        results['step5'] = {'success': step5_success, 'data': step5_data}

        # 生成最终报告
        self.generate_final_report(results)

        return results

    def generate_final_report(self, results):
        """生成最终测试报告"""
        print(f"\n📋 完整券使用流程测试报告")
        print("=" * 80)

        step1_success = results.get('step1', {}).get('success', False)
        step2_success = results.get('step2', {}).get('success', False)
        step3_success = results.get('step3', {}).get('success', False)
        step4_success = results.get('step4', {}).get('success', False)
        step5_success = results.get('step5', {}).get('success', False)

        print(f"🎯 各步骤执行结果:")
        print(f"   步骤1 - 创建新订单: {'✅ 成功' if step1_success else '❌ 失败'}")
        print(f"   步骤2 - 获取订单信息: {'✅ 成功' if step2_success else '❌ 失败'}")
        print(f"   步骤3 - 获取券列表: {'✅ 成功' if step3_success else '❌ 失败'}")
        print(f"   步骤4 - 计算券价格: {'✅ 成功' if step4_success else '❌ 失败'}")
        print(f"   步骤5 - 绑定券到订单: {'✅ 成功' if step5_success else '❌ 失败'}")

        # 分析核心验证结果
        if step5_success:
            step5_data = results.get('step5', {}).get('data', {})
            if step5_data and step5_data.get('ret') == 0 and step5_data.get('sub') == 0:
                data_section = step5_data.get('data', {})

                print(f"\n🎉 券绑定成功验证:")
                print(f"   ✅ 接口调用成功: 是")
                print(f"   ✅ 返回状态: ret={step5_data.get('ret')}, sub={step5_data.get('sub')}")
                print(f"   ✅ 响应消息: {step5_data.get('msg')}")

                if data_section:
                    has_price_info = any(field in data_section for field in [
                        'order_total_price', 'order_payment_price', 'ticket_total_price'
                    ])
                    has_voucher_info = any(field in data_section for field in [
                        'voucher_use', 'voucher_discounts', 'voucher_use_goods'
                    ])

                    print(f"   ✅ 包含价格信息: {'是' if has_price_info else '否'}")
                    print(f"   ✅ 包含券信息: {'是' if has_voucher_info else '否'}")
                    print(f"   ✅ 数据完整性: {'完整' if data_section else '空'}")

                    if has_price_info and has_voucher_info:
                        print(f"\n🎊 最终验证结论:")
                        print(f"   ✅ 券码 {self.voucher_code} 使用成功")
                        print(f"   ✅ POST /order/change/ 接口完全支持券绑定")
                        print(f"   ✅ 单接口模式验证成功")
                        print(f"   ✅ 这是真实的API响应数据")

                        # 显示关键价格信息
                        original_price = data_section.get('order_total_price', 0)
                        payment_price = data_section.get('order_payment_price', 0)
                        voucher_use = data_section.get('voucher_use', {})

                        print(f"\n💰 价格计算结果:")
                        print(f"   订单原价: {original_price}")
                        print(f"   实际支付: {payment_price}")
                        if isinstance(voucher_use, dict):
                            voucher_discount = voucher_use.get('use_total_price', 0)
                            print(f"   券抵扣: {voucher_discount}")
                            print(f"   节省金额: {voucher_discount}")

        # 保存完整测试结果
        with open(f'voucher_flow_test_results_{self.voucher_code}.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 完整测试结果已保存到: voucher_flow_test_results_{self.voucher_code}.json")

def main():
    """主函数"""
    tester = CompleteVoucherFlowTester()
    tester.run_complete_flow_test()

if __name__ == "__main__":
    main()
