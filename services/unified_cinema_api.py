#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一影院API服务
支持多个影院连锁系统的统一API调用接口
"""

import requests
import json
from typing import Dict, List, Any, Optional, Union
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from config.cinema_systems_config import (
    CinemaSystemType, 
    CinemaSystemConfig, 
    cinema_system_manager
)

class UnifiedCinemaAPI:
    """统一影院API类"""
    
    def __init__(self, system_type: Optional[CinemaSystemType] = None, token: Optional[str] = None):
        """
        初始化API实例
        
        Args:
            system_type: 影院系统类型，如果不提供则使用当前系统
            token: 认证令牌
        """
        self.system_type = system_type or cinema_system_manager.get_current_system()
        self.token = token or cinema_system_manager.current_token
        
        if not self.system_type:
            raise ValueError("必须指定影院系统类型或设置当前系统")
        
        self.session = requests.Session()
        self.session.timeout = 30
        
        # 获取系统配置
        self.config = CinemaSystemConfig.get_system_config(self.system_type)
        self.api_config = self.config["api_config"]
        
        print(f"[统一API] 初始化 {self.config['system_name']} API服务")
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        cinema_system_manager.current_token = token
    
    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行HTTP请求

        Args:
            endpoint: 接口端点名称
            method: 请求方法
            data: 请求数据

        Returns:
            API响应数据
        """
        url = CinemaSystemConfig.build_api_url(self.system_type, endpoint)
        headers = CinemaSystemConfig.build_request_headers(self.system_type, self.token)

        # 🔍 详细调试输出
        print(f"\n{'='*60}")
        print(f"🌐 API请求调试信息 - {self.config['system_name']}")
        print(f"{'='*60}")
        print(f"📍 请求URL: {url}")
        print(f"🔧 请求方法: {method}")
        print(f"📊 系统类型: {self.system_type.value}")

        print(f"\n📋 请求头信息:")
        for key, value in headers.items():
            # 隐藏敏感信息的部分内容
            if key.lower() == 'token' and len(value) > 10:
                display_value = value[:8] + "..." + value[-4:]
            else:
                display_value = value
            print(f"  {key}: {display_value}")

        if data:
            print(f"\n📦 请求数据:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"\n📦 请求数据: 无")

        # 生成等效的curl命令
        print(f"\n🔄 等效curl命令:")
        curl_cmd = f"curl -X {method} '{url}'"
        for key, value in headers.items():
            curl_cmd += f" \\\n  -H '{key}: {value}'"
        if data and method.upper() == 'POST':
            for key, value in data.items():
                curl_cmd += f" \\\n  -d '{key}={value}'"
        print(curl_cmd)
        print(f"{'='*60}")

        try:
            print(f"🚀 发送请求...")

            if method.upper() == 'GET':
                response = self.session.get(url, headers=headers, params=data, verify=False)
            elif method.upper() == 'POST':
                # 移除content-type让requests自动设置multipart/form-data
                headers_copy = headers.copy()
                headers_copy.pop('content-type', None)
                response = self.session.post(url, headers=headers_copy, data=data, verify=False)
            else:
                raise ValueError(f"不支持的请求方法: {method}")

            # 🔍 响应调试信息
            print(f"\n📥 响应信息:")
            print(f"  状态码: {response.status_code}")
            print(f"  响应头: {dict(response.headers)}")
            print(f"  响应大小: {len(response.content)} 字节")

            # 显示响应内容（前500字符）
            response_text = response.text
            print(f"  响应内容预览: {response_text[:500]}{'...' if len(response_text) > 500 else ''}")

            response.raise_for_status()
            result = response.json()

            print(f"✅ 请求成功，返回数据类型: {type(result)}")
            if isinstance(result, dict):
                print(f"   字典键: {list(result.keys())}")
            elif isinstance(result, list):
                print(f"   列表长度: {len(result)}")
                if result:
                    print(f"   第一个元素类型: {type(result[0])}")
                    if isinstance(result[0], dict):
                        print(f"   第一个元素键: {list(result[0].keys())}")

            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"   响应状态码: {e.response.status_code}")
                print(f"   响应内容: {e.response.text[:200]}...")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            print(f"   原始响应: {response.text[:200]}...")
            raise
    
    def get_cities(self) -> List[Dict[str, Any]]:
        """
        获取城市列表

        Returns:
            城市列表，统一格式：
            [
                {
                    "id": "城市ID",
                    "name": "城市名称",
                    "code": "城市代码",
                    "system_type": "系统类型"
                }
            ]
        """
        try:
            raw_data = self._make_request('cities')

            print(f"🔍 原始响应数据类型: {type(raw_data)}")
            if isinstance(raw_data, dict):
                print(f"🔍 响应字典键: {list(raw_data.keys())}")

            # 数据格式标准化
            cities = []

            # 处理沃美/华联API的标准响应格式
            if isinstance(raw_data, dict):
                if 'ret' in raw_data and 'data' in raw_data:
                    # 沃美格式: {"ret": 0, "msg": "successfully", "data": {"hot": [...], "normal": [...]}}
                    print(f"🔍 检测到沃美API格式")
                    data_section = raw_data['data']

                    # 合并热门城市和普通城市
                    all_cities = []
                    if 'hot' in data_section and isinstance(data_section['hot'], list):
                        all_cities.extend(data_section['hot'])
                        print(f"🔍 热门城市数量: {len(data_section['hot'])}")

                    if 'normal' in data_section and isinstance(data_section['normal'], list):
                        all_cities.extend(data_section['normal'])
                        print(f"🔍 普通城市数量: {len(data_section['normal'])}")

                    # 去重处理（基于city_id）
                    seen_ids = set()
                    for city_data in all_cities:
                        city_id = city_data.get('city_id')
                        if city_id and city_id not in seen_ids:
                            seen_ids.add(city_id)
                            city = {
                                "id": str(city_id),
                                "name": city_data.get('city_name', '未知城市'),
                                "code": city_data.get('city_pinyin', ''),
                                "cinema_total": city_data.get('cinema_total', 0),
                                "system_type": self.system_type.value,
                                "raw_data": city_data
                            }
                            cities.append(city)

                elif 'data' in raw_data and isinstance(raw_data['data'], list):
                    # 华联格式: {"data": [...]}
                    print(f"🔍 检测到华联API格式")
                    for city_data in raw_data['data']:
                        city = {
                            "id": city_data.get('id') or city_data.get('cityId') or city_data.get('code'),
                            "name": city_data.get('name') or city_data.get('cityName'),
                            "code": city_data.get('code') or city_data.get('cityCode'),
                            "system_type": self.system_type.value,
                            "raw_data": city_data
                        }
                        cities.append(city)

                else:
                    # 直接是城市数据的字典
                    print(f"🔍 检测到直接字典格式")
                    city = {
                        "id": raw_data.get('id') or raw_data.get('cityId') or raw_data.get('city_id'),
                        "name": raw_data.get('name') or raw_data.get('cityName') or raw_data.get('city_name'),
                        "code": raw_data.get('code') or raw_data.get('cityCode') or raw_data.get('city_pinyin'),
                        "system_type": self.system_type.value,
                        "raw_data": raw_data
                    }
                    cities.append(city)

            elif isinstance(raw_data, list):
                # 直接是城市数组
                print(f"🔍 检测到直接数组格式")
                for city_data in raw_data:
                    city = {
                        "id": city_data.get('id') or city_data.get('cityId') or city_data.get('city_id'),
                        "name": city_data.get('name') or city_data.get('cityName') or city_data.get('city_name'),
                        "code": city_data.get('code') or city_data.get('cityCode') or city_data.get('city_pinyin'),
                        "system_type": self.system_type.value,
                        "raw_data": city_data
                    }
                    cities.append(city)

            print(f"✅ [统一API] 成功解析 {len(cities)} 个城市")
            if cities:
                print(f"🔍 第一个城市示例: {cities[0]}")

            return cities

        except Exception as e:
            print(f"❌ [统一API] 获取城市列表失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_cinemas(self, city_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取影院列表
        
        Args:
            city_id: 城市ID，如果不提供则获取所有影院
            
        Returns:
            影院列表，统一格式
        """
        try:
            data = {'cityId': city_id} if city_id else None
            method = 'POST' if city_id else 'GET'
            
            raw_data = self._make_request('cinemas', method, data)
            
            # 数据格式标准化
            cinemas = []
            cinema_list = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
            
            for cinema_data in cinema_list:
                cinema = {
                    "id": cinema_data.get('id') or cinema_data.get('cinemaId') or cinema_data.get('cinemaid'),
                    "name": cinema_data.get('name') or cinema_data.get('cinemaName') or cinema_data.get('cinemaShortName'),
                    "address": cinema_data.get('address') or cinema_data.get('cinemaAddress'),
                    "phone": cinema_data.get('phone') or cinema_data.get('cinemaPhone'),
                    "city_id": city_id,
                    "system_type": self.system_type.value,
                    "raw_data": cinema_data
                }
                cinemas.append(cinema)
            
            print(f"[统一API] 获取到 {len(cinemas)} 个影院")
            return cinemas
            
        except Exception as e:
            print(f"[统一API] 获取影院列表失败: {e}")
            return []
    
    def get_movies(self, cinema_id: str) -> List[Dict[str, Any]]:
        """
        获取电影列表
        
        Args:
            cinema_id: 影院ID
            
        Returns:
            电影列表，统一格式
        """
        try:
            data = {'cinemaId': cinema_id}
            raw_data = self._make_request('movies', 'POST', data)
            
            # 数据格式标准化
            movies = []
            movie_list = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
            
            for movie_data in movie_list:
                movie = {
                    "id": movie_data.get('id') or movie_data.get('movieId') or movie_data.get('fc'),
                    "name": movie_data.get('name') or movie_data.get('movieName') or movie_data.get('fn'),
                    "duration": movie_data.get('duration') or movie_data.get('movieDuration'),
                    "type": movie_data.get('type') or movie_data.get('movieType'),
                    "poster": movie_data.get('poster') or movie_data.get('moviePoster'),
                    "cinema_id": cinema_id,
                    "system_type": self.system_type.value,
                    "raw_data": movie_data
                }
                movies.append(movie)
            
            print(f"[统一API] 获取到 {len(movies)} 部电影")
            return movies
            
        except Exception as e:
            print(f"[统一API] 获取电影列表失败: {e}")
            return []
    
    def get_sessions(self, cinema_id: str, movie_id: str, date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取场次列表
        
        Args:
            cinema_id: 影院ID
            movie_id: 电影ID
            date: 日期（可选）
            
        Returns:
            场次列表，统一格式
        """
        try:
            data = {
                'cinemaId': cinema_id,
                'movieId': movie_id
            }
            if date:
                data['date'] = date
            
            raw_data = self._make_request('sessions', 'POST', data)
            
            # 数据格式标准化
            sessions = []
            session_list = raw_data if isinstance(raw_data, list) else raw_data.get('data', [])
            
            for session_data in session_list:
                session = {
                    "id": session_data.get('id') or session_data.get('sessionId') or session_data.get('seqno'),
                    "time": session_data.get('time') or session_data.get('sessionTime') or session_data.get('st'),
                    "date": session_data.get('date') or session_data.get('sessionDate'),
                    "hall": session_data.get('hall') or session_data.get('hallName') or session_data.get('hname'),
                    "price": session_data.get('price') or session_data.get('sessionPrice'),
                    "cinema_id": cinema_id,
                    "movie_id": movie_id,
                    "system_type": self.system_type.value,
                    "raw_data": session_data
                }
                sessions.append(session)
            
            print(f"[统一API] 获取到 {len(sessions)} 个场次")
            return sessions
            
        except Exception as e:
            print(f"[统一API] 获取场次列表失败: {e}")
            return []
    
    def get_seats(self, session_id: str) -> Dict[str, Any]:
        """
        获取座位图
        
        Args:
            session_id: 场次ID
            
        Returns:
            座位图数据，统一格式
        """
        try:
            data = {'sessionId': session_id}
            raw_data = self._make_request('seats', 'POST', data)
            
            # 数据格式标准化
            seat_data = {
                "session_id": session_id,
                "hall_name": raw_data.get('hallName') or raw_data.get('hname'),
                "seat_matrix": raw_data.get('seatMatrix') or raw_data.get('seats'),
                "system_type": self.system_type.value,
                "raw_data": raw_data
            }
            
            print(f"[统一API] 获取座位图成功: {seat_data['hall_name']}")
            return seat_data
            
        except Exception as e:
            print(f"[统一API] 获取座位图失败: {e}")
            return {}

class CinemaAPIFactory:
    """影院API工厂类"""
    
    @staticmethod
    def create_api(system_type: CinemaSystemType, token: Optional[str] = None) -> UnifiedCinemaAPI:
        """创建指定系统的API实例"""
        return UnifiedCinemaAPI(system_type, token)
    
    @staticmethod
    def create_huanlian_api(token: Optional[str] = None) -> UnifiedCinemaAPI:
        """创建华联影院API实例"""
        return UnifiedCinemaAPI(CinemaSystemType.HUANLIAN, token)
    
    @staticmethod
    def create_womei_api(token: Optional[str] = None) -> UnifiedCinemaAPI:
        """创建沃美影院API实例"""
        return UnifiedCinemaAPI(CinemaSystemType.WOMEI, token)
    
    @staticmethod
    def create_current_api(token: Optional[str] = None) -> UnifiedCinemaAPI:
        """创建当前系统的API实例"""
        current_system = cinema_system_manager.get_current_system()
        if not current_system:
            raise ValueError("未设置当前影院系统")
        return UnifiedCinemaAPI(current_system, token)

# 导出主要类
__all__ = [
    'UnifiedCinemaAPI',
    'CinemaAPIFactory'
]
