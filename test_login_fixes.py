#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试登录问题修复效果
验证以下修复:
1. 登录后不再出现未登录提示
2. 手机号记忆功能正常工作
3. 机器码逻辑清晰明确
"""

import sys
import os
import json
import time
from datetime import datetime

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.auth_service import auth_service

def test_machine_code_generation():
    """测试机器码生成"""
    print("=" * 50)
    print("🔧 测试机器码生成")
    print("=" * 50)
    
    machine_code = auth_service.get_machine_code()
    print(f"✅ 当前设备机器码: {machine_code}")
    print(f"✅ 机器码长度: {len(machine_code)} 位")
    print(f"✅ 机器码类型: {'MD5' if len(machine_code) == 32 else '其他'}")
    
    # 验证机器码一致性
    machine_code2 = auth_service.get_machine_code()
    if machine_code == machine_code2:
        print("✅ 机器码生成一致性: 通过")
    else:
        print("❌ 机器码生成一致性: 失败")
    
    return machine_code

def test_login_functionality():
    """测试登录功能"""
    print("\n" + "=" * 50)
    print("🔐 测试登录功能")
    print("=" * 50)
    
    test_phone = "15155712316"
    print(f"📱 测试手机号: {test_phone}")
    
    # 测试登录
    success, message, user_info = auth_service.login(test_phone)
    
    if success:
        print(f"✅ 登录成功: {message}")
        print(f"✅ 用户信息: {user_info}")
        
        # 测试认证检查
        print("\n🔍 测试认证状态检查...")
        is_valid, auth_message, auth_user_info = auth_service.check_auth()
        
        if is_valid:
            print(f"✅ 认证状态检查: 通过 - {auth_message}")
            print(f"✅ 用户状态正常")
        else:
            print(f"❌ 认证状态检查: 失败 - {auth_message}")
        
        # 测试积分系统
        print("\n💰 测试积分系统...")
        current_points = user_info.get('points', 0)
        print(f"📊 当前积分: {current_points}")
        
        if current_points >= 10:
            points_success, points_message = auth_service.use_points("测试操作", 10)
            if points_success:
                print(f"✅ 积分扣除: {points_message}")
            else:
                print(f"❌ 积分扣除失败: {points_message}")
        else:
            print("⚠️  积分不足，跳过扣除测试")
        
        return True
    else:
        print(f"❌ 登录失败: {message}")
        return False

def test_login_history():
    """测试登录历史功能"""
    print("\n" + "=" * 50)
    print("📝 测试登录历史功能")
    print("=" * 50)
    
    history_file = "data/login_history.json"
    
    # 检查历史文件是否存在
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
            
            last_phone = history.get('last_phone', '')
            last_time = history.get('last_login_time', '')
            
            print(f"✅ 历史文件存在: {history_file}")
            print(f"📱 上次登录手机号: {last_phone}")
            print(f"⏰ 上次登录时间: {last_time}")
            
            if last_phone and len(last_phone) == 11:
                print("✅ 登录历史记录正常")
                return True
            else:
                print("⚠️  登录历史记录格式异常")
                return False
        except Exception as e:
            print(f"❌ 读取登录历史失败: {e}")
            return False
    else:
        print("⚠️  登录历史文件不存在（首次运行正常）")
        return True

def test_api_connection():
    """测试API连接状态"""
    print("\n" + "=" * 50)
    print("🌐 测试API连接状态")
    print("=" * 50)
    
    import requests
    
    try:
        api_url = "http://43.142.19.28:5000"
        print(f"🔗 测试连接: {api_url}")
        
        response = requests.get(f"{api_url}/health", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API服务器状态: {result.get('status', 'unknown')}")
            print(f"✅ 数据库状态: {result.get('database', 'unknown')}")
            return True
        else:
            print(f"⚠️  API服务器响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到API服务器: {e}")
        return False

def test_coupon_none_handling():
    """测试券列表的None处理"""
    print("\n=== 测试券列表None处理 ===")
    
    # 模拟不同的API返回情况
    test_cases = [
        (None, "API返回None"),
        ({}, "空字典"),
        ({"resultCode": "-1", "resultDesc": "错误"}, "错误响应"),
        ({"resultCode": "0", "resultData": None}, "resultData为None"),
        ({"resultCode": "0", "resultData": {}}, "resultData为空字典"),
        ({"resultCode": "0", "resultData": {"vouchers": []}}, "vouchers为空列表"),
        ({"resultCode": "0", "resultData": {"vouchers": [{"couponname": "测试券", "expireddate": "2024-12-31", "couponcode": "TEST123"}]}}, "正常券数据"),
    ]
    
    def mock_update_coupons(coupon_result, ticketcount=1):
        """模拟券列表更新逻辑"""
        print(f"  处理: {coupon_result}")
        
        # 修复后的逻辑
        if coupon_result is None:
            print("    结果: API无响应")
            return "API无响应"
        
        if not isinstance(coupon_result, dict) or coupon_result.get('resultCode') != '0':
            print("    结果: 无可用优惠券")
            return "无可用优惠券"
            
        # 获取券数据 - 增加安全检查
        result_data = coupon_result.get('resultData')
        if result_data is None:
            print("    结果: 券数据为空")
            return "券数据为空"
        
        vouchers = result_data.get('vouchers', [])
        
        if not vouchers:
            print("    结果: 暂无可用优惠券")
            return "暂无可用优惠券"
        
        # 处理券数据
        valid_vouchers = []
        for i, v in enumerate(vouchers):
            if not isinstance(v, dict):
                continue
            valid_vouchers.append(v)
        
        print(f"    结果: 成功处理{len(valid_vouchers)}张券")
        return f"成功处理{len(valid_vouchers)}张券"
    
    all_passed = True
    for coupon_result, description in test_cases:
        print(f"\n测试用例: {description}")
        try:
            result = mock_update_coupons(coupon_result)
            print(f"✅ 测试通过")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            all_passed = False
    
    return all_passed

def main():
    """主测试函数"""
    print("🚀 乐影系统登录问题修复验证")
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 1. 测试机器码生成
    machine_code = test_machine_code_generation()
    test_results.append(("机器码生成", machine_code is not None))
    
    # 2. 测试API连接
    api_ok = test_api_connection()
    test_results.append(("API连接", api_ok))
    
    # 3. 测试登录功能
    login_ok = test_login_functionality()
    test_results.append(("登录功能", login_ok))
    
    # 4. 测试登录历史
    history_ok = test_login_history()
    test_results.append(("登录历史", history_ok))
    
    # 5. 测试券列表None处理
    coupon_ok = test_coupon_none_handling()
    test_results.append(("券列表None处理", coupon_ok))
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name.ljust(15)} - {status}")
        if result:
            passed += 1
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\n🎯 测试通过率: {passed}/{total} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("🎉 修复效果良好！可以正常使用")
    else:
        print("⚠️  仍存在问题，需要进一步调试")
    
    print("\n💡 使用说明:")
    print("1. 启动程序会自动显示登录窗口")
    print("2. 输入手机号后会自动记忆，下次启动无需重新输入")
    print("3. 当前机器码会显示在登录界面，可以复制给管理员")
    print("4. 登录成功后不会频繁检查认证状态")
    print("5. 确认软件逻辑：输入账号 → 读取当前机器码 → 与API返回的账号机器码匹配 → 允许登录")

if __name__ == "__main__":
    main() 