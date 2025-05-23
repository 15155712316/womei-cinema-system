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

def bind_coupon(params: dict) -> dict:
    """
    绑定优惠券接口
    :param params: dict，需包含couponcode, cinemaid, userid, openid, token等
    :return: dict，接口返回的json
    """
    import requests
    url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniCoupon/bindCoupon"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'xweb_xhr': '1',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i',
    }
    resp = requests.get(url, params=params, headers=headers, verify=False, timeout=10)
    return resp.json()

def coupon_pay_order(params: dict) -> dict:
    """
    全部用券支付订单接口（MiniPay/couponPay）
    :param params: dict，需包含 orderno, payprice, discountprice, couponcodes, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，若支付成功自动返回订单详情，否则返回支付接口原始结果
    """
    url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniPay/couponPay"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'xweb_xhr': '1',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    try:
        resp = requests.post(url, data=params, headers=headers, timeout=10, verify=False)
        result = resp.json()
    except Exception as e:
        return {"resultCode": "-1", "resultDesc": f"支付请求异常: {str(e)}", "resultData": None}
    # 支付成功自动查单
    if result.get("resultCode") == "0":
        orderno = params.get("orderno")
        detail_params = {
            "orderno": orderno,
            "groupid": params.get("groupid", ""),
            "cinemaid": params.get("cinemaid", ""),
            "cardno": params.get("cardno", ""),
            "userid": params.get("userid", ""),
            "openid": params.get("openid", ""),
            "CVersion": params.get("CVersion", "3.9.12"),
            "OS": params.get("OS", "Windows"),
            "token": params.get("token", ""),
            "source": params.get("source", "2")
        }
        detail = get_order_detail(detail_params)
        return {"resultCode": "0", "resultDesc": "支付成功，已查单", "resultData": detail}
    else:
        return result

def get_order_detail(params: dict) -> dict:
    """
    查询订单详情接口（MiniOrder/getOrderDetail）
    :param params: dict，需包含 orderno, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json
    """
    url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniOrder/getOrderDetail"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'xweb_xhr': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10, verify=False)
        try:
            return resp.json()
        except Exception:
            import json
            return json.loads(resp.content.decode('utf-8-sig'))
    except Exception as e:
        return {"resultCode": "-1", "resultDesc": f"查单请求异常: {str(e)}", "resultData": None}

def get_order_qrcode_api(orderno: str) -> bytes:
    """
    获取订单取票二维码图片（MiniTicket/Cqrcode/generateQrcode/<orderno>）
    :param orderno: 订单号（字符串）
    :return: 二进制图片内容，异常时返回None
    """
    url = f"https://zcxzs7.cityfilms.cn/MiniTicket/index.php/Cqrcode/generateQrcode/{orderno}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'image/wxpic,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'image',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'i'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            return resp.content
        else:
            return None
    except Exception as e:
        return None

def get_order_list(params: dict) -> dict:
    """
    获取订单列表接口（MiniOrder/getOrderList）
    :param params: dict，需包含pageNo, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，异常时resultCode=-1
    """
    url = "https://zcxzs7.cityfilms.cn/MiniTicket/index.php/MiniOrder/getOrderList"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'xweb_xhr': '1',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wxaea711f302cc71ec/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }
    try:
        resp = requests.post(url, data=params, headers=headers, timeout=10, verify=False)
        try:
            return resp.json()
        except Exception:
            import json
            return json.loads(resp.content.decode('utf-8-sig'))
    except Exception as e:
        return {"resultCode": "-1", "resultDesc": f"订单列表请求异常: {str(e)}", "resultData": None}

