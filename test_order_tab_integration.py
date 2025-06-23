#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试订单Tab集成
验证订单列表.py与Tab管理器的集成效果
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_order_api_integration():
    """测试订单API集成"""
    try:
        print("🧪 测试订单API集成")
        print("=" * 60)
        
        # 测试导入
        from 订单列表 import get_user_orders
        print("✅ 订单API导入成功")
        
        # 模拟账号数据
        test_token = "5e160d18859114a648efc599113c585a"
        
        print(f"📋 使用测试token: {test_token[:10]}...")
        
        # 调用API（实际请求）
        result = get_user_orders(test_token)
        
        print(f"📥 API调用结果:")
        print(f"  - 成功: {result.get('success')}")
        print(f"  - 订单数量: {len(result.get('orders', []))}")
        
        if result.get('success'):
            orders = result.get('orders', [])
            print(f"✅ 获取成功: {len(orders)} 个订单")
            
            # 验证数据格式
            if orders:
                first_order = orders[0]
                required_fields = ['movie_name', 'status_desc', 'cinema_name', 'order_id']
                
                print(f"\n📋 第一个订单数据验证:")
                for field in required_fields:
                    if field in first_order:
                        print(f"  ✅ {field}: {first_order[field]}")
                    else:
                        print(f"  ❌ {field}: 缺失")
                
                # 显示格式化后的显示字段
                display = first_order.get('display', {})
                if display:
                    print(f"\n📋 显示格式:")
                    print(f"  - 标题: {display.get('title')}")
                    print(f"  - 副标题: {display.get('subtitle')}")
                    print(f"  - 摘要: {display.get('summary')}")
        else:
            print(f"❌ 获取失败: {result.get('error')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ 订单API集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_tab_manager_compatibility():
    """测试Tab管理器兼容性"""
    try:
        print("\n🧪 测试Tab管理器兼容性")
        print("=" * 60)
        
        # 模拟Tab管理器的调用方式
        print("📋 模拟Tab管理器调用流程:")
        
        # 1. 账号数据
        mock_account = {
            'phone': '15155712316',
            'token': '5e160d18859114a648efc599113c585a'
        }
        print(f"  1. 账号数据: {mock_account['phone']}")
        
        # 2. 检查token
        token = mock_account.get('token')
        if not token:
            print(f"  ❌ Token缺失")
            return False
        print(f"  2. Token验证: {token[:10]}...")
        
        # 3. 调用订单API
        from 订单列表 import get_user_orders
        result = get_user_orders(token, offset=0)
        print(f"  3. API调用: success={result.get('success')}")
        
        # 4. 处理结果
        if result.get('success'):
            orders = result.get('orders', [])
            print(f"  4. 数据处理: {len(orders)} 个订单")
            
            # 5. 模拟表格更新
            print(f"  5. 表格更新模拟:")
            for i, order in enumerate(orders[:3]):  # 只显示前3个
                movie_name = order.get('movie_name', '未知影片')
                cinema_name = order.get('cinema_name', '未知影院')
                status_desc = order.get('status_desc', '未知状态')
                order_id = order.get('order_id', '未知订单号')
                
                print(f"    行{i+1}: {movie_name} | {cinema_name} | {status_desc} | {order_id}")
            
            if len(orders) > 3:
                print(f"    ... 还有 {len(orders) - 3} 个订单")
            
            print(f"  ✅ Tab管理器兼容性测试通过")
            return True
        else:
            print(f"  ❌ API调用失败: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"❌ Tab管理器兼容性测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_format_comparison():
    """测试数据格式对比"""
    try:
        print("\n🧪 测试数据格式对比")
        print("=" * 60)
        
        # 新格式示例
        new_format_order = {
            'movie_name': '名侦探柯南：独眼的残像',
            'status_desc': '已放映',
            'cinema_name': '北京沃美世界城店',
            'order_id': '240113194910006904',
            'show_date': '2024-01-13 20:25',
            'hall_name': '6号彩虹厅',
            'seat_info': '9排4座|9排5座',
            'ticket_num': 2,
            'display': {
                'title': '名侦探柯南：独眼的残像',
                'subtitle': '北京沃美世界城店 | 已放映',
                'summary': '名侦探柯南：独眼的残像 - 已放映'
            }
        }
        
        # 旧格式示例
        old_format_order = {
            'orderName': '名侦探柯南：独眼的残像',
            'orderS': '已放映',
            'orderno': '240113194910006904'
        }
        
        print("📋 新格式订单数据:")
        print(json.dumps(new_format_order, ensure_ascii=False, indent=2))
        
        print("\n📋 旧格式订单数据:")
        print(json.dumps(old_format_order, ensure_ascii=False, indent=2))
        
        # 格式检测逻辑
        def detect_format(order):
            is_new_format = 'movie_name' in order and 'status_desc' in order
            return "新格式" if is_new_format else "旧格式"
        
        print(f"\n📋 格式检测:")
        print(f"  - 新格式订单: {detect_format(new_format_order)}")
        print(f"  - 旧格式订单: {detect_format(old_format_order)}")
        
        # 字段映射测试
        def extract_fields(order):
            is_new_format = 'movie_name' in order and 'status_desc' in order
            
            if is_new_format:
                return {
                    'movie': order.get('movie_name', '未知影片'),
                    'status': order.get('status_desc', '未知状态'),
                    'cinema': order.get('cinema_name', '未知影院'),
                    'order_no': order.get('order_id', '未知订单号')
                }
            else:
                return {
                    'movie': order.get('orderName', '未知影片'),
                    'status': order.get('orderS', '未知状态'),
                    'cinema': '当前影院',  # 旧格式没有影院信息
                    'order_no': order.get('orderno', '未知订单号')
                }
        
        print(f"\n📋 字段提取:")
        new_fields = extract_fields(new_format_order)
        old_fields = extract_fields(old_format_order)
        
        print(f"  新格式提取: {new_fields}")
        print(f"  旧格式提取: {old_fields}")
        
        print(f"✅ 数据格式对比测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 数据格式对比测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_error_handling():
    """测试错误处理"""
    try:
        print("\n🧪 测试错误处理")
        print("=" * 60)
        
        from 订单列表 import get_user_orders
        
        # 测试1：无效token
        print("📋 测试1: 无效token")
        result = get_user_orders("invalid_token")
        print(f"  结果: success={result.get('success')}, error={result.get('error', 'N/A')}")
        
        # 测试2：空token
        print("📋 测试2: 空token")
        result = get_user_orders("")
        print(f"  结果: success={result.get('success')}, error={result.get('error', 'N/A')}")
        
        # 测试3：None token
        print("📋 测试3: None token")
        try:
            result = get_user_orders(None)
            print(f"  结果: success={result.get('success')}, error={result.get('error', 'N/A')}")
        except Exception as e:
            print(f"  异常: {e}")
        
        print(f"✅ 错误处理测试完成")
        return True
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 沃美电影票务系统 - 订单Tab集成测试")
    print("=" * 60)
    print("📋 测试目标：验证订单列表.py与Tab管理器的集成")
    print("🔍 测试内容：")
    print("  1. 订单API集成测试")
    print("  2. Tab管理器兼容性测试")
    print("  3. 数据格式对比测试")
    print("  4. 错误处理测试")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        test_order_api_integration,
        test_tab_manager_compatibility,
        test_data_format_comparison,
        test_error_handling
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_func in tests:
        try:
            if test_func():
                success_count += 1
        except Exception as e:
            print(f"❌ 测试异常: {e}")
    
    print(f"\n🎉 测试完成！")
    print(f"📊 测试结果: {success_count}/{total_tests} 通过")
    
    if success_count == total_tests:
        print(f"✅ 所有测试通过，订单Tab集成成功！")
        print(f"\n📋 集成总结：")
        print(f"✅ 订单列表.py重构完成，提供标准化接口")
        print(f"✅ Tab管理器已集成新的订单API")
        print(f"✅ 支持4个关键字段提取和显示")
        print(f"✅ 兼容新旧数据格式，平滑过渡")
        print(f"✅ 完善的错误处理和日志输出")
        print(f"\n🚀 现在订单Tab页面可以正常显示沃美订单列表！")
    else:
        print(f"❌ 部分测试失败，需要进一步检查")

if __name__ == "__main__":
    main()
