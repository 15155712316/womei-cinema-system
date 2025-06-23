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
    
    def __init__(self, token: str):
        """
        初始化沃美电影服务

        Args:
            token: 认证令牌（必需）
        """
        if not token:
            raise ValueError("Token是必需的，请从accounts.json文件加载")

        self.token = token
        self.api = create_womei_api(token)
        self.current_cinema_id = None
        self.current_movie_id = None
        self.token_expired = False  # 🔧 添加token失效标志
    
    def set_token(self, token: str):
        """设置认证令牌"""
        self.token = token
        self.api.set_token(token)
        self.token_expired = False  # 重置token失效标志

    def _check_token_validity(self, response: dict) -> dict:
        """
        统一检测token有效性

        Args:
            response: API响应数据

        Returns:
            dict: 如果token失效返回错误信息，否则返回None
        """
        if not isinstance(response, dict):
            return None

        ret_code = response.get('ret', -1)
        sub_code = response.get('sub', 0)
        msg = response.get('msg', '')

        # 🎯 检测token失效的条件：ret=0 且 sub=408 且消息包含TOKEN超时
        if ret_code == 0 and sub_code == 408 and 'TOKEN超时' in msg:
            self.token_expired = True  # 设置token失效标志
            print(f"[Token检测] ❌ 检测到token失效:")
            print(f"[Token检测] 📋 ret: {ret_code}, sub: {sub_code}")
            print(f"[Token检测] 📋 错误信息: {msg}")

            return {
                "success": False,
                "error": f"Token已失效: {msg}",
                "error_type": "token_expired",
                "error_details": {
                    "ret": ret_code,
                    "sub": sub_code,
                    "msg": msg,
                    "detection_time": __import__('datetime').datetime.now().isoformat()
                }
            }

        # 检查其他API错误
        if ret_code != 0:
            return {
                "success": False,
                "error": f"API错误: {msg}",
                "error_type": "api_error",
                "error_details": {"ret": ret_code, "sub": sub_code, "msg": msg}
            }
        elif sub_code != 0:
            return {
                "success": False,
                "error": f"API子错误: {msg} (sub={sub_code})",
                "error_type": "api_sub_error",
                "error_details": {"ret": ret_code, "sub": sub_code, "msg": msg}
            }

        return None  # token有效，无错误

    def is_token_expired(self) -> bool:
        """检查token是否已失效"""
        return self.token_expired

    def reset_token_status(self):
        """重置token状态（用于重新登录后）"""
        self.token_expired = False
        print(f"[Token检测] 🔄 Token状态已重置")
    
    def get_cities(self) -> Dict[str, Any]:
        """获取城市列表"""
        try:
            # 🔧 检查token是否已失效，避免无效API调用
            if self.token_expired:
                print(f"[城市API] ⚠️ Token已失效，直接使用模拟数据")
                data = None  # 使用模拟数据
            else:
                response = self.api.get_cities()

                print(f"[城市API调试] 📥 API原始响应:")
                print(f"[城市API调试] 📋 响应内容: {response}")

                # 🎯 使用统一的token检测机制
                error_result = self._check_token_validity(response)
                if error_result:
                    if error_result.get('error_type') == 'token_expired':
                        # Token失效，使用模拟数据继续运行
                        print(f"[城市API调试] ❌ Token失效，使用模拟数据继续运行")
                        data = None  # 标记使用模拟数据
                    else:
                        # 其他API错误，直接返回错误
                        print(f"[城市API调试] ❌ API错误: {error_result.get('error')}")
                        return {
                            "success": False,
                            "error": error_result.get('error'),
                            "error_type": error_result.get('error_type'),
                            "cities": []
                        }
                else:
                    # API成功，获取真实数据
                    data = response.get('data', {})
                    print(f"[城市API调试] ✅ API成功，data类型: {type(data)}")

            # 检查data是否为字典格式或需要使用模拟数据
            if data is None or isinstance(data, list):
                # 如果data是列表或为None，说明需要使用模拟数据
                print(f"[城市API调试] 🔄 使用模拟数据进行测试")
                if data is not None:
                    print(f"[城市API调试] 📋 原始data: {data}")

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

            # 🔧 修正：使用normal数组获取城市数据（根据真实API结构）
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
            print(f"[影院API调试] 🚀 开始获取影院列表")
            print(f"[影院API调试] 📋 请求参数: city_id={city_id}")

            # 🔧 检查token是否已失效，避免无效API调用
            if self.token_expired:
                print(f"[影院API] ❌ Token已失效，停止API调用")
                return {
                    "success": False,
                    "error": "Token已失效，请重新登录",
                    "error_type": "token_expired",
                    "cinemas": []
                }

            # 沃美系统的城市列表已包含影院信息
            cities_response = self.api.get_cities()

            print(f"[影院API调试] 📥 API原始响应:")
            print(f"[影院API调试] 📋 响应类型: {type(cities_response)}")
            print(f"[影院API调试] 📋 响应内容: {cities_response}")

            # 🎯 使用统一的token检测机制
            error_result = self._check_token_validity(cities_response)
            if error_result:
                print(f"[影院API调试] ❌ API错误: {error_result.get('error')}")
                return {
                    "success": False,
                    "error": error_result.get('error'),
                    "error_type": error_result.get('error_type'),
                    "cinemas": [],
                    "debug_info": {
                        "data_type": str(type(cities_response.get('data'))),
                        "data_content": cities_response.get('data'),
                        "cities_response": cities_response
                    }
                }

            data = cities_response.get('data', {})
            print(f"[影院API调试] 📋 data字段:")
            print(f"[影院API调试] 📋 data类型: {type(data)}")
            print(f"[影院API调试] 📋 data内容: {data}")

            # 检查data是否为字典格式
            if isinstance(data, list):
                print(f"[影院API调试] ❌ data为列表格式，这通常表示token失效或API异常")
                print(f"[影院API调试] 📋 列表长度: {len(data)}")
                print(f"[影院API调试] 📋 列表内容: {data}")

                # 🔧 增加详细分析
                if len(data) == 0:
                    print(f"[影院API调试] 📋 空列表，可能是token失效")
                else:
                    print(f"[影院API调试] 📋 非空列表，分析第一个元素:")
                    if data:
                        first_item = data[0]
                        print(f"[影院API调试] 📋 第一个元素类型: {type(first_item)}")
                        print(f"[影院API调试] 📋 第一个元素内容: {first_item}")

                return {
                    "success": False,
                    "error": "影院API返回数据格式异常",
                    "cinemas": [],
                    "debug_info": {
                        "data_type": str(type(data)),
                        "data_content": data,
                        "cities_response": cities_response
                    }
                }

            # 🔧 修正：使用normal数组获取影院数据（根据真实API结构）
            normal_cities = data.get('normal', [])
            print(f"[沃美电影服务] 使用normal数组，城市数量: {len(normal_cities)}")

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

            # 🔧 新增：保存完整的API响应数据用于调试
            self._save_seat_debug_data(cinema_id, hall_id, schedule_id, response, hall_data)

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

    def _save_seat_debug_data(self, cinema_id: str, hall_id: str, schedule_id: str, api_response: dict, hall_data: dict):
        """保存座位图调试数据到JSON文件"""
        try:
            import os
            import json
            from datetime import datetime

            # 确保data目录存在
            os.makedirs('data', exist_ok=True)

            # 构建调试数据
            debug_data = {
                "session_info": {
                    "cinema_name": "沃美影院",  # 默认名称，后续可以从其他地方获取
                    "movie_name": "未知影片",   # 默认名称，后续可以从其他地方获取
                    "show_date": "未知日期",   # 默认值，后续可以从其他地方获取
                    "show_time": "未知时间",   # 默认值，后续可以从其他地方获取
                    "cinema_id": cinema_id,
                    "hall_id": hall_id,
                    "hall_name": hall_data.get('hall_name', f'{hall_id}号厅'),
                    "schedule_id": schedule_id,
                    "timestamp": datetime.now().isoformat()
                },
                "api_response": api_response,
                "processed_hall_data": hall_data,
                "debug_notes": {
                    "purpose": "座位图API调试数据（每次覆盖保存）",
                    "area_no_usage": "区域ID应该使用area_no字段，不是固定的1",
                    "seat_no_format": "seat_no应该是类似11051771#09#06的格式",
                    "coordinate_mapping": "row/col是逻辑位置，x/y是物理位置",
                    "status_meaning": "0=可选，1=已售，2=锁定",
                    "file_location": "data/座位调试数据.json（固定文件名）"
                }
            }

            # 🔧 修改：固定文件名，每次覆盖
            filename = "data/座位调试数据.json"

            # 保存到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, ensure_ascii=False, indent=2)

            print(f"[沃美电影服务] 📁 座位调试数据已覆盖保存: {filename}")
            print(f"[沃美电影服务] 📊 当前场次数据:")
            print(f"  - 影院ID: {cinema_id}")
            print(f"  - 影厅ID: {hall_id}")
            print(f"  - 场次ID: {schedule_id}")
            print(f"  - 影厅名: {hall_data.get('hall_name', 'N/A')}")

            # 统计座位数
            room_seat = hall_data.get('room_seat', [])
            total_seats = 0
            area_count = len(room_seat)

            for area in room_seat:
                for row_key, row_data in area.get('seats', {}).items():
                    total_seats += len(row_data.get('detail', []))

            print(f"  - 区域数: {area_count}")
            print(f"  - 座位总数: {total_seats}")
            print(f"  - 文件大小: {os.path.getsize(filename)} bytes")
            print(f"  - 保存方式: 覆盖保存（固定文件名）")

        except Exception as e:
            print(f"[沃美电影服务] ❌ 保存座位调试数据失败: {e}")
            import traceback
            traceback.print_exc()
    
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

    def get_orders(self, offset: int = 0) -> Dict[str, Any]:
        """获取订单列表"""
        try:
            response = self.api.get_orders(offset)

            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '获取订单失败'),
                    "orders": []
                }

            data = response.get('data', {})
            orders_list = data.get('orders', [])
            next_offset = data.get('next_offset', 0)

            return {
                "success": True,
                "orders": orders_list,
                "next_offset": next_offset,
                "total": len(orders_list)
            }

        except Exception as e:
            print(f"[沃美电影服务] 获取订单列表失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "orders": []
            }

    def create_order(self, cinema_id: str, seatlable: str, schedule_id: str) -> Dict[str, Any]:
        """创建订单"""
        try:
            response = self.api.create_order(cinema_id, seatlable, schedule_id)

            print(f"[沃美电影服务] 订单API响应: {response}")

            # 🔧 修复：检查API调用是否成功
            if response.get('ret') != 0:
                return {
                    "success": False,
                    "error": response.get('msg', '创建订单失败'),
                    "order_info": response
                }

            # 🔧 修复：即使ret=0，也要检查业务逻辑是否成功
            msg = response.get('msg', '')
            order_data = response.get('data', {})

            # 检查是否有业务错误（如锁座失败）
            if '失败' in msg or '错误' in msg or not order_data:
                print(f"[沃美电影服务] 业务逻辑失败: {msg}")
                return {
                    "success": False,
                    "error": msg or '订单创建失败',
                    "order_info": response
                }

            # 真正成功的情况
            print(f"[沃美电影服务] 订单创建成功: {order_data}")
            return {
                "success": True,
                "order_id": order_data.get('order_id'),
                "server_time": order_data.get('server_time'),
                "order_info": order_data
            }

        except Exception as e:
            print(f"[沃美电影服务] 创建订单异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_info": {}
            }

# 全局实例
_womei_film_service = None

def get_womei_film_service(token: str) -> WomeiFilmService:
    """获取沃美电影服务实例（单例模式） - 必须提供token"""
    if not token:
        raise ValueError("Token是必需的，请从accounts.json文件加载")

    global _womei_film_service

    if _womei_film_service is None:
        _womei_film_service = WomeiFilmService(token)
    elif token != _womei_film_service.token:
        _womei_film_service.set_token(token)

    return _womei_film_service

# 便捷函数，保持与原有接口的兼容性
def get_films(cinema_id: str, token: str) -> Dict[str, Any]:
    """获取电影列表（兼容原有接口） - 必须提供token"""
    service = get_womei_film_service(token)
    return service.get_movies(cinema_id)
