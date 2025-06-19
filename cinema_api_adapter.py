"""
沃美影院API适配器 - Python版本
专门用于沃美影院系统的API调用接口
"""

import requests
import urllib3
from typing import Dict, Any, Optional, List
import json

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WomeiConfig:
    """沃美影院系统配置类"""

    # 沃美系统配置
    CONFIG = {
        "system_name": "沃美连锁影院",
        "api_config": {
            "base_url": "https://ct.womovie.cn",
            "tenant_short": "wmyc",
            "channel_id": "40000",
            "client_version": "4.0",
            "wx_app_id": "wx4bb9342b9d97d53c",
            "default_token": None  # 不使用默认token，必须从accounts.json加载
        },
        "endpoints": {
            # 基础端点（不需要cinema_id）
            "cities": "/ticket/{tenant_short}/citys/",

            # 影院相关端点（需要cinema_id）
            "cinema_info": "/ticket/{tenant_short}/cinema/{cinema_id}/info/",
            "movies": "/ticket/{tenant_short}/cinema/{cinema_id}/movies/",
            "shows": "/ticket/{tenant_short}/cinema/{cinema_id}/shows/",

            # 座位相关端点
            "hall_info": "/ticket/{tenant_short}/cinema/{cinema_id}/hall/info/",
            "hall_saleable": "/ticket/{tenant_short}/cinema/{cinema_id}/hall/saleable/",

            # 订单相关端点
            "order_ticket": "/ticket/{tenant_short}/cinema/{cinema_id}/order/ticket/",
            "order_info": "/ticket/{tenant_short}/cinema/{cinema_id}/order/info/",
            "order_change": "/ticket/{tenant_short}/cinema/{cinema_id}/order/change/",

            # 用户相关端点
            "user_info": "/ticket/{tenant_short}/cinema/{cinema_id}/user/info/",
            "user_cards": "/ticket/{tenant_short}/cinema/{cinema_id}/user/cards/",
            "user_vouchers": "/ticket/{tenant_short}/cinema/{cinema_id}/user/vouchers",
            "user_check_phone": "/ticket/{tenant_short}/user/check_phone/",

            # 会员相关端点
            "member_card": "/ticket/{tenant_short}/cinema/{cinema_id}/member/card/auto_solid/",

            # 广告相关端点
            "cinema_ads": "/ticket/{tenant_short}/cinema/{cinema_id}/ads/"
        }
    }
    
    # 通用请求头
    COMMON_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13639',
        'content-type': 'multipart/form-data',
        'xweb_xhr': '1',
        'x-requested-with': 'wxapp',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9',
        'priority': 'u=1, i'
    }

    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """获取沃美系统配置"""
        return cls.CONFIG

    @classmethod
    def build_api_url(cls, endpoint: str, cinema_id: str = None, **params) -> str:
        """构建API完整URL，支持cinema_id参数"""
        config = cls.get_config()
        api_config = config["api_config"]
        endpoint_path = config["endpoints"].get(endpoint)

        if not endpoint_path:
            raise ValueError(f"不支持的接口端点: {endpoint}")

        # 替换路径中的占位符
        path = endpoint_path.format(
            tenant_short=api_config["tenant_short"],
            cinema_id=cinema_id or ""
        )

        url = f"{api_config['base_url']}{path}"

        # 添加查询参数
        if params:
            query_string = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
            if query_string:
                url += f"?{query_string}"

        return url

    @classmethod
    def build_request_headers(cls, token: str) -> Dict[str, str]:
        """构建请求头 - 必须提供token"""
        if not token:
            raise ValueError("Token是必需的，请从accounts.json文件加载")

        config = cls.get_config()
        api_config = config["api_config"]

        headers = cls.COMMON_HEADERS.copy()
        headers.update({
            'x-channel-id': api_config["channel_id"],
            'tenant-short': api_config["tenant_short"],
            'client-version': api_config["client_version"],
            'token': token,
            'referer': f"https://servicewechat.com/{api_config['wx_app_id']}/33/page-frame.html"
        })

        return headers

