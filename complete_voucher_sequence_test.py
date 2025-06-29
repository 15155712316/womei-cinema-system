#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的沃美券绑定业务序列测试
严格按照HAR文件中的成功序列执行，显示每个步骤的完整API响应数据
"""

import requests
import json
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompleteVoucherSequenceTest:
    """完整券绑定序列测试"""
    
    def __init__(self):
        # 测试参数
        self.cinema_id = "9934"
        self.order_id = "250624183610000972"
        self.voucher_code = "GZJY01002948416827"
        self.token = "afebc43f2b18da363fd78a6a10b01b72"
        
        # 基于HAR分析的完整请求头
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
    
    def step_1_get_order_info(self):
        """步骤1: 获取订单信息"""
        print("📋 步骤1: 获取订单信息")
        print("=" * 80)
        
        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.cinema_id}/order/info/?version=tp_version&order_id={self.order_id}"
        
        print(f"🌐 API URL:")
        print(f"   {url}")
        print(f"📤 请求方法: GET")
        print(f"📤 请求头: 使用完整的HAR分析请求头")
        print()
        
        try:
            response = requests.get(url, headers=self.headers, timeout=15, verify=False)
            
            print(f"📥 HTTP状态码: {response.status_code}")
            print(f"📥 响应头:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                print(f"\n🔍 关键信息提取:")
                if result.get('ret') == 0:
                    order_data = result.get('data', {})
                    print(f"   ✅ 请求成功")
                    print(f"   📋 订单ID: {order_data.get('order_id', 'N/A')}")
                    print(f"   📊 订单状态: {order_data.get('status', 'N/A')}")
                    print(f"   📊 状态描述: {order_data.get('status_desc', 'N/A')}")
                    print(f"   💰 订单总价: {order_data.get('order_total_price', 'N/A')}")
                    print(f"   💰 支付金额: {order_data.get('order_payment_price', 'N/A')}")
                    print(f"   🎬 电影名称: {order_data.get('movie_name', 'N/A')}")
                    print(f"   🏢 影院名称: {order_data.get('cinema_name', 'N/A')}")
                    print(f"   ⏰ 放映时间: {order_data.get('show_date', 'N/A')}")
                    
                    ticket_items = order_data.get('ticket_items', {})
                    if ticket_items:
                        print(f"   🎫 票数: {ticket_items.get('ticket_num', 'N/A')}")
                        print(f"   🪑 座位信息: {ticket_items.get('seat_info', 'N/A')}")
                    
                    return True, result
                else:
                    print(f"   ❌ 请求失败: ret={result.get('ret')}, sub={result.get('sub')}, msg={result.get('msg')}")
                    return False, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_2_get_voucher_list(self):
        """步骤2: 获取券列表"""
        print(f"\n🎫 步骤2: 获取券列表")
        print("=" * 80)
        
        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.cinema_id}/user/voucher/list/"
        
        print(f"🌐 API URL:")
        print(f"   {url}")
        print(f"📤 请求方法: GET")
        print(f"📤 目标券码: {self.voucher_code}")
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
                    
                    print(f"   ✅ 请求成功")
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
                        print(f"   券名称: {target_voucher.get('voucher_name', 'N/A')}")
                        print(f"   有效期: {target_voucher.get('expire_time_string', 'N/A')}")
                        print(f"   券数量: {target_voucher.get('voucher_num', 'N/A')}")
                        print(f"   券描述: {target_voucher.get('voucher_desc', 'N/A')}")
                        return True, result
                    else:
                        print(f"   ❌ 未找到目标券码")
                        return False, result
                else:
                    print(f"   ❌ 请求失败: ret={result.get('ret')}, sub={result.get('sub')}, msg={result.get('msg')}")
                    return False, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_3_calculate_voucher_price(self):
        """步骤3: 计算券价格"""
        print(f"\n🧮 步骤3: 计算券价格")
        print("=" * 80)
        
        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.cinema_id}/order/voucher/price/"
        
        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.order_id
        }
        
        print(f"🌐 API URL:")
        print(f"   {url}")
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
                print(f"   sub: {result.get('sub')}")
                print(f"   msg: {result.get('msg')}")
                
                data_section = result.get('data', {})
                if data_section:
                    print(f"\n💰 价格计算详情:")
                    for key, value in data_section.items():
                        print(f"   {key}: {value}")
                else:
                    print(f"   📋 data字段为空")
                
                return result.get('ret') == 0, result
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None

    def step_4_voucher_binding(self):
        """步骤4: 券绑定（核心验证）"""
        print(f"\n🔄 步骤4: 券绑定（核心验证）")
        print("=" * 80)

        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{self.cinema_id}/order/change/?version=tp_version"

        data = {
            'card_id': '',
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',
            'limit_cards': '[]',
            'order_id': self.order_id,
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'ticket_pack_goods': ' ',
            'use_limit_cards': 'N',
            'use_rewards': 'Y',
            'voucher_code': self.voucher_code,
            'voucher_code_type': 'VGC_T',
        }

        print(f"🌐 API URL:")
        print(f"   {url}")
        print(f"📤 请求方法: POST")
        print(f"📤 请求参数:")
        for key, value in data.items():
            print(f"   {key}: '{value}'")
        print()

        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)

            print(f"📥 HTTP状态码: {response.status_code}")
            print(f"📥 响应头:")
            for key, value in response.headers.items():
                print(f"   {key}: {value}")

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
                        'rewards_use', 'rewards_discounts',
                        'limit_card_use', 'evgc_voucher_use', 'evgc_limit_use'
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

                    print(f"\n🎯 单接口模式能力验证:")
                    has_price_info = any(field in data_section for field in price_fields)
                    has_voucher_info = any(field in data_section for field in voucher_fields)

                    print(f"   ✅ 接口调用成功: 是")
                    print(f"   ✅ 返回完整价格信息: {'是' if has_price_info else '否'}")
                    print(f"   ✅ 返回券使用详情: {'是' if has_voucher_info else '否'}")
                    print(f"   ✅ 数据结构完整性: {'完整' if data_section else '空'}")
                    print(f"   ✅ 支持单接口模式: {'是' if (has_price_info and has_voucher_info) else '否'}")

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

    def run_complete_sequence(self):
        """运行完整的券绑定业务序列"""
        print("🎬 沃美券绑定完整业务序列测试")
        print("🎯 验证POST /order/change/接口的券绑定功能和完整数据返回能力")
        print("=" * 80)

        print(f"🔧 测试配置:")
        print(f"   订单ID: {self.order_id}")
        print(f"   券码: {self.voucher_code}")
        print(f"   影院ID: {self.cinema_id}")
        print(f"   Token: {self.token[:20]}...")
        print()

        results = {}

        # 步骤1: 获取订单信息
        step1_success, step1_data = self.step_1_get_order_info()
        results['step1'] = {'success': step1_success, 'data': step1_data}

        if not step1_success:
            print(f"\n❌ 步骤1失败，但继续执行后续步骤...")

        # 等待间隔
        time.sleep(1)

        # 步骤2: 获取券列表
        step2_success, step2_data = self.step_2_get_voucher_list()
        results['step2'] = {'success': step2_success, 'data': step2_data}

        if not step2_success:
            print(f"\n❌ 步骤2失败，但继续执行后续步骤...")

        # 等待间隔
        time.sleep(1)

        # 步骤3: 计算券价格
        step3_success, step3_data = self.step_3_calculate_voucher_price()
        results['step3'] = {'success': step3_success, 'data': step3_data}

        if not step3_success:
            print(f"\n❌ 步骤3失败，但继续执行后续步骤...")

        # 等待间隔（模拟用户查看价格的时间）
        time.sleep(2)

        # 步骤4: 券绑定（核心验证）
        step4_success, step4_data = self.step_4_voucher_binding()
        results['step4'] = {'success': step4_success, 'data': step4_data}

        # 生成最终报告
        self.generate_final_report(results)

        return results

    def generate_final_report(self, results):
        """生成最终测试报告"""
        print(f"\n📋 完整业务序列测试报告")
        print("=" * 80)

        step1_success = results.get('step1', {}).get('success', False)
        step2_success = results.get('step2', {}).get('success', False)
        step3_success = results.get('step3', {}).get('success', False)
        step4_success = results.get('step4', {}).get('success', False)

        print(f"🎯 各步骤执行结果:")
        print(f"   步骤1 - 获取订单信息: {'✅ 成功' if step1_success else '❌ 失败'}")
        print(f"   步骤2 - 获取券列表: {'✅ 成功' if step2_success else '❌ 失败'}")
        print(f"   步骤3 - 计算券价格: {'✅ 成功' if step3_success else '❌ 失败'}")
        print(f"   步骤4 - 券绑定: {'✅ 成功' if step4_success else '❌ 失败'}")

        # 分析步骤4的详细结果
        step4_data = results.get('step4', {}).get('data', {})
        if step4_data and step4_data.get('ret') == 0:
            data_section = step4_data.get('data', {})

            print(f"\n🎯 POST /order/change/ 接口能力验证:")
            print(f"   ✅ 接口调用成功: 是")
            print(f"   ✅ 返回状态: ret={step4_data.get('ret')}, sub={step4_data.get('sub')}")
            print(f"   ✅ 响应消息: {step4_data.get('msg')}")

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

                if step4_success and has_price_info and has_voucher_info:
                    print(f"\n🎉 最终结论:")
                    print(f"   ✅ POST /order/change/ 接口完全支持单接口模式")
                    print(f"   ✅ 能够返回完整的订单和券信息")
                    print(f"   ✅ 可以将HAR分析报告状态更新为'完全实现'")
                    print(f"   ✅ 验证了券绑定功能的完整性")
                else:
                    print(f"\n⚠️  部分验证成功:")
                    print(f"   ✅ 接口功能正常")
                    print(f"   ⚠️  数据返回可能受业务状态影响")
            else:
                print(f"   ❌ data字段为空")
        else:
            print(f"\n❌ 步骤4失败或返回错误")

        # 保存完整测试结果
        with open('complete_voucher_sequence_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 完整测试结果已保存到: complete_voucher_sequence_results.json")

def main():
    """主函数"""
    tester = CompleteVoucherSequenceTest()
    tester.run_complete_sequence()

if __name__ == "__main__":
    main()