def cancel_order(params: dict) -> dict:
    """
    取消订单接口（MiniOrder/cancelorder）
    :param params: dict，需包含 orderno, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，异常时resultCode=-1
    """
    # 构建URL - 需要根据影院base_url动态构建
    base_url = params.get('base_url', 'tt7.cityfilms.cn')  # 默认使用tt7
    url = f"https://{base_url}/MiniTicket/index.php/MiniOrder/cancelorder"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'application/json',
        'xweb_xhr': '1',
        'Content-Type': 'application/x-www-form-urlencoded',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html',
        'accept-language': 'zh-CN,zh;q=0.9'
    }
    
    # 构建请求参数
    request_params = {
        'orderno': params.get('orderno', ''),
        'groupid': params.get('groupid', ''),
        'cinemaid': params.get('cinemaid', ''),
        'cardno': params.get('cardno', ''),
        'userid': params.get('userid', ''),
        'openid': params.get('openid', ''),
        'CVersion': params.get('CVersion', '3.9.12'),
        'OS': params.get('OS', 'Windows'),
        'token': params.get('token', ''),
        'source': params.get('source', '2')
    }
    
    print(f"[取消订单API] URL: {url}")
    print(f"[取消订单API] 订单号: {request_params['orderno']}")
    
    try:
        resp = requests.get(url, params=request_params, headers=headers, timeout=10, verify=False)
        try:
            result = resp.json()
            print(f"[取消订单API] 返回结果: {result}")
            return result
        except Exception:
            import json
            result = json.loads(resp.content.decode('utf-8-sig'))
            print(f"[取消订单API] 返回结果(BOM): {result}")
            return result
    except Exception as e:
        error_result = {"resultCode": "-1", "resultDesc": f"取消订单请求异常: {str(e)}", "resultData": None}
        print(f"[取消订单API] 异常: {error_result}")
        return error_result

def cancel_all_unpaid_orders(account: dict, cinema: dict) -> dict:
    """
    取消账号下所有未付款订单
    :param account: 账号信息字典
    :param cinema: 影院信息字典
    :return: dict，包含取消结果统计信息
    """
    print(f"[批量取消订单] 开始检查账号 {account.get('userid')} 的未付款订单")
    
    # 1. 先获取订单列表
    list_params = {
        'pageNo': 1,
        'groupid': '',
        'cinemaid': account['cinemaid'],
        'cardno': account.get('cardno', ''),
        'userid': account['userid'],
        'openid': account['openid'],
        'CVersion': '3.9.12',
        'OS': 'Windows',
        'token': account['token'],
        'source': '2'
    }
    
    order_list_result = get_order_list(list_params)
    
    if order_list_result.get('resultCode') != '0':
        return {
            "resultCode": "-1", 
            "resultDesc": f"获取订单列表失败: {order_list_result.get('resultDesc', '未知错误')}", 
            "cancelledCount": 0,
            "failedCount": 0,
            "totalCount": 0
        }
    
    # 2. 提取未付款订单
    unpaid_orders = order_list_result.get('resultData', {}).get('unpaidorders', [])
    total_count = len(unpaid_orders)
    
    if total_count == 0:
        print("[批量取消订单] 没有未付款订单，无需取消")
        return {
            "resultCode": "0",
            "resultDesc": "没有未付款订单",
            "cancelledCount": 0,
            "failedCount": 0,
            "totalCount": 0
        }
    
    print(f"[批量取消订单] 发现 {total_count} 个未付款订单，开始逐个取消")
    
    # 3. 逐个取消未付款订单 - 不判断返回结果，都认为成功
    cancelled_count = 0
    
    for order in unpaid_orders:
        orderno = order.get('orderno', '')
        order_name = order.get('orderName', '')
        
        cancel_params = {
            'orderno': orderno,
            'groupid': '',
            'cinemaid': account['cinemaid'],
            'cardno': account.get('cardno', ''),
            'userid': account['userid'],
            'openid': account['openid'],
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'token': account['token'],
            'source': '2',
            'base_url': cinema.get('base_url', 'tt7.cityfilms.cn')  # 传递base_url
        }
        
        print(f"[批量取消订单] 正在取消订单: {orderno} ({order_name})")
        cancel_result = cancel_order(cancel_params)
        
        # 不管返回什么结果，都认为取消成功
        cancelled_count += 1
        print(f"[批量取消订单] ✓ 订单 {orderno} 已发送取消请求 (返回: {cancel_result.get('resultCode', 'unknown')})")
    
    # 4. 返回统计结果 - 全部成功
    result_desc = f"已发送取消请求给 {cancelled_count} 个订单"
    
    return {
        "resultCode": "0",
        "resultDesc": result_desc,
        "cancelledCount": cancelled_count,
        "failedCount": 0,
        "totalCount": total_count,
        "failedOrders": []
    } 