import requests
import json
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
    'Accept': 'application/json',
    'xweb_xhr': '1',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Sec-Fetch-Site': 'cross-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'Referer': 'https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

response = requests.get(
    'https://tt7.cityfilms.cn/MiniTicket/index.php/MiniFilm/getPlanSeatInfo?showCode=34442505190VRF0D&hallCode=0000000000000003&filmCode=null&filmNo=001a05892024&showDate=2025-05-19%2019:35&startTime=19:35&eventCode=undefined&haltSales=0&userid=14700283316&groupid&cinemaid=11b7e4bcc265&cardno&openid=ohA6p7VxLxzcHoBw1_E8VcyEvVVs&CVersion=3.9.12&OS=Windows&token=9de4d8353cd30172&source=2',
    headers=headers,
    verify=False,
)
data = json.loads(response.content)
with open('result1.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(data) 