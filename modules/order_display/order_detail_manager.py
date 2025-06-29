#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单详情显示管理器 - 统一所有订单详情显示逻辑
解决 _show_order_detail 和 _update_order_details 方法重复问题
"""

from typing import Dict, List, Any, Optional
import json


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
            
            # 基础信息
            info_lines.extend(self._build_basic_info(order_data))
            
            # 密码策略信息
            password_info = self._build_password_policy_info(order_data)
            if password_info:
                info_lines.append(password_info)
            
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
        
        # 影片信息
        movie = order_data.get('movie_name', order_data.get('movie', 'N/A'))
        info_lines.append(f"影片: {movie}")
        
        # 时间信息
        session_time = order_data.get('session_time', '')
        if not session_time:
            date = order_data.get('date', '')
            session = order_data.get('session', '')
            if date and session:
                session_time = f"{date} {session}"
        info_lines.append(f"时间: {session_time}")
        
        # 影厅信息
        cinema = order_data.get('cinema_name', order_data.get('cinema', 'N/A'))
        hall = order_data.get('hall_name', '')
        if hall:
            info_lines.append(f"影厅: {hall}")
        else:
            info_lines.append(f"影院: {cinema}")
        
        # 座位信息
        seats = order_data.get('seats', [])
        if isinstance(seats, list) and seats:
            # 🔧 修复：确保座位数据是字符串格式
            seat_strings = []
            for seat in seats:
                if isinstance(seat, str):
                    seat_strings.append(seat)
                elif isinstance(seat, dict):
                    # 如果是字典，尝试提取座位信息
                    seat_str = seat.get('num', seat.get('seat_name', f"{seat.get('row', '?')}排{seat.get('col', '?')}座"))
                    seat_strings.append(str(seat_str))
                else:
                    # 其他类型，转换为字符串
                    seat_strings.append(str(seat))

            if len(seat_strings) == 1:
                info_lines.append(f"座位: {seat_strings[0]}")
            else:
                seat_str = ", ".join(seat_strings)
                info_lines.append(f"座位: {seat_str}")
        else:
            info_lines.append(f"座位: {seats}")
        
        # ⚠️ 【同步维护点1】状态信息 - 必须与main_modular.py第1465行保持一致
        # 修复：使用中文状态映射
        status = order_data.get('status', '待支付')
        print(f"[订单详情管理器] 原始状态: {status}")

        # 状态映射：英文状态转中文状态
        # TODO: 修改此映射时，必须同步更新main_modular.py中的_legacy_order_detail_display方法
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
    
    def _build_password_policy_info(self, order_data: Dict[str, Any]) -> Optional[str]:
        """构建密码策略信息"""
        try:
            enable_mempassword = None
            
            # 从api_data获取
            api_data = order_data.get('api_data', {})
            if api_data and isinstance(api_data, dict):
                enable_mempassword = api_data.get('enable_mempassword')
            
            # 直接从order_data获取
            if enable_mempassword is None:
                enable_mempassword = order_data.get('enable_mempassword')
            
            # 使用主窗口的增强密码显示方法
            if hasattr(self.main_window, '_get_enhanced_password_display'):
                return self.main_window._get_enhanced_password_display(enable_mempassword)
            else:
                # 降级处理
                if enable_mempassword == '1':
                    return "密码: 需要输入"
                elif enable_mempassword == '0':
                    return "密码: 无需输入"
                else:
                    return "密码: 检测中..."
                    
        except Exception as e:
            print(f"[订单详情管理器] 构建密码策略信息失败: {e}")
            return "密码: 检测失败"
    
    def _build_price_info(self, order_data: Dict[str, Any]) -> List[str]:
        """构建价格信息"""
        info_lines = []
        
        try:
            # 安全的类型转换函数
            def safe_int_convert(value, default=0):
                try:
                    if isinstance(value, str):
                        return int(value) if value.strip() else default
                    elif isinstance(value, (int, float)):
                        return int(value)
                    else:
                        return default
                except (ValueError, TypeError):
                    return default
            
            # 从api_data中获取价格信息
            api_data = order_data.get('api_data', {})
            api_total_price = 0
            api_mem_price = 0
            
            if api_data and isinstance(api_data, dict):
                api_mem_price = safe_int_convert(api_data.get('mem_totalprice', 0))
                api_total_price = safe_int_convert(api_data.get('totalprice', 0))
            
            # 检查会员状态
            has_member_card = False
            if hasattr(self.main_window, 'member_info') and self.main_window.member_info:
                has_member_card = self.main_window.member_info.get('has_member_card', False)
                if not has_member_card:
                    raw_data = self.main_window.member_info.get('raw_data')
                    has_member_card = raw_data is not None and isinstance(raw_data, dict)
            
            # 显示原价
            if api_total_price > 0:
                original_price_yuan = api_total_price / 100.0
                info_lines.append(f"原价: ¥{original_price_yuan:.2f}")
            else:
                # 备选方案
                amount = order_data.get('amount', order_data.get('total_price', 0))
                if isinstance(amount, str):
                    try:
                        amount = float(amount) / 100
                    except:
                        amount = 0
                if amount > 0:
                    info_lines.append(f"原价: ¥{amount:.2f}")
            
            # ⚠️ 【同步维护点2】券信息 - 必须与main_modular.py第1521行保持一致
            # 修复：正确获取券信息
            coupon_count = 0
            has_coupon_info = False

            print(f"[订单详情管理器] 检查券信息...")
            print(f"[订单详情管理器] 主窗口类型: {type(self.main_window)}")
            print(f"[订单详情管理器] 主窗口是否有selected_coupons: {hasattr(self.main_window, 'selected_coupons')}")
            if hasattr(self.main_window, 'selected_coupons'):
                print(f"[订单详情管理器] selected_coupons值: {self.main_window.selected_coupons}")
            print(f"[订单详情管理器] 主窗口是否有current_coupon_info: {hasattr(self.main_window, 'current_coupon_info')}")
            if hasattr(self.main_window, 'current_coupon_info'):
                print(f"[订单详情管理器] current_coupon_info值: {self.main_window.current_coupon_info}")

            # 从主窗口获取券选择状态
            if hasattr(self.main_window, 'selected_coupons') and self.main_window.selected_coupons:
                coupon_count = len(self.main_window.selected_coupons)
                has_coupon_info = True
                print(f"[订单详情管理器] 从主窗口获取券数量: {coupon_count}")
            elif order_data.get('selected_coupons'):
                coupon_count = len(order_data.get('selected_coupons', []))
                has_coupon_info = True
                print(f"[订单详情管理器] 从订单数据获取券数量: {coupon_count}")
            else:
                print(f"[订单详情管理器] 未找到券信息")

            # 获取券抵扣信息 - 🆕 支持沃美券绑定结果格式
            discount_price_yuan = 0
            pay_amount_yuan = 0
            used_voucher_codes = []

            if has_coupon_info and hasattr(self.main_window, 'current_coupon_info') and self.main_window.current_coupon_info:
                # 🆕 检查是否为沃美券绑定结果
                womei_bind_result = self.main_window.current_coupon_info.get('womei_bind_result')

                if womei_bind_result and womei_bind_result.get('success'):
                    # 🆕 使用沃美券绑定结果的价格信息
                    price_info = womei_bind_result.get('price_info', {})
                    voucher_info = womei_bind_result.get('voucher_info', {})

                    # 获取价格信息（元）
                    original_price = price_info.get('order_total_price', 0)
                    pay_amount_yuan = price_info.get('order_payment_price', 0)
                    discount_price_yuan = voucher_info.get('use_total_price', 0)
                    used_voucher_codes = voucher_info.get('use_codes', [])

                    print(f"[订单详情管理器] 🆕 沃美券信息: 原价={original_price}, 支付={pay_amount_yuan}, 优惠={discount_price_yuan}")

                else:
                    # 🔄 兼容原有格式（传统券系统）
                    coupon_data = self.main_window.current_coupon_info.get('resultData', {})
                    if coupon_data:
                        # 获取券抵扣金额（分转元）
                        discount_price_fen = int(coupon_data.get('discountprice', '0') or '0')
                        discount_price_yuan = discount_price_fen / 100.0

                        # 获取实付金额（分转元）
                        pay_amount_fen = int(coupon_data.get('paymentAmount', '0') or '0')

                        # 检查会员支付金额
                        if has_member_card:
                            mem_payment_fen = int(coupon_data.get('mempaymentAmount', '0') or '0')
                            if mem_payment_fen != 0:
                                pay_amount_fen = mem_payment_fen  # 会员优先使用会员支付金额

                        pay_amount_yuan = pay_amount_fen / 100.0

            # 显示券信息
            if coupon_count > 0:
                info_lines.append(f"使用券: {coupon_count}张")
                if discount_price_yuan > 0:
                    info_lines.append(f"券优惠: -¥{discount_price_yuan:.2f}")

                # 🆕 显示券码信息（如果有）
                if used_voucher_codes:
                    if len(used_voucher_codes) <= 2:
                        info_lines.append(f"券码: {', '.join(used_voucher_codes)}")
                    else:
                        info_lines.append(f"券码: {', '.join(used_voucher_codes[:2])}...")

            # 实付金额
            if coupon_count > 0 and has_coupon_info:
                # 有券的情况
                if pay_amount_yuan == 0:
                    info_lines.append(f"实付金额: ¥0.00 (纯券支付)")
                else:
                    final_amount = f"实付金额: ¥{pay_amount_yuan:.2f}"
                    if has_member_card and pay_amount_yuan != (api_total_price / 100.0):
                        final_amount += " (会员价)"
                    info_lines.append(final_amount)
            else:
                # 无券的情况 - 检查会员价格
                if has_member_card and api_mem_price > 0:
                    # 有会员卡且有会员价格，显示会员价
                    member_amount = api_mem_price / 100.0
                    info_lines.append(f"实付金额: ¥{member_amount:.2f} (会员价)")
                else:
                    # 无会员卡或无会员价格，显示原价
                    if api_total_price > 0:
                        total_amount = api_total_price / 100.0
                        info_lines.append(f"实付金额: ¥{total_amount:.2f}")
                    else:
                        # 备选方案
                        amount = order_data.get('amount', 0)
                        if isinstance(amount, str):
                            try:
                                amount = float(amount) / 100
                            except:
                                amount = 0
                        info_lines.append(f"实付金额: ¥{amount:.2f}")
            
            return info_lines
            
        except Exception as e:
            print(f"[订单详情管理器] 构建价格信息失败: {e}")
            return ["价格信息: 计算失败"]
    
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
