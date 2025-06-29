#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券绑定服务差异分析报告
对比当前实现与目标curl命令的详细差异
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def analyze_headers_differences():
    """分析请求头差异"""
    print("📋 请求头（Headers）差异分析")
    print("=" * 80)
    
    # 目标curl命令的请求头
    target_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': 'ae6dbb683e74a71fa5e2c8cca3b5fc72',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    
    # 当前实现的请求头模板
    current_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13907',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
        # 注意：token是动态添加的
    }
    
    print("📊 请求头对比表:")
    print(f"{'Header名称':<20} {'目标值':<15} {'当前值':<15} {'状态':<10} {'重要性':<10}")
    print("-" * 90)
    
    # 检查所有目标头
    all_headers = set(target_headers.keys()) | set(current_headers.keys())
    
    differences = []
    
    for header in sorted(all_headers):
        target_val = target_headers.get(header, '缺失')
        current_val = current_headers.get(header, '缺失')
        
        if header == 'token':
            # token是动态添加的
            status = "✅ 动态"
            importance = "高"
            current_val = "动态添加"
        elif target_val == current_val:
            status = "✅ 一致"
            importance = "正常"
        elif target_val == '缺失':
            status = "⚠️ 多余"
            importance = "低"
            differences.append({
                'type': 'extra_header',
                'header': header,
                'current_value': current_val,
                'impact': '可能无影响'
            })
        elif current_val == '缺失':
            status = "❌ 缺失"
            importance = "高"
            differences.append({
                'type': 'missing_header',
                'header': header,
                'target_value': target_val,
                'impact': '可能影响请求'
            })
        else:
            status = "❌ 不同"
            importance = "中"
            differences.append({
                'type': 'different_header',
                'header': header,
                'target_value': target_val,
                'current_value': current_val,
                'impact': '需要检查'
            })
        
        # 截断长值用于显示
        target_display = target_val[:12] + "..." if len(str(target_val)) > 15 else str(target_val)
        current_display = current_val[:12] + "..." if len(str(current_val)) > 15 else str(current_val)
        
        print(f"{header:<20} {target_display:<15} {current_display:<15} {status:<10} {importance:<10}")
    
    return differences

def analyze_data_parameters_differences():
    """分析POST数据参数差异"""
    print(f"\n📋 POST数据参数差异分析")
    print("=" * 80)
    
    # 目标curl命令的POST数据参数
    target_data = {
        'order_id': '250625205610001295',
        'discount_id': '0',
        'discount_type': 'TP_VOUCHER',
        'card_id': '',
        'pay_type': 'WECHAT',
        'rewards': '[]',
        'use_rewards': 'Y',
        'use_limit_cards': 'N',
        'limit_cards': '[]',
        'voucher_code': 'GZJY01003062558469',
        'voucher_code_type': 'VGC_T',
        'ticket_pack_goods': ' '
    }
    
    # 当前实现的POST数据参数
    current_data = {
        'card_id': '',
        'discount_id': '0',
        'discount_type': 'TP_VOUCHER',
        'limit_cards': '[]',
        'order_id': 'order_id',  # 动态值
        'pay_type': 'WECHAT',
        'rewards': '[]',
        'ticket_pack_goods': ' ',
        'use_limit_cards': 'N',
        'use_rewards': 'Y',
        'voucher_code': 'voucher_code',  # 动态值
        'voucher_code_type': 'voucher_type'  # 动态值
    }
    
    print("📊 POST参数对比表:")
    print(f"{'参数名称':<20} {'目标值':<20} {'当前值':<20} {'状态':<10} {'重要性':<10}")
    print("-" * 100)
    
    # 检查所有参数
    all_params = set(target_data.keys()) | set(current_data.keys())
    
    differences = []
    
    for param in sorted(all_params):
        target_val = target_data.get(param, '缺失')
        current_val = current_data.get(param, '缺失')
        
        # 处理动态值
        if param in ['order_id', 'voucher_code', 'voucher_code_type']:
            if current_val in ['order_id', 'voucher_code', 'voucher_type']:
                status = "✅ 动态"
                importance = "高"
                current_val = "动态值"
            else:
                status = "❌ 缺失"
                importance = "高"
        elif target_val == current_val:
            status = "✅ 一致"
            importance = "正常"
        elif target_val == '缺失':
            status = "⚠️ 多余"
            importance = "低"
            differences.append({
                'type': 'extra_param',
                'param': param,
                'current_value': current_val,
                'impact': '可能无影响'
            })
        elif current_val == '缺失':
            status = "❌ 缺失"
            importance = "高"
            differences.append({
                'type': 'missing_param',
                'param': param,
                'target_value': target_val,
                'impact': '可能影响功能'
            })
        else:
            status = "❌ 不同"
            importance = "中"
            differences.append({
                'type': 'different_param',
                'param': param,
                'target_value': target_val,
                'current_value': current_val,
                'impact': '需要检查'
            })
        
        print(f"{param:<20} {str(target_val):<20} {str(current_val):<20} {status:<10} {importance:<10}")
    
    return differences

