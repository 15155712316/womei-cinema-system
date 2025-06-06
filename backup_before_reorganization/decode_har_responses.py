#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接解码HAR文件中的关键响应内容
"""

import json
import base64

# 需要密码的影城 - 订单详情响应
password_required_order_detail = "77u/eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTYyMTBcdTUyOWYiLCJyZXN1bHREYXRhIjp7Im9yZGVyVHlwZSI6MSwiZmlsbUxhbmciOiJcdTU2ZmRcdThiZWQiLCJnb29kc0Ftb3VudCI6bnVsbCwiZ29vZHNGYXZvclByaWNlIjowLCJnb29kcyI6W10sInRpY2tldEZhdm9yUHJpY2UiOjAsIm9yZGVyUHJpY2UiOiIzMzkwIiwidGlja2V0Rmlyc3RQcmljZSI6IjMzOTAiLCJ0aWNrZXRQcmljZSI6IjMzOTAiLCJmYXZvclByaWNlIjowLCJ0aWNrZXRjb3VudCI6IjEiLCJTZXJ2aWNlQ2hhcmdlIjowLCJwYXlBbW91bnQiOiIzMzkwIiwib25seVRpY2tldEFtb3VudCI6IjMzOTAiLCJtZW1fdG90YWxwcmljZSI6IjI1MDAiLCJtZW1wcmljZSI6IjI1MDAiLCJ0b3RhbHByaWNlIjoiMzM5MCIsInByaWNlIjoiMzM5MCIsImJhbGFuY2UiOm51bGwsIm9yZGVyVGltZU91dCI6NDIwMDAwLCJmaWxtQ291bnQiOiIxXHU1ZjIwIiwidGhlYXRlclBob25lIjoiIiwiY2luZW1hTmFtZSI6Ilx1NTM0ZVx1NTkwZlx1NGYxOFx1NTJhMFx1ODM1Zlx1NTkyN1x1OTBmZFx1ODM1ZiIsInNlYXRJbmZvIjoiNlx1NjM5MjRcdTVlYTciLCJjaW5lbWFTdGF0dXMiOjEsIm9yZGVybm8iOiIyMDI1MDYwNDE2MjIyODYwNzIzODUiLCJzaG93VGltZSI6IjIwMjUtMDYtMDYgIDEyOjAwIiwiZ29vZHNUZXJyYWNlQW1vdW50IjowLCJvcmRlck1vYmlsZSI6IjE1MTU1NzEyMzE2IiwiZ29vZHNQcmljZSI6MCwiY2luZW1haWQiOiI2MTAxMTU3MSIsImZpbG1OYW1lIjoiXHU5OGNlXHU1NDczXHU1ZmViXHU5OTEwXHU4ZjY2IiwiZmlsbVNpZ2h0IjoiMkQiLCJoYWxsTmFtZSI6IjFcdTUzZjdcdTZmYzBcdTUxNDlcdTUzODUiLCJlbmFibGVfbWVtcGFzc3dvcmQiOiIxIiwibWVtUGF5T05MWSI6IjAiLCJmaWxtX2ltZyI6Imh0dHBzOlwvXC96Y3pjMC5oeHlzd2hjbS5jblwvV2ViVGlja2V0XC9hc3NldHNcL2ltZ1wvbW9iaWxlXC9maWxtLmpwZyIsImZlYXR1cmVubyI6Ijg3NjQyNTA2MDM2RDJSMDAifX0="

# 不需要密码的影城 - 订单详情响应
no_password_order_detail = "77u/eyJyZXN1bHRDb2RlIjoiMCIsInJlc3VsdERlc2MiOiJcdTYyMTBcdTUyOWYiLCJyZXN1bHREYXRhIjp7Im9yZGVyVHlwZSI6MSwiZmlsbUxhbmciOiJcdTdjYTRcdThiZWQiLCJnb29kc0Ftb3VudCI6bnVsbCwiZ29vZHNGYXZvclByaWNlIjowLCJnb29kcyI6W10sInRpY2tldEZhdm9yUHJpY2UiOjAsIm9yZGVyUHJpY2UiOiI0MjAwIiwidGlja2V0Rmlyc3RQcmljZSI6IjQyMDAiLCJ0aWNrZXRQcmljZSI6IjQyMDAiLCJmYXZvclByaWNlIjowLCJ0aWNrZXRjb3VudCI6IjEiLCJTZXJ2aWNlQ2hhcmdlIjowLCJwYXlBbW91bnQiOiI0MjAwIiwib25seVRpY2tldEFtb3VudCI6IjQyMDAiLCJtZW1fdG90YWxwcmljZSI6IjQwMDAiLCJtZW1wcmljZSI6IjQwMDAiLCJ0b3RhbHByaWNlIjoiNDIwMCIsInByaWNlIjoiNDIwMCIsImJhbGFuY2UiOm51bGwsIm9yZGVyVGltZU91dCI6NDIwMDAwLCJmaWxtQ291bnQiOiIxXHU1ZjIwIiwidGhlYXRlclBob25lIjoiIiwiY2luZW1hTmFtZSI6Ilx1NmRmMVx1NTczM1x1NGUwN1x1NTNjYlx1NWY3MVx1NTdjZUlCQ01hbGxcdTVlOTciLCJzZWF0SW5mbyI6IjVcdTYzOTI2XHU1ZWE3IiwiY2luZW1hU3RhdHVzIjoxLCJvcmRlcm5vIjoiMjAyNTA2MDQxNjIzMTMwOTUxOTE3Iiwic2hvd1RpbWUiOiIyMDI1LTA2LTA0ICAyMjowMCIsImdvb2RzVGVycmFjZUFtb3VudCI6MCwib3JkZXJNb2JpbGUiOiIxNTE1NTcxMjMxNiIsImdvb2RzUHJpY2UiOjAsImNpbmVtYWlkIjoiNDQwMTI5OTEiLCJmaWxtTmFtZSI6Ilx1NzljMVx1NWJiNlx1NGZhNlx1NjNhMiIsImZpbG1TaWdodCI6IjJEIiwiaGFsbE5hbWUiOiIzXHU1M2Y3XHU2ZmMwXHU1MTQ5XHU1Mzg1IiwiZW5hYmxlX21lbXBhc3N3b3JkIjoiMCIsIm1lbVBheU9OTFkiOiIwIiwiZmlsbV9pbWciOiJodHRwczpcL1wvdHQ3LmNpdHlmaWxtcy5jblwvV2ViVGlja2V0XC9maWxtaW1nc1wvMzY1NjM0MDYuanBnIiwiZmVhdHVyZW5vIjoiODI2MzI1MDYwNDYyMDRSOCJ9fQ=="

def decode_and_analyze(base64_content, title):
    """解码并分析base64内容"""
    print(f"\n{'='*80}")
    print(f"📊 {title}")
    print(f"{'='*80}")
    
    try:
        # 去掉BOM标记
        if base64_content.startswith('77u/'):
            base64_content = base64_content[4:]
        
        decoded = base64.b64decode(base64_content).decode('utf-8')
        data = json.loads(decoded)
        
        result_data = data.get('resultData', {})
        
        print("🔍 关键字段分析:")
        print(f"  📋 订单号: {result_data.get('orderno', 'N/A')}")
        print(f"  🎬 影院名称: {result_data.get('cinemaName', 'N/A')}")
        print(f"  💰 订单价格: {result_data.get('orderPrice', 'N/A')} 分")
        print(f"  💰 支付金额: {result_data.get('payAmount', 'N/A')} 分")
        print(f"  👤 会员总价: {result_data.get('mem_totalprice', 'N/A')} 分")
        print(f"  👤 会员价格: {result_data.get('memprice', 'N/A')} 分")
        
        print(f"\n🔐 密码策略关键字段:")
        enable_mempassword = result_data.get('enable_mempassword', 'N/A')
        mem_pay_only = result_data.get('memPayONLY', 'N/A')
        
        print(f"  🔑 enable_mempassword: {enable_mempassword}")
        print(f"  🔒 memPayONLY: {mem_pay_only}")
        
        if enable_mempassword == '1':
            print(f"  ✅ 需要会员卡密码")
        elif enable_mempassword == '0':
            print(f"  ❌ 不需要会员卡密码")
        else:
            print(f"  ❓ 密码策略未知")
        
        return result_data
        
    except Exception as e:
        print(f"❌ 解码失败: {e}")
        return None

def main():
    print("🔐 会员卡密码支付差异分析")
    print("基于HAR文件中的订单详情API响应")
    
    # 分析需要密码的影城
    password_data = decode_and_analyze(
        password_required_order_detail, 
        "需要密码的影城 (黑白影业 - www.heibaiyingye.cn)"
    )
    
    # 分析不需要密码的影城
    no_password_data = decode_and_analyze(
        no_password_order_detail, 
        "不需要密码的影城 (城市影院 - zcxzs7.cityfilms.cn)"
    )
    
    # 对比分析
    print(f"\n{'='*80}")
    print("📊 密码策略对比总结")
    print(f"{'='*80}")
    
    if password_data and no_password_data:
        print("\n🔍 关键差异:")
        print(f"  黑白影业 enable_mempassword: {password_data.get('enable_mempassword', 'N/A')}")
        print(f"  城市影院 enable_mempassword: {no_password_data.get('enable_mempassword', 'N/A')}")
        
        print(f"\n💡 判断逻辑:")
        print(f"  - enable_mempassword = '1' → 需要会员卡密码")
        print(f"  - enable_mempassword = '0' → 不需要会员卡密码")
        
        print(f"\n🎯 实现要点:")
        print(f"  1. 订单创建后调用 getUnpaidOrderDetail API")
        print(f"  2. 解析响应中的 enable_mempassword 字段")
        print(f"  3. 动态显示/隐藏密码输入框")
        print(f"  4. 支付时根据策略包含或排除密码参数")

if __name__ == "__main__":
    main()
