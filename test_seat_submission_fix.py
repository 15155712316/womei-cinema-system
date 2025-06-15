import requests

# 请求配置
url = "https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/ticket/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839",
    "Content-Type": "application/x-www-form-urlencoded",
    "x-channel-id": "40000",
    "tenant-short": "wmyc",
    "client-version": "4.0",
    "xweb_xhr": "1",
    "x-requested-with": "wxapp",
    "token": "47794858a832916d8eda012e7cabd269",  # 请替换为有效token
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html",
    "accept-language": "zh-CN,zh;q=0.9",
    "priority": "u=1, i"
}
data = {
    "seatlable": "10015:1:1:11051771#10#17",  # 测试1排1座
    "schedule_id": "16624418"
}

try:
    # 发送请求
    response = requests.post(url, headers=headers, data=data,verify=False)
    response.raise_for_status()
    
    # 打印结果
    print("请求成功！")
    print("HTTP状态码:", response.status_code)
    print("响应内容:", response.json())
    
except requests.exceptions.RequestException as e:
    print("请求失败:", str(e))
except ValueError:
    print("响应不是有效JSON:", response.text)
