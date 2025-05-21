import requests
from urllib.parse import urlparse, parse_qs

def login_and_check_card(
    phone: str,
    ck: str,
    openid: str,
    cinemaid: str,
    pageNo: str = "1",
    groupid: str = "",
    cardno: str = "",
    CVersion: str = "3.9.12",
    OS: str = "Windows",
    source: str = "2"
) -> dict:
    url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniMember/getMemcardList"
    params = {
        "cinemaid": cinemaid,
        "userid": phone,
        "openid": openid,
        "token": ck,
        "pageNo": pageNo,
        "groupid": groupid,
        "cardno": cardno,
        "CVersion": CVersion,
        "OS": OS,
        "source": source
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
    resp = requests.get(url, params=params, headers=headers, timeout=5, verify=False)
    
    return resp.json()

def extract_params_and_request(url: str, headers: dict = None) -> dict:
    """
    提取url中的参数并发起GET请求，返回json结果。
    :param url: 完整的带参数url
    :param headers: 可选headers
    :return: 响应json
    """
    parsed = urlparse(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    params = {k: v[0] for k, v in parse_qs(parsed.query).items()}
    resp = requests.get(base_url, params=params, headers=headers, timeout=5, verify=False)
    try:
        return resp.json()
    except Exception:
        return {"error": "响应不是合法JSON", "text": resp.text}

def extract_params_from_url(url: str) -> dict:
    """
    仅提取url中的参数，不发起请求，便于测试和调试。
    :param url: 完整的带参数url
    :return: 参数字典
    """
    parsed = urlparse(url)
    return {k: v[0] for k, v in parse_qs(parsed.query).items()} 