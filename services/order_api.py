import requests
import urllib3
import os
from datetime import datetime
from .api_base import api_get, api_post

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def save_qrcode_image(image_data: bytes, order_no: str, cinema_id: str) -> str:
    """
    保存二维码图片到本地
    :param image_data: 图片二进制数据
    :param order_no: 订单号
    :param cinema_id: 影院ID
    :return: 保存的文件路径，失败返回None
    """
    try:
        # 🎯 获取影院名称映射
        cinema_name_map = {
            "35fec8259e74": "华夏优加荟大都荟",
            "b8e8b8b8b8b8": "其他影院1",  # 示例
            "c9f9c9f9c9f9": "其他影院2"   # 示例
        }

        cinema_name = cinema_name_map.get(cinema_id, "未知影院")

        # 🎯 生成日期字符串 (MMDD格式)
        current_date = datetime.now().strftime("%m%d")

        # 🎯 构建文件名：影院+日期+订单号.png
        filename = f"{cinema_name}_{current_date}_{order_no}.png"

        # 🎯 确保data/img目录存在
        img_dir = os.path.join("data", "img")
        os.makedirs(img_dir, exist_ok=True)

        # 🎯 完整文件路径
        file_path = os.path.join(img_dir, filename)

        # 🎯 保存图片
        with open(file_path, 'wb') as f:
            f.write(image_data)

        print(f"[图片保存] 📁 路径: {file_path}")
        print(f"[图片保存] 📏 大小: {len(image_data)} bytes")

        return file_path

    except Exception as e:
        print(f"[图片保存] ❌ 保存失败: {e}")
        import traceback
        traceback.print_exc()
        return None

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
    获取指定订单的可用优惠券列表 - 🔧 修复空值处理错误
    :param params: dict，需包含 orderno, cinemaid, userid, openid, token 等
    :return: dict，接口返回的json，确保不返回None
    """
    # 🔧 修复：检查params参数
    if params is None:
        return {"resultCode": "-1", "resultDesc": "参数为空", "resultData": None}

    if not isinstance(params, dict):
        print(f"[优惠券API] 参数类型错误: {type(params)}")
        return {"resultCode": "-1", "resultDesc": "参数类型错误", "resultData": None}

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

    try:
        # 调用API
        result = api_get('MiniTicket/index.php/MiniCoupon/getCouponByOrder', cinemaid, params=params, headers=special_headers)

        # 🔧 修复：确保返回值不为None
        if result is None:
            print("[优惠券API] API返回None，可能是网络异常")
            return {"resultCode": "-1", "resultDesc": "网络异常，API无响应", "resultData": None}

        # 🔧 修复：确保返回值是字典类型
        if not isinstance(result, dict):
            print(f"[优惠券API] API返回类型错误: {type(result)}")
            return {"resultCode": "-1", "resultDesc": "API响应格式错误", "resultData": None}

        return result

    except Exception as e:
        print(f"[优惠券API] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return {"resultCode": "-1", "resultDesc": f"请求异常: {e}", "resultData": None}

def get_coupon_list(params: dict) -> dict:
    """
    获取账号券列表接口（MiniCoupon/getCouponList） - 🔧 修复空值处理错误
    :param params: dict，需包含 voucherType, pageNo, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，确保不返回None
    """
    # 🔧 修复：检查params参数
    if params is None:
        return {"resultCode": "-1", "resultDesc": "参数为空", "resultData": None}

    if not isinstance(params, dict):
        print(f"[券列表API] 参数类型错误: {type(params)}")
        return {"resultCode": "-1", "resultDesc": "参数类型错误", "resultData": None}

    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}

    print(f"[券列表API] 获取账号券列表")
    print(f"[券列表API] 影院ID: {cinemaid}")
    print(f"[券列表API] 用户ID: {params.get('userid')}")

    try:
        # 调用API
        result = api_get('MiniTicket/index.php/MiniCoupon/getCouponList', cinemaid, params=params)

        # 🔧 修复：确保返回值不为None
        if result is None:
            print("[券列表API] API返回None，可能是网络异常")
            return {"resultCode": "-1", "resultDesc": "网络异常，API无响应", "resultData": None}

        # 🔧 修复：确保返回值是字典类型
        if not isinstance(result, dict):
            print(f"[券列表API] API返回类型错误: {type(result)}")
            return {"resultCode": "-1", "resultDesc": "API响应格式错误", "resultData": None}

        return result

    except Exception as e:
        print(f"[券列表API] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return {"resultCode": "-1", "resultDesc": f"请求异常: {e}", "resultData": None}

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

def get_order_qrcode_api(orderno: str, cinemaid: str, account: dict = None) -> bytes:
    """
    获取订单取票二维码图片（MiniTicket/Cqrcode/generateQrcode/<orderno>） - 使用动态base_url
    :param orderno: 订单号（字符串）
    :param cinemaid: 影院ID
    :param account: 账号信息（包含userid、openid、token等认证信息）
    :return: 二进制图片内容，异常时返回None
    """
    from .api_base import api_base

    if not cinemaid:
        return None

    base_url = api_base.get_base_url_for_cinema(cinemaid)

    # 🔧 修复：构建带认证参数的URL
    if account:
        # 添加认证参数到URL
        auth_params = {
            'userid': account.get('userid', ''),
            'openid': account.get('openid', ''),
            'token': account.get('token', ''),
            'cinemaid': cinemaid,
            'CVersion': '3.9.12',
            'OS': 'Windows',
            'source': '2'
        }

        # 构建带参数的URL
        from urllib.parse import urlencode
        base_path = f'MiniTicket/index.php/Cqrcode/generateQrcode/{orderno}'
        query_string = urlencode(auth_params)
        url = api_base.build_url(base_url, f'{base_path}?{query_string}')
    else:
        # 不带认证参数的URL（向后兼容）
        url = api_base.build_url(base_url, f'MiniTicket/index.php/Cqrcode/generateQrcode/{orderno}')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'Accept': 'image/wxpic,image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Dest': 'image',
        'Accept-Language': 'zh-CN,zh;q=0.9'
        # 🔧 移除Referer参数，按照您的要求
    }

    try:
        print(f"[订单二维码API] 订单号: {orderno}")
        print(f"[订单二维码API] 影院ID: {cinemaid}")
        print(f"[订单二维码API] 请求URL: {url}")
        print(f"[订单二维码API] 请求头: {headers}")

        resp = requests.get(url, headers=headers, timeout=10, verify=False)


        if resp.status_code == 200:
            # 检查响应内容类型
            content_type = resp.headers.get('content-type', '')
            print(f"[订单二维码API] 📊 内容类型: {content_type}")

            # 显示响应内容的前100个字符（用于调试）
            if len(resp.content) > 0:
                try:
                    # 尝试解码为文本（如果是文本响应）
                    content_preview = resp.content[:100].decode('utf-8', errors='ignore')
                except:
                    # 如果是二进制数据，显示十六进制
                    content_preview = resp.content[:50].hex()

                # 检查是否为有效的图片格式
                if resp.content.startswith(b'\x89PNG'):
                    pass
                elif resp.content.startswith(b'\xff\xd8\xff'):
                    pass
                elif resp.content.startswith(b'GIF'):
                    pass
                elif resp.content.startswith(b'<'):
                    pass
                else:
                    pass

            # 🎯 保存二维码图片到本地
            if account:
                try:
                    save_path = save_qrcode_image(resp.content, orderno, account.get('cinemaid', cinemaid))
                    if save_path:
                        print(f"[订单二维码API] 💾 二维码图片已保存: {save_path}")
                except Exception as e:
                    print(f"[订单二维码API] ⚠️ 保存图片失败: {e}")

            return resp.content
        else:
            print(f"[订单二维码API] ❌ HTTP错误: {resp.status_code}")
            print(f"[订单二维码API] ❌ 错误响应内容: {resp.text[:200]}")
            return None
    except Exception as e:
        print(f"[订单二维码API] ❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
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
    获取选券后的价格信息接口（ordercouponPrepay） - 🔧 修复空值处理错误
    :param params: dict，需包含 orderno, couponcode, groupid, cinemaid, cardno, userid, openid, CVersion, OS, token, source
    :return: dict，接口返回的json，确保不返回None
    """
    # 🔧 修复：检查params参数
    if params is None:
        return {"resultCode": "-1", "resultDesc": "参数为空", "resultData": None}

    if not isinstance(params, dict):
        print(f"[券价格API] 参数类型错误: {type(params)}")
        return {"resultCode": "-1", "resultDesc": "参数类型错误", "resultData": None}

    cinemaid = params.get('cinemaid')
    if not cinemaid:
        return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}

    try:
        # 调用API
        result = api_get('MiniTicket/index.php/MiniOrder/ordercouponPrepay', cinemaid, params=params)

        # 🔧 修复：确保返回值不为None
        if result is None:
            print("[券价格API] API返回None，可能是网络异常")
            return {"resultCode": "-1", "resultDesc": "网络异常，API无响应", "resultData": None}

        # 🔧 修复：确保返回值是字典类型
        if not isinstance(result, dict):
            print(f"[券价格API] API返回类型错误: {type(result)}")
            return {"resultCode": "-1", "resultDesc": "API响应格式错误", "resultData": None}

        return result

    except Exception as e:
        print(f"[券价格API] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return {"resultCode": "-1", "resultDesc": f"请求异常: {e}", "resultData": None}

def member_card_pay(params):
    """
    会员卡支付接口 - 支持纯会员卡支付和混合支付
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
        # 🆕 构建会员卡支付参数
        couponcodes = params.get('couponcodes', '')
        payprice = params.get('payprice', '0')

        print(f"[会员卡支付API] 影院ID: {cinemaid}")
        print(f"[会员卡支付API] 订单号: {params.get('orderno')}")
        print(f"[会员卡支付API] 券号: '{couponcodes}'")
        print(f"[会员卡支付API] 支付金额: {payprice}")

        # 🆕 构建会员卡支付专用参数
        member_pay_params = {
            # 基础订单信息
            'orderno': params.get('orderno', ''),
            'cinemaid': cinemaid,
            'userid': params.get('userid', ''),
            'openid': params.get('openid', ''),
            'token': params.get('token', ''),
            'source': params.get('source', '2'),
            'CVersion': params.get('CVersion', '3.9.12'),
            'OS': params.get('OS', 'Windows'),

            # 🆕 会员卡支付特有参数
            'totalprice': payprice,  # 总支付金额
            'couponcodes': couponcodes,  # 券码（空字符串表示纯会员卡支付）
            'price': str(int(int(payprice) // 2)) if payprice.isdigit() else '0',  # 实际单张会员价（示例计算）
            'discountprice': '0' if not couponcodes else params.get('discountprice', '0'),  # 券抵扣金额

            # 🆕 会员信息和密码
            'memberinfo': params.get('memberinfo', '{}'),  # 会员信息JSON
            'mempass': params.get('mempass', ''),  # 会员卡密码

            # 🆕 订单详情信息
            'filmname': params.get('filmname', ''),
            'featureno': params.get('featureno', ''),
            'ticketcount': params.get('ticketcount', '1'),
            'cinemaname': params.get('cinemaname', ''),
            'groupid': params.get('groupid', ''),
            'cardno': params.get('cardno', '')
        }

        print(f"[会员卡支付API] 会员信息: {member_pay_params.get('memberinfo', 'N/A')}")
        print(f"[会员卡支付API] 密码长度: {len(member_pay_params.get('mempass', ''))}")
        print(f"[会员卡支付API] 支付类型: {'混合支付' if couponcodes else '纯会员卡支付'}")

        result = api_post('MiniTicket/index.php/MiniPay/memcardPay', cinemaid, data=member_pay_params, headers=special_headers)

        return result

    except Exception as e:
        print(f"[会员卡支付API] 支付异常: {e}")
        import traceback
        traceback.print_exc()
        return {"resultCode": "-1", "resultDesc": f"会员卡支付异常: {e}", "resultData": None}

def coupon_pay(params):
    """
    券支付接口 - 纯券支付（最终金额为0）
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
        print(f"[券支付API] 影院ID: {cinemaid}")
        print(f"[券支付API] 订单号: {params.get('orderno')}")
        print(f"[券支付API] 券号: {params.get('couponcodes')}")
        print(f"[券支付API] 支付金额: {params.get('payprice')}")

        result = api_post('MiniTicket/index.php/MiniPay/couponPay', cinemaid, data=params, headers=special_headers)

        return result

    except Exception as e:
        print(f"[券支付API] 支付异常: {e}")
        return {"resultCode": "-1", "resultDesc": f"券支付异常: {e}", "resultData": None}

def pay_order(params):
    """
    🆕 智能支付接口 - 根据支付参数自动选择正确的支付接口
    """
    try:
        cinemaid = params.get('cinemaid')
        if not cinemaid:
            return {"resultCode": "-1", "resultDesc": "缺少影院ID参数", "resultData": None}

        # 🆕 获取关键参数进行支付方式判断
        couponcodes = params.get('couponcodes', '')
        payprice = params.get('payprice', '0')

        print(f"[智能支付] 券码: '{couponcodes}'")
        print(f"[智能支付] 支付金额: {payprice}")

        # 🆕 支付接口选择逻辑
        if not couponcodes or couponcodes.strip() == '':
            # 情况1: 纯会员卡支付 - couponcodes为空
            return member_card_pay(params)

        else:
            # 情况2: 有券码 - 需要进一步判断
            try:
                pay_amount = int(payprice) if payprice.isdigit() else 0
            except (ValueError, TypeError):
                pay_amount = 0

            if pay_amount == 0:
                # 情况2a: 纯券支付 - 券完全抵扣，最终金额为0
                return coupon_pay(params)
            else:
                # 情况2b: 混合支付 - 券部分抵扣，剩余金额用会员卡支付
                return member_card_pay(params)

    except Exception as e:
        print(f"[智能支付] 支付方式判断异常: {e}")
        import traceback
        traceback.print_exc()
        return {"resultCode": "-1", "resultDesc": f"支付方式判断异常: {e}", "resultData": None}