def analyze_parameter_order():
    """分析参数顺序差异"""
    print(f"\n📋 参数顺序分析")
    print("=" * 80)
    
    # 目标参数顺序（基于curl命令）
    target_order = [
        'order_id',
        'discount_id', 
        'discount_type',
        'card_id',
        'pay_type',
        'rewards',
        'use_rewards',
        'use_limit_cards',
        'limit_cards',
        'voucher_code',
        'voucher_code_type',
        'ticket_pack_goods'
    ]
    
    # 当前参数顺序
    current_order = [
        'card_id',
        'discount_id',
        'discount_type',
        'limit_cards',
        'order_id',
        'pay_type',
        'rewards',
        'ticket_pack_goods',
        'use_limit_cards',
        'use_rewards',
        'voucher_code',
        'voucher_code_type'
    ]
    
    print("📊 参数顺序对比:")
    print(f"{'位置':<5} {'目标顺序':<20} {'当前顺序':<20} {'状态':<10}")
    print("-" * 70)
    
    max_len = max(len(target_order), len(current_order))
    order_differences = []
    
    for i in range(max_len):
        target_param = target_order[i] if i < len(target_order) else '无'
        current_param = current_order[i] if i < len(current_order) else '无'
        
        if target_param == current_param:
            status = "✅ 一致"
        else:
            status = "❌ 不同"
            order_differences.append({
                'position': i + 1,
                'target': target_param,
                'current': current_param
            })
        
        print(f"{i+1:<5} {target_param:<20} {current_param:<20} {status:<10}")
    
    print(f"\n📋 参数顺序影响分析:")
    if order_differences:
        print(f"   发现 {len(order_differences)} 个位置差异")
        print(f"   影响程度: 低 (HTTP POST参数顺序通常不影响功能)")
        print(f"   建议: 可选择性调整以保持一致性")
    else:
        print(f"   参数顺序完全一致 ✅")
    
    return order_differences

def analyze_simplification_opportunities():
    """分析简化机会"""
    print(f"\n📋 简化机会分析")
    print("=" * 80)
    
    print("🔧 当前实现复杂度:")
    print("   1. 两步流程: 券价格计算 + 券绑定")
    print("   2. 错误处理: 多层次错误检查")
    print("   3. 数据处理: Unicode解码 + 数据提取")
    print("   4. 日志记录: 详细的调试信息")
    
    print(f"\n💡 简化建议:")
    
    simplifications = [
        {
            "项目": "移除券价格计算步骤",
            "当前": "调用 _calculate_voucher_price() 方法",
            "建议": "直接调用券绑定API",
            "影响": "减少API调用，提高性能",
            "风险": "低 (测试证明价格计算是可选的)"
        },
        {
            "项目": "简化参数构建",
            "当前": "字典形式构建参数",
            "建议": "保持当前方式",
            "影响": "无",
            "风险": "无"
        },
        {
            "项目": "保留错误处理",
            "当前": "详细的错误类型识别",
            "建议": "保持当前实现",
            "影响": "提供良好的用户体验",
            "风险": "无"
        },
        {
            "项目": "保留Unicode解码",
            "当前": "decode_unicode_message() 方法",
            "建议": "保持当前实现",
            "影响": "正确显示中文错误消息",
            "风险": "无"
        }
    ]
    
    for i, item in enumerate(simplifications, 1):
        print(f"\n{i}. {item['项目']}:")
        print(f"   当前实现: {item['当前']}")
        print(f"   建议修改: {item['建议']}")
        print(f"   预期影响: {item['影响']}")
        print(f"   风险评估: {item['风险']}")

