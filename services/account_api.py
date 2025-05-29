import requests
from urllib.parse import urlparse, parse_qs
from .api_base import api_get

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
    """登录并检查会员卡信息 - 使用动态base_url"""
    
    # 构建请求参数
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
    
    print(f"[登录API] 开始调用登录接口")
    print(f"[登录API] 影院ID: {cinemaid}")
    print(f"[登录API] 手机号: {phone}")
    print(f"[登录API] CK长度: {len(ck)}")
    print(f"[登录API] OpenID: {openid}")
    print(f"[登录API] 请求参数: {params}")
    
    # 使用新的API基础服务，自动根据cinemaid选择base_url
    result = api_get('MiniTicket/index.php/MiniMember/getMemcardList', cinemaid, params=params)
    
    print(f"[登录API] 返回数据: {result}")
    return result

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


# 账号管理相关函数
import json
import os

def get_account_list():
    """获取账号列表"""
    try:
        accounts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'accounts.json')
        if os.path.exists(accounts_file):
            with open(accounts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"[账号API] 获取账号列表错误: {e}")
        return []

def save_account(account):
    """保存账号"""
    try:
        accounts = get_account_list()
        
        # 检查是否已存在
        for i, existing_account in enumerate(accounts):
            if existing_account.get('userid') == account.get('userid'):
                accounts[i] = account
                break
        else:
            accounts.append(account)
        
        # 保存到文件
        accounts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'accounts.json')
        os.makedirs(os.path.dirname(accounts_file), exist_ok=True)
        
        with open(accounts_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"[账号API] 保存账号错误: {e}")
        return False

def delete_account(userid):
    """删除账号"""
    try:
        accounts = get_account_list()
        accounts = [acc for acc in accounts if acc.get('userid') != userid]
        
        # 保存到文件
        accounts_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'accounts.json')
        with open(accounts_file, 'w', encoding='utf-8') as f:
            json.dump(accounts, f, ensure_ascii=False, indent=2)
        
        return True
    except Exception as e:
        print(f"[账号API] 删除账号错误: {e}")
        return False 