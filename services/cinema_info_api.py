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
        base_url (str): API域名（不包含协议）
        cinemaid (str): 影院ID

    Returns:
        dict or None: 影院信息字典，失败返回None
    """
    # 构建完整的API URL
    # 尝试多个可能的API端点，按优先级排序
    api_endpoints = [
        "/MiniTicket/index.php/MiniCommonSystem/getCinemaInfo",       # 影院详细信息端点
        "/MiniTicket/index.php/MiniCommonSystem/getCinemaSettings",   # 影院设置端点
        "/MiniTicket/index.php/MiniCommonSystem/getCinemaDetail",     # 影院详情端点
        "/MiniTicket/index.php/MiniCommonSystem/getCinemaData",       # 影院数据端点
        "/MiniTicket/index.php/MiniFilm/getAllFilmsIndexNew",         # 影片列表端点（可能包含影院信息）
    ]

    for endpoint in api_endpoints:
        url = f"https://{base_url}{endpoint}"
        print(f"[影院信息API] 尝试端点: {url}")

        result = _try_get_cinema_info(url, cinemaid)
        if result:
            return result

    print(f"[影院信息API] ✗ 所有端点都失败")
    return None

def _try_get_cinema_info(url, cinemaid):
    """尝试从指定URL获取影院信息"""
    params = {
        'sortType': '1',
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'xweb_xhr': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/',
        'priority': 'u=1, i'
    }

    try:
        # 发送请求
        response = requests.get(url, params=params, headers=headers, timeout=15, verify=False)

        if response.status_code == 200:
            try:
                data = response.json()

                # 分析响应
                result_code = data.get('resultCode')
                result_desc = data.get('resultDesc')
                result_data = data.get('resultData')

                # 检查成功条件
                if result_code == "0" and result_data is not None:
                    print(f"[影院信息API] ✓ 成功获取影院信息")

                    # 如果resultData是字符串，尝试解析为JSON
                    if isinstance(result_data, str):
                        try:
                            result_data = json.loads(result_data)
                        except:
                            pass

                    # 检查数据是否包含影院名称信息
                    if isinstance(result_data, dict):
                        cinema_name = (result_data.get('cinemaShortName') or
                                     result_data.get('cinemaName') or
                                     result_data.get('name'))

                        if cinema_name:
                            print(f"[影院信息API] ✓ 影院名称: {cinema_name}")
                            return result_data
                        else:
                            # 如果没有影院名称，但有其他有用信息，也返回
                            # 这种情况下会在format_cinema_data中生成默认名称
                            print(f"[影院信息API] ✓ 获取到影院配置信息（无名称）")
                            return result_data

                    # 如果是列表，取第一个
                    elif isinstance(result_data, list) and len(result_data) > 0:
                        return result_data[0]

                    # 即使是简单数据也返回，表示影院ID有效
                    return result_data
                else:
                    print(f"[影院信息API] ✗ API返回错误: resultCode={result_code}, resultDesc={result_desc}")
                    return None

            except ValueError as e:
                print(f"[影院信息API] JSON解析失败: {e}")
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
        base_url (str): API域名（不包含协议）
        original_cinemaid (str): 原始影院ID（可选，如果提供则优先使用原始ID而不是API返回的ID）

    Returns:
        dict: 格式化后的影院数据
    """
    # 使用原始影院ID，如果没有则使用API返回的ID
    cinema_id = original_cinemaid if original_cinemaid else cinema_info.get('cinemaid', '')

    # 提取影院名称（尝试多个可能的字段）
    cinema_name = (cinema_info.get('cinemaShortName') or
                   cinema_info.get('cinemaName') or
                   cinema_info.get('name'))

    # 如果没有找到影院名称，生成一个基于域名和ID的名称
    if not cinema_name:
        # 从域名提取可能的影院品牌名
        domain_parts = base_url.split('.')
        brand_hint = ""

        # 常见影院品牌域名映射
        brand_mapping = {
            'heibaiyingye': '黑白影业',
            'cityfilms': '城市影院',
            'wanda': '万达影城',
            'cgv': 'CGV影城',
            'bona': '博纳影城',
            'dadi': '大地影院',
            'jinyi': '金逸影城',
            'huaxia': '华夏影城'
        }

        for domain_part in domain_parts:
            for key, brand in brand_mapping.items():
                if key in domain_part.lower():
                    brand_hint = brand
                    break
            if brand_hint:
                break

        # 生成影院名称
        if brand_hint:
            cinema_name = f"{brand_hint}({cinema_id[:8]})"
        else:
            cinema_name = f"影院_{cinema_id[:8]}"

    # 提取城市名称
    city_name = (cinema_info.get('cityName') or
                 cinema_info.get('city') or
                 cinema_info.get('province') or
                 '未知城市')

    # 提取地址信息
    address = (cinema_info.get('cinemaAddress') or
               cinema_info.get('address') or
               cinema_info.get('location') or
               '地址未知')

    # 提取电话信息
    phone = (cinema_info.get('cinemaPhone') or
             cinema_info.get('phone') or
             cinema_info.get('tel') or
             '')

    return {
        'cinemaid': cinema_id,
        'cinemaShortName': cinema_name,
        'cityName': city_name,
        'cinemaAddress': address,
        'cinemaPhone': phone,
        'base_url': base_url,  # 不包含协议的域名
        'limitTicketAmount': '6',  # 默认限购6张
        'cinemaState': 0,  # 默认正常状态
        'createTime': time.strftime('%Y-%m-%d %H:%M:%S'),
        'updateTime': time.strftime('%Y-%m-%d %H:%M:%S'),
        'auto_added': True,  # 标记为自动添加
        'api_verified': True  # 标记为API验证通过
    }