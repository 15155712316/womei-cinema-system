import requests
import json
import os
import urllib3
# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_films(base_url, cinemaid, openid, userid,  token, cversion='3.9.12', os='Windows', source='2'):
    """
    实时请求影院影片及排期信息
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    params = {
        'cinemaid': cinemaid,
        'openid': openid,
        'token': token,
        'userid': userid,
        'CVersion': cversion,
        'OS': os,
        'source': source,
        'type': '0',
    }
    url = f'https://{base_url}/MiniTicket/index.php/MiniFilm/getAllFilmsIndexNew'
    response = requests.get(url, headers=headers, params=params, verify=False)
    # 处理BOM
    data = json.loads(response.content.decode('utf-8-sig'))
    # print(data['resultData'] if 'resultData' in data else {})
    return data['resultData'] if 'resultData' in data else {}

def load_cinemas():
    """
    读取所有影院参数 - 支持新的影院信息管理
    """
    # 首先尝试从新的影院信息管理器加载
    try:
        from .cinema_manager import cinema_manager
        cinema_list = cinema_manager.load_cinema_list()
        
        if cinema_list:
            print(f"[影院加载] 从新影院管理器加载 {len(cinema_list)} 个影院")
            # 转换为兼容的格式（保持向后兼容）
            compatible_cinemas = []
            for cinema in cinema_list:
                compatible_cinema = {
                    'name': cinema.get('cinemaShortName', cinema.get('cinemaName', '未知影院')),
                    'cinemaid': cinema.get('cinemaid', ''),
                    'base_url': cinema.get('base_url', ''),
                    'address': cinema.get('cinemaAddress', ''),
                    'cityName': cinema.get('cityName', ''),
                    'cinemaName': cinema.get('cinemaName', ''),
                    'cinemaTel': cinema.get('cinemaTel', ''),
                    # 这些字段现在从账号信息中获取，设为空值
                    'openid': '',
                    'token': '',
                    'userid': ''
                }
                compatible_cinemas.append(compatible_cinema)
            return compatible_cinemas
    except Exception as e:
        print(f"[影院加载] 从新影院管理器加载失败: {e}")
    
    # 如果新的管理器没有数据，尝试从旧的 cinemas.json 加载并迁移
    old_path = os.path.join(os.path.dirname(__file__), 'cinemas.json')
    if os.path.exists(old_path):
        try:
            print(f"[影院加载] 发现旧的影院文件，正在迁移数据...")
            with open(old_path, 'r', encoding='utf-8') as f:
                old_cinemas = json.load(f)
            
            # 迁移数据到新的管理器
            from .cinema_manager import cinema_manager
            migrated_cinemas = []
            
            for old_cinema in old_cinemas:
                # 构建新格式的影院数据
                new_cinema = {
                    'cinemaid': old_cinema.get('cinemaid', ''),
                    'cityName': '未知城市',  # 旧数据没有这个字段
                    'cinemaShortName': old_cinema.get('name', '未知影院'),
                    'cinemaName': old_cinema.get('name', '未知影院'),
                    'cinemaAddress': old_cinema.get('address', old_cinema.get('base_url', '地址未知')),
                    'cinemaTel': '',
                    'base_url': old_cinema.get('base_url', ''),
                    'limitTicketAmount': '6',
                    'cinemaState': 0
                }
                migrated_cinemas.append(new_cinema)
            
            # 保存到新的管理器
            if cinema_manager.save_cinema_list(migrated_cinemas):
                print(f"[影院加载] 成功迁移 {len(migrated_cinemas)} 个影院到新管理器")
                
                # 迁移成功后，重命名旧文件作为备份
                backup_path = old_path + '.backup'
                os.rename(old_path, backup_path)
                print(f"[影院加载] 旧文件已备份为: {backup_path}")
                
                # 返回迁移后的数据
                return load_cinemas()  # 递归调用，从新管理器加载
            else:
                print(f"[影院加载] 迁移失败，继续使用旧文件")
                return old_cinemas
                
        except Exception as e:
            print(f"[影院加载] 迁移旧数据失败: {e}")
            try:
                with open(old_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
    
    # 如果都没有，返回空列表
    print(f"[影院加载] 未找到影院数据，返回空列表")
    return []

def normalize_film_data(raw_data):
    """
    将接口返回的原始数据标准化为统一结构，便于前端使用
    返回：
    {
        'films': [{'name': ..., 'key': ...}, ...],
        'shows': {film_key: {date: [场次, ...], ...}, ...}
    }
    """
    # 兼容不同字段名
    print(raw_data)
    films_raw = raw_data.get('films') 
    shows_raw = raw_data.get('shows', {})

    films = []
    for film in films_raw:
        # 兼容 fn/film_name, fc/film_key
        name = film.get('fn') or film.get('film_name')
        key = film.get('fc') or film.get('film_key')
        if name and key:
            films.append({'name': name, 'key': key})
    print(films)
    print(shows_raw)
    # shows结构直接用
    return {
        'films': films,
        'shows': shows_raw
    }

def get_plan_seat_info(
    base_url,           # 域名，如 'zcxzs7.cityfilms.cn'
    showCode,           # 场次唯一编码（小程序抓包showCode，对应session['g']）
    hallCode,           # 影厅编码（小程序抓包hallCode，对应session['j']，如'0000000000000007'）
    filmCode,           # 影片编码（小程序抓包filmCode，优先session['h']，否则film['fc']）
    filmNo,             # 影片No（小程序抓包filmNo，film['fno']）
    showDate,           # 放映日期（小程序抓包showDate，session['k']的日期部分，如'2025-05-21'）
    startTime,          # 放映开始时间（小程序抓包startTime，session['q']，如'16:45'）
    userid,             # 用户ID（小程序抓包userid，手机号或用户唯一标识）
    openid,             # openid（小程序抓包openid，微信用户唯一标识）
    token,              # token（小程序抓包token，登录后获取）
    cinemaid,           # 影院ID（小程序抓包cinemaid，影院唯一标识）
    cardno='',          # 会员卡号（如有会员卡购票需求，默认空字符串）
):
    """
    请求指定场次的座位图信息，返回json数据
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'xweb_xhr': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    params = {
        'showCode': showCode,         # 场次唯一编码
        'hallCode': hallCode,         # 影厅编码
        'filmCode': filmCode,         # 影片编码
        'filmNo': filmNo,             # 影片No
        'showDate': showDate,         # 放映日期（格式：2025-05-21）
        'startTime': startTime,       # 放映开始时间（格式：16:45）
        'eventCode': 'undefined',     # 活动编码（如有活动，默认'undefined'）
        'haltSales': '0',             # 是否停售（0=正常，1=停售，默认'0'）
        'userid': userid,             # 用户ID
        'cinemaid': cinemaid,         # 影院ID
        'cardno': cardno,             # 会员卡号
        'openid': openid,             # openid
        'token': token,               # token
    }
    url = f'https://{base_url}/MiniTicket/index.php/MiniFilm/getPlanSeatInfo'
    response = requests.get(url, headers=headers, params=params, verify=False)
    try:
        print(response.content.decode('utf-8-sig'))
        return json.loads(response.content.decode('utf-8-sig'))
    except Exception:
        return {'error': '接口返回内容不是合法JSON', 'text': response.text}

# 你可以继续添加 get_cities, get_cinemas, get_sessions 等函数

