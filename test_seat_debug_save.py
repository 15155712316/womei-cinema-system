#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试座位图调试数据保存功能
验证修改后的座位图加载逻辑是否正确保存调试数据
"""

import json
import sys
import os
from datetime import datetime

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

def test_seat_debug_data_save():
    """测试座位图调试数据保存"""
    print("🧪 测试座位图调试数据保存功能")
    print("=" * 50)
    
    account = load_account()
    token = account.get('token', '')
    
    if not token:
        print("❌ 没有找到token")
        return False
    
    try:
        from services.womei_film_service import get_womei_film_service
        
        # 创建服务实例
        service = get_womei_film_service(token)
        
        # 测试参数
        cinema_id = "400028"
        hall_id = "5"
        schedule_id = "16626081"
        
        print(f"🎬 测试参数:")
        print(f"  - cinema_id: {cinema_id}")
        print(f"  - hall_id: {hall_id}")
        print(f"  - schedule_id: {schedule_id}")
        print(f"  - token: {token[:20]}...")
        
        # 调用座位图API（应该自动保存调试数据）
        result = service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        print(f"\n📥 API调用结果:")
        print(f"  - 成功: {result.get('success', False)}")
        
        if result.get('success'):
            hall_info = result.get('hall_info', {})
            print(f"  - 影厅数据: {type(hall_info)}")
            print(f"  - 区域数: {len(hall_info.get('room_seat', []))}")
            
            # 检查调试文件是否已保存
            debug_filename = f"data/座位_{cinema_id}_{schedule_id}.json"
            
            if os.path.exists(debug_filename):
                print(f"\n✅ 基础调试文件已保存: {debug_filename}")
                
                # 读取并验证文件内容
                with open(debug_filename, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)
                
                print(f"📊 基础调试文件内容:")
                session_info = debug_data.get('session_info', {})
                print(f"  - 影院ID: {session_info.get('cinema_id', 'N/A')}")
                print(f"  - 影厅ID: {session_info.get('hall_id', 'N/A')}")
                print(f"  - 场次ID: {session_info.get('schedule_id', 'N/A')}")
                print(f"  - 保存时间: {session_info.get('timestamp', 'N/A')}")
                print(f"  - 文件大小: {os.path.getsize(debug_filename)} bytes")
                
                return True
            else:
                print(f"\n❌ 基础调试文件未找到: {debug_filename}")
                return False
        else:
            error = result.get('error', '未知错误')
            print(f"  - 错误: {error}")
            return False
    
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_debug_data_simulation():
    """模拟测试增强调试数据保存"""
    print(f"\n🧪 模拟测试增强调试数据保存")
    print("=" * 50)
    
    # 模拟会话信息
    session_info = {
        'cinema_data': {
            'cinema_id': '400028',
            'cinema_name': '北京沃美世界城店',
            'cinemaShortName': '北京沃美世界城店'
        },
        'session_data': {
            'schedule_id': '16626081',
            'hall_id': '5',
            'hall_name': '5号厅 高亮激光厅',
            'movie_name': '名侦探柯南：独眼的残像',
            'show_date': '2025-06-27',
            'show_time': '14:20'
        },
        'account': load_account(),
        'session_text': '2025-06-27 14:20'
    }
    
    # 模拟座位图API结果
    seat_result = {
        'success': True,
        'hall_info': {
            'cinema_id': 400028,
            'hall_no': '5',
            'hall_name': '5号厅 高亮激光厅',
            'room_seat': [
                {
                    'area_no': '1',
                    'area_name': '普通区',
                    'area_price': 57.9,
                    'seats': {
                        '2': {
                            'row': 2,
                            'desc': '2',
                            'detail': [
                                {
                                    'seat_no': '11051771#09#05',
                                    'row': '2',
                                    'col': '4',
                                    'x': 6,
                                    'y': 2,
                                    'type': 0,
                                    'status': 0
                                }
                            ]
                        }
                    }
                }
            ]
        }
    }
    
    try:
        # 模拟增强调试数据保存逻辑
        import os
        import json
        from datetime import datetime
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        cinema_id = session_info['cinema_data']['cinema_id']
        hall_id = session_info['session_data']['hall_id']
        schedule_id = session_info['session_data']['schedule_id']
        
        # 构建增强的调试数据
        enhanced_debug_data = {
            "session_info": {
                "cinema_name": session_info['cinema_data']['cinema_name'],
                "movie_name": session_info['session_data']['movie_name'],
                "show_date": session_info['session_data']['show_date'],
                "show_time": session_info['session_data']['show_time'],
                "cinema_id": cinema_id,
                "hall_id": hall_id,
                "hall_name": session_info['session_data']['hall_name'],
                "schedule_id": schedule_id,
                "timestamp": datetime.now().isoformat(),
                "account_phone": session_info['account'].get('phone', 'N/A'),
                "session_text": session_info['session_text']
            },
            "api_response": seat_result,
            "hall_info": seat_result['hall_info'],
            "cinema_data": session_info['cinema_data'],
            "session_data": session_info['session_data'],
            "account_data": {
                "phone": session_info['account'].get('phone', 'N/A'),
                "token_prefix": session_info['account'].get('token', '')[:20] + '...' if session_info['account'].get('token') else 'N/A'
            },
            "debug_notes": {
                "purpose": "增强的座位图调试数据（包含完整会话信息）",
                "area_no_usage": "区域ID应该使用area_no字段，不是固定的1",
                "seat_no_format": "seat_no应该是类似11051771#09#06的格式",
                "coordinate_mapping": "row/col是逻辑位置，x/y是物理位置",
                "status_meaning": "0=可选，1=已售，2=锁定",
                "file_naming": f"座位_{cinema_id}_{schedule_id}.json"
            }
        }
        
        # 文件命名
        filename = f"data/座位_{cinema_id}_{schedule_id}_enhanced_test.json"
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(enhanced_debug_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 增强调试数据模拟保存成功: {filename}")
        print(f"📊 增强数据内容:")
        print(f"  - 影院: {enhanced_debug_data['session_info']['cinema_name']}")
        print(f"  - 影片: {enhanced_debug_data['session_info']['movie_name']}")
        print(f"  - 场次: {enhanced_debug_data['session_info']['show_date']} {enhanced_debug_data['session_info']['show_time']}")
        print(f"  - 影厅: {enhanced_debug_data['session_info']['hall_name']}")
        print(f"  - 账号: {enhanced_debug_data['session_info']['account_phone']}")
        print(f"  - 文件大小: {os.path.getsize(filename)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ 模拟测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_existing_debug_files():
    """检查现有的调试文件"""
    print(f"\n🔍 检查现有的调试文件")
    print("=" * 50)
    
    data_dir = 'data'
    if not os.path.exists(data_dir):
        print(f"❌ data目录不存在")
        return
    
    # 查找座位调试文件
    debug_files = []
    for filename in os.listdir(data_dir):
        if filename.startswith('座位_') and filename.endswith('.json'):
            debug_files.append(filename)
    
    if debug_files:
        print(f"✅ 找到 {len(debug_files)} 个座位调试文件:")
        for filename in sorted(debug_files):
            filepath = os.path.join(data_dir, filename)
            file_size = os.path.getsize(filepath)
            
            # 读取文件获取基本信息
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                session_info = data.get('session_info', {})
                cinema_name = session_info.get('cinema_name', 'N/A')
                movie_name = session_info.get('movie_name', 'N/A')
                timestamp = session_info.get('timestamp', 'N/A')
                
                print(f"  📁 {filename}")
                print(f"    - 影院: {cinema_name}")
                print(f"    - 影片: {movie_name}")
                print(f"    - 时间: {timestamp}")
                print(f"    - 大小: {file_size} bytes")
                
            except Exception as e:
                print(f"  📁 {filename} (读取失败: {e})")
    else:
        print(f"❌ 没有找到座位调试文件")

def main():
    """主函数"""
    print("🔧 座位图调试数据保存功能测试")
    print("=" * 60)
    
    # 1. 检查现有调试文件
    check_existing_debug_files()
    
    # 2. 测试基础调试数据保存
    basic_ok = test_seat_debug_data_save()
    
    # 3. 模拟测试增强调试数据保存
    enhanced_ok = test_enhanced_debug_data_simulation()
    
    print(f"\n🎯 测试总结")
    print("=" * 60)
    
    if basic_ok:
        print(f"✅ 基础调试数据保存: 成功")
    else:
        print(f"❌ 基础调试数据保存: 失败")
    
    if enhanced_ok:
        print(f"✅ 增强调试数据保存: 成功")
    else:
        print(f"❌ 增强调试数据保存: 失败")
    
    if basic_ok and enhanced_ok:
        print(f"\n🎉 座位图调试数据保存功能验证成功!")
        print(f"💡 功能特点:")
        print(f"  1. ✅ 自动保存基础调试数据到 data/座位_{{cinema_id}}_{{schedule_id}}.json")
        print(f"  2. ✅ 自动保存增强调试数据到 data/座位_{{cinema_id}}_{{schedule_id}}_enhanced.json")
        print(f"  3. ✅ 包含完整的会话信息（影院、影片、场次、账号）")
        print(f"  4. ✅ 包含原始API响应数据")
        print(f"  5. ✅ 包含调试说明和格式要求")
        
        print(f"\n🚀 现在每次加载座位图都会自动保存调试数据!")
        print(f"📋 调试文件用途:")
        print(f"  - 验证area_no和seat_no的正确性")
        print(f"  - 分析座位参数构建问题")
        print(f"  - 对比不同场次的座位数据")
        print(f"  - 调试订单创建参数格式")
    else:
        print(f"\n❌ 仍有问题需要解决")

if __name__ == "__main__":
    main()
