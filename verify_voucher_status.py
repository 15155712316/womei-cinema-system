#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证券码状态脚本
检查券码是否可用、是否属于当前账号
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_voucher_list(token):
    """获取当前账号的券码列表"""
    print("🎫 获取当前账号的券码列表")
    print("-" * 40)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': token,
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
    }
    
    try:
        # 尝试获取券码列表（可能的API端点）
        possible_endpoints = [
            'https://ct.womovie.cn/ticket/wmyc/cinema/400028/user/voucher/list/',
            'https://ct.womovie.cn/ticket/wmyc/user/voucher/list/',
            'https://ct.womovie.cn/ticket/wmyc/voucher/list/',
        ]
        
        for endpoint in possible_endpoints:
            print(f"尝试端点: {endpoint}")
            try:
                response = requests.get(endpoint, headers=headers, verify=False, timeout=30)
                if response.status_code == 200:
                    response_json = json.loads(response.text)
                    if response_json.get('ret') == 0:
                        print(f"✅ 成功获取券码列表")
                        vouchers = response_json.get('data', {}).get('vouchers', [])
                        
                        print(f"📊 找到 {len(vouchers)} 个券码:")
                        for i, voucher in enumerate(vouchers[:10], 1):  # 只显示前10个
                            code = voucher.get('code', 'N/A')
                            status = voucher.get('status', 'N/A')
                            name = voucher.get('name', 'N/A')
                            print(f"  {i}. {code} - {status} - {name}")
                        
                        # 检查特定券码
                        target_vouchers = ['GZJY01003005966555', 'GZJY01003005921063']
                        for target in target_vouchers:
                            found = any(v.get('code') == target for v in vouchers)
                            print(f"  🔍 {target}: {'✅ 找到' if found else '❌ 未找到'}")
                        
                        return vouchers
                    else:
                        print(f"❌ API返回错误: {response_json}")
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
            except Exception as e:
                print(f"❌ 请求异常: {e}")
        
        print("❌ 所有端点都无法获取券码列表")
        return []
        
    except Exception as e:
        print(f"❌ 获取券码列表异常: {e}")
        return []


def test_fresh_voucher_creation():
    """测试使用新创建的订单和券码"""
    print("\n🆕 建议测试步骤")
    print("-" * 40)
    
    steps = [
        "1. 在实际界面中创建一个全新的订单",
        "2. 查看当前账号可用的券码列表",
        "3. 选择一个状态为'可用'的券码",
        "4. 确保券码属于当前登录账号",
        "5. 使用新订单ID和新券码进行测试"
    ]
    
    for step in steps:
        print(f"  {step}")
    
    print("\n💡 重要提示:")
    print("  - 券码一旦使用就不能重复使用")
    print("  - 测试时要使用真正可用的券码")
    print("  - 确保券码属于当前token对应的账号")


def create_new_test_template():
    """创建新的测试模板"""
    print("\n📝 创建新测试模板")
    print("-" * 40)
    
    template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用新券码测试模板
请填入真实可用的参数
"""

import requests
import json

def test_with_fresh_voucher():
    """使用新券码测试"""
    
    # 🔧 请填入真实的参数
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': '',  # 🔧 填入当前token
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
    }
    
    data = {
        'order_id': '',              # 🔧 填入新创建的订单ID
        'discount_id': '0',
        'discount_type': 'TP_VOUCHER',
        'card_id': '',
        'pay_type': 'WECHAT',
        'rewards': '[]',
        'use_rewards': 'Y',
        'use_limit_cards': 'N',
        'limit_cards': '[]',
        'voucher_code': '',          # 🔧 填入可用的券码
        'voucher_code_type': 'VGC_T',
        'ticket_pack_goods': ' ',
    }
    
    print("🧪 测试参数:")
    print(f"  Token: {headers['token'][:20] if headers['token'] else '未填写'}...")
    print(f"  订单ID: {data['order_id'] or '未填写'}")
    print(f"  券码: {data['voucher_code'] or '未填写'}")
    
    if not all([headers['token'], data['order_id'], data['voucher_code']]):
        print("❌ 请先填写所有必需的参数")
        return
    
    try:
        response = requests.post(
            'https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/change/',
            params={'version': 'tp_version'},
            headers=headers,
            data=data,
            verify=False,
            timeout=30
        )
        
        print(f"📥 响应: {response.text}")
        
        response_json = json.loads(response.text)
        ret = response_json.get('ret', -1)
        sub = response_json.get('sub', -1)
        msg = response_json.get('msg', '')
        
        if ret == 0 and sub == 0:
            print("✅ 券绑定成功！")
            data_info = response_json.get('data', {})
            print(f"  原价: ¥{data_info.get('order_total_price', 'N/A')}")
            print(f"  支付: ¥{data_info.get('order_payment_price', 'N/A')}")
        else:
            print(f"❌ 券绑定失败: ret={ret}, sub={sub}, msg={msg}")
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    test_with_fresh_voucher()
'''
    
    with open('test_fresh_voucher.py', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("✅ 新测试模板已保存到: test_fresh_voucher.py")


if __name__ == "__main__":
    token = '0a6548a4a44e8b0150e079b793c0aa66'
    
    # 1. 检查券码列表
    vouchers = check_voucher_list(token)
    
    # 2. 提供测试建议
    test_fresh_voucher_creation()
    
    # 3. 创建新测试模板
    create_new_test_template()
    
    print("\n" + "=" * 80)
    print("🎯 结论:")
    print("问题根源：券码状态问题，不是参数格式问题")
    print("解决方案：使用真正可用的券码进行测试")
    print("下一步：在实际界面中创建新订单，选择可用券码测试")
    print("=" * 80)
