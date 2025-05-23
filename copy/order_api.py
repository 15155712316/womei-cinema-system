import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ORDER_API_URL = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniOrder/createOrder"

def create_order(params: dict) -> dict:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'xweb_xhr': '1',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    response = requests.post(ORDER_API_URL, data=params, headers=headers, timeout=10, verify=False)
    try:
        return response.json()
    except Exception:
        import json
        return json.loads(response.content.decode('utf-8-sig'))

def get_unpaid_order_detail(params: dict) -> dict:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'content-type': 'application/x-www-form-urlencoded',
        'xweb_xhr': '1',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniOrder/getUnpaidOrderDetail"
    response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
    try:
        return response.json()
    except Exception:
        import json
        return json.loads(response.content.decode('utf-8-sig'))

def get_coupons_by_order(params: dict) -> dict:
    """
    获取指定订单的可用优惠券列表
    :param params: dict，需包含 orderno, cinemaid, userid, openid, token 等
    :return: dict，接口返回的json
    """
    url = "https://tt7.cityfilms.cn/MiniTicket/index.php/MiniCoupon/getCouponByOrder"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'xweb_xhr': '1',
        'referer': 'https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
    }
    # 打印请求信息
    import urllib.parse
    full_url = url + '?' + urllib.parse.urlencode(params)
    print("[优惠券API请求] URL:", full_url)
    print("[优惠券API请求] headers:", headers)
    print("[优惠券API请求] params:", params)
    response = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
    try:
        return response.json()
    except Exception:
        import json
        return json.loads(response.content.decode('utf-8-sig')) 