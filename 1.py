import requests
import urllib3
import json
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

# 示例：万友影城
get_films(
    base_url='zcxzs7.cityfilms.cn',
    cinemaid='0f1e21d86ac8',
    userid='14700283316',
    openid='oEW4I7NdSlziiCBWQQVelGbFEPSU',
    token='64921354c989cf73',
    referer='https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html'
)
# 示例：虹湾影城
# get_films(
#     base_url='tt7.cityfilms.cn',
#     cinemaid='11b7e4bcc265',
#     userid='14700283316',
#     openid='ohA6p7VxLxzcHoBw1_E8VcyEvVVs',
#     token='9de4d8353cd30172',
#     referer='https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html'
# )