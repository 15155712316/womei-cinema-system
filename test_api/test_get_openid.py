import requests
import json

url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniMember/getMemcardList"

params = {
    "cinemaid": "0f1e21d86ac8",
    "userid": "15155712316",
    "openid": "oEW4I7LA3s0PONMaw-36M6YalsxQ",
    "token": "52468f74519cfbcb",
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639",
    "Accept": "application/json",
    "xweb_xhr": "1",
    "content-type": "application/x-www-form-urlencoded",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i"
}

response = requests.get(url, params=params, headers=headers, verify=False)
result = json.loads(response.content.decode('utf-8-sig'))

print('状态码:', response.status_code)
print('响应内容:', result)

# 判断登录是否成功
if result.get('resultCode') == '0':
    print("账号登录成功")
    # 判断是否有会员卡
    if result.get('resultData'):
        print("有会员卡，会员卡信息如下：")
        print(result['resultData'])
    else:
        print("没有会员卡")
else:
    print("账号登录失败，错误信息：", result.get('resultDesc'))
