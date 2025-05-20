import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
}

# 1. 基础url
base_url = 'https://tt7.cityfilms.cn/MiniTicket/index.php/MiniFilm/getPlanSeatInfo'

# 2. 参数字典，灵活修改
params = {
    'showCode': '3444250519RZ4R08',
    'hallCode': '0000000000000002',
    'filmNo': '051a00712025',
    'showDate': '2025-05-20 18:00',
    'startTime': '20:50',
    'userid': '15155712316',
    'cinemaid': '11b7e4bcc265',
    'openid': 'ohA6p7Z0kejTSi40QVYXQtMF9SDY',
    'token': '02849a78647f5af9',
}

# 3. 发起请求
response = requests.get(
    base_url,
    headers=headers,
    params=params,
    verify=False,
)
data = json.loads(response.content)

# 4. 保存结果
with open('result座位.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("请求完成，已保存到 result座位.json")