#!/usr/bin/env python3
"""
调试版客户端 - 用于分析API请求和响应问题
"""

import requests
import hashlib
import platform
import uuid
import json

def get_machine_code():
    """获取机器码"""
    try:
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'machine': platform.machine(),
            'node': platform.node(),
        }
        
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                          for elements in range(0, 2*6, 2)][::-1])
            system_info['mac'] = mac
        except:
            pass
        
        info_str = json.dumps(system_info, sort_keys=True)
        machine_code = hashlib.md5(info_str.encode()).hexdigest()
        return machine_code[:16].upper()
    except:
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()[:16].upper()

def debug_login(phone):
    """调试登录请求"""
    base_url = "http://43.142.19.28:5000"
    machine_code = get_machine_code()
    
    print(f"🔍 调试信息:")
    print(f"   服务器地址: {base_url}")
    print(f"   手机号: {phone}")
    print(f"   机器码: {machine_code}")
    
    data = {
        "phone": phone,
        "machineCode": machine_code
    }
    
    print(f"   请求数据: {json.dumps(data, indent=2)}")
    
    try:
        print(f"\n📡 发送POST请求到: {base_url}/login")
        
        # 创建请求
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Debug-Client/1.0'
        }
        
        response = requests.post(
            f"{base_url}/login",
            json=data,
            headers=headers,
            timeout=10
        )
        
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应头: {dict(response.headers)}")
        print(f"📊 响应内容长度: {len(response.content)} bytes")
        
        # 打印原始响应内容
        print(f"\n📋 原始响应内容:")
        print(f"   类型: {type(response.content)}")
        print(f"   内容: {response.content}")
        
        # 尝试解析为文本
        try:
            text_content = response.text
            print(f"\n📋 文本内容:")
            print(f"   长度: {len(text_content)}")
            print(f"   内容: {repr(text_content)}")
        except Exception as e:
            print(f"❌ 无法解析为文本: {e}")
        
        # 尝试解析为JSON
        try:
            json_content = response.json()
            print(f"\n📋 JSON内容:")
            print(json.dumps(json_content, indent=2, ensure_ascii=False))
            return json_content
        except Exception as e:
            print(f"❌ JSON解析失败: {e}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {e}")
        return None

def test_api_endpoints():
    """测试各个API端点"""
    base_url = "http://43.142.19.28:5000"
    
    endpoints = [
        "/",
        "/health", 
        "/admin"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 测试端点: {endpoint}")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            print(f"   状态码: {response.status_code}")
            print(f"   内容类型: {response.headers.get('content-type', 'unknown')}")
            print(f"   内容长度: {len(response.content)}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    json_data = response.json()
                    print(f"   JSON: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
                except:
                    print(f"   JSON解析失败")
            else:
                # 只显示前100个字符
                preview = response.text[:100]
                print(f"   内容预览: {repr(preview)}")
                
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")

def main():
    print("🔧 API调试工具")
    print("=" * 50)
    
    # 测试各个端点
    test_api_endpoints()
    
    # 测试登录
    print(f"\n" + "=" * 50)
    print("🔐 测试登录功能")
    
    phone = "15155712316"  # 管理页面显示的已有用户
    result = debug_login(phone)
    
    if result:
        print(f"\n✅ 登录测试完成，返回数据: {json.dumps(result, indent=2, ensure_ascii=False)}")
    else:
        print(f"\n❌ 登录测试失败")

if __name__ == "__main__":
    main() 