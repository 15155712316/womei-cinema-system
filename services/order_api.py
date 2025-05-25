import requests
import urllib3
from .api_base import api_get, api_post

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_order(params: dict) -> dict:
    """创建订单 - 使用动态base_url"""
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    return api_post('MiniTicket/index.php/MiniOrder/createOrder', cinemaid, data=params)

def get_unpaid_order_detail(params: dict) -> dict:
    """获取未支付订单详情 - 使用动态base_url"""
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    return api_get('MiniTicket/index.php/MiniOrder/getUnpaidOrderDetail', cinemaid, params=params)

def get_coupons_by_order(params: dict) -> dict:
    """
    获取指定订单的可用优惠券列表 - 使用动态base_url
    :param params: dict，需包含 orderno, cinemaid, userid, openid, token 等
    :return: dict，接口返回的json
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    # 特殊的headers for 券接口
    special_headers = {
        'referer': 'https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html'
    }
    
    # 打印请求信息
    import urllib.parse
    print(f"[优惠券API请求] 影院ID: {cinemaid}")
    print(f"[优惠券API请求] params: {params}")
    
    return api_get('MiniTicket/index.php/MiniCoupon/getCouponByOrder', cinemaid, params=params, headers=special_headers)

def get_coupon_list(params: dict) -> dict:
    """
    获取账号券列表接口（MiniCoupon/getCouponList） - 使用GET请求
    :param params: dict，需包含 voucherType, pageNo, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    print(f"[券列表API] 获取账号券列表")
    print(f"[券列表API] 影院ID: {cinemaid}")
    print(f"[券列表API] 用户ID: {params.get('userid')}")
    
    return api_get('MiniTicket/index.php/MiniCoupon/getCouponList', cinemaid, params=params)

def bind_coupon(params: dict) -> dict:
    """
    绑定优惠券接口 - 使用GET请求（修复：匹配真实小程序请求方式）
    :param params: dict，需包含 couponcode, cinemaid, userid, openid, token 等
    :return: dict，接口返回的json
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    # 使用GET请求，参数作为查询字符串
    return api_get('MiniTicket/index.php/MiniCoupon/bindCoupon', cinemaid, params=params)

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
    查询订单详情接口（MiniOrder/getOrderDetail） - 使用动态base_url
    :param params: dict，需包含 orderno, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    return api_get('MiniTicket/index.php/MiniOrder/getOrderDetail', cinemaid, params=params)

def get_order_qrcode_api(orderno: str, cinemaid: str) -> bytes:
    """
    获取订单取票二维码图片（MiniTicket/Cqrcode/generateQrcode/<orderno>） - 使用动态base_url
    :param orderno: 订单号（字符串）
    :param cinemaid: 影院ID
    :return: 二进制图片内容，异常时返回None
    """
    from .api_base import api_base
    
    if not cinemaid:
        print(f"[订单二维码] 缺少影院ID参数")
        return None
    
    base_url = api_base.get_base_url_for_cinema(cinemaid)
    url = api_base.build_url(base_url, f'MiniTicket/index.php/Cqrcode/generateQrcode/{orderno}')
    
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
        print(f"[订单二维码] 请求URL: {url}")
        resp = requests.get(url, headers=headers, timeout=10, verify=False)
        if resp.status_code == 200:
            return resp.content
        else:
            print(f"[订单二维码] HTTP错误: {resp.status_code}")
            return None
    except Exception as e:
        print(f"[订单二维码] 请求异常: {e}")
        return None

def get_order_list(params: dict) -> dict:
    """
    获取订单列表接口（MiniOrder/getOrderList） - 使用动态base_url
    :param params: dict，需包含pageNo, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，异常时resultCode=-1
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    return api_post('MiniTicket/index.php/MiniOrder/getOrderList', cinemaid, data=params)

