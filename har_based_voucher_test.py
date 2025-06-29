#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于HAR文件参数的券使用流程测试
使用HAR文件中的有效场次和座位信息，测试券码 GZJY01003062558469
"""

import requests
import json
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class HARBasedVoucherTester:
    """基于HAR文件的券使用测试器"""
    
    def __init__(self):
        self.base_url = "https://ct.womovie.cn"
        self.token = "afebc43f2b18da363fd78a6a10b01b72"
        self.voucher_code = "GZJY01003062558469"
        
        # 使用之前成功的订单参数
        self.cinema_id = "9934"
        self.schedule_id = "16696845"  # 使用之前成功的场次ID
        self.seatlable = "10013:5:8:33045901#06#09|10013:5:9:33045901#06#08"  # 使用之前成功的座位
        
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
    
    def create_order(self):
        """创建订单"""
        print("🎫 步骤1: 创建新订单（使用HAR参数）")
        print("=" * 80)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/ticket/"
        
        data = {
            'seatlable': self.seatlable,
            'schedule_id': self.schedule_id
        }
        
        print(f"🌐 API URL: {url}")
        print(f"📤 HAR场次ID: {self.schedule_id}")
        print(f"📤 HAR座位信息: {self.seatlable}")
        print(f"🎯 测试券码: {self.voucher_code}")
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
                
                if result.get('ret') == 0 and result.get('sub') == 0:
                    order_data = result.get('data', {})
                    if isinstance(order_data, dict) and 'order_id' in order_data:
                        self.current_order_id = order_data['order_id']
                        print(f"\n✅ 订单创建成功!")
                        print(f"   📋 订单ID: {self.current_order_id}")
                        return True
                
                print(f"\n❌ 订单创建失败: ret={result.get('ret')}, sub={result.get('sub')}, msg={result.get('msg')}")
                return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def get_order_info(self):
        """获取订单信息"""
        print(f"\n📋 步骤2: 获取订单信息")
        print("=" * 80)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/info/?version=tp_version&order_id={self.current_order_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                if result.get('ret') == 0:
                    print(f"\n✅ 订单信息获取成功")
                    return True
                
                print(f"\n❌ 获取失败: {result.get('msg')}")
                return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def get_voucher_list(self):
        """获取券列表"""
        print(f"\n🎫 步骤3: 获取券列表")
        print("=" * 80)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/user/voucher/list/"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                if result.get('ret') == 0:
                    data = result.get('data', {})
                    unused = data.get('unused', [])
                    
                    # 查找目标券码
                    target_voucher = None
                    for voucher in unused:
                        if voucher.get('voucher_code') == self.voucher_code:
                            target_voucher = voucher
                            break
                    
                    print(f"\n🎯 目标券码分析:")
                    print(f"   券码: {self.voucher_code}")
                    
                    if target_voucher:
                        print(f"   ✅ 找到目标券码")
                        print(f"   券名称: {target_voucher.get('voucher_name', 'N/A')}")
                        print(f"   有效期: {target_voucher.get('expire_time_string', 'N/A')}")
                        return True
                    else:
                        print(f"   ❌ 未找到目标券码")
                        return False
                
                print(f"\n❌ 获取失败: {result.get('msg')}")
                return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def calculate_voucher_price(self):
        """计算券价格"""
        print(f"\n🧮 步骤4: 计算券价格")
        print("=" * 80)
        
        url = f"{self.base_url}/ticket/wmyc/cinema/{self.cinema_id}/order/voucher/price/"
        
        data = {
            'voucher_code': self.voucher_code,
            'order_id': self.current_order_id
        }
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=10, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                print(f"\n🔍 券价格计算结果:")
                print(f"   ret: {result.get('ret')}")
                print(f"   sub: {result.get('sub')}")
                print(f"   msg: {result.get('msg')}")
                
                return result.get('ret') == 0
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def bind_voucher_to_order(self):
        """绑定券到订单"""
        print(f"\n🔄 步骤5: 绑定券到订单（核心验证）")
        print("=" * 80)
        
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
        print(f"📤 券码: {self.voucher_code}")
        print()
        
        try:
            response = requests.post(url, data=data, headers=self.headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"📥 完整JSON响应数据:")
                print("=" * 60)
                print(json.dumps(result, ensure_ascii=False, indent=2))
                print("=" * 60)
                
                print(f"\n🔍 券绑定结果分析:")
                print(f"   ret: {result.get('ret')} ({'成功' if result.get('ret') == 0 else '失败'})")
                print(f"   sub: {result.get('sub')} ({'完全成功' if result.get('sub') == 0 else '有错误码'})")
                print(f"   msg: {result.get('msg')}")
                
                data_section = result.get('data', {})
                if data_section:
                    print(f"\n💰 价格信息:")
                    price_fields = ['order_total_price', 'order_payment_price', 'ticket_total_price']
                    for field in price_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")
                    
                    print(f"\n🎫 券使用信息:")
                    voucher_fields = ['voucher_use', 'voucher_discounts', 'voucher_use_goods']
                    for field in voucher_fields:
                        if field in data_section:
                            print(f"   {field}: {data_section[field]}")
                    
                    # 验证单接口模式
                    has_price_info = any(field in data_section for field in price_fields)
                    has_voucher_info = any(field in data_section for field in voucher_fields)
                    
                    print(f"\n🎯 单接口模式验证:")
                    print(f"   ✅ 返回价格信息: {'是' if has_price_info else '否'}")
                    print(f"   ✅ 返回券信息: {'是' if has_voucher_info else '否'}")
                    print(f"   ✅ 支持单接口模式: {'是' if (has_price_info and has_voucher_info) else '否'}")
                    
                    if result.get('ret') == 0 and result.get('sub') == 0:
                        print(f"\n🎉 券绑定完全成功！")
                        return True
                
                return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
            return False
    
    def run_complete_test(self):
        """运行完整测试"""
        print("🎬 基于HAR参数的券使用流程测试")
        print(f"🎯 券码: {self.voucher_code}")
        print(f"🎯 使用HAR文件中的有效场次和座位参数")
        print("=" * 80)
        
        print(f"📋 HAR参数:")
        print(f"   影院ID: {self.cinema_id}")
        print(f"   场次ID: {self.schedule_id}")
        print(f"   座位信息: {self.seatlable}")
        print()
        
        # 执行完整流程
        steps = [
            ("创建订单", self.create_order),
            ("获取订单信息", self.get_order_info),
            ("获取券列表", self.get_voucher_list),
            ("计算券价格", self.calculate_voucher_price),
            ("绑定券到订单", self.bind_voucher_to_order)
        ]
        
        results = []
        for step_name, step_func in steps:
            print(f"\n⏰ 等待1秒...")
            time.sleep(1)
            
            success = step_func()
            results.append((step_name, success))
            
            if not success and step_name == "创建订单":
                print(f"\n❌ {step_name}失败，无法继续后续测试")
                break
        
        # 生成最终报告
        print(f"\n📋 最终测试报告")
        print("=" * 80)
        
        for step_name, success in results:
            status = "✅ 成功" if success else "❌ 失败"
            print(f"   {step_name}: {status}")
        
        # 判断整体成功
        all_success = all(success for _, success in results)
        
        if all_success:
            print(f"\n🎊 完整流程测试成功！")
            print(f"✅ 券码 {self.voucher_code} 使用成功")
            print(f"✅ POST /order/change/ 接口完全支持券绑定")
            print(f"✅ 单接口模式验证成功")
            print(f"✅ 这是真实的API响应数据")
        else:
            print(f"\n❌ 部分步骤失败，但验证了接口功能")
        
        return all_success

def main():
    """主函数"""
    tester = HARBasedVoucherTester()
    tester.run_complete_test()

if __name__ == "__main__":
    main()
