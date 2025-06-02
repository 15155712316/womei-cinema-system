#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码显示功能调试测试脚本
用于测试二维码API和显示功能
"""

import sys
import os
from services.order_api import get_order_qrcode_api

def test_qrcode_api():
    """测试二维码API"""
    print("=" * 60)
    print("🧪 开始测试二维码API功能")
    print("=" * 60)

    # 测试参数
    test_order_no = "2025060239828060"  # 使用您提供的订单号
    test_cinema_id = "35fec8259e74"  # 华夏优加荟大都荟的影院ID

    # 🔧 添加账号认证信息
    test_account = {
        "userid": "14700283316",
        "openid": "oAOCp7fvQZ57uCG-5H0XZyUSbO-4",
        "token": "a53201ca598cfcc8",
        "cinemaid": "35fec8259e74"
    }

    print(f"📋 测试参数:")
    print(f"   订单号: {test_order_no}")
    print(f"   影院ID: {test_cinema_id}")
    print(f"   账号ID: {test_account['userid']}")
    print(f"   OpenID: {test_account['openid'][:10]}...")
    print(f"   Token: {test_account['token'][:10]}...")
    print()

    # 测试1：不带认证信息
    print("🚀 测试1: 调用二维码API（无认证）...")
    qr_result_no_auth = get_order_qrcode_api(test_order_no, test_cinema_id)

    if qr_result_no_auth:
        print(f"✅ 无认证API调用成功: {len(qr_result_no_auth)} bytes")
        # 保存无认证版本
        with open(f"qrcode_no_auth_{test_order_no}.png", 'wb') as f:
            f.write(qr_result_no_auth)
        print(f"💾 无认证二维码已保存")
    else:
        print(f"❌ 无认证API调用失败")

    print()

    # 测试2：带认证信息
    print("🚀 测试2: 调用二维码API（带认证）...")
    qr_result = get_order_qrcode_api(test_order_no, test_cinema_id, test_account)
    
    if qr_result:
        print(f"✅ API调用成功!")
        print(f"📊 返回数据大小: {len(qr_result)} bytes")
        
        # 分析数据格式
        print(f"🔍 数据格式分析:")
        if qr_result.startswith(b'\x89PNG'):
            print(f"   ✅ 检测到PNG图片格式")
            data_format = "PNG"
        elif qr_result.startswith(b'\xff\xd8\xff'):
            print(f"   ✅ 检测到JPEG图片格式")
            data_format = "JPEG"
        elif qr_result.startswith(b'GIF'):
            print(f"   ✅ 检测到GIF图片格式")
            data_format = "GIF"
        elif qr_result.startswith(b'<'):
            print(f"   ⚠️ 响应似乎是HTML/XML文本，不是图片")
            data_format = "HTML/XML"
        else:
            print(f"   ⚠️ 未知的数据格式")
            data_format = "UNKNOWN"
        
        # 显示数据预览
        print(f"📄 数据预览:")
        try:
            # 尝试解码为文本
            content_preview = qr_result[:100].decode('utf-8', errors='ignore')
            print(f"   文本预览（前100字符）: {repr(content_preview)}")
        except:
            # 如果是二进制数据，显示十六进制
            content_preview = qr_result[:50].hex()
            print(f"   十六进制预览（前50字节）: {content_preview}")
        
        # 如果是图片格式，尝试保存到文件
        if data_format in ["PNG", "JPEG", "GIF"]:
            try:
                filename = f"test_qrcode_{test_order_no}.{data_format.lower()}"
                with open(filename, 'wb') as f:
                    f.write(qr_result)
                print(f"💾 二维码图片已保存到: {filename}")
            except Exception as e:
                print(f"❌ 保存图片失败: {e}")
        
        return True, qr_result, data_format
    else:
        print(f"❌ API调用失败，返回空数据")
        return False, None, None

def test_qrcode_display():
    """测试二维码显示功能"""
    print("\n" + "=" * 60)
    print("🖼️ 开始测试二维码显示功能")
    print("=" * 60)
    
    # 先测试API
    success, qr_data, data_format = test_qrcode_api()
    
    if not success:
        print("❌ 无法测试显示功能，因为API调用失败")
        return
    
    # 测试事件总线
    try:
        from utils.signals import event_bus
        
        print("🔗 测试事件总线连接...")
        
        # 创建测试数据
        test_qr_data = {
            'order_no': "202506021611295648804",
            'qr_bytes': qr_data,
            'data_size': len(qr_data),
            'data_format': data_format
        }
        
        print(f"📤 准备发送测试数据:")
        print(f"   订单号: {test_qr_data['order_no']}")
        print(f"   数据大小: {test_qr_data['data_size']} bytes")
        print(f"   数据格式: {test_qr_data['data_format']}")
        
        # 发送事件（注意：这需要主窗口正在运行才能看到效果）
        print("📡 发送二维码显示事件...")
        event_bus.show_qrcode.emit(test_qr_data)
        
        print("✅ 事件发送成功！")
        print("💡 如果主窗口正在运行，应该能看到二维码显示在取票码区域")
        
    except Exception as e:
        print(f"❌ 事件总线测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 二维码功能调试测试")
    print("=" * 60)
    
    # 运行测试
    test_qrcode_display()
    
    print("\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)