def cancel_order(params: dict) -> dict:
    """
    取消订单接口（MiniOrder/cancelorder） - 使用动态base_url
    修复：使用GET请求，与真实小程序保持一致
    :param params: dict，需包含 orderno, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，异常时resultCode=-1
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    # 构建请求参数 - 修复：cardno使用空值，与真实小程序保持一致
    request_params = {
        'orderno': params.get('orderno', ''),
        'groupid': params.get('groupid', ''),
        'cinemaid': params.get('cinemaid', ''),
        'cardno': '',  # 修复：使用空值，与真实小程序保持一致
        'userid': params.get('userid', ''),
        'openid': params.get('openid', ''),
        'CVersion': params.get('CVersion', '3.9.12'),
        'OS': params.get('OS', 'Windows'),
        'token': params.get('token', ''),
        'source': params.get('source', '2')
    }
    
    print(f"[取消订单API] 订单号: {request_params['orderno']}")
    print(f"[取消订单API] 影院ID: {request_params['cinemaid']}")
    print(f"[取消订单API] 使用GET请求（修复）")
    
    # 修复：使用GET请求而不是POST请求
    return api_get('MiniTicket/index.php/MiniOrder/cancelorder', cinemaid, params=request_params)

def cancel_all_unpaid_orders(account: dict, cinemaid: str) -> dict:
    """
    取消该账号在指定影院的所有未付款订单 - 使用动态base_url
    :param account: 账号信息字典
    :param cinemaid: 影院ID
    :return: dict，包含取消结果和取消数量
    """
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    print(f"[取消未付款订单] 开始取消账号 {account.get('userid')} 在影院 {cinemaid} 的所有未付款订单")
    
    # 首先获取订单列表
    list_params = {
        'pageNo': 1,
        'groupid': '',
        'cinemaid': cinemaid,
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
        print(f"[取消未付款订单] 获取订单列表失败: {order_list_result.get('resultDesc')}")
        return {"resultCode": "0", "resultDesc": "success", "cancelledCount": 0}
    
    orders = order_list_result.get('resultData', {}).get('orders', [])
    unpaid_orders = [order for order in orders if order.get('orderS') == '待付款']
    
    print(f"[取消未付款订单] 找到 {len(unpaid_orders)} 个未付款订单")
    
    cancelled_count = 0
    for order in unpaid_orders:
        orderno = order.get('orderno')
        if orderno:
            cancel_result = cancel_order({
                'orderno': orderno,
                'groupid': '',
                'cinemaid': cinemaid,
                'cardno': account.get('cardno', ''),
                'userid': account['userid'],
                'openid': account['openid'],
                'CVersion': '3.9.12',
                'OS': 'Windows',
                'token': account['token'],
                'source': '2'
            })
            
            if cancel_result.get('resultCode') == '0':
                cancelled_count += 1
                print(f"[取消未付款订单] 订单 {orderno} 取消成功")
            else:
                print(f"[取消未付款订单] 订单 {orderno} 取消失败: {cancel_result.get('resultDesc')}")
    
    print(f"[取消未付款订单] 总共取消了 {cancelled_count} 个订单")
    return {"resultCode": "0", "resultDesc": "success", "cancelledCount": cancelled_count}

def get_coupon_prepay_info(params: dict) -> dict:
    """
    获取选券后的价格信息接口（ordercouponPrepay） - 使用动态base_url
    :param params: dict，需包含 orderno, couponcode, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    return api_get('MiniTicket/index.php/MiniOrder/ordercouponPrepay', cinemaid, params=params)

def pay_order(params):
    """
    订单支付接口 - 使用券支付 - 使用动态base_url
    """
    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}
    
    # 特殊的headers for 支付接口
    special_headers = {
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://servicewechat.com/wx03aeb42bd6a3580e/1/page-frame.html',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    
    try:
        print(f"[支付API] 开始调用支付接口")
        print(f"[支付API] 影院ID: {cinemaid}")
        print(f"[支付API] 订单号: {params.get('orderno')}")
        print(f"[支付API] 券号: {params.get('couponcodes')}")
        print(f"[支付API] 支付金额: {params.get('payprice')}")
        
        result = api_post('MiniTicket/index.php/MiniPay/couponPay', cinemaid, data=params, headers=special_headers)
        
        print(f"[支付API] 支付响应: {result}")
        return result
        
    except Exception as e:
        print(f"[支付API] 支付异常: {e}")
        return {"resultCode": "-1", "resultDesc": f"支付异常: {e}", "resultData": None} 