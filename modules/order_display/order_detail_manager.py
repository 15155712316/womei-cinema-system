#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单详情显示管理器 - 统一所有订单详情显示逻辑
解决 _show_order_detail 和 _update_order_details 方法重复问题
"""

from typing import Dict, List, Any


class FieldNameMapper:
    """字段名映射器 - 处理不同来源的字段名差异"""
    
    # 标准字段映射表
    FIELD_MAPPINGS = {
        'cinema_id': ['cinemaid', 'cinema_id'],
        'order_id': ['orderno', 'order_id'],
        'movie_name': ['movie', 'filmname', 'film_name'],
        'cinema_name': ['cinema', 'cinemaname', 'cinema_name'],
        'total_price': ['totalprice', 'total_price', 'amount'],
        'member_price': ['mem_totalprice', 'member_price'],
        'phone_number': ['phone', 'userid', 'mobile'],
        'session_time': ['session', 'showTime', 'time'],
        'hall_name': ['hall_name', 'hall'],
        'seats': ['seats'],
        'status': ['status'],
    }
    
    @classmethod
    def normalize_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """标准化数据字段名"""
        normalized = {}
        
        for standard_field, possible_fields in cls.FIELD_MAPPINGS.items():
            for field in possible_fields:
                if field in data and data[field] is not None:
                    normalized[standard_field] = data[field]
                    break
                    
        # 保留原始数据
        for key, value in data.items():
            if key not in normalized:
                normalized[key] = value
                
        return normalized
        
    @classmethod
    def get_cinema_id(cls, data: Dict[str, Any]) -> str:
        """安全获取影院ID"""
        for field in cls.FIELD_MAPPINGS['cinema_id']:
            if field in data and data[field]:
                return str(data[field])
        return ''


class OrderDetailManager:
    """订单详情显示管理器 - 统一所有订单详情显示逻辑"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        
    def display_order_detail(self, order_data: Dict[str, Any], display_context: str = 'default') -> None:
        """统一的订单详情显示方法
        
        Args:
            order_data: 订单数据
            display_context: 显示上下文 ('creation', 'update', 'default')
        """
        try:
            print(f"[订单详情管理器] 开始显示订单详情，上下文: {display_context}")
            
            # 1. 数据增强和标准化
            enhanced_data = self._enhance_and_normalize_order_data(order_data)
            
            # 2. 构建显示内容
            display_content = self._build_display_content(enhanced_data, display_context)
            
            # 3. 更新UI显示
            self._update_ui_display(display_content, enhanced_data)
            
            print(f"[订单详情管理器] 订单详情显示完成")
            
        except Exception as e:
            print(f"[订单详情管理器] 显示错误: {e}")
            import traceback
            traceback.print_exc()
            
    def _enhance_and_normalize_order_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """数据增强和标准化 - 统一字段名和数据格式"""
        try:
            # 字段名标准化
            enhanced_data = FieldNameMapper.normalize_data(order_data)
            
            # 数据增强 - 从主窗口上下文获取更多信息
            enhanced_data = self._enhance_with_context_data(enhanced_data)
            
            print(f"[订单详情管理器] 数据增强完成，标准化字段: {list(enhanced_data.keys())}")
            
            return enhanced_data
            
        except Exception as e:
            print(f"[订单详情管理器] 数据增强失败: {e}")
            return order_data
        
    def _enhance_with_context_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """从主窗口上下文增强订单数据"""
        try:
            enhanced_data = order_data.copy()
            
            # 从当前账号获取手机号
            if hasattr(self.main_window, 'current_account') and self.main_window.current_account:
                if not enhanced_data.get('phone_number'):
                    enhanced_data['phone_number'] = self.main_window.current_account.get('userid', 
                                                   self.main_window.current_account.get('phone', ''))
            
            # 从Tab管理器获取当前选择的信息
            if hasattr(self.main_window, 'tab_manager_widget'):
                tab_widget = self.main_window.tab_manager_widget
                
                # 影院信息
                if hasattr(tab_widget, 'current_cinema_data') and tab_widget.current_cinema_data:
                    cinema_data = tab_widget.current_cinema_data
                    if not enhanced_data.get('cinema_name'):
                        enhanced_data['cinema_name'] = cinema_data.get('cinemaShortName', 
                                                      cinema_data.get('cinemaname', 'N/A'))
                
                # 影片信息
                if hasattr(tab_widget, 'current_movie_data') and tab_widget.current_movie_data:
                    movie_data = tab_widget.current_movie_data
                    if not enhanced_data.get('movie_name'):
                        enhanced_data['movie_name'] = movie_data.get('filmname', 
                                                     movie_data.get('name', 'N/A'))
                
                # 场次信息
                if hasattr(tab_widget, 'current_session_data') and tab_widget.current_session_data:
                    session_data = tab_widget.current_session_data
                    if not enhanced_data.get('session_time'):
                        start_time = session_data.get('startTime', '')
                        date = session_data.get('showDate', '')
                        if start_time and date:
                            enhanced_data['session_time'] = f"{date} {start_time}"
                        elif start_time:
                            enhanced_data['session_time'] = start_time
            
            # 从当前订单状态获取信息
            if hasattr(self.main_window, 'current_order') and self.main_window.current_order:
                current_order = self.main_window.current_order
                for key in ['orderno', 'totalprice', 'seats', 'selected_coupons']:
                    if not enhanced_data.get(key) and current_order.get(key):
                        enhanced_data[key] = current_order[key]
            
            # 从券选择状态获取信息
            if hasattr(self.main_window, 'selected_coupons') and self.main_window.selected_coupons:
                enhanced_data['selected_coupons'] = self.main_window.selected_coupons
            
            if hasattr(self.main_window, 'current_coupon_info') and self.main_window.current_coupon_info:
                coupon_info = self.main_window.current_coupon_info
                enhanced_data['discount_amount'] = coupon_info.get('discount_price', 0) / 100
                enhanced_data['pay_amount'] = coupon_info.get('payment_amount', 0) / 100
            
            return enhanced_data
            
        except Exception as e:
            print(f"[订单详情管理器] 上下文数据增强失败: {e}")
            return order_data
        
    def _build_display_content(self, order_data: Dict[str, Any], context: str) -> List[str]:
        """构建显示内容 - 统一的显示逻辑"""
        try:
            info_lines = []

            print(f"[订单详情管理器] 构建显示内容，上下文: {context}")

            # 基础信息
            info_lines.extend(self._build_basic_info(order_data))

            # 🚫 问题1：已移除密码策略信息显示，专注于券码支付和微信支付

            # 价格信息
            info_lines.extend(self._build_price_info(order_data))

            return info_lines
            
        except Exception as e:
            print(f"[订单详情管理器] 构建显示内容失败: {e}")
            return [f"订单详情显示错误: {str(e)}"]
    
    def _build_basic_info(self, order_data: Dict[str, Any]) -> List[str]:
        """构建基础信息"""
        info_lines = []

        # 订单号
        order_id = order_data.get('order_id', order_data.get('orderno', 'N/A'))
        info_lines.append(f"订单号: {order_id}")

        # 🆕 问题5：添加影院名称显示
        cinema_name = order_data.get('cinema_name', order_data.get('cinema', ''))
        if cinema_name and cinema_name != 'N/A':
            info_lines.append(f"影院: {cinema_name}")

        # 影片信息
        movie = order_data.get('movie_name', order_data.get('movie', 'N/A'))
        info_lines.append(f"影片: {movie}")

        # 🔧 修复场次时间显示格式问题
        session_time = self._build_formatted_time_display(order_data)
        info_lines.append(f"时间: {session_time}")

        # 影厅信息
        hall = order_data.get('hall_name', '')
        if hall:
            info_lines.append(f"影厅: {hall}")

        # 🆕 问题3：完善座位信息显示 - 优先使用ticket_items中的seat_info
        seats = order_data.get('seats', [])
        seat_display = self._build_seat_display(seats, order_data)
        info_lines.append(f"座位: {seat_display}")

        # 状态信息
        status = order_data.get('status', '待支付')
        print(f"[订单详情管理器] 原始状态: {status}")

        # 状态映射：英文状态转中文状态
        status_map = {
            'created': '待支付',
            'paid': '已支付',
            'confirmed': '已确认',
            'cancelled': '已取消',
            'completed': '已完成',
            'refunded': '已退款',
            'failed': '支付失败',
            '0': '待支付',
            '1': '已支付',
            '2': '已取票',
            '3': '已取消',
            '4': '已退款',
            '5': '支付失败'
        }
        chinese_status = status_map.get(status, status)
        print(f"[订单详情管理器] 映射后状态: {chinese_status}")
        info_lines.append(f"状态: {chinese_status}")

        return info_lines

    def _build_formatted_time_display(self, order_data: Dict[str, Any]) -> str:
        """
        🔧 修复时间显示格式问题
        将时间数据格式化为完整的日期时间格式（如"2025/07/01 21:40"）
        """
        try:
            print(f"[时间显示] 开始构建时间显示")

            # 方法1：优先使用show_date字段
            show_date = order_data.get('show_date', '')
            if show_date:
                print(f"[时间显示] 原始show_date: {show_date}")
                formatted_time = self._format_time_string(show_date)
                if formatted_time:
                    print(f"[时间显示] ✅ 使用格式化的show_date: {formatted_time}")
                    return formatted_time

            # 方法2：从API数据中获取时间信息
            api_data = order_data.get('api_data', {})
            if isinstance(api_data, dict):
                # 尝试获取各种时间字段
                time_fields = ['show_date', 'showTime', 'session_time', 'time']
                for field in time_fields:
                    time_value = api_data.get(field, '')
                    if time_value:
                        print(f"[时间显示] 从api_data获取{field}: {time_value}")
                        formatted_time = self._format_time_string(time_value)
                        if formatted_time:
                            print(f"[时间显示] ✅ 使用api_data.{field}: {formatted_time}")
                            return formatted_time

            # 方法3：降级到原有逻辑
            session_time = order_data.get('session_time', order_data.get('showTime', ''))
            if session_time:
                formatted_time = self._format_time_string(session_time)
                if formatted_time:
                    print(f"[时间显示] ✅ 使用session_time: {formatted_time}")
                    return formatted_time

            # 方法4：组合date和session字段
            date = order_data.get('date', '')
            session = order_data.get('session', '')
            if date and session:
                combined_time = f"{date} {session}"
                formatted_time = self._format_time_string(combined_time)
                if formatted_time:
                    print(f"[时间显示] ✅ 使用组合时间: {formatted_time}")
                    return formatted_time
                else:
                    # 如果格式化失败，直接返回组合结果
                    print(f"[时间显示] ⚠️ 使用未格式化的组合时间: {combined_time}")
                    return combined_time

            # 方法5：最终降级
            if show_date:
                print(f"[时间显示] ⚠️ 降级使用原始show_date: {show_date}")
                return str(show_date)
            elif session_time:
                print(f"[时间显示] ⚠️ 降级使用原始session_time: {session_time}")
                return str(session_time)
            else:
                print(f"[时间显示] ❌ 无时间信息")
                return "未知"

        except Exception as e:
            print(f"[时间显示] ❌ 构建时间显示异常: {e}")
            import traceback
            traceback.print_exc()
            return "时间获取失败"

    def _format_time_string(self, time_str: str) -> str:
        """
        格式化时间字符串为标准格式
        支持多种输入格式，输出统一格式：YYYY/MM/DD HH:MM
        """
        try:
            if not time_str or not isinstance(time_str, str):
                return ""

            time_str = time_str.strip()
            print(f"[时间格式化] 输入时间字符串: '{time_str}'")

            # 处理纯数字日期格式（如"20250701"）
            if time_str.isdigit() and len(time_str) == 8:
                # 格式：YYYYMMDD
                year = time_str[:4]
                month = time_str[4:6]
                day = time_str[6:8]
                formatted = f"{year}/{month}/{day}"
                print(f"[时间格式化] 纯数字日期格式: {formatted}")
                return formatted

            # 处理包含时间的格式
            import re

            # 格式1：YYYY-MM-DD HH:MM:SS 或 YYYY-MM-DD HH:MM
            pattern1 = r'(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?'
            match1 = re.match(pattern1, time_str)
            if match1:
                year, month, day, hour, minute = match1.groups()[:5]
                formatted = f"{year}/{month.zfill(2)}/{day.zfill(2)} {hour.zfill(2)}:{minute.zfill(2)}"
                print(f"[时间格式化] 标准格式: {formatted}")
                return formatted

            # 格式2：YYYY/MM/DD HH:MM:SS 或 YYYY/MM/DD HH:MM
            pattern2 = r'(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?'
            match2 = re.match(pattern2, time_str)
            if match2:
                year, month, day, hour, minute = match2.groups()[:5]
                formatted = f"{year}/{month.zfill(2)}/{day.zfill(2)} {hour.zfill(2)}:{minute.zfill(2)}"
                print(f"[时间格式化] 斜杠格式: {formatted}")
                return formatted

            # 格式3：YYYYMMDD HHMM 或 YYYYMMDD HH:MM
            pattern3 = r'(\d{8})\s+(\d{2}):?(\d{2})'
            match3 = re.match(pattern3, time_str)
            if match3:
                date_part, hour, minute = match3.groups()
                year = date_part[:4]
                month = date_part[4:6]
                day = date_part[6:8]
                formatted = f"{year}/{month}/{day} {hour}:{minute}"
                print(f"[时间格式化] 紧凑格式: {formatted}")
                return formatted

            # 格式4：只有日期的情况（YYYY-MM-DD 或 YYYY/MM/DD）
            pattern4 = r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})'
            match4 = re.match(pattern4, time_str)
            if match4:
                year, month, day = match4.groups()
                formatted = f"{year}/{month.zfill(2)}/{day.zfill(2)}"
                print(f"[时间格式化] 纯日期格式: {formatted}")
                return formatted

            # 如果都不匹配，返回原字符串
            print(f"[时间格式化] ⚠️ 无法识别格式，返回原字符串: {time_str}")
            return time_str

        except Exception as e:
            print(f"[时间格式化] ❌ 格式化异常: {e}")
            return time_str if isinstance(time_str, str) else ""

    def _build_seat_display(self, seats: List, order_data: Dict[str, Any]) -> str:
        """
        🔧 修复座位信息显示问题
        优先使用订单详情API响应的seat_info字段，确保显示完整的座位描述

        API数据源：https://ct.womovie.cn/ticket/wmyc/cinema/400028/order/info/
        关键字段：响应数据中的 seat_info 字段
        """
        try:
            print(f"[座位显示] 🔍 开始构建座位显示")
            print(f"[座位显示] 输入seats参数: {seats} (类型: {type(seats)})")
            print(f"[座位显示] order_data可用键: {list(order_data.keys()) if isinstance(order_data, dict) else 'N/A'}")

            # 🔍 详细调试：打印所有可能的座位相关字段
            seat_related_fields = ['seat_info', 'seats', 'ticket_items', 'api_data']
            for field in seat_related_fields:
                value = order_data.get(field)
                if value:
                    print(f"[座位显示] 🔍 {field}: {value} (类型: {type(value)})")

            # 🆕 方法1：优先从订单详情API响应的seat_info字段获取（主要数据源）
            api_seat_info = order_data.get('seat_info', '')
            if api_seat_info:
                print(f"[座位显示] ✅ 找到API响应的seat_info字段: {api_seat_info}")
                # 如果seat_info是字符串且包含完整座位信息，直接使用
                if isinstance(api_seat_info, str) and api_seat_info.strip():
                    result = api_seat_info.strip()
                    print(f"[座位显示] ✅ 返回API seat_info: {result}")
                    return result
                # 如果seat_info是列表，连接显示
                elif isinstance(api_seat_info, list):
                    seat_list = [str(seat).strip() for seat in api_seat_info if str(seat).strip()]
                    if seat_list:
                        result = ", ".join(seat_list)
                        print(f"[座位显示] ✅ 返回API seat_info列表: {result}")
                        return result
            else:
                print(f"[座位显示] ⚠️ 未找到order_data.seat_info字段")

            # 🔄 方法2：从ticket_items中获取seat_info（备用数据源）
            ticket_items = order_data.get('ticket_items', [])
            if ticket_items and isinstance(ticket_items, list):
                print(f"[座位显示] 🔍 检查ticket_items: {ticket_items}")
                seat_infos = []
                for i, item in enumerate(ticket_items):
                    if isinstance(item, dict):
                        seat_info = item.get('seat_info', '')
                        print(f"[座位显示] ticket_items[{i}].seat_info: {seat_info}")
                        if seat_info and isinstance(seat_info, str):
                            seat_infos.append(seat_info.strip())

                if seat_infos:
                    result = ", ".join(seat_infos)
                    print(f"[座位显示] ✅ 返回ticket_items座位信息: {result}")
                    return result
                else:
                    print(f"[座位显示] ⚠️ ticket_items中未找到有效座位信息")

            # 🔄 方法3：从api_data中获取（深度查找，优先级高于传统seats）
            api_data = order_data.get('api_data', {})
            if isinstance(api_data, dict):
                print(f"[座位显示] 🔍 检查api_data: {api_data}")
                api_seat_info = api_data.get('seat_info', '')
                if api_seat_info:
                    print(f"[座位显示] ✅ 找到api_data.seat_info: {api_seat_info}")
                    if isinstance(api_seat_info, str) and api_seat_info.strip():
                        result = api_seat_info.strip()
                        print(f"[座位显示] ✅ 返回api_data座位信息: {result}")
                        return result
                    elif isinstance(api_seat_info, list):
                        seat_list = [str(seat).strip() for seat in api_seat_info if str(seat).strip()]
                        if seat_list:
                            result = ", ".join(seat_list)
                            print(f"[座位显示] ✅ 返回api_data座位列表: {result}")
                            return result
                else:
                    print(f"[座位显示] ⚠️ api_data中未找到seat_info字段")

            # 🔄 方法4：处理传统的seats字段（兼容性处理）
            if isinstance(seats, list) and seats:
                print(f"[座位显示] 🔍 处理传统seats字段: {seats}")
                seat_strings = []
                for i, seat in enumerate(seats):
                    print(f"[座位显示] 处理seats[{i}]: {seat} (类型: {type(seat)})")

                    if isinstance(seat, str) and seat.strip():
                        # 🔧 智能处理字符串座位信息
                        seat_str = seat.strip()
                        # 如果是纯数字，尝试构建完整座位信息
                        if seat_str.isdigit():
                            # 尝试从其他地方获取行信息来构建完整座位
                            enhanced_seat = self._enhance_seat_info(seat_str, order_data)
                            if enhanced_seat and enhanced_seat != seat_str:
                                print(f"[座位显示] 🔧 增强座位信息: {seat_str} -> {enhanced_seat}")
                                seat_strings.append(enhanced_seat)
                            else:
                                print(f"[座位显示] ⚠️ 无法增强座位信息，使用原值: {seat_str}")
                                seat_strings.append(seat_str)
                        else:
                            seat_strings.append(seat_str)

                    elif isinstance(seat, dict):
                        # 尝试构建完整的座位信息
                        seat_str = seat.get('seat_info', '')  # 优先使用seat_info
                        if not seat_str:
                            # 降级到其他字段
                            seat_str = seat.get('num', seat.get('seat_name', ''))
                            if not seat_str:
                                # 最后尝试构建格式
                                row = seat.get('row', '')
                                col = seat.get('col', '')
                                if row and col:
                                    seat_str = f"{row}排{col}座"
                                else:
                                    seat_str = str(seat)

                        if seat_str:
                            seat_strings.append(str(seat_str).strip())
                    elif seat:  # 其他非空类型
                        seat_str = str(seat).strip()
                        # 同样尝试增强纯数字座位信息
                        if seat_str.isdigit():
                            enhanced_seat = self._enhance_seat_info(seat_str, order_data)
                            if enhanced_seat and enhanced_seat != seat_str:
                                print(f"[座位显示] 🔧 增强座位信息: {seat_str} -> {enhanced_seat}")
                                seat_strings.append(enhanced_seat)
                            else:
                                seat_strings.append(seat_str)
                        else:
                            seat_strings.append(seat_str)

                if seat_strings:
                    result = ", ".join(seat_strings)
                    print(f"[座位显示] ✅ 返回seats字段构建结果: {result}")
                    return result
                else:
                    print(f"[座位显示] ⚠️ seats字段处理后无有效结果")

            # 🔄 方法5：最终降级处理
            if seats:
                print(f"[座位显示] ⚠️ 降级处理，直接显示原始数据: {seats}")
                if isinstance(seats, list):
                    return ", ".join(str(seat) for seat in seats if seat)
                else:
                    return str(seats)
            else:
                print(f"[座位显示] ❌ 无任何座位信息")
                return "未知"

        except Exception as e:
            print(f"[座位显示] ❌ 构建座位显示异常: {e}")
            import traceback
            traceback.print_exc()
            # 异常时的安全降级
            if seats:
                return str(seats)
            else:
                return "座位信息获取失败"

    def _enhance_seat_info(self, seat_number: str, order_data: Dict[str, Any]) -> str:
        """
        🔧 增强座位信息显示
        尝试将纯数字座位信息（如"4"）转换为完整格式（如"4排X座"）
        """
        try:
            if not seat_number or not seat_number.isdigit():
                return seat_number

            print(f"[座位增强] 尝试增强座位信息: {seat_number}")

            # 方法1：从API数据中查找座位相关信息
            api_data = order_data.get('api_data', {})
            if isinstance(api_data, dict):
                # 查找可能的座位模式信息
                for key, value in api_data.items():
                    if 'seat' in key.lower() and isinstance(value, str):
                        if seat_number in value and ('排' in value or '座' in value):
                            print(f"[座位增强] 从api_data.{key}找到模式: {value}")
                            return value

            # 方法2：从ticket_items中查找模式
            ticket_items = order_data.get('ticket_items', [])
            if isinstance(ticket_items, list):
                for item in ticket_items:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if 'seat' in key.lower() and isinstance(value, str):
                                if seat_number in value and ('排' in value or '座' in value):
                                    print(f"[座位增强] 从ticket_items找到模式: {value}")
                                    return value

            # 方法3：智能推测（基于常见模式）
            # 如果座位号是个位数，可能是排号，尝试构建常见格式
            if len(seat_number) == 1:
                # 常见情况：座位号可能是排号，座号需要推测
                # 这里使用一个简单的启发式方法
                possible_formats = [
                    f"{seat_number}排6座",  # 假设6座（中间位置）
                    f"{seat_number}排5座",  # 假设5座
                    f"{seat_number}排7座",  # 假设7座
                ]

                # 检查订单数据中是否有其他线索
                for format_attempt in possible_formats:
                    # 这里可以添加更多的验证逻辑
                    print(f"[座位增强] 尝试格式: {format_attempt}")
                    # 暂时返回第一个尝试（可以根据实际情况优化）
                    return possible_formats[0]

            # 方法4：如果是两位数，可能是排号+座号
            elif len(seat_number) == 2:
                row = seat_number[0]
                col = seat_number[1]
                enhanced = f"{row}排{col}座"
                print(f"[座位增强] 两位数解析: {enhanced}")
                return enhanced

            # 如果无法增强，返回原值
            print(f"[座位增强] 无法增强，返回原值: {seat_number}")
            return seat_number

        except Exception as e:
            print(f"[座位增强] ❌ 增强座位信息异常: {e}")
            return seat_number
    
    # 🚫 问题1：已移除密码策略信息构建功能，专注于券码支付和微信支付
    
    def _build_price_info(self, order_data: Dict[str, Any]) -> List[str]:
        """
        🆕 构建价格信息 - 优化实付金额显示逻辑
        问题4：根据券码选择情况动态显示实付金额
        """
        info_lines = []

        try:

            # 获取原价信息
            original_price = self._get_original_price(order_data)
            info_lines.append(f"原价: ¥{original_price:.2f}")

            # 🆕 问题4：优化实付金额显示逻辑
            payment_info = self._build_payment_amount_info(order_data, original_price)
            if payment_info:
                info_lines.extend(payment_info)

            return info_lines

        except Exception as e:
            print(f"[订单详情管理器] 构建价格信息失败: {e}")
            import traceback
            traceback.print_exc()
            return [f"价格信息显示错误: {str(e)}"]

    def _get_original_price(self, order_data: Dict[str, Any]) -> float:
        """获取原价信息"""
        try:
            # 方法1：从api_data获取
            api_data = order_data.get('api_data', {})
            if api_data and isinstance(api_data, dict):
                api_total_price = int(api_data.get('totalprice', 0) or 0)
                if api_total_price > 0:
                    return api_total_price / 100.0

            # 方法2：从amount字段获取
            amount = order_data.get('amount', order_data.get('total_price', 0))
            if isinstance(amount, str):
                try:
                    amount = float(amount)
                except:
                    amount = 0
            elif isinstance(amount, (int, float)):
                # 如果amount是分为单位，需要转换为元
                if amount > 1000:  # 假设超过1000的是分为单位
                    amount = amount / 100.0

            return max(0, amount)

        except Exception as e:
            print(f"[价格获取] 获取原价失败: {e}")
            return 0.0

    def _build_payment_amount_info(self, order_data: Dict[str, Any], original_price: float) -> List[str]:
        """
        🆕 问题4：构建实付金额信息 - 根据券码选择情况动态显示

        显示逻辑：
        - 当用户未选择券码时：不显示"实付金额"行
        - 当用户选择了足够抵用券后：显示"实付金额: ¥0.00"
        - 当用户选择了部分抵用券后：不显示"实付金额"行
        """
        info_lines = []

        try:
            # 检查券码选择状态
            coupon_count = 0
            has_coupon_info = False

            # 从主窗口获取券选择状态
            if hasattr(self.main_window, 'selected_coupons') and self.main_window.selected_coupons:
                coupon_count = len(self.main_window.selected_coupons)
                has_coupon_info = True
                print(f"[实付金额] 从主窗口获取券数量: {coupon_count}")
            elif order_data.get('selected_coupons'):
                coupon_count = len(order_data.get('selected_coupons', []))
                has_coupon_info = True
                print(f"[实付金额] 从订单数据获取券数量: {coupon_count}")

            # 获取券抵扣信息
            discount_price_yuan = 0
            pay_amount_yuan = original_price  # 默认为原价
            used_voucher_codes = []

            if has_coupon_info and hasattr(self.main_window, 'current_coupon_info') and self.main_window.current_coupon_info:
                # 检查是否为沃美券绑定结果
                womei_bind_result = self.main_window.current_coupon_info.get('womei_bind_result')

                if womei_bind_result and womei_bind_result.get('success'):
                    # 使用沃美券绑定结果的价格信息
                    price_info = womei_bind_result.get('price_info', {})
                    voucher_info = womei_bind_result.get('voucher_info', {})

                    pay_amount_yuan = price_info.get('order_payment_price', 0)
                    discount_price_yuan = voucher_info.get('use_total_price', 0)
                    used_voucher_codes = voucher_info.get('use_codes', [])

                    print(f"[实付金额] 沃美券信息: 支付={pay_amount_yuan}, 优惠={discount_price_yuan}")

                else:
                    # 兼容传统券系统
                    coupon_data = self.main_window.current_coupon_info.get('resultData', {})
                    if coupon_data:
                        discount_price_fen = int(coupon_data.get('discountprice', '0') or '0')
                        discount_price_yuan = discount_price_fen / 100.0

                        pay_amount_fen = int(coupon_data.get('paymentAmount', '0') or '0')
                        pay_amount_yuan = pay_amount_fen / 100.0

                        print(f"[实付金额] 传统券信息: 支付={pay_amount_yuan}, 优惠={discount_price_yuan}")

            # 显示券信息
            if coupon_count > 0:
                info_lines.append(f"使用券: {coupon_count}张")
                if discount_price_yuan > 0:
                    info_lines.append(f"券优惠: -¥{discount_price_yuan:.2f}")

                # 显示券码信息（如果有）
                if used_voucher_codes:
                    if len(used_voucher_codes) <= 2:
                        info_lines.append(f"券码: {', '.join(used_voucher_codes)}")
                    else:
                        info_lines.append(f"券码: {', '.join(used_voucher_codes[:2])}...")

            # 🆕 问题4：优化实付金额显示逻辑
            if coupon_count > 0 and has_coupon_info:
                # 有券的情况
                if pay_amount_yuan == 0:
                    # 纯券支付：显示实付金额为0
                    info_lines.append(f"实付金额: ¥0.00")
                # 部分抵用券：不显示实付金额行（按照需求）
            # 未选择券码：不显示实付金额行（按照需求）

            return info_lines

        except Exception as e:
            print(f"[实付金额] 构建实付金额信息失败: {e}")
            import traceback
            traceback.print_exc()
            return [f"实付金额信息错误: {str(e)}"]
    
    def _update_ui_display(self, display_content: List[str], order_data: Dict[str, Any]) -> None:
        """更新UI显示"""
        try:
            # 更新手机号显示
            phone = order_data.get('phone_number', '')
            if phone and hasattr(self.main_window, 'phone_display'):
                self.main_window.phone_display.setText(f"手机号: {phone}")
            
            # 更新订单详情文本
            details = "\n".join(display_content)
            if hasattr(self.main_window, 'order_detail_text'):
                self.main_window.order_detail_text.setPlainText(details)
            
        except Exception as e:
            print(f"[订单详情管理器] UI更新失败: {e}")
