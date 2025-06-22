#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
券API调试工具
用于捕获和分析实际运行时的API响应格式
"""

import requests
import json
import time
from datetime import datetime

def debug_voucher_api():
    """调试券API响应格式"""
    print("🔍 券API调试工具启动")
    print("=" * 60)
    
    # API参数
    url = 'https://ct.womovie.cn/ticket/wmyc/cinema/400028/user/vouchers_page'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 MicroMessenger/6.8.0(0x16080000) NetType/WIFI MiniProgramEnv/Mac MacWechat/WMPF MacWechat/3.8.10(0x13080a10) XWEB/1227',
        'x-channel-id': '40000',
        'wechat-referrer-appid': 'wx4bb9342b9d97d53c',
        'tenant-short': 'wmyc',
        'client-version': '4.0',
        'content-type': 'multipart/form-data',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'wechat-referrer-info': '{"appId":"wx4bb9342b9d97d53c"}',
        'token': 'c33d6b500b34c87b71ac8fad4cfb6769',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    
    # 测试多次请求，看是否有格式变化
    for i in range(5):
        print(f"\n🔄 第 {i+1} 次请求 ({datetime.now().strftime('%H:%M:%S')})")
        print("-" * 40)
        
        try:
            params = {'voucher_type': 'VGC_T', 'page_index': 1}
            response = requests.get(url, params=params, headers=headers, timeout=30)
            
            print(f"HTTP状态码: {response.status_code}")
            print(f"响应头Content-Type: {response.headers.get('content-type', '未知')}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # 基本结构分析
                    print(f"响应根级别类型: {type(data)}")
                    if isinstance(data, dict):
                        print(f"根级别keys: {list(data.keys())}")
                        print(f"ret: {data.get('ret')}")
                        print(f"msg: {data.get('msg')}")
                        
                        # 重点分析data字段
                        data_field = data.get('data')
                        print(f"data字段类型: {type(data_field)}")
                        
                        if isinstance(data_field, dict):
                            print(f"✅ data是字典格式")
                            print(f"data keys: {list(data_field.keys())}")
                            
                            if 'result' in data_field:
                                result = data_field['result']
                                print(f"result类型: {type(result)}")
                                print(f"result长度: {len(result) if isinstance(result, list) else '不是列表'}")
                                
                        elif isinstance(data_field, list):
                            print(f"⚠️ data是列表格式！")
                            print(f"列表长度: {len(data_field)}")
                            if data_field:
                                first_item = data_field[0]
                                print(f"第一个元素类型: {type(first_item)}")
                                if isinstance(first_item, dict):
                                    print(f"第一个元素keys: {list(first_item.keys())}")
                        else:
                            print(f"❌ data字段格式异常: {type(data_field)}")
                            print(f"data内容: {str(data_field)[:100]}...")
                    
                    else:
                        print(f"❌ 响应不是字典格式: {type(data)}")
                        print(f"响应内容: {str(data)[:200]}...")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"响应文本: {response.text[:200]}...")
                    
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                print(f"响应文本: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ 请求异常: {e}")
        
        # 间隔1秒
        if i < 4:
            time.sleep(1)
    
    print("\n" + "=" * 60)
    print("🔍 调试完成")

def test_voucher_service_with_debug():
    """使用调试模式测试券服务"""
    print("\n🧪 使用调试模式测试券服务")
    print("=" * 60)
    
    try:
        from services.voucher_service import get_voucher_service
        import logging
        
        # 设置详细调试日志
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        voucher_service = get_voucher_service()
        cinema_id = '400028'
        token = 'c33d6b500b34c87b71ac8fad4cfb6769'
        
        print(f"📞 调用券服务...")
        vouchers, page_info = voucher_service.get_all_vouchers(cinema_id, token, only_valid=True)
        
        print(f"✅ 券服务调用成功")
        print(f"券数量: {len(vouchers)}")
        print(f"页面信息: {page_info}")
        
        if vouchers:
            first_voucher = vouchers[0]
            print(f"第一张券: {first_voucher.voucher_name}")
            print(f"券状态: {first_voucher.is_valid()}")
        
    except Exception as e:
        print(f"❌ 券服务测试失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("🚀 券API调试工具")
    print("用于分析API响应格式变化和调试数据类型问题")
    print()
    
    # 1. 调试API响应格式
    debug_voucher_api()
    
    # 2. 测试券服务
    test_voucher_service_with_debug()

if __name__ == "__main__":
    main()
