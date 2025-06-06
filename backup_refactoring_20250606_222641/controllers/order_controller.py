#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
订单控制器 - 处理订单相关的业务逻辑
"""

from typing import Dict, List, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from utils.signals import event_bus, event_handler
from services.order_api import (
    create_order, get_unpaid_order_detail, get_coupons_by_order,
    bind_coupon, get_order_list, get_order_detail, get_order_qrcode_api,
    cancel_all_unpaid_orders, get_coupon_prepay_info, pay_order
)
from services.ui_utils import MessageManager


class OrderController(QObject):
    """订单控制器"""
    
    # 信号定义
    order_created = pyqtSignal(dict)  # 订单创建成功
    order_submitted = pyqtSignal(dict)  # 订单提交成功
    order_paid = pyqtSignal(dict)  # 订单支付成功
    order_cancelled = pyqtSignal(str)  # 订单取消
    order_error = pyqtSignal(str, str)  # 订单错误 (title, message)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 当前状态
        self.current_order = None
        self.current_account = None
        self.selected_coupons = []
        self.selected_coupons_info = None
        
        # 连接事件总线
        self._connect_events()
        
        print("[订单控制器] 初始化完成")
    
    def _connect_events(self):
        """连接事件总线"""
        event_bus.account_selected.connect(self._on_account_selected)
        event_bus.coupon_selected.connect(self._on_coupon_selected)
        event_bus.order_submitted.connect(self._handle_order_submission)
    
    @event_handler("account_selected")
    def _on_account_selected(self, account_data: dict):
        """账号选择处理"""
        self.current_account = account_data
        print(f"[订单控制器] 账号已选择: {account_data.get('phone', 'N/A')}")
    
    @event_handler("coupon_selected")
    def _on_coupon_selected(self, coupon_list: List[dict]):
        """券选择处理"""
        self.selected_coupons = coupon_list
        print(f"[订单控制器] 已选择 {len(coupon_list)} 张券")
    
    @event_handler("order_submitted")
    def _handle_order_submission(self, order_data: dict):
        """处理订单提交"""
        try:
            # 验证必要信息
            if not self.current_account:
                self.order_error.emit("提交失败", "请先选择账号")
                return
            
            seats = order_data.get('seats', [])
            if not seats:
                self.order_error.emit("提交失败", "请先选择座位")
                return
            
            session_info = order_data.get('session_info', {})
            if not session_info:
                self.order_error.emit("提交失败", "请先选择场次")
                return
            
            # 创建订单
            result = self.create_order(seats, session_info)
            
            if result:
                self.order_submitted.emit(result)
                event_bus.order_created.emit(result)
            else:
                self.order_error.emit("创建失败", "订单创建失败")
                
        except Exception as e:
            print(f"[订单控制器] 处理订单提交错误: {e}")
            self.order_error.emit("处理错误", f"处理订单时出错: {str(e)}")
    
    def create_order(self, seats: List[dict], session_info: dict) -> Optional[dict]:
        """创建订单"""
        try:
            print(f"[订单控制器] 开始创建订单")
            print(f"[订单控制器] 座位数量: {len(seats)}")
            print(f"[订单控制器] 场次信息: {session_info.get('session_text', 'N/A')}")
            
            # 构建订单参数
            order_params = {
                'account': self.current_account,
                'seats': seats,
                'session_info': session_info,
                'coupons': self.selected_coupons
            }
            
            # 调用API创建订单
            result = create_order(order_params)
            
            if result and result.get('resultCode') == '0':
                # 订单创建成功
                order_data = result.get('resultData', {})
                self.current_order = order_data
                
                print(f"[订单控制器] 订单创建成功: {order_data.get('order_id', 'N/A')}")
                
                # 获取订单详情
                self._load_order_detail(order_data.get('order_id'))
                
                return order_data
            else:
                error_msg = result.get('resultDesc', '创建订单失败') if result else '网络错误'
                print(f"[订单控制器] 订单创建失败: {error_msg}")
                return None
                
        except Exception as e:
            print(f"[订单控制器] 创建订单错误: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_order_detail(self, order_id: str):
        """加载订单详情"""
        try:
            if not order_id:
                return
            
            # 获取订单详情
            detail_result = get_order_detail({'order_id': order_id})
            
            if detail_result and detail_result.get('resultCode') == '0':
                order_detail = detail_result.get('resultData', {})
                
                # 发布订单详情更新事件
                event_bus.order_detail_updated.emit(order_detail)
                
                # 获取可用券列表
                self._load_available_coupons(order_detail)
                
        except Exception as e:
            print(f"[订单控制器] 加载订单详情错误: {e}")
    
    def _load_available_coupons(self, order_detail: dict):
        """加载可用券列表"""
        try:
            if not self.current_account or not order_detail:
                return
            
            # 获取订单可用券
            coupon_result = get_coupons_by_order({
                'account': self.current_account,
                'order': order_detail
            })
            
            if coupon_result and coupon_result.get('resultCode') == '0':
                coupons = coupon_result.get('resultData', [])
                
                # 发布券列表更新事件
                event_bus.coupon_list_updated.emit(coupons)
                
        except Exception as e:
            print(f"[订单控制器] 加载可用券错误: {e}")
    
    def pay_order(self, order_id: str) -> bool:
        """支付订单"""
        try:
            if not self.current_account or not order_id:
                return False
            
            # 构建支付参数
            pay_params = {
                'account': self.current_account,
                'order_id': order_id,
                'coupons': self.selected_coupons
            }
            
            # 调用支付API
            result = pay_order(pay_params)
            
            if result and result.get('resultCode') == '0':
                # 支付成功
                print(f"[订单控制器] 订单支付成功: {order_id}")
                
                # 获取取票码
                self._get_order_qrcode(order_id)
                
                # 发布支付成功事件
                self.order_paid.emit({'order_id': order_id})
                event_bus.order_paid.emit(order_id)
                
                # 清空当前订单
                self.current_order = None
                self.selected_coupons.clear()
                
                return True
            else:
                error_msg = result.get('resultDesc', '支付失败') if result else '网络错误'
                self.order_error.emit("支付失败", error_msg)
                return False
                
        except Exception as e:
            print(f"[订单控制器] 支付订单错误: {e}")
            self.order_error.emit("支付错误", f"支付处理失败: {str(e)}")
            return False
    
    def _get_order_qrcode(self, order_id: str):
        """获取订单取票码"""
        try:
            qr_result = get_order_qrcode_api({'order_id': order_id})
            
            if qr_result and qr_result.get('resultCode') == '0':
                qr_data = qr_result.get('resultData', {})
                qr_code = qr_data.get('qrcode', '')
                
                if qr_code:
                    # 发布取票码事件
                    event_bus.emit_custom('qrcode_received', {
                        'order_id': order_id,
                        'qrcode': qr_code
                    })
                    
        except Exception as e:
            print(f"[订单控制器] 获取取票码错误: {e}")
    
    def cancel_order(self, order_id: str) -> bool:
        """取消订单"""
        try:
            # 这里可以添加取消订单的API调用
            # 目前使用取消所有未支付订单的API
            
            if not self.current_account:
                return False
            
            result = cancel_all_unpaid_orders({
                'account': self.current_account
            })
            
            if result and result.get('resultCode') == '0':
                print(f"[订单控制器] 订单取消成功: {order_id}")
                
                # 发布取消事件
                self.order_cancelled.emit(order_id)
                event_bus.order_cancelled.emit(order_id)
                
                # 清空当前订单
                if self.current_order and self.current_order.get('order_id') == order_id:
                    self.current_order = None
                    self.selected_coupons.clear()
                
                return True
            else:
                error_msg = result.get('resultDesc', '取消失败') if result else '网络错误'
                self.order_error.emit("取消失败", error_msg)
                return False
                
        except Exception as e:
            print(f"[订单控制器] 取消订单错误: {e}")
            self.order_error.emit("取消错误", f"取消订单失败: {str(e)}")
            return False
    
    def get_order_list(self) -> List[dict]:
        """获取订单列表"""
        try:
            if not self.current_account:
                return []
            
            result = get_order_list({'account': self.current_account})
            
            if result and result.get('resultCode') == '0':
                orders = result.get('resultData', [])
                
                # 发布订单列表更新事件
                event_bus.order_list_updated.emit(orders)
                
                return orders
            else:
                print(f"[订单控制器] 获取订单列表失败: {result.get('resultDesc', '未知错误') if result else '网络错误'}")
                return []
                
        except Exception as e:
            print(f"[订单控制器] 获取订单列表错误: {e}")
            return []
    
    def bind_coupon(self, coupon_code: str) -> bool:
        """绑定券"""
        try:
            if not self.current_account:
                self.order_error.emit("绑定失败", "请先选择账号")
                return False
            
            result = bind_coupon({
                'account': self.current_account,
                'coupon_code': coupon_code
            })
            
            if result and result.get('resultCode') == '0':
                print(f"[订单控制器] 券绑定成功: {coupon_code}")
                
                # 发布券绑定事件
                event_bus.coupon_bound.emit({
                    'coupon_code': coupon_code,
                    'result': result
                })
                
                return True
            else:
                error_msg = result.get('resultDesc', '绑定失败') if result else '网络错误'
                self.order_error.emit("绑定失败", error_msg)
                return False
                
        except Exception as e:
            print(f"[订单控制器] 绑定券错误: {e}")
            self.order_error.emit("绑定错误", f"绑定券失败: {str(e)}")
            return False
