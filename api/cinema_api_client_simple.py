#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的API客户端 - 解决依赖问题
临时解决方案，避免复杂依赖
"""

import requests
import json
from typing import Dict, Any, Optional

class CinemaAPIClient:
    """电影院API简化客户端"""
    
    def __init__(self, base_url: str = None, default_headers: Dict[str, str] = None):
        self.base_url = base_url or "https://api.example.com"
        self.session = requests.Session()
        self.default_headers = default_headers or {
            'Content-Type': 'application/json',
            'User-Agent': 'CinemaApp/3.9.12'
        }
        self.session.headers.update(self.default_headers)
        
        # API端点配置
        self.endpoints = {
            'login': '/user/login',
            'cinema_list': '/cinema/list',
            'movie_list': '/movie/list',
            'seat_map': '/seat/map',
            'order_create': '/order/create',
            'order_detail': '/order/detail',
            'payment_process': '/payment/process',
            'coupon_list': '/coupon/list',
            'member_info': '/member/info'
        }
    
    def request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[str, Any]]:
        """统一API请求方法"""
        try:
            url = self._build_url(endpoint)
            
            # 添加默认参数
            if 'timeout' not in kwargs:
                kwargs['timeout'] = 30
            
            response = self.session.request(method.upper(), url, **kwargs)
            return self._handle_response(response)
        except Exception as e:
            print(f"API请求失败: {e}")
            return None
    
    def _build_url(self, endpoint: str) -> str:
        """构建完整URL"""
        if endpoint.startswith('http'):
            return endpoint
        
        # 如果是预定义端点
        if endpoint in self.endpoints:
            endpoint = self.endpoints[endpoint]
        
        return f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def _handle_response(self, response: requests.Response) -> Optional[Dict[str, Any]]:
        """处理API响应"""
        try:
            if response.status_code == 200:
                result = json.loads(response.text)
                if result and result.get('success', True):
                    return result
                else:
                    error_msg = result.get('message', '未知错误') if result else 'API返回格式错误'
                    raise APIException(f"API业务错误: {error_msg}")
            else:
                raise APIException(f"HTTP错误: {response.status_code}")
                
        except json.JSONDecodeError:
            raise APIException("响应不是有效的JSON格式")
    
    # 具体业务API方法
    def login(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户登录"""
        data = {
            'username': username,
            'password': password,
            'version': '3.9.12'
        }
        return self.request('POST', 'login', json=data)
    
    def get_cinema_list(self, city_id: str = None) -> Optional[Dict[str, Any]]:
        """获取影院列表"""
        params = {}
        if city_id:
            params['city_id'] = city_id
        return self.request('GET', 'cinema_list', params=params)
    
    def get_movie_list(self, cinema_id: str) -> Optional[Dict[str, Any]]:
        """获取电影列表"""
        params = {'cinema_id': cinema_id}
        return self.request('GET', 'movie_list', params=params)
    
    def get_seat_map(self, show_id: str) -> Optional[Dict[str, Any]]:
        """获取座位图"""
        params = {'show_id': show_id}
        return self.request('GET', 'seat_map', params=params)
    
    def create_order(self, order_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建订单"""
        return self.request('POST', 'order_create', json=order_data)
    
    def get_order_detail(self, order_id: str, user_token: str) -> Optional[Dict[str, Any]]:
        """获取订单详情"""
        params = {
            'order_id': order_id,
            'token': user_token
        }
        return self.request('GET', 'order_detail', params=params)
    
    def process_payment(self, payment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理支付"""
        return self.request('POST', 'payment_process', json=payment_data)
    
    def get_coupon_list(self, user_id: str, user_token: str) -> Optional[Dict[str, Any]]:
        """获取优惠券列表"""
        params = {
            'user_id': user_id,
            'token': user_token
        }
        return self.request('GET', 'coupon_list', params=params)
    
    def get_member_info(self, user_id: str, user_token: str) -> Optional[Dict[str, Any]]:
        """获取会员信息"""
        params = {
            'user_id': user_id,
            'token': user_token
        }
        return self.request('GET', 'member_info', params=params)

class APIException(Exception):
    """API异常类"""
    pass

# 全局API客户端实例
api_client = CinemaAPIClient()

def get_api_client() -> CinemaAPIClient:
    """获取API客户端实例"""
    return api_client

def set_api_base_url(base_url: str):
    """设置API基础URL"""
    global api_client
    api_client.base_url = base_url

def set_api_headers(headers: Dict[str, str]):
    """设置API请求头"""
    global api_client
    api_client.session.headers.update(headers)
