#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
对比真实小程序请求和我们的实现
找出参数差异
"""

import requests
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def load_account():
    """加载账号数据"""
    try:
        with open('data/accounts.json', 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        
        if accounts and len(accounts) > 0:
            return accounts[0]
    except:
        pass
    
    return {}

def test_real_miniprogram_request():
    """测试真实小程序请求"""
    print("🧪 测试真实小程序请求")
    print("=" * 50)
    
    # 真实小程序的请求参数
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': '1bb7e07bb7c832f17322b61c790aeed2',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
    }

    data = {
        'seatlable': '1:2:5:11051771#09#06|1:2:4:11051771#09#05',
        'schedule_id': '16626081',
    }
    
    print(f"🔍 真实小程序请求:")
    print(f"  URL: https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/ticket/")
    print(f"  Headers: {len(headers)} 个")
    print(f"  Data: {data}")
    
    try:
        response = requests.post(
            'https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/ticket/', 
            headers=headers, 
            data=data,
            timeout=30,
            verify=False
        )
        
        print(f"\n📥 真实小程序响应:")
        print(f"  状态码: {response.status_code}")
        print(f"  响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"  解析结果: {result}")
                return result
            except:
                print(f"  JSON解析失败")
                return None
        else:
            print(f"  HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 真实小程序请求异常: {e}")
        return None

def test_our_implementation():
    """测试我们的实现"""
    print(f"\n🧪 测试我们的实现")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    try:
        from cinema_api_adapter import create_womei_api
        
        # 创建API适配器
        api = create_womei_api(token)
        
        # 测试参数
        cinema_id = "400028"
        schedule_id = "16626081"
        seatlable = "1:2:5:11051771#09#06|1:2:4:11051771#09#05"
        
        print(f"🔍 我们的实现:")
        print(f"  cinema_id: {cinema_id}")
        print(f"  schedule_id: {schedule_id}")
        print(f"  seatlable: {seatlable}")
        print(f"  token: {token[:20]}...")
        
        # 调用我们的API
        result = api.create_order(cinema_id, seatlable, schedule_id)
        
        print(f"\n📥 我们的实现响应:")
        print(f"  结果: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 我们的实现异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_requests():
    """对比请求差异"""
    print(f"\n🔍 对比请求差异")
    print("=" * 50)
    
    account = load_account()
    our_token = account.get('token', '')
    real_token = '1bb7e07bb7c832f17322b61c790aeed2'
    
    print(f"Token对比:")
    print(f"  真实小程序: {real_token}")
    print(f"  我们的实现: {our_token}")
    print(f"  是否相同: {'✅' if our_token == real_token else '❌'}")
    
    # 对比座位参数
    real_seatlable = '1:2:5:11051771#09#06|1:2:4:11051771#09#05'
    our_seatlable = '1:2:4:11051771#09#05|1:2:5:11051771#09#06'  # 我们测试中生成的
    
    print(f"\n座位参数对比:")
    print(f"  真实小程序: {real_seatlable}")
    print(f"  我们的实现: {our_seatlable}")
    print(f"  是否相同: {'✅' if our_seatlable == real_seatlable else '❌'}")
    
    if our_seatlable != real_seatlable:
        print(f"  差异分析:")
        real_parts = real_seatlable.split('|')
        our_parts = our_seatlable.split('|')
        
        print(f"    真实: {real_parts}")
        print(f"    我们: {our_parts}")
        
        # 检查是否只是顺序不同
        if set(real_parts) == set(our_parts):
            print(f"    💡 只是座位顺序不同，内容相同")
        else:
            print(f"    ❌ 座位内容有差异")
    
    # 对比其他参数
    print(f"\n其他参数对比:")
    print(f"  schedule_id: 16626081 (相同)")
    print(f"  cinema_id: 400028 (相同)")

def test_with_real_token():
    """使用真实token测试"""
    print(f"\n🧪 使用真实token测试")
    print("=" * 50)
    
    # 使用真实小程序的token
    real_token = '1bb7e07bb7c832f17322b61c790aeed2'
    
    try:
        from cinema_api_adapter import create_womei_api
        
        # 使用真实token创建API适配器
        api = create_womei_api(real_token)
        
        # 使用真实的座位参数（包括顺序）
        cinema_id = "400028"
        schedule_id = "16626081"
        seatlable = "1:2:5:11051771#09#06|1:2:4:11051771#09#05"  # 真实顺序
        
        print(f"🔍 使用真实参数:")
        print(f"  token: {real_token}")
        print(f"  seatlable: {seatlable}")
        
        # 调用API
        result = api.create_order(cinema_id, seatlable, schedule_id)
        
        print(f"\n📥 使用真实token的响应:")
        print(f"  结果: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 真实token测试异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("🔧 真实小程序 vs 我们的实现对比测试")
    print("=" * 60)
    
    # 1. 测试真实小程序请求
    real_result = test_real_miniprogram_request()
    
    # 2. 测试我们的实现
    our_result = test_our_implementation()
    
    # 3. 对比请求差异
    compare_requests()
    
    # 4. 使用真实token测试
    real_token_result = test_with_real_token()
    
    print(f"\n🎯 对比测试总结")
    print("=" * 60)
    
    if real_result:
        print(f"✅ 真实小程序请求: 成功")
        real_ret = real_result.get('ret', -1)
        real_msg = real_result.get('msg', '')
        print(f"  - ret: {real_ret}, msg: {real_msg}")
    else:
        print(f"❌ 真实小程序请求: 失败")
    
    if our_result:
        print(f"✅ 我们的实现: 成功")
        our_ret = our_result.get('ret', -1)
        our_msg = our_result.get('msg', '')
        print(f"  - ret: {our_ret}, msg: {our_msg}")
    else:
        print(f"❌ 我们的实现: 失败")
    
    if real_token_result:
        print(f"✅ 真实token测试: 成功")
        token_ret = real_token_result.get('ret', -1)
        token_msg = real_token_result.get('msg', '')
        print(f"  - ret: {token_ret}, msg: {token_msg}")
    else:
        print(f"❌ 真实token测试: 失败")
    
    print(f"\n💡 可能的差异原因:")
    print(f"  1. Token不同或已过期")
    print(f"  2. 座位参数顺序不同")
    print(f"  3. 请求头细微差异")
    print(f"  4. 座位已被其他用户占用")
    print(f"  5. 时间窗口问题（座位锁定时间）")

if __name__ == "__main__":
    main()
