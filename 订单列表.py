import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
    'x-channel-id': '40000',
    'tenant-short': 'wmyc',
    'client-version': '4.0',
    'content-type': 'multipart/form-data',
    'xweb_xhr': '1',
    'x-requested-with': 'wxapp',
    'token': 'f0fc8c185ecf4e241320811c84157bbf',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
    'accept-language': 'zh-CN,zh;q=0.9',
    'priority': 'u=1, i',
}

params = {
    'version': 'tp_version',
    'order_id': '240113194910006904',
}

response = requests.get('https://ct.womovie.cn/ticket/wmyc/cinema/9934/order/info/', params=params, headers=headers)

# print(response.text)
print(response.json())