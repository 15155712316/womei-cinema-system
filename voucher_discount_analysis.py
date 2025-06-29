#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券抵扣效果分析
对比HAR文件与当前结果，分析券抵扣未生效的原因
"""

import sys
import os
import json
import requests
import urllib3
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def analyze_current_voucher_response():
    """分析当前券绑定响应"""
    print("🔍 当前券绑定响应分析")
    print("=" * 80)
    
    # 当前测试结果数据
    current_response = {
        "ret": 0,
        "sub": 0,
        "msg": "successfully",
        "data": {
            "order_id": "250625184410001025",
            "order_total_price": 62.9,
            "order_payment_price": 62.9,  # 🚨 问题：支付金额未变化
            "ticket_total_price": 62.9,
            "voucher_use": {},  # 🚨 问题：券使用信息为空
            "voucher_discounts": [],  # 🚨 问题：券抵扣信息为空
            "marketing_discounts": [],
            "coupon_discounts": []
        }
    }
    
    print("📊 当前响应关键字段分析:")
    print(f"   API调用状态: ret={current_response['ret']}, sub={current_response['sub']} ✅")
    print(f"   订单总价: {current_response['data']['order_total_price']}元")
    print(f"   支付金额: {current_response['data']['order_payment_price']}元 🚨")
    print(f"   券使用信息: {current_response['data']['voucher_use']} 🚨")
    print(f"   券抵扣信息: {current_response['data']['voucher_discounts']} 🚨")
    
    print(f"\n🚨 发现的问题:")
    print(f"   1. 支付金额未变化 - 应该从62.9元变为0元")
    print(f"   2. voucher_use为空 - 应该包含券使用详情")
    print(f"   3. voucher_discounts为空 - 应该包含抵扣金额")
    print(f"   4. API返回成功但券抵扣未生效")
    
    return current_response

def analyze_har_success_cases():
    """分析HAR文件中的成功案例"""
    print(f"\n📋 HAR文件成功案例分析")
    print("=" * 80)
    
    # 基于之前HAR文件分析的成功案例数据
    expected_success_response = {
        "ret": 0,
        "sub": 0,
        "msg": "successfully",
        "data": {
            "order_id": "订单ID",
            "order_total_price": 62.9,  # 原始总价
            "order_payment_price": 0.0,  # 🎯 应该变为0（完全抵扣）
            "ticket_total_price": 62.9,
            "voucher_use": {  # 🎯 应该包含券使用信息
                "use_codes": ["GZJY01003062558469"],
                "use_total_price": 62.9,
                "use_detail": [
                    {
                        "voucher_code": "GZJY01003062558469",
                        "discount_amount": 62.9
                    }
                ]
            },
            "voucher_discounts": [  # 🎯 应该包含抵扣详情
                {
                    "voucher_code": "GZJY01003062558469",
                    "discount_amount": 62.9,
                    "voucher_name": "广州佳意--电影票"
                }
            ]
        }
    }
    
    print("📊 HAR文件中的预期成功响应:")
    print(f"   API调用状态: ret=0, sub=0 ✅")
    print(f"   订单总价: 62.9元 (保持不变)")
    print(f"   支付金额: 0元 🎯 (完全抵扣)")
    print(f"   券使用信息: 包含券码和抵扣金额 🎯")
    print(f"   券抵扣信息: 包含详细抵扣记录 🎯")
    
    return expected_success_response

def compare_responses():
    """对比当前响应与预期响应"""
    print(f"\n📊 响应对比分析")
    print("=" * 80)
    
    current = analyze_current_voucher_response()
    expected = analyze_har_success_cases()
    
    # 创建对比表
    comparison_fields = [
        ("API状态", "ret/sub", "0/0", "0/0", "✅ 一致"),
        ("订单总价", "order_total_price", "62.9", "62.9", "✅ 一致"),
        ("支付金额", "order_payment_price", "62.9", "0.0", "❌ 不一致"),
        ("券使用信息", "voucher_use", "{}", "包含券码和金额", "❌ 不一致"),
        ("券抵扣信息", "voucher_discounts", "[]", "包含抵扣详情", "❌ 不一致"),
        ("抵扣效果", "总价-支付", "0", "62.9", "❌ 未生效")
    ]
    
    print("📋 详细对比表:")
    print(f"{'字段':<12} {'当前结果':<20} {'预期结果':<20} {'状态':<15}")
    print("-" * 80)
    
    for field_name, field_key, current_val, expected_val, status in comparison_fields:
        print(f"{field_name:<12} {current_val:<20} {expected_val:<20} {status:<15}")
    
    print(f"\n🎯 关键差异总结:")
    print(f"   1. 支付金额未变化: 当前62.9元 vs 预期0元")
    print(f"   2. 券使用信息缺失: 当前空对象 vs 预期包含券详情")
    print(f"   3. 券抵扣信息缺失: 当前空数组 vs 预期包含抵扣记录")
    print(f"   4. 抵扣效果未生效: 券绑定成功但未实际抵扣")

def analyze_voucher_parameters():
    """分析券绑定参数问题"""
    print(f"\n🔍 券绑定参数分析")
    print("=" * 80)
    
    current_params = {
        "card_id": "",
        "discount_id": "0",
        "discount_type": "VOUCHER",  # 已修复
        "limit_cards": "[]",
        "order_id": "250625184410001025",
        "pay_type": "WECHAT",
        "rewards": "[]",
        "ticket_pack_goods": " ",
        "use_limit_cards": "N",
        "use_rewards": "Y",
        "voucher_code": "GZJY01003062558469",
        "voucher_code_type": "VGC_T"
    }
    
    print("📋 当前使用的参数:")
    for key, value in current_params.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 可能的参数问题:")
    
    parameter_issues = [
        {
            "参数": "voucher_code_type",
            "当前值": "VGC_T",
            "问题": "可能需要使用不同的券类型",
            "建议": "尝试VGC_P或其他类型"
        },
        {
            "参数": "discount_id",
            "当前值": "0",
            "问题": "可能需要指定具体的折扣ID",
            "建议": "从券列表API获取正确的discount_id"
        },
        {
            "参数": "use_rewards",
            "当前值": "Y",
            "问题": "可能与券使用冲突",
            "建议": "尝试设置为N"
        },
        {
            "参数": "pay_type",
            "当前值": "WECHAT",
            "问题": "可能需要特定的支付类型",
            "建议": "尝试其他支付类型或留空"
        }
    ]
    
    for issue in parameter_issues:
        print(f"\n📋 {issue['参数']}:")
        print(f"   当前值: {issue['当前值']}")
        print(f"   可能问题: {issue['问题']}")
        print(f"   建议: {issue['建议']}")

def analyze_voucher_code_type():
    """分析券码类型问题"""
    print(f"\n🎫 券码类型深度分析")
    print("=" * 80)
    
    voucher_info = {
        "voucher_code": "GZJY01003062558469",
        "voucher_name": "广州佳意--电影票",
        "voucher_desc": "本兑换券不可与优惠活动同时使用，且不支持退票",
        "expire_time_string": "2026年1月1日 00:00"
    }
    
    print("📋 券码详细信息:")
    for key, value in voucher_info.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 券码类型分析:")
    print(f"   券码格式: GZJY + 17位数字")
    print(f"   券名称: 广州佳意--电影票")
    print(f"   券描述: 兑换券，不可与优惠活动同时使用")
    print(f"   券性质: 🎯 这是兑换券，应该完全抵扣订单金额")
    
    print(f"\n💡 关键发现:")
    print(f"   1. 这是兑换券，不是折扣券")
    print(f"   2. 兑换券应该完全抵扣订单金额")
    print(f"   3. 当前API调用成功但抵扣未生效")
    print(f"   4. 可能需要特定的参数来激活兑换券功能")

def suggest_debugging_approaches():
    """建议调试方法"""
    print(f"\n💡 调试方法建议")
    print("=" * 80)
    
    approaches = [
        {
            "方法": "1. 参数对比测试",
            "描述": "测试不同的参数组合",
            "步骤": [
                "尝试voucher_code_type='VGC_P'",
                "尝试use_rewards='N'",
                "尝试不同的discount_id值",
                "尝试空的pay_type"
            ]
        },
        {
            "方法": "2. HAR文件参数复制",
            "描述": "完全复制HAR文件中成功案例的参数",
            "步骤": [
                "查找HAR文件中券绑定成功的请求",
                "复制所有请求参数",
                "确保参数格式完全一致",
                "测试复制后的参数效果"
            ]
        },
        {
            "方法": "3. 券信息详细查询",
            "描述": "获取券码的详细使用规则",
            "步骤": [
                "调用券详情API获取更多信息",
                "确认券码的具体使用条件",
                "检查券码是否需要特殊激活",
                "验证券码的抵扣规则"
            ]
        },
        {
            "方法": "4. 分步调试",
            "描述": "逐步验证券绑定过程",
            "步骤": [
                "先确认券码在可用列表中",
                "再确认订单状态支持券绑定",
                "然后测试券绑定API",
                "最后验证抵扣效果"
            ]
        }
    ]
    
    for approach in approaches:
        print(f"\n{approach['方法']}")
        print(f"   描述: {approach['描述']}")
        print(f"   步骤:")
        for step in approach['步骤']:
            print(f"     - {step}")

def generate_analysis_summary():
    """生成分析总结"""
    print(f"\n📋 券抵扣问题分析总结")
    print("=" * 80)
    
    print(f"🎯 问题确认:")
    print(f"   ✅ API调用成功 (ret=0, sub=0)")
    print(f"   ❌ 券抵扣未生效 (支付金额未变化)")
    print(f"   ❌ 券使用信息缺失 (voucher_use为空)")
    print(f"   ❌ 券抵扣信息缺失 (voucher_discounts为空)")
    
    print(f"\n🔍 可能原因:")
    print(f"   1. 参数问题: voucher_code_type或其他参数不正确")
    print(f"   2. 业务逻辑: 券码需要特定的激活条件")
    print(f"   3. 系统状态: 券码系统可能有特殊要求")
    print(f"   4. 接口差异: 当前接口可能不是完整的券绑定接口")
    
    print(f"\n💡 下一步行动:")
    print(f"   1. 🔍 查看HAR文件中的成功案例参数")
    print(f"   2. 🧪 测试不同的参数组合")
    print(f"   3. 📋 获取券码的详细使用规则")
    print(f"   4. 🔄 可能需要调用额外的激活接口")
    
    print(f"\n🎯 预期结果:")
    print(f"   修复后应该看到:")
    print(f"   - order_payment_price: 0元")
    print(f"   - voucher_use: 包含券码和抵扣金额")
    print(f"   - voucher_discounts: 包含抵扣详情")
    print(f"   - 用户看到券抵扣生效")

def main():
    """主函数"""
    print("🎬 券抵扣效果分析")
    print("🎯 对比HAR文件与当前结果，找出券抵扣未生效的原因")
    print("=" * 80)
    
    # 1. 分析当前响应
    current_response = analyze_current_voucher_response()
    
    # 2. 分析HAR成功案例
    expected_response = analyze_har_success_cases()
    
    # 3. 对比响应差异
    compare_responses()
    
    # 4. 分析参数问题
    analyze_voucher_parameters()
    
    # 5. 分析券码类型
    analyze_voucher_code_type()
    
    # 6. 建议调试方法
    suggest_debugging_approaches()
    
    # 7. 生成总结
    generate_analysis_summary()
    
    return {
        'current_response': current_response,
        'expected_response': expected_response,
        'analysis_complete': True
    }

if __name__ == "__main__":
    main()
