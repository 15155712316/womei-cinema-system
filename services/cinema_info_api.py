import requests
import json
import urllib3
import time

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_cinema_info(base_url, cinemaid):
    """
    从指定域名获取影院信息
    
    Args:
        base_url (str): API域名
        cinemaid (str): 影院ID
        
    Returns:
        dict or None: 影院信息字典，失败返回None
    """
    # 请求URL和参数
    url = f"https://{base_url}/MiniTicket/index.php/MiniCommonSystem/getCinemaInfo"
    params = {
        'groupid': '',
        'cinemaid': cinemaid,
        'cardno': '',
        'userid': '',
        'openid': '',
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': '',
        'source': '2'
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive'
    }
    
    print(f"[影院信息API] 正在获取影院信息: {cinemaid}")
    print(f"[影院信息API] 请求URL: {url}")
    print(f"[影院信息API] 请求参数: {params}")
    
    try:
        # 发送请求
        response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        print(f"[影院信息API] 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"[影院信息API] 响应内容: {response.text}")
                
                # 分析响应
                result_code = data.get('resultCode')
                result_desc = data.get('resultDesc')
                result_data = data.get('resultData')
                success = data.get('success')
                
                print(f"[影院信息API] 详细分析:")
                print(f"[影院信息API]   - resultCode: {result_code} (类型: {type(result_code)})")
                print(f"[影院信息API]   - resultDesc: {result_desc}")
                print(f"[影院信息API]   - resultData: {result_data} (类型: {type(result_data)})")
                print(f"[影院信息API]   - success: {success}")
                
                # 检查成功条件
                if result_code == "0" and result_data is not None:
                    print(f"[影院信息API] ✓ 成功获取影院信息")
                    return result_data
                elif result_code == "400" and result_desc == "success":
                    print(f"[影院信息API] 特殊情况：影院ID可能不存在 (resultCode=400, resultDesc=success)")
                    print(f"[影院信息API] 这通常表示影院ID格式正确但该影院不存在于当前域名")
                    return None
                else:
                    print(f"[影院信息API] ✗ API返回错误: resultCode={result_code}, resultDesc={result_desc}")
                    return None
                    
            except ValueError as e:
                print(f"[影院信息API] JSON解析失败: {e}")
                print(f"[影院信息API] 响应内容: {response.text}")
                return None
        else:
            print(f"[影院信息API] HTTP请求失败: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"[影院信息API] 网络请求异常: {e}")
        return None
    except Exception as e:
        print(f"[影院信息API] 未知异常: {e}")
        return None

def validate_cinema(cinemaid, base_urls=None):
    """
    验证影院ID是否有效
    参数：
        cinemaid: 影院ID
        base_urls: 可选的域名列表，如果不提供则使用默认域名列表
    返回：
        (是否有效, 影院信息, 有效的base_url) 的元组
    """
    if not base_urls:
        # 扩展默认尝试的域名列表
        base_urls = [
            'tt7.cityfilms.cn',      # 虹湾影城域名
            'zcxzs7.cityfilms.cn',   # 万友影城域名
            'cityfilms.cn',          # 主域名
            'wap.cityfilms.cn',      # WAP域名
            'api.cityfilms.cn',      # API域名
            # 可以根据需要添加更多域名
        ]
    
    print(f"[影院验证] 开始验证影院ID: {cinemaid}")
    print(f"[影院验证] 将尝试 {len(base_urls)} 个域名: {base_urls}")
    
    for i, base_url in enumerate(base_urls, 1):
        print(f"[影院验证] ({i}/{len(base_urls)}) 尝试域名: {base_url}")
        cinema_info = get_cinema_info(base_url, cinemaid)
        
        if cinema_info:
            print(f"[影院验证] ✓ 验证成功！域名: {base_url}")
            print(f"[影院验证] ✓ 影院信息: {cinema_info.get('cinemaName', '未知影院')}")
            return True, cinema_info, base_url
        else:
            print(f"[影院验证] ✗ 域名 {base_url} 验证失败")
    
    print(f"[影院验证] ✗ 所有域名验证失败，影院ID可能无效: {cinemaid}")
    print(f"[影院验证] 建议检查：")
    print(f"[影院验证]   1. 影院ID格式是否正确")
    print(f"[影院验证]   2. 该影院是否确实存在")
    print(f"[影院验证]   3. 是否需要添加新的API域名")
    return False, None, None

def format_cinema_data(cinema_info, base_url, original_cinemaid=None):
    """
    格式化影院数据
    
    Args:
        cinema_info (dict): API返回的影院信息
        base_url (str): API域名
        original_cinemaid (str): 原始影院ID（可选，如果提供则优先使用原始ID而不是API返回的ID）
        
    Returns:
        dict: 格式化后的影院数据
    """
    # 修复bug 2：如果提供了原始影院ID，则使用原始ID，否则使用API返回的ID
    cinema_id = original_cinemaid if original_cinemaid else cinema_info.get('cinemaid', '')
    
    return {
        'cinemaid': cinema_id,  # 使用原始添加的ID
        'cinemaShortName': cinema_info.get('cinemaShortName', ''),
        'cityName': cinema_info.get('cityName', ''),
        'cinemaAddress': cinema_info.get('cinemaAddress', ''),
        'cinemaPhone': cinema_info.get('cinemaPhone', ''),
        'base_url': base_url,  # 修正字段名，保持一致性
        'limitTicketAmount': '6',  # 默认限购6张
        'cinemaState': 0,  # 默认正常状态
        'createTime': time.strftime('%Y-%m-%d %H:%M:%S'),
        'updateTime': time.strftime('%Y-%m-%d %H:%M:%S')
    } 