class WomeiAPIAdapter:
    """沃美影院API适配器"""

    def __init__(self, token: str):
        """
        初始化API适配器

        Args:
            token: 认证令牌（必需）
        """
        if not token:
            raise ValueError("Token是必需的，请从accounts.json文件加载")

        self.token = token
        self.session = requests.Session()

        # 设置默认超时
        self.session.timeout = 30
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token

    def request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None,
                cinema_id: str = None, **params) -> Dict[str, Any]:
        """
        执行HTTP请求

        Args:
            endpoint: 接口端点
            method: 请求方法
            data: 请求数据
            cinema_id: 影院ID（沃美系统需要）
            **params: 查询参数

        Returns:
            API响应数据
        """
        url = WomeiConfig.build_api_url(endpoint, cinema_id, **params)
        headers = WomeiConfig.build_request_headers(self.token)

        try:
            print(f"[沃美] 请求API: {url}")

            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, verify=False)
            elif method.upper() == 'POST':
                # 移除content-type让requests自动设置multipart/form-data
                headers_copy = headers.copy()
                headers_copy.pop('content-type', None)
                response = self.session.post(url, headers=headers_copy, data=data, verify=False)
            else:
                raise ValueError(f"不支持的请求方法: {method}")

            response.raise_for_status()

            result = response.json()
            print(f"[沃美] API响应成功")

            return result

        except requests.exceptions.RequestException as e:
            print(f"[沃美] API请求失败: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"[沃美] JSON解析失败: {e}")
            raise
    
    def get_cities(self) -> Dict[str, Any]:
        """获取城市列表"""
        return self.request('cities')

    def get_cinema_info(self, cinema_id: str) -> Dict[str, Any]:
        """获取影院信息"""
        return self.request('cinema_info', cinema_id=cinema_id)

    def get_movies(self, cinema_id: str) -> Dict[str, Any]:
        """获取指定影院的电影列表"""
        return self.request('movies', cinema_id=cinema_id)

    def get_shows(self, cinema_id: str, movie_id: str) -> Dict[str, Any]:
        """获取电影场次列表"""
        return self.request('shows', cinema_id=cinema_id, movie_id=movie_id)

    def get_hall_info(self, cinema_id: str, hall_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取影厅座位信息"""
        return self.request('hall_info', cinema_id=cinema_id, hall_id=hall_id, schedule_id=schedule_id)

    def get_hall_saleable(self, cinema_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取可售座位信息"""
        return self.request('hall_saleable', cinema_id=cinema_id, schedule_id=schedule_id)

    def create_order(self, cinema_id: str, seatlable: str, schedule_id: str) -> Dict[str, Any]:
        """创建订单 - 使用真实的沃美系统格式"""
        # 🔧 修复：使用真实的沃美系统订单创建API
        url = f"https://ct.womovie.cn/ticket/wmyc/cinema/{cinema_id}/order/ticket/"

        # 🔧 修复：使用正确的请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c33)XWEB/13839',
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-channel-id': '40000',
            'tenant-short': 'wmyc',
            'client-version': '4.0',
            'xweb_xhr': '1',
            'x-requested-with': 'wxapp',
            'token': self.token,
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://servicewechat.com/wx4bb9342b9d97d53c/33/page-frame.html',
            'accept-language': 'zh-CN,zh;q=0.9',
            'priority': 'u=1, i'
        }

        # 🔧 修复：使用form-urlencoded格式的数据
        data = {
            'seatlable': seatlable,
            'schedule_id': schedule_id
        }

        print(f"[沃美订单API] 🚀 创建订单请求:")
        print(f"  - URL: {url}")
        print(f"  - 座位参数: {seatlable}")
        print(f"  - 场次ID: {schedule_id}")
        print(f"  - Token: {self.token[:20]}...")

        try:
            import requests
            response = requests.post(url, data=data, headers=headers, timeout=30, verify=False)

            print(f"[沃美订单API] 📥 响应状态: {response.status_code}")
            print(f"[沃美订单API] 📥 响应内容: {response.text[:500]}...")

            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"[沃美订单API] ✅ 解析成功: {result}")
                    return result
                except Exception as e:
                    print(f"[沃美订单API] ❌ JSON解析失败: {e}")
                    return {"ret": -1, "msg": f"响应解析失败: {e}", "data": {}}
            else:
                print(f"[沃美订单API] ❌ HTTP错误: {response.status_code}")
                return {"ret": -1, "msg": f"HTTP错误: {response.status_code}", "data": {}}

        except Exception as e:
            print(f"[沃美订单API] ❌ 请求异常: {e}")
            return {"ret": -1, "msg": f"请求异常: {e}", "data": {}}

    def get_order_info(self, cinema_id: str, order_id: str, version: str = "tp_version") -> Dict[str, Any]:
        """获取订单信息"""
        return self.request('order_info', cinema_id=cinema_id, version=version, order_id=order_id)

# 便捷的工厂函数
def create_womei_api(token: str) -> WomeiAPIAdapter:
    """创建沃美API适配器实例 - 必须提供token"""
    return WomeiAPIAdapter(token)

# 使用示例
if __name__ == "__main__":
    print("请从accounts.json文件加载token后使用API")
    print("示例:")
    print("  import json")
    print("  with open('data/accounts.json', 'r') as f:")
    print("      accounts = json.load(f)")
    print("  token = accounts[0]['token']")
    print("  api = create_womei_api(token)")
