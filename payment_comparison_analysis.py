#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
支付方式对比分析 - 纯会员卡支付 vs 混合支付
"""

import json
import base64
import urllib.parse
from datetime import datetime

def decode_base64_content(content):
    """解码base64内容"""
    try:
        decoded = base64.b64decode(content).decode('utf-8')
        # 移除BOM标记
        if decoded.startswith('\ufeff'):
            decoded = decoded[1:]
        try:
            return json.loads(decoded)
        except:
            return decoded
    except:
        return content

def parse_member_card_payment_har():
    """解析纯会员卡支付HAR文件"""
    print("🔍 解析纯会员卡支付HAR文件")
    print("="*80)
    
    # 从HAR文件中提取的关键数据
    
    # 1. createOrder 响应 (base64解码)
    create_order_response = "77u/eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTYyMTBcdTUyOWYiLCJyZXN1bHREYXRhIjp7Im9yZGVyVHlwZSI6IjAiLCJvcmRlcm5vIjoiMjAyNTA1MzExODQ2MDgwODk5NjMxIiwib3JkZXJUaW1lT3V0Ijo0MjAwMDAsInNlYXRzIjpbeyJ0aWNrZXRQcmljZSI6IjM1LjAwIiwic3RyYXRlZ3lQcmljZSI6IjMwLjAwIiwiZXZlbnRQcmljZSI6MCwic2VhdENvbElkIjoiMTEiLCJzZWF0Um93Ijo4LCJscyI6IiIsInNlYXRDb2wiOjgsImluZGV4IjoxNiwic2VhdFJvd0lkIjo4LCJzZWN0aW9uSWQiOiIxMTExMSIsImNvbEluZGV4Ijo1LCJyb3dJbmRleCI6Nywic2VhdEluZm8iOiI4XHU2MzkyOFx1NWVhNyIsInNlYXRObyI6IjAwMDAwMDAxMTExMS02LTgifSx7InRpY2tldFByaWNlIjoiMzUuMDAiLCJzdHJhdGVneVByaWNlIjoiMzAuMDAiLCJldmVudFByaWNlIjowLCJzZWF0Q29sSWQiOiIxMSIsInNlYXRSb3ciOjgsImxzIjoiIiwic2VhdENvbCI6OSwiaW5kZXgiOjE3LCJzZWF0Um93SWQiOjgsInNlY3Rpb25JZCI6IjExMTExIiwiY29sSW5kZXgiOjQsInJvd0luZGV4Ijo3LCJzZWF0SW5mbyI6IjhcdTYzOTI5XHU1ZWE3Iiwic2VhdE5vIjoiMDAwMDAwMDExMTExLTUtOCJ9XX19"
    
    # 2. getUnpaidOrderDetail 响应
    order_detail_response = "77u/eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTYyMTBcdTUyOWYiLCJyZXN1bHREYXRhIjp7Im9yZGVyVHlwZSI6MSwiZmlsbUxhbmciOiJcdTgyZjFcdThiZWQiLCJnb29kc0Ftb3VudCI6bnVsbCwiZ29vZHNGYXZvclByaWNlIjowLCJnb29kcyI6W10sInRpY2tldEZhdm9yUHJpY2UiOjAsIm9yZGVyUHJpY2UiOiI3MDAwIiwidGlja2V0Rmlyc3RQcmljZSI6IjcwMDAiLCJ0aWNrZXRQcmljZSI6IjcwMDAiLCJmYXZvclByaWNlIjowLCJ0aWNrZXRjb3VudCI6IjIiLCJTZXJ2aWNlQ2hhcmdlIjowLCJwYXlBbW91bnQiOiI3MDAwIiwib25seVRpY2tldEFtb3VudCI6IjcwMDAiLCJtZW1fdG90YWxwcmljZSI6IjYwMDAiLCJtZW1wcmljZSI6IjMwMDAiLCJ0b3RhbHByaWNlIjoiNzAwMCIsInByaWNlIjoiMzUwMCIsImJhbGFuY2UiOm51bGwsIm9yZGVyVGltZU91dCI6NDIwMDAwLCJmaWxtQ291bnQiOiIyXHU1ZjIwIiwidGhlYXRlclBob25lIjoiIiwiY2luZW1hTmFtZSI6Ilx1NTM0ZVx1NTkwZlx1NGYxOFx1NTJhMFx1ODM1Zlx1NTkyN1x1OTBmZFx1ODM1ZiIsInNlYXRJbmZvIjoiOFx1NjM5MjhcdTVlYTcsOFx1NjM5MjlcdTVlYTciLCJjaW5lbWFTdGF0dXMiOjEsIm9yZGVybm8iOiIyMDI1MDUzMTE4NDYwODA4OTk2MzEiLCJzaG93VGltZSI6IjIwMjUtMDUtMzEgIDIwOjI1IiwiZ29vZHNUZXJyYWNlQW1vdW50IjowLCJvcmRlck1vYmlsZSI6IjE1MTU1NzEyMzE2IiwiZ29vZHNQcmljZSI6MCwiY2luZW1haWQiOiI2MTAxMTU3MSIsImZpbG1OYW1lIjoiXHU2NjFmXHU5NjQ1XHU1YjlkXHU4ZDFkXHU1M2YyXHU4ZmVhXHU1OTQ3IiwiZmlsbVNpZ2h0IjoiMkQiLCJoYWxsTmFtZSI6IjFcdTUzZjdcdTZmYzBcdTUxNDlcdTUzODUiLCJlbmFibGVfbWVtcGFzc3dvcmQiOiIxIiwibWVtUGF5T05MWSI6IjAiLCJmaWxtX2ltZyI6Imh0dHBzOlwvXC96Y3pjMC5oeHlzd2hjbS5jblwvV2ViVGlja2V0XC9maWxtaW1nc1wvMzAzNDU3NDMuanBnIiwiZmVhdHVyZW5vIjoiODc2NDI1MDUyOUQ0ODJaNiJ9fQ=="
    
    # 3. getMemberInfo 响应
    member_info_response = "eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTYyMTBcdTUyOWYiLCJyZXN1bHREYXRhIjp7ImNhcmRubyI6IjE1MTU1NzEyMzE2IiwibW9iaWxlIjoiMTUxNTU3MTIzMTYiLCJtZW1iZXJJZCI6IjE1MTU1NzEyMzE2IiwiY2FyZHR5cGUiOiIwIiwiY2FyZGNpbmVtYWlkIjoiMzVmZWM4MjU5ZTc0IiwiYmFsYW5jZSI6NDMzfX0="
    
    # 4. getCouponByOrder 响应
    coupon_response = "eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTYyMTBcdTUyOWYiLCJyZXN1bHREYXRhIjp7InRvdGFsQ291bnQiOjAsInZvdWNoZXJzIjpbXSwiaGFzTmV4dCI6ZmFsc2UsImN1cnJlbnRQYWdlIjoxLCJtYXhVc2VDb3Vwb24iOiIyIn19"
    
    # 5. memcardPay 请求
    memcard_request = "dG90YWxwcmljZT02MDAwJm1lbWJlcmluZm89JTdCJTIyY2FyZG5vJTIyJTNBJTIyMTUxNTU3MTIzMTYlMjIlMkMlMjJtb2JpbGUlMjIlM0ElMjIxNTE1NTcxMjMxNiUyMiUyQyUyMm1lbWJlcklkJTIyJTNBJTIyMTUxNTU3MTIzMTYlMjIlMkMlMjJjYXJkdHlwZSUyMiUzQSUyMjAlMjIlMkMlMjJjYXJkY2luZW1haWQlMjIlM0ElMjIzNWZlYzgyNTllNzQlMjIlMkMlMjJiYWxhbmNlJTIyJTNBNDMzJTdEJm1lbXBhc3M9NzEwMjU0Jm9yZGVybm89MjAyNTA1MzExODQ2MDgwODk5NjMxJmNvdXBvbmNvZGVzPSZwcmljZT0zMDAwJmRpc2NvdW50cHJpY2U9MCZmaWxtbmFtZT0lRTYlOTglOUYlRTklOTklODUlRTUlQUUlOUQlRTglQjQlOUQlRTUlOEYlQjIlRTglQkYlQUElRTUlQTUlODcmZmVhdHVyZW5vPTg3NjQyNTA1MjlENDgyWjYmdGlja2V0Y291bnQ9MiZjaW5lbWFuYW1lPSVFNSU4RCU4RSVFNSVBNCU4RiVFNCVCQyU5OCVFNSU4QSVBMCVFOCU4RCU5RiVFNSVBNCVBNyVFOSU4MyVCRCVFOCU4RCU5RiZncm91cGlkPSZjaW5lbWFpZD0zNWZlYzgyNTllNzQmY2FyZG5vPSZ1c2VyaWQ9MTUxNTU3MTIzMTYmb3BlbmlkPW9BT0NwN1ZiZWVvcU1NNHlDOGUyaTNHM2x4STgmQ1ZlcnNpb249My45LjEyJk9TPVdpbmRvd3MmdG9rZW49M2EzMGI5ZTk4MDg5MjcxNCZzb3VyY2U9Mg=="
    
    # 6. memcardPay 响应
    memcard_response = "77u/eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTRmMWFcdTU0NThcdTUzNjFcdTY1MmZcdTRlZDhcdTYyMTBcdTUyOWZcdWZmMDEiLCJyZXN1bHREYXRhIjpudWxsfQ=="
    
    # 解析数据
    analysis = {
        'payment_type': '纯会员卡支付',
        'order_info': {},
        'member_info': {},
        'coupon_info': {},
        'payment_request': {},
        'payment_response': {}
    }
    
    # 解析订单详情
    order_data = decode_base64_content(order_detail_response)
    if isinstance(order_data, dict):
        result_data = order_data.get('resultData', {})
        analysis['order_info'] = {
            'orderno': result_data.get('orderno'),
            'totalprice': result_data.get('totalprice'),  # 原价
            'mem_totalprice': result_data.get('mem_totalprice'),  # 会员价
            'memprice': result_data.get('memprice'),  # 单张会员价
            'price': result_data.get('price'),  # 单张原价
            'enable_mempassword': result_data.get('enable_mempassword'),
            'filmName': result_data.get('filmName'),
            'seatInfo': result_data.get('seatInfo')
        }
    
    # 解析会员信息
    member_data = decode_base64_content(member_info_response)
    if isinstance(member_data, dict):
        result_data = member_data.get('resultData', {})
        analysis['member_info'] = {
            'cardno': result_data.get('cardno'),
            'balance': result_data.get('balance'),
            'cardtype': result_data.get('cardtype'),
            'cardcinemaid': result_data.get('cardcinemaid')
        }
    
    # 解析券信息
    coupon_data = decode_base64_content(coupon_response)
    if isinstance(coupon_data, dict):
        result_data = coupon_data.get('resultData', {})
        analysis['coupon_info'] = {
            'totalCount': result_data.get('totalCount'),
            'vouchers': result_data.get('vouchers', []),
            'maxUseCoupon': result_data.get('maxUseCoupon')
        }
    
    # 解析支付请求
    payment_req_data = decode_base64_content(memcard_request)
    if isinstance(payment_req_data, str):
        parsed_data = urllib.parse.parse_qs(payment_req_data)
        analysis['payment_request'] = {
            'totalprice': parsed_data.get('totalprice', [''])[0],
            'price': parsed_data.get('price', [''])[0],
            'couponcodes': parsed_data.get('couponcodes', [''])[0],
            'discountprice': parsed_data.get('discountprice', [''])[0],
            'orderno': parsed_data.get('orderno', [''])[0],
            'memberinfo': urllib.parse.unquote(parsed_data.get('memberinfo', [''])[0]) if parsed_data.get('memberinfo') else ''
        }
    
    # 解析支付响应
    payment_resp_data = decode_base64_content(memcard_response)
    if isinstance(payment_resp_data, dict):
        analysis['payment_response'] = {
            'resultCode': payment_resp_data.get('resultCode'),
            'resultDesc': payment_resp_data.get('resultDesc'),
            'resultData': payment_resp_data.get('resultData')
        }
    
    return analysis

def compare_payment_methods():
    """对比两种支付方式"""
    print("\n🔍 支付方式对比分析")
    print("="*80)
    
    # 获取纯会员卡支付分析
    member_card_analysis = parse_member_card_payment_har()
    
    # 混合支付数据（从之前的分析中获取）
    mixed_payment_analysis = {
        'payment_type': '混合支付（券+会员卡）',
        'order_info': {
            'orderno': '202505301058196041368',
            'totalprice': '7000',  # 原价 70.00元
            'mem_totalprice': '6000',  # 会员价 60.00元
        },
        'coupon_info': {
            'totalCount': 1,
            'couponcodes': '83839924607',
            'discountprice': '1510',  # 券抵扣金额(基于原价)
            'discountmemprice': '1010'  # 券抵扣金额(基于会员价)
        },
        'payment_request': {
            'totalprice': '4990',  # 券抵扣后的会员支付金额
            'price': '3000',  # 实际从会员卡扣除的金额
            'couponcodes': '83839924607',
            'discountprice': '1010',  # 券抵扣金额
            'orderno': '202505301058196041368'
        }
    }
    
    print("\n📊 详细对比分析:")
    print("-" * 80)
    
    # 1. API调用流程对比
    print("\n1. API调用流程对比:")
    print("纯会员卡支付:")
    print("  1. createOrder - 创建订单")
    print("  2. getMiniToken - 获取token")
    print("  3. getUnpaidOrderDetail - 获取订单详情")
    print("  4. getCouponByOrder - 获取券列表（无券）")
    print("  5. getMemberInfo - 获取会员信息")
    print("  6. getComments - 获取评论")
    print("  7. memcardPay - 会员卡支付")
    print("  ❌ 无 ordercouponPrepay 调用")
    
    print("\n混合支付:")
    print("  1. createOrder - 创建订单")
    print("  2. getMiniToken - 获取token")
    print("  3. getUnpaidOrderDetail - 获取订单详情")
    print("  4. getCouponByOrder - 获取券列表（多次）")
    print("  5. getMemberInfo - 获取会员信息（多次）")
    print("  6. getComments - 获取评论")
    print("  ✅ 7. ordercouponPrepay - 券预支付验证")
    print("  8. memcardPay - 会员卡支付")
    
    # 2. memcardPay 参数对比
    print("\n2. memcardPay 接口参数对比:")
    print(f"{'参数名':<20} {'纯会员卡支付':<25} {'混合支付':<25} {'差异说明'}")
    print("-" * 90)
    
    member_req = member_card_analysis['payment_request']
    mixed_req = mixed_payment_analysis['payment_request']
    
    print(f"{'totalprice':<20} {member_req.get('totalprice', 'N/A'):<25} {mixed_req.get('totalprice', 'N/A'):<25} 支付总价")
    print(f"{'price':<20} {member_req.get('price', 'N/A'):<25} {mixed_req.get('price', 'N/A'):<25} 实际扣款金额")
    print(f"{'couponcodes':<20} {member_req.get('couponcodes', '空'):<25} {mixed_req.get('couponcodes', 'N/A'):<25} 券码")
    print(f"{'discountprice':<20} {member_req.get('discountprice', 'N/A'):<25} {mixed_req.get('discountprice', 'N/A'):<25} 券抵扣金额")
    
    # 3. 价格计算对比
    print("\n3. 价格计算机制对比:")
    
    print("\n纯会员卡支付:")
    member_order = member_card_analysis['order_info']
    print(f"  原价: {member_order.get('totalprice', 'N/A')} 分 = {int(member_order.get('totalprice', 0))/100:.2f} 元")
    print(f"  会员价: {member_order.get('mem_totalprice', 'N/A')} 分 = {int(member_order.get('mem_totalprice', 0))/100:.2f} 元")
    print(f"  支付总价: {member_req.get('totalprice', 'N/A')} 分 = {int(member_req.get('totalprice', 0))/100:.2f} 元")
    print(f"  实际扣款: {member_req.get('price', 'N/A')} 分 = {int(member_req.get('price', 0))/100:.2f} 元")
    print(f"  券抵扣: {member_req.get('discountprice', 'N/A')} 分 = {int(member_req.get('discountprice', 0))/100:.2f} 元")
    
    print("\n混合支付:")
    mixed_order = mixed_payment_analysis['order_info']
    mixed_coupon = mixed_payment_analysis['coupon_info']
    print(f"  原价: {mixed_order.get('totalprice', 'N/A')} 分 = {int(mixed_order.get('totalprice', 0))/100:.2f} 元")
    print(f"  会员价: {mixed_order.get('mem_totalprice', 'N/A')} 分 = {int(mixed_order.get('mem_totalprice', 0))/100:.2f} 元")
    print(f"  券抵扣(会员价): {mixed_coupon.get('discountmemprice', 'N/A')} 分 = {int(mixed_coupon.get('discountmemprice', 0))/100:.2f} 元")
    print(f"  券抵扣后会员价: {mixed_req.get('totalprice', 'N/A')} 分 = {int(mixed_req.get('totalprice', 0))/100:.2f} 元")
    print(f"  实际扣款: {mixed_req.get('price', 'N/A')} 分 = {int(mixed_req.get('price', 0))/100:.2f} 元")
    
    return member_card_analysis, mixed_payment_analysis

if __name__ == "__main__":
    try:
        member_analysis, mixed_analysis = compare_payment_methods()
        print(f"\n✅ 对比分析完成")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
