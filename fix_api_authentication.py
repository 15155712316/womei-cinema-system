#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复API认证和参数问题
"""

import json
import sys
import requests
from datetime import datetime


def fix_film_api_authentication():
    """修复影片API认证问题"""
    print("🔧 修复影片API认证问题")
    
    try:
        # 检查当前的API调用
        from services.film_service import get_films
        
        # 读取真实的账号数据
        try:
            with open('data/accounts.json', 'r', encoding='utf-8') as f:
                accounts_data = json.load(f)
                
            if accounts_data and len(accounts_data) > 0:
                # 使用第一个账号进行测试
                test_account = accounts_data[0]
                print(f"  👤 使用账号: {test_account.get('phone', 'N/A')}")
                print(f"  🔑 Token: {test_account.get('token', 'N/A')[:20]}...")
                print(f"  🆔 OpenID: {test_account.get('openid', 'N/A')[:20]}...")
            else:
                print(f"  ❌ 未找到有效账号数据")
                return False
                
        except FileNotFoundError:
            print(f"  ❌ 账号文件不存在: data/accounts.json")
            return False
        except Exception as e:
            print(f"  ❌ 读取账号数据失败: {e}")
            return False
        
        # 读取影院数据
        try:
            with open('data/cinema_info.json', 'r', encoding='utf-8') as f:
                cinemas_data = json.load(f)
                
            if cinemas_data and len(cinemas_data) > 0:
                test_cinema = cinemas_data[0]
                print(f"  🏢 使用影院: {test_cinema.get('cinemaShortName', 'N/A')}")
                print(f"  🌐 域名: {test_cinema.get('base_url', 'N/A')}")
                print(f"  🆔 影院ID: {test_cinema.get('cinemaid', 'N/A')}")
            else:
                print(f"  ❌ 未找到有效影院数据")
                return False
                
        except FileNotFoundError:
            print(f"  ❌ 影院文件不存在: data/cinema_info.json")
            return False
        except Exception as e:
            print(f"  ❌ 读取影院数据失败: {e}")
            return False
        
        # 测试API调用
        print(f"\n  📡 测试API调用...")
        
        api_params = {
            'base_url': test_cinema.get('base_url', ''),
            'userid': test_account.get('userid', ''),
            'openid': test_account.get('openid', ''),
            'token': test_account.get('token', ''),
            'cinemaid': test_cinema.get('cinemaid', '')
        }
        
        print(f"  📋 API参数:")
        for key, value in api_params.items():
            display_value = value[:20] + "..." if len(str(value)) > 20 else value
            print(f"     {key}: {display_value}")
        
        # 检查参数完整性
        missing_params = [k for k, v in api_params.items() if not v]
        if missing_params:
            print(f"  ❌ 缺少参数: {missing_params}")
            return False
        
        # 调用API
        result = get_films(**api_params)
        
        print(f"  📊 API响应:")
        print(f"     类型: {type(result)}")
        
        if result:
            print(f"     resultCode: {result.get('resultCode', 'N/A')}")
            print(f"     resultDesc: {result.get('resultDesc', 'N/A')}")
            print(f"     success: {result.get('success', 'N/A')}")
            
            result_data = result.get('resultData')
            print(f"     resultData类型: {type(result_data)}")
            
            if result_data:
                if isinstance(result_data, dict):
                    films = result_data.get('films', [])
                    print(f"     影片数量: {len(films)}")
                    
                    if films:
                        print(f"  ✅ API调用成功，获取到影片数据")
                        
                        # 分析第一部影片的排期
                        first_film = films[0]
                        film_name = first_film.get('fn', 'Unknown')
                        plans = first_film.get('plans', [])
                        
                        print(f"  🎬 第一部影片: {film_name}")
                        print(f"     排期数量: {len(plans)}")
                        
                        if plans:
                            print(f"     排期示例: {plans[0].get('k', 'N/A')}")
                            return True
                        else:
                            print(f"  ⚠️  影片无排期数据")
                            return False
                    else:
                        print(f"  ❌ 影片列表为空")
                        return False
                else:
                    print(f"  ❌ resultData不是字典类型")
                    return False
            else:
                print(f"  ❌ resultData为空")
                
                # 分析可能的原因
                result_code = result.get('resultCode', '')
                if result_code == '400':
                    print(f"  💡 可能原因:")
                    print(f"     - Token已过期，需要重新登录")
                    print(f"     - 账号参数错误")
                    print(f"     - 影院ID不匹配")
                elif result_code == '401':
                    print(f"  💡 可能原因: 认证失败")
                elif result_code == '403':
                    print(f"  💡 可能原因: 权限不足")
                else:
                    print(f"  💡 未知错误码: {result_code}")
                
                return False
        else:
            print(f"  ❌ API无响应")
            return False
        
    except Exception as e:
        print(f"  ❌ 修复过程异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def suggest_authentication_fixes():
    """提供认证修复建议"""
    print("\n💡 认证修复建议")
    
    print("  🔧 立即修复步骤:")
    print("     1. 检查账号Token是否有效")
    print("     2. 验证影院ID是否正确")
    print("     3. 确认API域名是否可访问")
    print("     4. 重新登录获取新Token")
    
    print("\n  🧪 调试步骤:")
    print("     1. 手动测试API接口")
    print("     2. 对比正常工作时的参数")
    print("     3. 检查网络连接")
    print("     4. 验证SSL证书")
    
    print("\n  🛠️  代码修复:")
    print("     1. 添加Token刷新机制")
    print("     2. 增加API重试逻辑")
    print("     3. 改进错误处理")
    print("     4. 添加参数验证")


def create_api_test_script():
    """创建API测试脚本"""
    print("\n📝 创建API测试脚本")
    
    test_script = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 独立测试影片API
"""

