#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试真实的沃美订单创建格式
基于curl命令重新构建API调用
"""

import json
import sys
import os
import requests

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

def test_real_womei_order_api():
    """测试真实的沃美订单API"""
    print("🧪 测试真实的沃美订单API")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    # 真实的API参数
    cinema_id = "400028"
    schedule_id = "16626083"
    
    # 真实的座位参数格式：10013:7:3:11051771#02#05|10013:7:4:11051771#02#04
    # 格式：区域ID:行:列:场次ID#价格类型#座位编号
    seatlable = f"10013:7:3:{schedule_id}#02#03|10013:7:4:{schedule_id}#02#04"
    
    url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/ticket/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
        'Content-Type': 'application/x-www-form-urlencoded',
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
        'priority': 'u=1, i'
    }
    
    data = {
        'seatlable': seatlable,
        'schedule_id': schedule_id
    }
    
    print(f"🔍 请求参数:")
    print(f"  - URL: {url}")
    print(f"  - 座位参数: {seatlable}")
    print(f"  - 场次ID: {schedule_id}")
    print(f"  - Token: {token[:20]}...")
    
    try:
        print(f"\n🚀 发送请求...")
        response = requests.post(url, data=data, headers=headers, timeout=30, verify=False)
        
        print(f"\n📥 响应结果:")
        print(f"  - 状态码: {response.status_code}")
        print(f"  - 响应头: {dict(response.headers)}")
        print(f"  - 响应内容: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"\n✅ JSON解析成功:")
                print(f"  - 结果: {result}")
                
                ret = result.get('ret', -1)
                msg = result.get('msg', '')
                data_result = result.get('data', {})
                
                if ret == 0:
                    print(f"\n🎉 订单创建成功!")
                    print(f"  - 订单数据: {data_result}")
                    return True
                else:
                    print(f"\n❌ 订单创建失败: {msg}")
                    print(f"  - 错误码: {ret}")
                    return False
                    
            except Exception as e:
                print(f"\n❌ JSON解析失败: {e}")
                return False
        else:
            print(f"\n❌ HTTP请求失败: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_updated_api_adapter():
    """测试更新后的API适配器"""
    print(f"\n🧪 测试更新后的API适配器")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    try:
        from cinema_api_adapter import create_womei_api
        
        # 创建API适配器
        api = create_womei_api(token)
        
        # 测试参数
        cinema_id = "400028"
        schedule_id = "16626083"
        
        # 使用真实格式的座位参数
        seatlable = f"10013:7:3:{schedule_id}#02#03|10013:7:4:{schedule_id}#02#04"
        
        print(f"🔍 API适配器测试:")
        print(f"  - cinema_id: {cinema_id}")
        print(f"  - schedule_id: {schedule_id}")
        print(f"  - seatlable: {seatlable}")
        
        # 调用更新后的API适配器
        result = api.create_order(cinema_id, seatlable, schedule_id)
        
        print(f"\n📥 API适配器返回:")
        print(f"  - 结果类型: {type(result)}")
        print(f"  - 结果内容: {result}")
        
        if result and isinstance(result, dict):
            ret = result.get('ret', -1)
            if ret == 0:
                data = result.get('data', {})
                print(f"\n✅ API适配器调用成功:")
                print(f"  - 返回数据: {data}")
                return True
            else:
                msg = result.get('msg', '未知错误')
                print(f"\n❌ API适配器调用失败: {msg}")
                return False
        else:
            print(f"\n❌ API适配器返回格式错误")
            return False
    
    except Exception as e:
        print(f"\n❌ API适配器测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_seat_format():
    """分析座位参数格式"""
    print(f"\n🔍 分析座位参数格式")
    print("=" * 50)
    
    print(f"真实curl中的座位参数:")
    print(f"  seatlable=10013:7:3:11051771#02#05|10013:7:4:11051771#02#04")
    
    print(f"\n格式解析:")
    print(f"  第一个座位: 10013:7:3:11051771#02#05")
    print(f"    - 区域ID: 10013")
    print(f"    - 行号: 7")
    print(f"    - 列号: 3")
    print(f"    - 场次ID: 11051771")
    print(f"    - 价格类型: 02")
    print(f"    - 座位编号: 05")
    
    print(f"\n  第二个座位: 10013:7:4:11051771#02#04")
    print(f"    - 区域ID: 10013")
    print(f"    - 行号: 7")
    print(f"    - 列号: 4")
    print(f"    - 场次ID: 11051771")
    print(f"    - 价格类型: 02")
    print(f"    - 座位编号: 04")
    
    print(f"\n关键发现:")
    print(f"  1. 多个座位用 | 分隔")
    print(f"  2. 每个座位格式: 区域ID:行:列:场次ID#价格类型#座位编号")
    print(f"  3. 座位编号似乎是列号的补零格式")
    print(f"  4. 价格类型固定为 02")
    print(f"  5. 区域ID固定为 10013")

def main():
    """主函数"""
    print("🔧 真实沃美订单创建测试")
    print("=" * 60)
    
    # 分析格式
    analyze_seat_format()
    
    # 测试真实API
    real_api_ok = test_real_womei_order_api()
    
    # 测试更新后的适配器
    adapter_ok = test_updated_api_adapter()
    
    print(f"\n🎯 测试结果总结")
    print("=" * 60)
    
    if real_api_ok:
        print(f"✅ 真实API测试: 通过")
    else:
        print(f"❌ 真实API测试: 失败")
    
    if adapter_ok:
        print(f"✅ API适配器测试: 通过")
    else:
        print(f"❌ API适配器测试: 失败")
    
    if real_api_ok or adapter_ok:
        print(f"\n✅ 沃美订单API修复成功")
        print(f"💡 现在使用正确的请求格式和参数")
    else:
        print(f"\n❌ 沃美订单API仍有问题")
        print(f"💡 可能需要进一步调试")

if __name__ == "__main__":
    main()
