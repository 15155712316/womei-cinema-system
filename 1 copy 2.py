import requests
import urllib3
import json
import re
from datetime import datetime, timedelta
# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def get_films(
    base_url,      # 域名
    cinemaid,      # 影院ID
    userid,        # 用户ID
    openid,        # openid
    token,         # token
    referer,       # Referer
    groupid='',    # 其它参数可选
    cardno='',
    cversion='3.9.12',
    os='Windows',
    source='2'
):
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
        'type': '0',
        'groupid': groupid,
        'cinemaid': cinemaid,
        'cardno': cardno,
        'userid': userid,
        'openid': openid,
        'CVersion': cversion,
        'OS': os,
        'token': token,
        'source': source,
    }
    url = f'https://{base_url}/MiniTicket/index.php/MiniFilm/getAllFilmsIndexNew'
    response = requests.get(url, headers=headers, params=params, verify=False)

    # 解析JSON，自动去除BOM
    data = json.loads(response.content)
    print(data) 
    # 美化打印结果（自动处理Unicode字符）
    # print(json.dumps(data, ensure_ascii=False, indent=2))
    with open('result排期.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return data  # 建议返回data字典，后续更方便处理

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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Referer': referer,
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
    print(f"[DEBUG] getPlanSeatInfo接口返回状态: {response.status_code}")
    print("请求URL:", response.url)
    if response.status_code != 200 or not response.content:
        print("[ERROR] 获取座位图失败，接口无响应或状态码异常！")
        print("返回内容：", response.text)
        return None
    try:
        data = json.loads(response.content)
        return data
    except Exception as e:
        print("[ERROR] 返回内容不是合法JSON！")
        print("返回内容：", response.text)
        raise e

def safe_filename(s):
    return re.sub(r'[\\/:*?"<>|\s]', '_', s)

# ========== 1. 获取万友影城最新排期 ==========
base_url = 'zcxzs7.cityfilms.cn'
cinemaid = '0f1e21d86ac8'
userid = '14700283316'
openid = 'oEW4I7NdSlziiCBWQQVelGbFEPSU'
token = '64921354c989cf73'
referer = 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html'
cinema_name = '万友影城'

schedule_data = get_films(base_url, cinemaid, userid, openid, token, referer)
with open(f'{cinema_name}最新排期.json', 'w', encoding='utf-8') as f:
    json.dump(schedule_data, f, ensure_ascii=False, indent=2)

# ========== 2. 自动选择第二天最后一场 ==========
resultData = schedule_data['resultData']
films = resultData['films']
shows = resultData['shows']

# 获取第二天日期字符串
now = datetime.now()
tomorrow = now + timedelta(days=1)
tomorrow_str = tomorrow.strftime('%Y-%m-%d')

# 自动尝试第二天所有场次，从最后一场往前找
sessions_to_try = []
for film in films:
    film_code = film['fc']
    film_name = film['fn']
    film_shows = shows.get(film_code, {})
    if tomorrow_str in film_shows:
        sessions = film_shows[tomorrow_str]
        for session in reversed(sessions):  # 从最后一场往前
            sessions_to_try.append((film, session, tomorrow_str))

found = False
for film, session, date in sessions_to_try:
    showCode = session['g']
    hallCode = session['j']
    filmCode = session.get('h', film['fc'])
    filmNo = film['fno']
    showDate = session['k'].split(' ')[0]
    startTime = session['q']
    print(f"尝试场次：{film['fn']} {showDate} {startTime} {session['t']} showCode={showCode} hallCode={hallCode}")
    seats_data = get_plan_seat_info(
        base_url, showCode, hallCode, filmCode, filmNo, showDate, startTime,
        userid, openid, token, cinemaid
    )
    if seats_data and 'resultData' in seats_data and 'seats' in seats_data['resultData']:
        selected_film = film
        selected_session = session
        selected_date = showDate
        found = True
        break
    else:
        print("该场次无效，尝试下一个...")

if not found:
    print('未找到第二天有可用座位图的影片场次！')
    exit(1)

# ========== 4. 打印详细说明 ==========
print(f"影院：{cinema_name}")
print(f"影片：{selected_film['fn']}")
print(f"日期：{selected_date}")
print(f"场次时间：{selected_session['q']}")
print(f"影厅：{selected_session['t']}")
print(f"场次ID：{selected_session['g']}")
print("="*40)

# 打印座位分布
seats = seats_data['resultData']['seats']
rows = set()
cols = set()
row_col_map = {}
for seat in seats:
    r = int(seat['rn'])
    c = int(seat['cn'])
    rows.add(r)
    cols.add(c)
    row_col_map.setdefault(r, set()).add(c)
print(f"所有排号: {sorted(rows)}")
print(f"所有列号: {sorted(cols)}")
for r in sorted(row_col_map):
    print(f"第{r}排有列: {sorted(row_col_map[r])}")