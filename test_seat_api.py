#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试沃美影院座位图API并验证座位数据结构
"""

import requests
import json
import os

def test_womei_seat_api():
    """测试沃美影院座位图API"""
    print("🎬 测试沃美影院座位图API")
    print("=" * 60)
    
    # API请求参数
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/hall/info/"
    params = {
        'hall_id': '2',
        'schedule_id': '16624418'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MicroProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'content-type': 'multipart/form-data',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': '47794858a832916d8eda012e7cabd269',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    
    print(f"📡 请求URL: {url}")
    print(f"📋 请求参数: {params}")
    print(f"🔑 使用Token: {headers['token'][:20]}...")
    
    try:
        # 发送API请求
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"\n📥 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 解析JSON响应
            data = response.json()
            
            # 保存API响应到文件
            with open('api_response_座位.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ API请求成功，响应已保存到 api_response_座位.json")
            
            # 分析响应数据结构
            analyze_api_response(data)
            
            return data
        else:
            print(f"❌ API请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 请求过程中出错: {e}")
        return None

def analyze_api_response(data):
    """分析API响应数据结构"""
    print(f"\n🔍 分析API响应数据结构:")
    print("=" * 60)
    
    # 检查响应基本结构
    if 'ret' in data:
        print(f"📊 响应状态: ret={data.get('ret')}, msg={data.get('msg', 'N/A')}")
    
    # 获取座位数据
    hall_data = data.get('data', {})
    room_seat = hall_data.get('room_seat', [])
    
    print(f"🏛️ 影厅信息:")
    print(f"  影厅编号: {hall_data.get('hall_no', 'N/A')}")
    print(f"  影厅名称: {hall_data.get('hall_name', 'N/A')}")
    print(f"  区域数量: {len(room_seat)}")
    
    # 分析座位数据
    total_seats = 0
    seat_samples = []
    
    for area_index, area in enumerate(room_seat):
        area_name = area.get('area_name', '未知区域')
        seats_data = area.get('seats', [])
        
        print(f"\n📍 区域 {area_index + 1}: {area_name}")
        print(f"  区域编号: {area.get('area_no', 'N/A')}")
        print(f"  区域价格: {area.get('area_price', 'N/A')}元")
        print(f"  座位数据类型: {type(seats_data)}")
        
        if isinstance(seats_data, dict):
            # 字典格式：按行组织
            print(f"  座位行数: {len(seats_data)}")
            
            for row_key, row_data in seats_data.items():
                seat_details = row_data.get('detail', [])
                print(f"    第{row_key}行: {len(seat_details)}个座位")
                
                for seat in seat_details:
                    total_seats += 1
                    if len(seat_samples) < 10:  # 收集前10个座位样本
                        seat_samples.append(seat)
                        
        elif isinstance(seats_data, list):
            # 列表格式：直接包含座位
            print(f"  座位数量: {len(seats_data)}")
            total_seats += len(seats_data)
            
            for seat in seats_data[:10]:  # 收集前10个座位样本
                seat_samples.append(seat)
    
    print(f"\n📊 座位统计:")
    print(f"  总座位数: {total_seats}")
    print(f"  样本数量: {len(seat_samples)}")
    
    # 分析座位样本
    if seat_samples:
        analyze_seat_samples(seat_samples)

def analyze_seat_samples(seat_samples):
    """分析座位样本数据"""
    print(f"\n🔬 座位样本数据分析:")
    print("=" * 60)
    
    # 分析前5个座位的详细结构
    for i, seat in enumerate(seat_samples[:5], 1):
        print(f"\n🪑 座位样本 {i}:")
        for key, value in seat.items():
            print(f"  {key}: {value}")
    
    # 统计字段出现频率
    field_stats = {}
    for seat in seat_samples:
        for key in seat.keys():
            field_stats[key] = field_stats.get(key, 0) + 1
    
    print(f"\n📈 字段统计 (基于{len(seat_samples)}个样本):")
    for field, count in sorted(field_stats.items()):
        print(f"  {field}: 出现{count}次 ({count/len(seat_samples)*100:.1f}%)")
    
    # 分析特定字段的值分布
    analyze_field_distribution(seat_samples)

def analyze_field_distribution(seat_samples):
    """分析字段值分布"""
    print(f"\n📊 关键字段值分布分析:")
    print("=" * 60)
    
    # 分析type字段
    type_values = [seat.get('type') for seat in seat_samples if 'type' in seat]
    if type_values:
        type_stats = {}
        for val in type_values:
            type_stats[val] = type_stats.get(val, 0) + 1
        print(f"🎭 type字段分布:")
        for val, count in sorted(type_stats.items()):
            print(f"  type={val}: {count}个座位")
    
    # 分析status字段
    status_values = [seat.get('status') for seat in seat_samples if 'status' in seat]
    if status_values:
        status_stats = {}
        for val in status_values:
            status_stats[val] = status_stats.get(val, 0) + 1
        print(f"📊 status字段分布:")
        for val, count in sorted(status_stats.items()):
            print(f"  status={val}: {count}个座位")
    
    # 分析row/col vs x/y的关系
    print(f"\n🔢 row/col vs x/y 关系分析:")
    for i, seat in enumerate(seat_samples[:3], 1):
        row = seat.get('row', 'N/A')
        col = seat.get('col', 'N/A') 
        x = seat.get('x', 'N/A')
        y = seat.get('y', 'N/A')
        seat_no = seat.get('seat_no', 'N/A')
        
        print(f"  座位{i} ({seat_no}): row={row}, col={col}, x={x}, y={y}")

def compare_with_existing_file():
    """与现有的座位.json文件进行对比"""
    print(f"\n🔄 与现有座位.json文件对比:")
    print("=" * 60)
    
    if os.path.exists('座位.json'):
        try:
            with open('座位.json', 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            
            print(f"✅ 成功加载现有座位.json文件")
            
            # 简单对比数据结构
            if os.path.exists('api_response_座位.json'):
                with open('api_response_座位.json', 'r', encoding='utf-8') as f:
                    new_data = json.load(f)
                
                print(f"📊 数据对比:")
                print(f"  现有文件大小: {len(json.dumps(existing_data))} 字符")
                print(f"  新API响应大小: {len(json.dumps(new_data))} 字符")
                
                # 对比基本结构
                existing_keys = set(existing_data.keys()) if isinstance(existing_data, dict) else set()
                new_keys = set(new_data.keys()) if isinstance(new_data, dict) else set()
                
                if existing_keys and new_keys:
                    common_keys = existing_keys & new_keys
                    only_existing = existing_keys - new_keys
                    only_new = new_keys - existing_keys
                    
                    print(f"  共同字段: {list(common_keys)}")
                    if only_existing:
                        print(f"  仅现有文件有: {list(only_existing)}")
                    if only_new:
                        print(f"  仅新响应有: {list(only_new)}")
            
        except Exception as e:
            print(f"❌ 读取现有文件失败: {e}")
    else:
        print(f"⚠️ 未找到现有的座位.json文件")

def verify_seat_structure_analysis():
    """验证座位数据结构分析"""
    print(f"\n✅ 验证座位数据结构分析:")
    print("=" * 60)
    
    analysis_points = [
        "1. seat_no: 座位唯一标识符",
        "2. row: 系统内部的逻辑排数", 
        "3. col: 系统内部的逻辑列数",
        "4. y: 物理排数（对应实际影厅的排数）",
        "5. x: 物理列数（对应实际影厅的列数）",
        "6. type: 座位类型（1或2表示情侣座）",
        "7. status: 座位状态（暂时跳过详细分析）"
    ]
    
    print("📋 需要验证的分析点:")
    for point in analysis_points:
        print(f"  {point}")
    
    print(f"\n💡 验证方法:")
    print(f"  1. 检查API响应中的实际字段名称和值")
    print(f"  2. 分析row/col与x/y的数值关系")
    print(f"  3. 观察type字段的值分布")
    print(f"  4. 对比不同座位的坐标系统")

def main():
    """主函数"""
    print("🎯 沃美影院座位图API测试与数据结构验证")
    print("=" * 80)
    
    # 测试API
    api_data = test_womei_seat_api()
    
    # 对比现有文件
    compare_with_existing_file()
    
    # 验证分析
    verify_seat_structure_analysis()
    
    print(f"\n🎉 测试完成！")
    print(f"📁 生成的文件:")
    print(f"  - api_response_座位.json: 最新的API响应数据")
    print(f"\n🔍 下一步:")
    print(f"  1. 查看生成的JSON文件")
    print(f"  2. 对比分析座位字段的实际含义")
    print(f"  3. 验证row/col vs x/y的关系")
    print(f"  4. 确认type字段的情侣座标识")

if __name__ == "__main__":
    main()