def generate_modification_recommendations():
    """生成修改建议"""
    print(f"\n💡 修改建议总结")
    print("=" * 80)
    
    recommendations = [
        {
            "优先级": "高",
            "类型": "功能简化",
            "建议": "移除券价格计算步骤",
            "原因": "测试证明单接口模式有效",
            "实现": "删除 _calculate_voucher_price 调用"
        },
        {
            "优先级": "中",
            "类型": "参数顺序",
            "建议": "调整POST参数顺序",
            "原因": "与目标curl命令保持一致",
            "实现": "重新排列data字典的键顺序"
        },
        {
            "优先级": "低",
            "类型": "代码清理",
            "建议": "移除未使用的方法",
            "原因": "减少代码复杂度",
            "实现": "删除 _calculate_voucher_price 方法定义"
        },
        {
            "优先级": "保持",
            "类型": "错误处理",
            "建议": "保留当前错误处理逻辑",
            "原因": "提供良好的用户体验",
            "实现": "无需修改"
        },
        {
            "优先级": "保持",
            "类型": "Unicode解码",
            "建议": "保留Unicode消息解码",
            "原因": "正确显示中文错误消息",
            "实现": "无需修改"
        }
    ]
    
    print("📋 修改建议列表:")
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. 【{rec['优先级']}】{rec['建议']}")
        print(f"   类型: {rec['类型']}")
        print(f"   原因: {rec['原因']}")
        print(f"   实现: {rec['实现']}")

def generate_code_modification_plan():
    """生成代码修改计划"""
    print(f"\n🔧 代码修改计划")
    print("=" * 80)
    
    modifications = [
        {
            "文件": "services/womei_order_voucher_service.py",
            "方法": "bind_voucher_to_order",
            "修改": [
                "移除券价格计算调用",
                "简化流程为单步券绑定",
                "调整POST参数顺序",
                "保留错误处理逻辑"
            ]
        },
        {
            "文件": "services/womei_order_voucher_service.py", 
            "方法": "_calculate_voucher_price",
            "修改": [
                "删除整个方法定义",
                "移除相关导入和引用"
            ]
        }
    ]
    
    print("📋 具体修改计划:")
    for i, mod in enumerate(modifications, 1):
        print(f"\n{i}. 文件: {mod['文件']}")
        print(f"   方法: {mod['方法']}")
        print(f"   修改内容:")
        for change in mod['修改']:
            print(f"     - {change}")

def main():
    """主函数"""
    print("🎬 券绑定服务差异分析报告")
    print("🎯 对比当前实现与目标curl命令的详细差异")
    print("=" * 80)
    
    # 1. 分析请求头差异
    header_diffs = analyze_headers_differences()
    
    # 2. 分析POST参数差异
    param_diffs = analyze_data_parameters_differences()
    
    # 3. 分析参数顺序
    order_diffs = analyze_parameter_order()
    
    # 4. 分析简化机会
    analyze_simplification_opportunities()
    
    # 5. 生成修改建议
    generate_modification_recommendations()
    
    # 6. 生成代码修改计划
    generate_code_modification_plan()
    
    print(f"\n📋 差异分析总结")
    print("=" * 80)
    
    print(f"🔍 发现的差异:")
    print(f"   请求头差异: {len(header_diffs)} 项")
    print(f"   参数差异: {len(param_diffs)} 项")
    print(f"   顺序差异: {len(order_diffs)} 项")
    
    print(f"\n🎯 主要结论:")
    print(f"   1. 当前实现与目标curl命令基本一致")
    print(f"   2. 主要差异在于券价格计算步骤（可移除）")
    print(f"   3. 参数顺序有差异但不影响功能")
    print(f"   4. 错误处理和Unicode解码应保留")
    
    print(f"\n✅ 建议执行:")
    print(f"   1. 移除券价格计算步骤")
    print(f"   2. 简化为单接口模式")
    print(f"   3. 保留现有的错误处理")
    print(f"   4. 保持良好的用户体验")
    
    print(f"\n⏸️ 开发暂停")
    print(f"   等待进一步指示后执行代码修改")
    
    return {
        'header_differences': header_diffs,
        'parameter_differences': param_diffs,
        'order_differences': order_diffs,
        'ready_for_modification': True
    }

if __name__ == "__main__":
    main()
