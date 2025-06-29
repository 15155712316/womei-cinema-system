#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整HAR工作流程分析和实现
基于HAR文件中的成功案例，实现完整的多步骤券绑定流程
"""

import sys
import os
import json
import requests
import urllib3
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CompleteVoucherWorkflow:
    """完整的券绑定工作流程"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
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
    
    def step_1_get_order_info(self, cinema_id, token, order_id):
        """步骤1: 获取订单信息"""
        print("📋 步骤1: 获取订单信息")
        print("-" * 60)
        
        headers = self.headers_template.copy()
        headers['token'] = token
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/info/?version=tp_version&order_id={order_id}"
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            print(f"📡 URL: {url}")
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 响应: ret={result.get('ret')}, sub={result.get('sub')}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    order_data = result.get('data', {})
                    print(f"✅ 订单信息获取成功")
                    print(f"   订单总价: {order_data.get('order_total_price', 'N/A')}")
                    print(f"   支付金额: {order_data.get('order_payment_price', 'N/A')}")
                    return True, order_data
                else:
                    print(f"❌ 订单信息获取失败: {result.get('msg')}")
                    return False, None
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_2_get_voucher_list(self, cinema_id, token):
        """步骤2: 获取用户券列表"""
        print(f"\n🎫 步骤2: 获取用户券列表")
        print("-" * 60)
        
        headers = self.headers_template.copy()
        headers['token'] = token
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/user/voucher/list/"
        
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=15)
            print(f"📡 URL: {url}")
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 响应: ret={result.get('ret')}, sub={result.get('sub')}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    data = result.get('data', {})
                    unused_vouchers = data.get('unused', [])
                    print(f"✅ 券列表获取成功，可用券数量: {len(unused_vouchers)}")
                    return True, unused_vouchers
                else:
                    print(f"❌ 券列表获取失败: {result.get('msg')}")
                    return False, []
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False, []
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, []
    
    def step_3_voucher_price_calculation(self, cinema_id, token, order_id, voucher_code):
        """步骤3: 券价格计算"""
        print(f"\n💰 步骤3: 券价格计算")
        print("-" * 60)
        
        headers = self.headers_template.copy()
        headers['token'] = token
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/voucher/price/"
        
        data = {
            'order_id': order_id,
            'voucher_code': voucher_code,
            'voucher_type': 'VGC_T'
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=15)
            print(f"📡 URL: {url}")
            print(f"📤 参数: {data}")
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 响应: ret={result.get('ret')}, sub={result.get('sub')}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    price_data = result.get('data', {})
                    print(f"✅ 券价格计算成功")
                    print(f"   计算结果: {json.dumps(price_data, ensure_ascii=False)}")
                    return True, price_data
                else:
                    print(f"❌ 券价格计算失败: {result.get('msg')}")
                    return False, None
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_4_order_change_without_voucher(self, cinema_id, token, order_id):
        """步骤4: 无券订单修改（基于HAR文件中的步骤）"""
        print(f"\n🔄 步骤4: 无券订单修改")
        print("-" * 60)
        
        headers = self.headers_template.copy()
        headers['token'] = token
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"
        
        # 基于HAR文件的无券修改参数
        data = {
            'card_id': '',
            'discount_id': '0',
            'discount_type': '',  # 空的discount_type
            'limit_cards': '[]',
            'order_id': order_id,
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'ticket_pack_goods': ' ',
            'use_limit_cards': 'N',
            'use_rewards': 'Y',
            'voucher_code': '',  # 空的voucher_code
            'voucher_code_type': '',  # 空的voucher_code_type
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            print(f"📡 URL: {url}")
            print(f"📤 参数: {json.dumps(data, ensure_ascii=False)}")
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 响应: ret={result.get('ret')}, sub={result.get('sub')}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    print(f"✅ 无券订单修改成功")
                    return True, result.get('data', {})
                else:
                    print(f"❌ 无券订单修改失败: {result.get('msg')}")
                    return False, None
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def step_5_voucher_binding(self, cinema_id, token, order_id, voucher_code):
        """步骤5: 券绑定（基于HAR文件的成功参数）"""
        print(f"\n🎫 步骤5: 券绑定")
        print("-" * 60)
        
        headers = self.headers_template.copy()
        headers['token'] = token
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{cinema_id}/order/change/?version=tp_version"
        
        # 基于HAR文件成功案例的参数
        data = {
            'card_id': '',
            'discount_id': '0',
            'discount_type': 'TP_VOUCHER',  # 使用HAR文件中的原始值
            'limit_cards': '[]',
            'order_id': order_id,
            'pay_type': 'WECHAT',
            'rewards': '[]',
            'ticket_pack_goods': ' ',
            'use_limit_cards': 'N',
            'use_rewards': 'Y',
            'voucher_code': voucher_code,
            'voucher_code_type': 'VGC_T',
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=30)
            print(f"📡 URL: {url}")
            print(f"📤 参数: {json.dumps(data, ensure_ascii=False)}")
            print(f"📥 状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"📊 响应: ret={result.get('ret')}, sub={result.get('sub')}")
                print(f"💬 消息: {result.get('msg')}")
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    data_section = result.get('data', {})
                    
                    # 详细分析响应数据
                    order_total = data_section.get('order_total_price', 0)
                    order_payment = data_section.get('order_payment_price', 0)
                    voucher_use = data_section.get('voucher_use', {})
                    voucher_discounts = data_section.get('voucher_discounts', [])
                    
                    print(f"✅ 券绑定API调用成功")
                    print(f"💰 价格信息:")
                    print(f"   订单总价: {order_total}")
                    print(f"   支付金额: {order_payment}")
                    print(f"🎫 券使用信息:")
                    print(f"   voucher_use: {json.dumps(voucher_use, ensure_ascii=False)}")
                    print(f"   voucher_discounts: {json.dumps(voucher_discounts, ensure_ascii=False)}")
                    
                    # 检查是否有实际的抵扣效果
                    has_discount = order_payment < order_total
                    has_voucher_data = bool(voucher_use) or bool(voucher_discounts)
                    
                    if has_discount and has_voucher_data:
                        savings = order_total - order_payment
                        print(f"🎉 券绑定完全成功！节省金额: {savings}元")
                        return True, data_section
                    elif has_discount:
                        savings = order_total - order_payment
                        print(f"⚠️ 有价格抵扣但券信息不完整，节省金额: {savings}元")
                        return True, data_section
                    else:
                        print(f"❌ 券绑定成功但无抵扣效果")
                        return False, data_section
                else:
                    print(f"❌ 券绑定失败: {result.get('msg')}")
                    return False, None
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                return False, None
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False, None
    
    def run_complete_workflow(self, cinema_id, token, order_id, voucher_code):
        """运行完整的券绑定工作流程"""
        print("🎬 完整HAR工作流程执行")
        print("🎯 基于HAR文件成功案例的多步骤券绑定流程")
        print("=" * 80)
        
        print(f"📋 执行参数:")
        print(f"   影院ID: {cinema_id}")
        print(f"   Token: {token[:20]}...")
        print(f"   订单ID: {order_id}")
        print(f"   券码: {voucher_code}")
        
        # 执行完整的工作流程
        workflow_results = {}
        
        # 步骤1: 获取订单信息
        success, order_data = self.step_1_get_order_info(cinema_id, token, order_id)
        workflow_results['step_1'] = {'success': success, 'data': order_data}
        if not success:
            print(f"\n❌ 工作流程在步骤1失败")
            return False, workflow_results
        
        # 步骤2: 获取券列表
        success, voucher_list = self.step_2_get_voucher_list(cinema_id, token)
        workflow_results['step_2'] = {'success': success, 'data': voucher_list}
        if not success:
            print(f"\n❌ 工作流程在步骤2失败")
            return False, workflow_results
        
        # 验证券码是否在列表中
        voucher_codes = [v.get('voucher_code') for v in voucher_list]
        if voucher_code not in voucher_codes:
            print(f"\n❌ 券码 {voucher_code} 不在可用券列表中")
            return False, workflow_results
        
        # 步骤3: 券价格计算
        success, price_data = self.step_3_voucher_price_calculation(cinema_id, token, order_id, voucher_code)
        workflow_results['step_3'] = {'success': success, 'data': price_data}
        if not success:
            print(f"\n❌ 工作流程在步骤3失败")
            return False, workflow_results
        
        # 步骤4: 无券订单修改（可选，基于HAR文件）
        success, change_data = self.step_4_order_change_without_voucher(cinema_id, token, order_id)
        workflow_results['step_4'] = {'success': success, 'data': change_data}
        # 这一步失败不影响后续流程
        
        # 短暂延迟，模拟HAR文件中的时序
        time.sleep(0.5)
        
        # 步骤5: 券绑定
        success, binding_data = self.step_5_voucher_binding(cinema_id, token, order_id, voucher_code)
        workflow_results['step_5'] = {'success': success, 'data': binding_data}
        
        # 生成最终报告
        self.generate_workflow_report(workflow_results, success)
        
        return success, workflow_results
    
    def generate_workflow_report(self, results, final_success):
        """生成工作流程报告"""
        print(f"\n📋 完整工作流程执行报告")
        print("=" * 80)
        
        step_names = {
            'step_1': '订单信息获取',
            'step_2': '券列表获取',
            'step_3': '券价格计算',
            'step_4': '无券订单修改',
            'step_5': '券绑定执行'
        }
        
        print(f"📊 各步骤执行结果:")
        for step_key, step_name in step_names.items():
            if step_key in results:
                status = "✅ 成功" if results[step_key]['success'] else "❌ 失败"
                print(f"   {step_name}: {status}")
            else:
                print(f"   {step_name}: ⏭️ 跳过")
        
        print(f"\n🎯 最终结果:")
        if final_success:
            print(f"🎉 完整工作流程执行成功！")
            print(f"✅ 券绑定功能正常工作")
            print(f"✅ 券抵扣效果已生效")
        else:
            print(f"❌ 工作流程执行失败")
            print(f"📋 需要进一步调试和优化")
        
        return results

def test_complete_har_workflow():
    """测试完整的HAR工作流程"""
    print("🎬 测试完整的HAR工作流程")
    print("=" * 80)
    
    # 测试参数
    cinema_id = "400303"
    token = "ae6dbb683e74a71fa5e2c8cca3b5fc72"
    order_id = "250625184410001025"
    voucher_code = "GZJY01003062558469"
    
    # 创建工作流程实例
    workflow = CompleteVoucherWorkflow()
    
    # 执行完整工作流程
    success, results = workflow.run_complete_workflow(cinema_id, token, order_id, voucher_code)
    
    return success, results

def main():
    """主函数"""
    success, results = test_complete_har_workflow()
    
    print(f"\n📋 HAR工作流程测试总结")
    print("=" * 80)
    
    if success:
        print(f"🎉 HAR工作流程测试成功！")
        print(f"✅ 找到了正确的券绑定方法")
        print(f"✅ 可以更新现有的券绑定服务")
    else:
        print(f"🔍 HAR工作流程仍需优化")
        print(f"📋 建议继续分析HAR文件中的细节")
    
    return success, results

if __name__ == "__main__":
    main()
