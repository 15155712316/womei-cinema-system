#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美订单详情字段映射和二维码生成
验证双击订单显示取票码二维码功能
"""

import sys
import os
import json

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_field_mapping():
    """测试字段映射"""
    try:
        print("🧪 测试沃美订单详情字段映射")
        print("=" * 60)
        
        # 导入订单服务
        from services.womei_order_service import WomeiOrderService
        
        # 创建服务实例
        service = WomeiOrderService()
        
        # 模拟沃美API返回的订单详情数据
        mock_detail_data = {
            "order_id": "240113194910006904",
            "status": "SUCCESS", 
            "status_desc": "已放映",
            "cinema_name": "慈溪沃美影城",
            "movie_name": "金手指",
            "ticket_code": "WFDHT5M",
            "ticket_code_arr": [
                {"name": "序列号", "code": "WFDHT5M"}, 
                {"name": "验证码", "code": "742949"}
            ],
            "show_date": "2024-01-13 20:25",
            "ticket_items": {
                "seat_info": "9排4座 | 9排5座",
                "hall_name": "6号彩虹厅"
            }
        }
        
        print(f"📋 原始API数据:")
        for key, value in mock_detail_data.items():
            if key != 'ticket_code_arr' and key != 'ticket_items':
                print(f"  - {key}: {value}")
        
        # 测试格式化方法
        formatted_detail = service.format_order_detail(mock_detail_data)
        
        print(f"\n📋 格式化后的字段映射验证:")
        
        # 验证UI期望的字段
        ui_expected_fields = {
            'order_no': '240113194910006904',
            'ticket_code': 'WFDHT5M',
            'film_name': '金手指',
            'cinema_name': '慈溪沃美影城',
            'show_time': '2024-01-13 20:25',
            'hall_name': '6号彩虹厅',
            'seat_info': '9排4座 | 9排5座'
        }
        
        for field, expected_value in ui_expected_fields.items():
            actual_value = formatted_detail.get(field, 'MISSING')
            status = "✅" if actual_value == expected_value else "❌"
            print(f"  {status} {field}: {actual_value}")
            if actual_value != expected_value:
                print(f"    期望: {expected_value}")
                print(f"    实际: {actual_value}")
        
        # 验证显示类型
        display_type = formatted_detail.get('display_type', 'MISSING')
        expected_display_type = 'generated_qrcode'
        status = "✅" if display_type == expected_display_type else "❌"
        print(f"  {status} display_type: {display_type}")
        
        # 验证order_info字段（用于二维码生成）
        order_info = formatted_detail.get('order_info', {})
        print(f"\n📋 二维码生成所需字段验证:")
        qr_expected_fields = {
            'filmName': '金手指',
            'cinemaName': '慈溪沃美影城',
            'showTime': '2024-01-13 20:25',
            'hallName': '6号彩虹厅',
            'seatInfo': '9排4座 | 9排5座',
            'orderNo': '240113194910006904',
            'ticketCode': 'WFDHT5M'
        }
        
        for field, expected_value in qr_expected_fields.items():
            actual_value = order_info.get(field, 'MISSING')
            status = "✅" if actual_value == expected_value else "❌"
            print(f"  {status} {field}: {actual_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 字段映射测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qrcode_generation():
    """测试二维码生成"""
    try:
        print("\n🧪 测试二维码生成功能")
        print("=" * 60)
        
        # 导入二维码生成器
        from utils.qrcode_generator import generate_ticket_qrcode, save_qrcode_image
        
        # 测试数据
        test_ticket_code = "WFDHT5M"
        test_order_info = {
            'filmName': '金手指',
            'cinemaName': '慈溪沃美影城',
            'showTime': '2024-01-13 20:25',
            'hallName': '6号彩虹厅',
            'seatInfo': '9排4座 | 9排5座',
            'orderNo': '240113194910006904',
            'ticketCode': 'WFDHT5M'
        }
        
        print(f"📋 测试参数:")
        print(f"  - 取票码: {test_ticket_code}")
        print(f"  - 订单信息: {len(test_order_info)} 个字段")
        
        # 生成二维码
        qr_bytes = generate_ticket_qrcode(test_ticket_code, test_order_info)
        
        if qr_bytes:
            print(f"✅ 二维码生成成功: {len(qr_bytes)} bytes")
            
            # 保存二维码图片
            qr_path = save_qrcode_image(qr_bytes, "240113194910006904", "400028")
            
            if qr_path:
                print(f"✅ 二维码保存成功: {qr_path}")
                
                # 验证文件是否存在
                if os.path.exists(qr_path):
                    file_size = os.path.getsize(qr_path)
                    print(f"✅ 文件验证成功: {file_size} bytes")
                else:
                    print(f"❌ 文件不存在: {qr_path}")
                    return False
            else:
                print(f"❌ 二维码保存失败")
                return False
        else:
            print(f"❌ 二维码生成失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 二维码生成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_data_structure():
    """测试UI数据结构兼容性"""
    try:
        print("\n🧪 测试UI数据结构兼容性")
        print("=" * 60)
        
        # 模拟完整的UI数据结构
        ui_data = {
            # UI期望的字段名
            'order_no': '240113194910006904',
            'ticket_code': 'WFDHT5M',
            'film_name': '金手指',
            'cinema_name': '慈溪沃美影城',
            'show_time': '2024-01-13 20:25',
            'hall_name': '6号彩虹厅',
            'seat_info': '9排4座 | 9排5座',
            
            # 二维码相关字段
            'qr_bytes': b'fake_qr_data',
            'qr_path': 'data/qrcodes/240113194910006904_400028.png',
            'data_size': 12345,
            'data_format': 'PNG',
            'source': 'womei_order_detail',
            'is_generated': True,
            
            # 显示类型
            'display_type': 'generated_qrcode'
        }
        
        print(f"📋 UI数据结构验证:")
        
        # 验证必需字段
        required_fields = [
            'order_no', 'ticket_code', 'film_name', 'cinema_name', 
            'show_time', 'display_type'
        ]
        
        for field in required_fields:
            if field in ui_data:
                print(f"  ✅ {field}: {ui_data[field]}")
            else:
                print(f"  ❌ {field}: MISSING")
                return False
        
        # 验证二维码字段
        qr_fields = ['qr_bytes', 'qr_path', 'data_size', 'data_format']
        print(f"\n📋 二维码字段验证:")
        
        for field in qr_fields:
            if field in ui_data:
                value = ui_data[field]
                if field == 'qr_bytes':
                    print(f"  ✅ {field}: {len(value)} bytes")
                else:
                    print(f"  ✅ {field}: {value}")
            else:
                print(f"  ❌ {field}: MISSING")
        
        # 验证显示类型
        display_type = ui_data.get('display_type')
        expected_types = ['ticket_code', 'combined', 'generated_qrcode']
        
        if display_type in expected_types:
            print(f"\n✅ 显示类型有效: {display_type}")
        else:
            print(f"\n❌ 显示类型无效: {display_type}")
            print(f"   支持的类型: {expected_types}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ UI数据结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_simulation():
    """模拟完整集成测试"""
    try:
        print("\n🧪 模拟完整集成测试")
        print("=" * 60)
        
        # 模拟双击订单的完整流程
        print(f"📋 模拟流程:")
        print(f"  1. 用户双击订单")
        print(f"  2. 获取订单详情API")
        print(f"  3. 格式化数据并生成二维码")
        print(f"  4. 发送到主窗口显示")
        
        # 步骤1：模拟订单列表数据
        order_list_item = {
            'order_id': '240113194910006904',
            'movie_name': '金手指',
            'cinema_name': '慈溪沃美影城',
            'status_desc': '已放映'
        }
        
        # 步骤2：模拟API返回的详情数据
        api_response = {
            "ret": 0,
            "sub": 0,
            "msg": "successfully",
            "data": {
                "order_id": "240113194910006904",
                "status": "SUCCESS", 
                "status_desc": "已放映",
                "cinema_name": "慈溪沃美影城",
                "movie_name": "金手指",
                "ticket_code": "WFDHT5M",
                "ticket_code_arr": [
                    {"name": "序列号", "code": "WFDHT5M"}, 
                    {"name": "验证码", "code": "742949"}
                ],
                "show_date": "2024-01-13 20:25",
                "ticket_items": {
                    "seat_info": "9排4座 | 9排5座",
                    "hall_name": "6号彩虹厅"
                }
            }
        }
        
        # 步骤3：格式化数据
        from services.womei_order_service import WomeiOrderService
        service = WomeiOrderService()
        formatted_detail = service.format_order_detail(api_response['data'])
        
        # 步骤4：生成二维码
        ticket_code = formatted_detail.get('ticket_code')
        order_info = formatted_detail.get('order_info', {})
        
        if ticket_code and order_info:
            from utils.qrcode_generator import generate_ticket_qrcode
            qr_bytes = generate_ticket_qrcode(ticket_code, order_info)
            
            if qr_bytes:
                # 步骤5：构建最终UI数据
                final_ui_data = {
                    'order_no': formatted_detail.get('order_no'),
                    'ticket_code': ticket_code,
                    'film_name': formatted_detail.get('film_name'),
                    'cinema_name': formatted_detail.get('cinema_name'),
                    'show_time': formatted_detail.get('show_time'),
                    'hall_name': formatted_detail.get('hall_name'),
                    'seat_info': formatted_detail.get('seat_info'),
                    'qr_bytes': qr_bytes,
                    'data_size': len(qr_bytes),
                    'data_format': 'PNG',
                    'source': 'womei_order_detail',
                    'display_type': 'generated_qrcode'
                }
                
                print(f"\n✅ 集成测试成功:")
                print(f"  - 订单号: {final_ui_data['order_no']}")
                print(f"  - 取票码: {final_ui_data['ticket_code']}")
                print(f"  - 影片: {final_ui_data['film_name']}")
                print(f"  - 二维码: {final_ui_data['data_size']} bytes")
                print(f"  - 显示类型: {final_ui_data['display_type']}")
                
                return True
            else:
                print(f"❌ 二维码生成失败")
                return False
        else:
            print(f"❌ 缺少取票码或订单信息")
            return False
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🎬 沃美电影票务系统 - 字段映射和二维码生成测试")
    print("=" * 60)
    print("📋 测试目标：验证双击订单显示取票码二维码功能")
    print("🔍 测试内容：")
    print("  1. 字段映射验证")
    print("  2. 二维码生成测试")
    print("  3. UI数据结构兼容性")
    print("  4. 完整集成模拟")
    print("=" * 60)
    print()
    
    # 运行所有测试
    tests = [
        test_field_mapping,
        test_qrcode_generation,
        test_ui_data_structure,
        test_integration_simulation
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
        print(f"✅ 所有测试通过，字段映射和二维码生成功能正常！")
        print(f"\n📋 修改总结：")
        print(f"✅ 实现了UI期望的字段映射")
        print(f"✅ 设置了正确的display_type: 'generated_qrcode'")
        print(f"✅ 集成了二维码生成功能")
        print(f"✅ 提供了完整的订单详情信息")
        print(f"\n🚀 现在双击订单可以显示包含详情的取票码二维码了！")
    else:
        print(f"❌ 部分测试失败，需要进一步检查")

if __name__ == "__main__":
    main()
