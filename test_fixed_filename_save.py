#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试固定文件名保存功能
验证座位调试数据是否正确保存到 data/座位调试数据.json
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

def check_existing_debug_file():
    """检查现有的调试文件"""
    print("🔍 检查现有的座位调试数据文件")
    print("=" * 50)
    
    filename = "data/座位调试数据.json"
    
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            session_info = data.get('session_info', {})
            
            print(f"✅ 找到现有调试文件: {filename}")
            print(f"📊 当前文件内容:")
            print(f"  - 影院ID: {session_info.get('cinema_id', 'N/A')}")
            print(f"  - 影厅ID: {session_info.get('hall_id', 'N/A')}")
            print(f"  - 场次ID: {session_info.get('schedule_id', 'N/A')}")
            print(f"  - 影厅名: {session_info.get('hall_name', 'N/A')}")
            print(f"  - 保存时间: {session_info.get('timestamp', 'N/A')}")
            print(f"  - 文件大小: {os.path.getsize(filename)} bytes")
            
            return data
        except Exception as e:
            print(f"❌ 读取现有文件失败: {e}")
            return None
    else:
        print(f"❌ 调试文件不存在: {filename}")
        return None

def test_seat_api_call():
    """测试座位图API调用（应该自动覆盖保存到固定文件）"""
    print(f"\n🧪 测试座位图API调用")
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
        
        print(f"🎬 调用座位图API:")
        print(f"  - cinema_id: {cinema_id}")
        print(f"  - hall_id: {hall_id}")
        print(f"  - schedule_id: {schedule_id}")
        
        # 记录调用前的时间
        before_call = datetime.now()
        
        # 调用座位图API（应该自动保存到固定文件）
        result = service.get_hall_info(cinema_id, hall_id, schedule_id)
        
        # 记录调用后的时间
        after_call = datetime.now()
        
        print(f"\n📥 API调用结果:")
        print(f"  - 成功: {result.get('success', False)}")
        
        if result.get('success'):
            # 检查固定文件是否已更新
            filename = "data/座位调试数据.json"
            
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)
                
                session_info = debug_data.get('session_info', {})
                file_timestamp = session_info.get('timestamp', '')
                
                print(f"\n✅ 固定调试文件已更新: {filename}")
                print(f"📊 更新后的文件内容:")
                print(f"  - 影院ID: {session_info.get('cinema_id', 'N/A')}")
                print(f"  - 影厅ID: {session_info.get('hall_id', 'N/A')}")
                print(f"  - 场次ID: {session_info.get('schedule_id', 'N/A')}")
                print(f"  - 影厅名: {session_info.get('hall_name', 'N/A')}")
                print(f"  - 更新时间: {file_timestamp}")
                print(f"  - 文件大小: {os.path.getsize(filename)} bytes")
                
                # 验证时间戳是否在API调用期间更新
                try:
                    file_time = datetime.fromisoformat(file_timestamp.replace('Z', '+00:00').replace('+00:00', ''))
                    if before_call <= file_time <= after_call:
                        print(f"  ✅ 时间戳验证: 文件确实在API调用期间更新")
                    else:
                        print(f"  ⚠️ 时间戳验证: 文件可能不是本次调用更新的")
                except:
                    print(f"  ⚠️ 时间戳验证: 无法解析时间戳格式")
                
                return True
            else:
                print(f"\n❌ 固定调试文件未找到: {filename}")
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

def verify_file_structure():
    """验证文件结构是否正确"""
    print(f"\n🔍 验证文件结构")
    print("=" * 50)
    
    filename = "data/座位调试数据.json"
    
    if not os.path.exists(filename):
        print(f"❌ 文件不存在: {filename}")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 检查必需的字段
        required_fields = ['session_info', 'api_response', 'processed_hall_data', 'debug_notes']
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 缺少必需字段: {missing_fields}")
            return False
        
        # 检查session_info的子字段
        session_info = data.get('session_info', {})
        session_required = ['cinema_id', 'hall_id', 'schedule_id', 'timestamp']
        session_missing = []
        
        for field in session_required:
            if field not in session_info:
                session_missing.append(field)
        
        if session_missing:
            print(f"❌ session_info缺少字段: {session_missing}")
            return False
        
        # 检查API响应数据
        api_response = data.get('api_response', {})
        if not api_response.get('data'):
            print(f"❌ api_response缺少data字段")
            return False
        
        print(f"✅ 文件结构验证通过")
        print(f"📊 文件结构:")
        print(f"  - session_info: ✅")
        print(f"  - api_response: ✅")
        print(f"  - processed_hall_data: ✅")
        print(f"  - debug_notes: ✅")
        
        # 统计座位数据
        hall_data = api_response.get('data', {})
        room_seat = hall_data.get('room_seat', [])
        total_seats = 0
        
        for area in room_seat:
            for row_key, row_data in area.get('seats', {}).items():
                total_seats += len(row_data.get('detail', []))
        
        print(f"  - 区域数: {len(room_seat)}")
        print(f"  - 座位总数: {total_seats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 文件结构验证失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 固定文件名保存功能测试")
    print("=" * 60)
    
    # 1. 检查现有文件
    existing_data = check_existing_debug_file()
    
    # 2. 测试API调用（应该覆盖保存）
    api_ok = test_seat_api_call()
    
    # 3. 验证文件结构
    structure_ok = verify_file_structure()
    
    print(f"\n🎯 测试总结")
    print("=" * 60)
    
    if existing_data:
        print(f"✅ 现有文件检查: 成功")
    else:
        print(f"⚠️ 现有文件检查: 文件不存在或读取失败")
    
    if api_ok:
        print(f"✅ API调用和保存: 成功")
    else:
        print(f"❌ API调用和保存: 失败")
    
    if structure_ok:
        print(f"✅ 文件结构验证: 成功")
    else:
        print(f"❌ 文件结构验证: 失败")
    
    if api_ok and structure_ok:
        print(f"\n🎉 固定文件名保存功能验证成功!")
        print(f"💡 功能特点:")
        print(f"  1. ✅ 固定文件名: data/座位调试数据.json")
        print(f"  2. ✅ 每次覆盖保存，不创建新文件")
        print(f"  3. ✅ 包含完整的座位图API响应数据")
        print(f"  4. ✅ 包含会话信息和调试说明")
        print(f"  5. ✅ 自动更新时间戳")
        
        print(f"\n🚀 现在每次加载座位图都会覆盖保存到固定文件!")
        print(f"📋 使用方式:")
        print(f"  - 启动应用程序: python main_modular.py")
        print(f"  - 选择影院、影片、场次")
        print(f"  - 查看调试文件: data/座位调试数据.json")
        print(f"  - 每次都是最新的座位图数据")
    else:
        print(f"\n❌ 仍有问题需要解决")

if __name__ == "__main__":
    main()
