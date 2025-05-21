import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
    'Accept': 'application/json',
}

url = 'https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniMember/getMemcardList?cinemaid=0f1e21d86ac8&cardno&userid=15155712316&openid=oEW4I7LA3s0PONMaw-36M6YalsxQ&token=52468f74519cfbcb'

params = extract_params_from_url(url)
print("提取的参数:", params)

response = requests.get(url.split('?')[0], params=params, headers=headers, verify=False)
print("返回结果:", response.json())