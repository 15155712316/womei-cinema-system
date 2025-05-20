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

# 你可以继续添加 get_cities, get_cinemas, get_sessions 等函数

