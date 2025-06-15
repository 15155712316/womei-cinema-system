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
            "default_token": "47794858a832916d8eda012e7cabd269"  # 有效token（来自HAR文件）
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
    def build_request_headers(cls, token: Optional[str] = None) -> Dict[str, str]:
        """构建请求头"""
        config = cls.get_config()
        api_config = config["api_config"]

        # 使用提供的token或默认token
        auth_token = token or api_config["default_token"]

        headers = cls.COMMON_HEADERS.copy()
        headers.update({
            'x-channel-id': api_config["channel_id"],
            'tenant-short': api_config["tenant_short"],
            'client-version': api_config["client_version"],
            'token': auth_token,
            'referer': f"https://servicewechat.com/{api_config['wx_app_id']}/33/page-frame.html"
        })

        return headers

class WomeiAPIAdapter:
    """沃美影院API适配器"""

    def __init__(self, token: Optional[str] = None):
        """
        初始化API适配器

        Args:
            token: 认证令牌（可选）
        """
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
        """创建订单"""
        data = {
            'seatlable': seatlable,
            'schedule_id': schedule_id
        }
        return self.request('order_ticket', 'POST', data, cinema_id=cinema_id)

    def get_order_info(self, cinema_id: str, order_id: str, version: str = "tp_version") -> Dict[str, Any]:
        """获取订单信息"""
        return self.request('order_info', cinema_id=cinema_id, version=version, order_id=order_id)

# 便捷的工厂函数
def create_womei_api(token: Optional[str] = None) -> WomeiAPIAdapter:
    """创建沃美API适配器实例"""
    return WomeiAPIAdapter(token)

# 使用示例
if __name__ == "__main__":
    # 创建沃美API实例
    api = create_womei_api()

    try:
        # 获取城市列表
        cities = api.get_cities()
        print(f"获取城市列表成功")

        if cities.get('ret') == 0:
            data = cities.get('data', {})
            hot_cities = data.get('hot', [])
            print(f"热门城市数量: {len(hot_cities)}")

    except Exception as e:
        print(f"API调用失败: {e}")