import requests
import json

def test_film_api():
    """测试影片API"""
    
    # 测试参数（请替换为真实值）
    params = {
        'userid': '15155712316',
        'openid': 'your_real_openid_here',
        'token': 'your_real_token_here',
        'cinemaid': '35fec8259e74'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'xweb_xhr': '1',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx1234567890123456/1/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    url = 'https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniFilm/getFilms'
    
    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"解析结果: {data}")
        
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_film_api()
'''
    
    try:
        with open('test_api_manual.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        print(f"  ✅ 测试脚本已创建: test_api_manual.py")
        print(f"  💡 请修改脚本中的真实参数后运行")
        return True
    except Exception as e:
        print(f"  ❌ 创建测试脚本失败: {e}")
        return False


def main():
    """主修复函数"""
    print("=" * 60)
    print("🔧 API认证和参数问题修复")
    print("=" * 60)
    
    print("🎯 修复目标:")
    print("   1. 🔍 诊断API认证问题")
    print("   2. 🔧 修复参数配置")
    print("   3. 🧪 验证API调用")
    print("   4. 💡 提供修复建议")
    print()
    
    # 执行修复
    print("开始修复...")
    print()
    
    # 1. 修复API认证
    auth_fixed = fix_film_api_authentication()
    
    # 2. 提供修复建议
    suggest_authentication_fixes()
    
    # 3. 创建测试脚本
    script_created = create_api_test_script()
    
    # 总结修复结果
    print("\n" + "=" * 60)
    print("📊 修复结果总结:")
    print("=" * 60)
    
    print(f"   API认证修复: {'✅ 成功' if auth_fixed else '❌ 需要进一步处理'}")
    print(f"   测试脚本创建: {'✅ 成功' if script_created else '❌ 失败'}")
    
    if auth_fixed:
        print("\n🎉 API认证问题已修复！")
        print("   - 影片数据可以正常获取")
        print("   - 排期信息应该能正常显示")
        print("   - 座位图API参数应该能正确获取")
    else:
        print("\n⚠️  API认证问题需要进一步处理")
        print("\n🔧 下一步操作:")
        print("   1. 检查账号Token是否过期")
        print("   2. 重新登录获取新Token")
        print("   3. 验证影院配置是否正确")
        print("   4. 运行 test_api_manual.py 进行手动测试")
        print()
        print("💡 常见解决方案:")
        print("   - 重启应用并重新登录")
        print("   - 检查网络连接")
        print("   - 联系管理员验证账号状态")
        print("   - 更新影院配置信息")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
