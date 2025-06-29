#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查券码可用性
验证券码是否在当前账户下可用
"""

import requests
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_valid_headers(token):
    """获取有效的请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Content-Type': 'application/x-www-form-urlencoded',
        'x-channel-id': '40000',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'token': token,
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }

def check_voucher_list(token, target_voucher_code):
    """检查券列表"""
    print(f"🎫 检查券列表")
    print("=" * 80)
    
    headers = get_valid_headers(token)
    # 🔧 修复：使用正确的影院ID
    url = "https://ct.womovie.cn/ticket/wmyc/cinema/400303/user/voucher/list/"
    
    try:
        response = requests.get(url, headers=headers, timeout=30, verify=False)
        
        print(f"📤 请求URL: {url}")
        print(f"📥 HTTP状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📊 API响应: ret={result.get('ret')}, sub={result.get('sub')}")
            
            if result.get('ret') == 0:
                data = result.get('data', {})

                # 处理不同的数据格式
                if isinstance(data, list):
                    # 如果data是列表，可能是直接的券列表
                    unused_vouchers = data
                    used_vouchers = []
                    disabled_vouchers = []
                elif isinstance(data, dict):
                    unused_vouchers = data.get('unused', [])
                    used_vouchers = data.get('used', [])
                    disabled_vouchers = data.get('disabled', [])
                else:
                    unused_vouchers = []
                    used_vouchers = []
                    disabled_vouchers = []
                
                print(f"\n📋 券统计:")
                print(f"   未使用券: {len(unused_vouchers)} 张")
                print(f"   已使用券: {len(used_vouchers)} 张")
                print(f"   已禁用券: {len(disabled_vouchers)} 张")
                
                # 查找目标券码
                target_found = False
                all_vouchers = unused_vouchers + used_vouchers + disabled_vouchers
                
                print(f"\n🔍 查找目标券码: {target_voucher_code}")
                
                for voucher in all_vouchers:
                    voucher_code = voucher.get('voucher_code', '')
                    if voucher_code == target_voucher_code:
                        target_found = True
                        voucher_name = voucher.get('voucher_name', 'N/A')
                        expire_time = voucher.get('expire_time_string', 'N/A')
                        
                        # 判断券状态
                        if voucher in unused_vouchers:
                            status = "✅ 未使用 (可用)"
                        elif voucher in used_vouchers:
                            status = "❌ 已使用"
                        else:
                            status = "❌ 已禁用"
                        
                        print(f"   ✅ 找到目标券码!")
                        print(f"   券名称: {voucher_name}")
                        print(f"   有效期: {expire_time}")
                        print(f"   状态: {status}")
                        
                        return True, status
                
                if not target_found:
                    print(f"   ❌ 未找到目标券码: {target_voucher_code}")
                    
                    # 显示前几张券作为参考
                    if unused_vouchers:
                        print(f"\n📝 可用券示例 (前3张):")
                        for i, voucher in enumerate(unused_vouchers[:3], 1):
                            code = voucher.get('voucher_code', 'N/A')
                            name = voucher.get('voucher_name', 'N/A')
                            print(f"   {i}. {code} - {name}")
                    
                    return False, "券码不存在"
            else:
                error_msg = result.get('msg', '未知错误')
                print(f"   ❌ API失败: {error_msg}")
                return False, f"API错误: {error_msg}"
        else:
            print(f"   ❌ HTTP失败: {response.status_code}")
            return False, f"HTTP错误: {response.status_code}"
            
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False, f"请求异常: {e}"

def main():
    """主函数"""
    print("🎬 券码可用性检查")
    print("🎯 验证券码是否在当前账户下可用")
    print("⏰ 开始时间:", "15:07:30")
    print("=" * 80)
    
    # 配置
    token = "bd871543a2419bb6c61ba1868ba5bf1dd"
    target_voucher_code = "GZJY01003062558469"  # 真实curl中的券码
    
    print(f"📋 检查配置:")
    print(f"   Token: {token[:20]}...")
    print(f"   目标券码: {target_voucher_code}")
    
    # 检查券列表
    found, status = check_voucher_list(token, target_voucher_code)
    
    print(f"\n📊 最终结果")
    print("=" * 80)
    if found:
        print(f"✅ 券码存在: {target_voucher_code}")
        print(f"📋 状态: {status}")
        
        if "可用" in status:
            print(f"💡 建议: 券码可用，问题可能在API参数或业务规则")
        else:
            print(f"💡 建议: 券码不可用，需要使用其他券码")
    else:
        print(f"❌ 券码不存在: {target_voucher_code}")
        print(f"💡 建议: 使用账户下的可用券码进行测试")

if __name__ == "__main__":
    main()
