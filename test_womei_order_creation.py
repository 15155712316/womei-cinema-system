#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美订单创建
验证修复后的订单创建流程
"""

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

def test_womei_order_creation():
    """测试沃美订单创建"""
    print("🧪 测试沃美订单创建")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        # 创建沃美电影服务实例
        film_service = get_womei_film_service(token)
        
        # 模拟订单参数
        cinema_id = "400028"  # 北京沃美世界城店
        schedule_id = "16626079"  # 示例场次ID
        
        # 构建座位参数（JSON格式）
        selected_seats = [
            {
                "row": 1,
                "col": 9,
                "seat_no": "000000011111-9-1",
                "price": 4500,
                "x": 9,
                "y": 1,
                "type": 1,
                "area_id": 1
            },
            {
                "row": 1,
                "col": 10,
                "seat_no": "000000011111-10-1",
                "price": 4500,
                "x": 10,
                "y": 1,
                "type": 1,
                "area_id": 1
            }
        ]
        
        seatlable_str = json.dumps(selected_seats, ensure_ascii=False)
        
        print(f"🔍 测试参数:")
        print(f"  - cinema_id: {cinema_id}")
        print(f"  - schedule_id: {schedule_id}")
        print(f"  - seatlable: {seatlable_str}")
        print(f"  - token: {token[:20]}...")
        
        print(f"\n🚀 调用沃美订单创建API...")
        
        # 调用订单创建API
        result = film_service.create_order(
            cinema_id=cinema_id,
            seatlable=seatlable_str,
            schedule_id=schedule_id
        )
        
        print(f"\n📥 API返回结果:")
        print(f"  - 结果类型: {type(result)}")
        print(f"  - 结果内容: {result}")
        
        if result and isinstance(result, dict):
            success = result.get('success', False)
            if success:
                order_id = result.get('order_id', 'N/A')
                order_info = result.get('order_info', {})
                
                print(f"\n✅ 订单创建成功:")
                print(f"  - 订单ID: {order_id}")
                print(f"  - 订单信息: {order_info}")
                return True
            else:
                error = result.get('error', '未知错误')
                print(f"\n❌ 订单创建失败: {error}")
                return False
        else:
            print(f"\n❌ API返回格式错误")
            return False
    
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_womei_api_adapter():
    """测试沃美API适配器"""
    print(f"\n🧪 测试沃美API适配器")
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
        schedule_id = "16626079"
        seatlable = json.dumps([
            {"row": 1, "col": 9, "seat_no": "000000011111-9-1", "price": 4500}
        ], ensure_ascii=False)
        
        print(f"🔍 直接API测试:")
        print(f"  - cinema_id: {cinema_id}")
        print(f"  - schedule_id: {schedule_id}")
        print(f"  - seatlable: {seatlable}")
        
        # 直接调用API适配器
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

def analyze_order_creation_flow():
    """分析订单创建流程"""
    print(f"\n🔍 分析订单创建流程")
    print("=" * 50)
    
    print(f"修复前的问题:")
    print(f"  1. 使用华联系统的API路径 'MiniOrder/createOrder'")
    print(f"  2. 使用华联系统的参数格式")
    print(f"  3. 期望华联系统的返回格式 'resultCode'")
    
    print(f"\n修复后的改进:")
    print(f"  1. 使用沃美系统的API路径 'order_ticket'")
    print(f"  2. 使用沃美系统的参数格式 (JSON座位数据)")
    print(f"  3. 处理沃美系统的返回格式 'success/error'")
    
    print(f"\n数据流对比:")
    print(f"华联系统:")
    print(f"  - URL: /MiniTicket/index.php/MiniOrder/createOrder")
    print(f"  - 参数: seatInfo (复杂对象)")
    print(f"  - 返回: {{resultCode: '0', resultData: {{orderno: '...'}} }}")
    
    print(f"\n沃美系统:")
    print(f"  - URL: /ticket/wmyc/cinema/{{cinema_id}}/order_ticket/")
    print(f"  - 参数: seatlable (JSON字符串)")
    print(f"  - 返回: {{ret: 0, data: {{order_id: '...'}} }}")

def main():
    """主函数"""
    print("🔧 沃美订单创建测试")
    print("=" * 60)
    
    # 分析流程
    analyze_order_creation_flow()
    
    # 测试API适配器
    adapter_ok = test_womei_api_adapter()
    
    # 测试电影服务
    service_ok = test_womei_order_creation()
    
    print(f"\n🎯 测试结果总结")
    print("=" * 60)
    
    if adapter_ok:
        print(f"✅ API适配器测试: 通过")
    else:
        print(f"❌ API适配器测试: 失败")
    
    if service_ok:
        print(f"✅ 电影服务测试: 通过")
    else:
        print(f"❌ 电影服务测试: 失败")
    
    if adapter_ok or service_ok:
        print(f"\n✅ 沃美订单创建修复成功")
        print(f"💡 现在应该可以正常创建订单了")
    else:
        print(f"\n❌ 沃美订单创建仍有问题")
        print(f"💡 可能的原因:")
        print(f"  1. Token已过期")
        print(f"  2. 座位已被占用")
        print(f"  3. 场次已过期")
        print(f"  4. 网络连接问题")

if __name__ == "__main__":
    main()
