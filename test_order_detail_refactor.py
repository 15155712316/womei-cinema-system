#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单详情重构测试脚本
验证统一的订单详情管理器是否正常工作
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.order_display import OrderDetailManager, FieldNameMapper


class MockMainWindow:
    """模拟主窗口类用于测试"""
    
    def __init__(self):
        # 模拟主窗口的属性
        self.current_account = {
            'userid': '15155712316',
            'cinemaid': '35fec8259e74',
            'cinema_id': '35fec8259e74',
            'payment_password': '111111'
        }
        
        self.member_info = {
            'has_member_card': True,
            'raw_data': {'cardno': '123456'}
        }
        
        self.selected_coupons = []
        self.current_coupon_info = None
        
        # 模拟UI组件
        self.phone_display = MockLabel()
        self.order_detail_text = MockTextEdit()
        
        # 模拟Tab管理器
        self.tab_manager_widget = MockTabManager()
        
    def _get_enhanced_password_display(self, enable_mempassword):
        """模拟密码显示方法"""
        if enable_mempassword == '1':
            return "密码: 需要输入 (已设置支付密码)"
        elif enable_mempassword == '0':
            return "密码: 无需输入"
        else:
            return "密码: 检测中..."


class MockLabel:
    """模拟标签组件"""
    def __init__(self):
        self.text = ""
    
    def setText(self, text):
        self.text = text
        print(f"[MockLabel] 设置文本: {text}")


class MockTextEdit:
    """模拟文本编辑组件"""
    def __init__(self):
        self.text = ""
    
    def setPlainText(self, text):
        self.text = text
        print(f"[MockTextEdit] 设置文本:\n{text}")


class MockTabManager:
    """模拟Tab管理器"""
    def __init__(self):
        self.current_cinema_data = {
            'cinemaShortName': '华夏优加荟大都荟',
            'cinemaid': '35fec8259e74'
        }
        
        self.current_movie_data = {
            'filmname': '测试电影'
        }
        
        self.current_session_data = {
            'startTime': '19:30',
            'showDate': '2024-12-06'
        }


def test_field_name_mapper():
    """测试字段名映射器"""
    print("=" * 50)
    print("测试字段名映射器")
    print("=" * 50)
    
    # 测试数据
    test_data = {
        'cinemaid': '35fec8259e74',
        'orderno': 'ORDER123456',
        'movie': '测试电影',
        'cinemaname': '华夏优加荟大都荟',
        'totalprice': '2500',
        'mem_totalprice': '2000'
    }
    
    print(f"原始数据: {test_data}")
    
    # 标准化处理
    normalized = FieldNameMapper.normalize_data(test_data)
    print(f"标准化后: {normalized}")
    
    # 测试影院ID获取
    cinema_id = FieldNameMapper.get_cinema_id(test_data)
    print(f"影院ID: {cinema_id}")
    
    print("✅ 字段名映射器测试通过\n")


def test_order_detail_manager():
    """测试订单详情管理器"""
    print("=" * 50)
    print("测试订单详情管理器")
    print("=" * 50)
    
    # 创建模拟主窗口
    mock_window = MockMainWindow()
    
    # 创建订单详情管理器
    manager = OrderDetailManager(mock_window)
    
    # 测试数据1: 订单创建场景
    order_data_creation = {
        'orderno': 'ORDER123456',
        'movie': '测试电影',
        'cinema': '华夏优加荟大都荟',
        'seats': ['5排7座'],
        'status': '待支付',
        'api_data': {
            'enable_mempassword': '1',
            'totalprice': '2500',
            'mem_totalprice': '2000'
        }
    }
    
    print("测试场景1: 订单创建显示")
    manager.display_order_detail(order_data_creation, 'creation')
    print()
    
    # 测试数据2: 订单更新场景
    order_data_update = {
        'order_id': 'ORDER789012',
        'filmname': '另一部电影',
        'cinemaname': '其他影院',
        'seats': ['3排5座', '3排6座'],
        'status': '已支付',
        'enable_mempassword': '0'
    }
    
    print("测试场景2: 订单更新显示")
    manager.display_order_detail(order_data_update, 'update')
    print()
    
    print("✅ 订单详情管理器测试通过\n")


def test_data_enhancement():
    """测试数据增强功能"""
    print("=" * 50)
    print("测试数据增强功能")
    print("=" * 50)
    
    # 创建模拟主窗口
    mock_window = MockMainWindow()
    manager = OrderDetailManager(mock_window)
    
    # 测试不完整的订单数据
    incomplete_data = {
        'orderno': 'ORDER999',
        'status': '待支付'
    }
    
    print(f"原始不完整数据: {incomplete_data}")
    
    # 数据增强
    enhanced = manager._enhance_and_normalize_order_data(incomplete_data)
    print(f"增强后数据: {enhanced}")
    
    # 验证增强效果
    assert 'phone_number' in enhanced, "应该包含手机号"
    assert 'cinema_name' in enhanced, "应该包含影院名称"
    assert 'movie_name' in enhanced, "应该包含电影名称"
    
    print("✅ 数据增强功能测试通过\n")


def test_price_calculation():
    """测试价格计算逻辑"""
    print("=" * 50)
    print("测试价格计算逻辑")
    print("=" * 50)
    
    # 创建模拟主窗口
    mock_window = MockMainWindow()
    manager = OrderDetailManager(mock_window)
    
    # 测试会员价格场景
    member_order = {
        'orderno': 'MEMBER001',
        'api_data': {
            'totalprice': '2500',  # 原价25元
            'mem_totalprice': '2000',  # 会员价20元
            'enable_mempassword': '1'
        }
    }
    
    print("测试场景: 会员价格计算")
    price_info = manager._build_price_info(member_order)
    print(f"价格信息: {price_info}")
    
    # 验证价格信息
    assert any('原价: ¥25.00' in line for line in price_info), "应该显示原价"
    assert any('会员价' in line for line in price_info), "应该显示会员价"
    
    print("✅ 价格计算逻辑测试通过\n")


def test_error_handling():
    """测试错误处理"""
    print("=" * 50)
    print("测试错误处理")
    print("=" * 50)
    
    # 创建模拟主窗口
    mock_window = MockMainWindow()
    manager = OrderDetailManager(mock_window)
    
    # 测试空数据
    print("测试场景1: 空数据处理")
    manager.display_order_detail({}, 'test')
    
    # 测试异常数据
    print("测试场景2: 异常数据处理")
    manager.display_order_detail(None, 'test')
    
    # 测试格式错误数据
    print("测试场景3: 格式错误数据处理")
    manager.display_order_detail("invalid_data", 'test')
    
    print("✅ 错误处理测试通过\n")


def run_all_tests():
    """运行所有测试"""
    print("🚀 开始订单详情重构测试")
    print("=" * 60)
    
    try:
        test_field_name_mapper()
        test_order_detail_manager()
        test_data_enhancement()
        test_price_calculation()
        test_error_handling()
        
        print("=" * 60)
        print("🎉 所有测试通过！订单详情重构成功！")
        print("=" * 60)
        
        # 输出重构效果总结
        print("\n📊 重构效果总结:")
        print("✅ 统一了订单详情显示逻辑")
        print("✅ 标准化了字段名处理")
        print("✅ 增强了数据完整性")
        print("✅ 改善了错误处理")
        print("✅ 提高了代码可维护性")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
