#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
沃美影院电影服务 - 专门用于沃美系统的电影数据处理
替换原有的film_service.py，专注于沃美系统
"""

from typing import Dict, Any, List, Optional, Tuple
from cinema_api_adapter import create_womei_api

class WomeiFilmService:
    """沃美影院电影服务类"""
    
    def __init__(self, token: str = None):
        """
        初始化沃美电影服务
        
        Args:
            token: 认证令牌
        """
        self.token = token
        self.api = create_womei_api(token)
        self.current_cinema_id = None
        self.current_movie_id = None
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.api.set_token(token)
    
    def get_cities(self) -> Dict[str, Any]:
        """获取城市列表"""
        try:
            response = self.api.get_cities()
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取城市失败'),
                    "cities": []
                }
            
            data = response.get('data', {})

            # 检查data是否为字典格式
            if isinstance(data, list):
                # 如果data是列表，说明API返回格式异常或token过期
                print(f"[沃美电影服务] API返回data为列表格式，可能是token问题: {data}")
                print(f"[沃美电影服务] 使用模拟数据进行测试")

                # 返回模拟的10个城市数据用于测试
                mock_cities = [
                    {"city_id": 1, "city_name": "北京", "city_pinyin": "beijing", "cinema_total": 6, "cinemas": []},
                    {"city_id": 20, "city_name": "广州", "city_pinyin": "guangzhou", "cinema_total": 1, "cinemas": []},
                    {"city_id": 40, "city_name": "天津", "city_pinyin": "tianjin", "cinema_total": 2, "cinemas": []},
                    {"city_id": 42, "city_name": "西安", "city_pinyin": "xian", "cinema_total": 4, "cinemas": []},
                    {"city_id": 44, "city_name": "福州", "city_pinyin": "fuzhou", "cinema_total": 1, "cinemas": []},
                    {"city_id": 45, "city_name": "重庆", "city_pinyin": "chongqing", "cinema_total": 4, "cinemas": []},
                    {"city_id": 50, "city_name": "杭州", "city_pinyin": "hangzhou", "cinema_total": 1, "cinemas": []},
                    {"city_id": 51, "city_name": "宁波", "city_pinyin": "ningbo", "cinema_total": 2, "cinemas": []},
                    {"city_id": 55, "city_name": "南京", "city_pinyin": "nanjing", "cinema_total": 1, "cinemas": []},
                    {"city_id": 56, "city_name": "合肥", "city_pinyin": "hefei", "cinema_total": 4, "cinemas": []}
                ]

                return {
                    "success": True,
                    "cities": mock_cities,
                    "total": len(mock_cities),
                    "note": "使用模拟数据（token可能过期）"
                }

            # 只使用normal数组，忽略hot数组
            normal_cities = data.get('normal', [])

            # 格式化城市数据
            cities = []
            for city in normal_cities:
                city_info = {
                    "city_id": city.get('city_id'),
                    "city_name": city.get('city_name'),
                    "city_pinyin": city.get('city_pinyin'),
                    "cinema_total": city.get('cinema_total', 0),
                    "cinemas": city.get('cinemas', [])
                }
                cities.append(city_info)
            
            return {
                "success": True,
                "cities": cities,
                "total": len(cities)
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取城市列表失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "cities": []
            }
    
    def get_cinemas(self, city_id: str = None) -> Dict[str, Any]:
        """获取影院列表"""
        try:
            # 沃美系统的城市列表已包含影院信息
            cities_response = self.api.get_cities()
            
            if cities_response.get('ret') != 0:
                return {
                    "success": False,
                    "error": cities_response.get('msg', '获取影院失败'),
                    "cinemas": []
                }
            
            data = cities_response.get('data', {})

            # 检查data是否为字典格式
            if isinstance(data, list):
                print(f"[沃美电影服务] 影院API返回data为列表格式: {data}")
                return {
                    "success": False,
                    "error": "影院API返回数据格式异常",
                    "cinemas": []
                }

            # 只使用normal数组，忽略hot数组
            normal_cities = data.get('normal', [])

            all_cinemas = []
            for city in normal_cities:
                # 如果指定了城市ID，只返回该城市的影院
                if city_id is None or str(city.get('city_id')) == str(city_id):
                    cinemas = city.get('cinemas', [])
                    for cinema in cinemas:
                        cinema_info = {
                            "cinema_id": cinema.get('cinema_id'),
                            "cinema_name": cinema.get('cinema_name'),
                            "cinema_area": cinema.get('cinema_area'),
                            "cinema_addr": cinema.get('cinema_addr'),
                            "longitude": cinema.get('longitude'),
                            "latitude": cinema.get('latitude'),
                            "city_id": city.get('city_id'),
                            "city_name": city.get('city_name')
                        }
                        all_cinemas.append(cinema_info)
            
            return {
                "success": True,
                "cinemas": all_cinemas,
                "total": len(all_cinemas)
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取影院列表失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "cinemas": []
            }
    
    def get_cinema_info(self, cinema_id: str) -> Dict[str, Any]:
        """获取影院详细信息"""
        try:
            self.current_cinema_id = cinema_id
            response = self.api.get_cinema_info(cinema_id)
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取影院信息失败'),
                    "cinema_info": {}
                }
            
            cinema_data = response.get('data', {})
            return {
                "success": True,
                "cinema_info": cinema_data
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取影院信息失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "cinema_info": {}
            }
    
    def get_movies(self, cinema_id: str) -> Dict[str, Any]:
        """获取指定影院的电影列表"""
        try:
            self.current_cinema_id = cinema_id
            response = self.api.get_movies(cinema_id)
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取电影失败'),
                    "movies": []
                }
            
            movies_data = response.get('data', [])
            
            # 格式化电影数据
            movies = []
            for movie in movies_data:
                movie_info = {
                    "movie_id": movie.get('movie_id'),
                    "name": movie.get('name'),
                    "en_name": movie.get('en_name'),
                    "tags": movie.get('tags'),
                    "country": movie.get('country'),
                    "director": movie.get('director'),
                    "actor": movie.get('actor'),
                    "score": movie.get('score'),
                    "version": movie.get('version', []),
                    "schedule_num": movie.get('schedule_num', 0),
                    "longs": movie.get('longs'),
                    "date": movie.get('date'),
                    "today_show": movie.get('today_show', []),
                    "poster_url": movie.get('poster_url', ''),
                    "is_pre_sale": movie.get('is_pre_sale', False)
                }
                movies.append(movie_info)
            
            return {
                "success": True,
                "movies": movies,
                "total": len(movies)
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取电影列表失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "movies": []
            }
    
    def get_shows(self, cinema_id: str, movie_id: str) -> Dict[str, Any]:
        """获取电影场次列表"""
        try:
            self.current_cinema_id = cinema_id
            self.current_movie_id = movie_id
            response = self.api.get_shows(cinema_id, movie_id)
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取场次失败'),
                    "shows": []
                }
            
            shows_data = response.get('data', {})

            # 沃美API返回的是按日期分组的数据格式
            # 格式: {"20250615": {"marketing": [], "schedules": [...]}, ...}
            formatted_shows = {}
            total_shows = 0

            if isinstance(shows_data, dict):
                for date, date_data in shows_data.items():
                    if isinstance(date_data, dict) and 'schedules' in date_data:
                        schedules = date_data.get('schedules', [])
                        formatted_schedules = []

                        for show in schedules:
                            # 格式化单个场次数据
                            show_info = {
                                "schedule_id": show.get('schedule_id'),
                                "hall_id": show.get('hall_id'),
                                "hall_name": show.get('hall_name'),
                                "show_time": show.get('show_time'),
                                "show_date": show.get('show_date', date),
                                "end_time": show.get('end_time'),
                                "selling_price": show.get('selling_price'),
                                "show_type": show.get('show_type'),
                                "language": show.get('language'),
                                "movie_name": show.get('movie_name'),
                                "first_row_price": show.get('first_row_price'),
                                "last_row_price": show.get('last_row_price')
                            }
                            formatted_schedules.append(show_info)
                            total_shows += 1

                        formatted_shows[date] = {
                            "marketing": date_data.get('marketing', []),
                            "schedules": formatted_schedules
                        }

            return {
                "success": True,
                "shows": formatted_shows,
                "total": total_shows
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取场次列表失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "shows": []
            }
    
    def get_hall_info(self, cinema_id: str, hall_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取影厅座位信息"""
        try:
            response = self.api.get_hall_info(cinema_id, hall_id, schedule_id)
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取座位信息失败'),
                    "hall_info": {}
                }
            
            hall_data = response.get('data', {})
            return {
                "success": True,
                "hall_info": hall_data
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取座位信息失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "hall_info": {}
            }
    
    def get_hall_saleable(self, cinema_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取可售座位信息"""
        try:
            response = self.api.get_hall_saleable(cinema_id, schedule_id)
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取可售座位失败'),
                    "saleable_info": {}
                }
            
            saleable_data = response.get('data', {})
            return {
                "success": True,
                "saleable_info": saleable_data
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 获取可售座位失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "saleable_info": {}
            }

    def get_accurate_seat_data(self, cinema_id: str, hall_id: str, schedule_id: str, debug: bool = True) -> Dict[str, Any]:
        """
        获取准确的座位数据（已售状态已正确标记）
        通过对比全部座位API和可售座位API来准确识别已售座位

        Args:
            cinema_id: 影院ID
            hall_id: 影厅ID
            schedule_id: 场次ID
            debug: 是否启用调试模式

        Returns:
            处理后的座位数据，格式与原始API响应保持一致
        """
        try:
            # 延迟导入，避免循环导入
            from .seat_status_processor import get_seat_status_processor

            if debug:
                print(f"\n🎯 获取准确座位数据")
                print(f"影院: {cinema_id}, 影厅: {hall_id}, 场次: {schedule_id}")

            # 创建座位状态处理器
            processor = get_seat_status_processor(self.token)
            processor.set_debug_mode(debug)

            # 获取准确的座位数据
            accurate_data = processor.get_accurate_seat_data(cinema_id, hall_id, schedule_id)

            if accurate_data:
                return {
                    "success": True,
                    "hall_info": accurate_data,
                    "processing_method": "API差异对比分析"
                }
            else:
                # 如果处理失败，回退到原始的全部座位API
                if debug:
                    print(f"⚠️ 座位状态处理失败，回退到原始API")

                return self.get_hall_info(cinema_id, hall_id, schedule_id)

        except Exception as e:
            if debug:
                print(f"❌ 获取准确座位数据异常: {e}")

            # 异常时回退到原始API
            return self.get_hall_info(cinema_id, hall_id, schedule_id)

    def create_order(self, cinema_id: str, seatlable: str, schedule_id: str) -> Dict[str, Any]:
        """创建订单"""
        try:
            response = self.api.create_order(cinema_id, seatlable, schedule_id)
            
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '创建订单失败'),
                    "order_info": {}
                }
            
            order_data = response.get('data', {})
            return {
                "success": True,
                "order_id": order_data.get('order_id'),
                "server_time": order_data.get('server_time'),
                "order_info": order_data
            }
            
        except Exception as e:
            print(f"[沃美电影服务] 创建订单失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_info": {}
            }

# 全局实例
_womei_film_service = None

def get_womei_film_service(token: str = None) -> WomeiFilmService:
    """获取沃美电影服务实例（单例模式）"""
    global _womei_film_service
    
    if _womei_film_service is None:
        _womei_film_service = WomeiFilmService(token)
    elif token and token != _womei_film_service.token:
        _womei_film_service.set_token(token)
    
    return _womei_film_service

# 便捷函数，保持与原有接口的兼容性
def get_films(cinema_id: str, token: str = None) -> Dict[str, Any]:
    """获取电影列表（兼容原有接口）"""
    service = get_womei_film_service(token)
    return service.get_movies(cinema_id)
