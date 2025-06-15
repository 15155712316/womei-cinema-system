#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一电影服务 - 支持华联和沃美两个系统
基于HAR文件分析结果，适配沃美系统的API结构
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from cinema_api_adapter import CinemaSystem, WomeiAPI, HuanlianAPI
from .film_service import get_films as get_huanlian_films, normalize_film_data

class UnifiedFilmService:
    """统一电影服务类，支持多影院系统"""
    
    def __init__(self, system_type: CinemaSystem = CinemaSystem.WOMEI, token: str = None):
        """
        初始化统一电影服务
        
        Args:
            system_type: 影院系统类型
            token: 认证令牌
        """
        self.system_type = system_type
        self.token = token
        
        # 创建对应的API适配器
        if system_type == CinemaSystem.WOMEI:
            self.api = WomeiAPI.create(token)
        elif system_type == CinemaSystem.HUANLIAN:
            self.api = HuanlianAPI.create(token)
        else:
            raise ValueError(f"不支持的影院系统类型: {system_type}")
    
    def get_cities(self) -> Dict[str, Any]:
        """获取城市列表"""
        try:
            response = self.api.get_cities()
            
            if self.system_type == CinemaSystem.WOMEI:
                return self._process_womei_cities(response)
            else:
                return self._process_huanlian_cities(response)
                
        except Exception as e:
            print(f"[统一电影服务] 获取城市列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cinemas_by_city(self, city_id: str = None) -> Dict[str, Any]:
        """获取指定城市的影院列表"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                # 沃美系统的城市列表已包含影院信息
                cities_response = self.api.get_cities()
                return self._extract_cinemas_from_cities(cities_response, city_id)
            else:
                # 华联系统需要单独调用影院接口
                response = self.api.get_cinemas(city_id)
                return self._process_huanlian_cinemas(response)
                
        except Exception as e:
            print(f"[统一电影服务] 获取影院列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_cinema_info(self, cinema_id: str) -> Dict[str, Any]:
        """获取影院详细信息"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                response = self.api.get_cinema_info(cinema_id)
                return self._process_womei_cinema_info(response)
            else:
                # 华联系统的影院信息获取方式
                # 这里需要根据华联系统的实际API调整
                return {"success": False, "error": "华联系统暂不支持此功能"}
                
        except Exception as e:
            print(f"[统一电影服务] 获取影院信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_movies(self, cinema_id: str) -> Dict[str, Any]:
        """获取指定影院的电影列表"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                response = self.api.get_movies_by_cinema(cinema_id)
                return self._process_womei_movies(response)
            else:
                # 华联系统的电影获取方式
                # 需要使用旧的get_films函数
                return self._get_huanlian_movies(cinema_id)
                
        except Exception as e:
            print(f"[统一电影服务] 获取电影列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_shows(self, cinema_id: str, movie_id: str) -> Dict[str, Any]:
        """获取电影场次列表"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                response = self.api.get_shows(cinema_id, movie_id)
                return self._process_womei_shows(response)
            else:
                # 华联系统的场次获取方式
                return {"success": False, "error": "华联系统暂不支持此功能"}
                
        except Exception as e:
            print(f"[统一电影服务] 获取场次列表失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_hall_info(self, cinema_id: str, hall_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取影厅座位信息"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                response = self.api.get_hall_info(cinema_id, hall_id, schedule_id)
                return self._process_womei_hall_info(response)
            else:
                # 华联系统的座位信息获取方式
                return {"success": False, "error": "华联系统暂不支持此功能"}
                
        except Exception as e:
            print(f"[统一电影服务] 获取座位信息失败: {e}")
            return {"success": False, "error": str(e)}
    
    def get_hall_saleable(self, cinema_id: str, schedule_id: str) -> Dict[str, Any]:
        """获取可售座位信息"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                response = self.api.get_hall_saleable(cinema_id, schedule_id)
                return self._process_womei_hall_saleable(response)
            else:
                return {"success": False, "error": "华联系统暂不支持此功能"}
                
        except Exception as e:
            print(f"[统一电影服务] 获取可售座位失败: {e}")
            return {"success": False, "error": str(e)}
    
    def create_order(self, cinema_id: str, seatlable: str, schedule_id: str) -> Dict[str, Any]:
        """创建订单"""
        try:
            if self.system_type == CinemaSystem.WOMEI:
                response = self.api.create_ticket_order(cinema_id, seatlable, schedule_id)
                return self._process_womei_order_response(response)
            else:
                return {"success": False, "error": "华联系统暂不支持此功能"}
                
        except Exception as e:
            print(f"[统一电影服务] 创建订单失败: {e}")
            return {"success": False, "error": str(e)}
    
    # 沃美系统数据处理方法
    def _process_womei_cities(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的城市数据"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取城市失败')}
        
        data = response.get('data', {})
        hot_cities = data.get('hot', [])
        
        cities = []
        for city in hot_cities:
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
    
    def _extract_cinemas_from_cities(self, response: Dict[str, Any], city_id: str = None) -> Dict[str, Any]:
        """从城市数据中提取影院信息"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取影院失败')}
        
        data = response.get('data', {})
        hot_cities = data.get('hot', [])
        
        all_cinemas = []
        for city in hot_cities:
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
    
    def _process_womei_cinema_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的影院信息"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取影院信息失败')}
        
        data = response.get('data', {})
        return {
            "success": True,
            "cinema_info": data
        }
    
    def _process_womei_movies(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的电影数据"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取电影失败')}
        
        movies_data = response.get('data', [])
        
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
                "today_show": movie.get('today_show', [])
            }
            movies.append(movie_info)
        
        return {
            "success": True,
            "movies": movies,
            "total": len(movies)
        }
    
    def _process_womei_shows(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的场次数据"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取场次失败')}
        
        shows_data = response.get('data', [])
        return {
            "success": True,
            "shows": shows_data,
            "total": len(shows_data)
        }
    
    def _process_womei_hall_info(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的影厅信息"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取影厅信息失败')}
        
        data = response.get('data', {})
        return {
            "success": True,
            "hall_info": data
        }
    
    def _process_womei_hall_saleable(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的可售座位信息"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '获取可售座位失败')}
        
        data = response.get('data', {})
        return {
            "success": True,
            "saleable_info": data
        }
    
    def _process_womei_order_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理沃美系统的订单响应"""
        if response.get('ret') != 0:
            return {"success": False, "error": response.get('msg', '创建订单失败')}
        
        data = response.get('data', {})
        return {
            "success": True,
            "order_id": data.get('order_id'),
            "server_time": data.get('server_time')
        }
    
    # 华联系统兼容方法
    def _process_huanlian_cities(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理华联系统的城市数据（待实现）"""
        return {"success": False, "error": "华联系统城市接口待实现"}
    
    def _process_huanlian_cinemas(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理华联系统的影院数据（待实现）"""
        return {"success": False, "error": "华联系统影院接口待实现"}
    
    def _get_huanlian_movies(self, cinema_id: str) -> Dict[str, Any]:
        """获取华联系统的电影数据（使用旧接口）"""
        # 这里需要根据实际情况调用华联系统的接口
        return {"success": False, "error": "华联系统电影接口待实现"}

# 便捷函数
def create_film_service(system_type: CinemaSystem = CinemaSystem.WOMEI, token: str = None) -> UnifiedFilmService:
    """创建统一电影服务实例"""
    return UnifiedFilmService(system_type, token)

def create_womei_film_service(token: str = None) -> UnifiedFilmService:
    """创建沃美电影服务实例"""
    return UnifiedFilmService(CinemaSystem.WOMEI, token)

def create_huanlian_film_service(token: str = None) -> UnifiedFilmService:
    """创建华联电影服务实例"""
    return UnifiedFilmService(CinemaSystem.HUANLIAN, token)
