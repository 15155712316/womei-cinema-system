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
    读取所有影院参数
    """
    path = os.path.join(os.path.dirname(__file__), 'cinemas.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

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

